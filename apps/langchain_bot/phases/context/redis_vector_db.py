# Author: Abhishek
# Description: The first step is to create an redis vector database for embedding documents by reading the JSON file data in the init method.
# This is the initial setup.
# Then, we have a class that has already loaded the "database". Now we can query the database to get the top k similar documents.
import json
from sentence_transformers import SentenceTransformer
from apps.langchain_bot.phases.context.table_formatter import TableFormatter
from apps.langchain_bot.env import  redis_url
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import redis
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.result import Result
from typing import List


class RedisDocumentRetriever:
    def __init__(self, redis_url:str,json_file_path='./data/data_for_embedding/tableinfo.json', model_name='./models/embedding_model/embedding_question2context'):
        # Initialize the SentenceTransformer model with the given model name
        self.model = SentenceTransformer(model_name)
        # Connect to the Redis server using the specified host and port
        self.client = redis.Redis.from_url(url=redis_url, decode_responses=True)
        # Load documents from the specified JSON file path
        self.documents = self.load_json(json_file_path)
        # Create document embeddings and store them in Redis
        self.create_doc_embeddings()
        # Create an index for the stored embeddings in Redis
        self.create_index()
        # Initialize the TableFormatter instance
        self.table_formatter = TableFormatter()

    def load_json(self, json_file_path):
        # Open the JSON file and load its content
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            # Create a pipeline to batch Redis commands
            pipeline = self.client.pipeline()
            # Iterate over the data and store each item in Redis with a unique key
            for i, ipedsdata in enumerate(data, start=1):
                redis_key = f"ipedsdata:{i:03}"
                pipeline.json().set(redis_key, "$", ipedsdata)
            # Execute the pipeline commands
            pipeline.execute()
            # Store the sorted keys of the inserted data
            self.keys = sorted(self.client.keys("ipedsdata:*"))
        return data

    def create_doc_embeddings(self):
        # Initialize dictionaries to store embeddings and descriptions
        embeddings = {}
        descriptions = []
        # Iterate over the loaded documents
        for doc in self.documents:
            table_info = doc.get('Table_Info', [])
            if table_info:
                # Append the table description to the descriptions list
                descriptions.append(table_info[0]['Table_Description'])
                # Generate metadata for the table
                metadata = self.metadata_func(table_info[0], {})
                # Store the metadata in the embeddings dictionary
                embeddings[table_info[0]['Table_Name']] = {
                    'metadata': metadata
                }

        # Encode the descriptions to generate embedding vectors
        embedding_vectors = self.model.encode(descriptions).astype(np.float32)
        # Get the dimension of the embedding vectors
        self.vector_dim = len(embedding_vectors[0]) if embedding_vectors.size > 0 else 0
        # Create a pipeline to batch Redis commands
        pipeline = self.client.pipeline()
        # Iterate over the keys, embedding vectors, and embeddings dictionary
        for key, embedding, (table_name, data) in zip(self.keys, embedding_vectors, embeddings.items()):
            # Store the embedding vector and metadata in Redis
            pipeline.json().set(key, "$.description_embeddings", embedding.tolist())
            pipeline.json().set(key, "$.Table_Name", json.dumps(table_name))
            pipeline.json().set(key, "$.Table_Description", json.dumps(data['metadata']['Table_Description']))
            pipeline.json().set(key, "$.Column_Names", json.dumps(data['metadata']['Column_Names']))
            pipeline.json().set(key, "$.Column_Description", json.dumps(data['metadata']['Column_Description']))
        # Execute the pipeline commands
        pipeline.execute()

    def metadata_func(self, record: dict, metadata: dict) -> dict:
        # Helper function to retrieve column information
        def column_retriever(ls):
            cname = []
            dtype = []
            cdesc = []
            for i in range(len(ls)):
                cname.append(record.get("Columns")[i].get("Column_Name"))
                dtype.append(record.get("Columns")[i].get("Data_Type"))
                cdesc.append(record.get("Columns")[i].get("Column_Description"))
            return cname, dtype, cdesc
        
        # Retrieve column names, data types, and descriptions
        cname, dtype, cdesc = column_retriever(record.get("Columns", []))
        
        # Store the retrieved information in the metadata dictionary
        metadata["Table_Name"] = record.get("Table_Name")
        metadata["Table_Description"] = record.get("Table_Description")
        metadata["Column_Names"] = str(cname)
        metadata["Data_Type"] = str(dtype)
        metadata["Column_Description"] = str(cdesc)
        return metadata

    def create_index(self):
        try:
            # Check if the index already exists and drop it if it does
            self.client.ft("idx:ipedsdata").info()
            self.client.ft("idx:ipedsdata").dropindex()
        except redis.exceptions.ResponseError:
            pass
        # Define the schema for the index
        schema = (
            TextField("$.Table_Name", as_name="table_name"),
            TextField("$.Table_Description", as_name="table_description"),
            TextField("$.Column_Names", as_name="column_names"),
            TextField("$.Column_Description", as_name="column_description"),
            VectorField(
                "$.description_embeddings", 
                "FLAT", 
                {"TYPE": "FLOAT32", "DIM": self.vector_dim, "DISTANCE_METRIC": "COSINE"},
                as_name="vector"
            )
        )
        
        # Define the index definition with the specified prefix and type
        definition = IndexDefinition(prefix=["ipedsdata:"], index_type=IndexType.JSON)
        # Create the index in Redis
        self.client.ft("idx:ipedsdata").create_index(fields=schema, definition=definition)
        
    def convert_docs_to_strings(self, result: Result) -> List[str]:
        # Convert the search result documents to a list of dictionaries
        tables_context = [
            {
                "Table_Name": doc["table_name"],
                "Table_Description": doc["table_description"],
                "Column_Names": doc["column_names"],
                "Column_Description": doc["column_description"]
            } for doc in result.docs
        ]
        return tables_context

    def find_top_k_similar(self, question: str, k=4) -> str:
        # Encode the question to generate its embedding vector
        question_embedding = self.model.encode([question]).astype(np.float32).tobytes()
        
        # Define the query to find the top k similar documents based on the embedding vector
        query = (
            Query(f"(*)=>[KNN {k} @vector $query_vector AS vector_score]")
            .sort_by("vector_score")
            .return_fields("vector_score", "table_name", "table_description", "column_names", "column_description")
            .dialect(2)
        )
        # Execute the query and get the search results
        res = self.client.ft("idx:ipedsdata").search(query, query_params={"query_vector": question_embedding})
        # Convert the search results to a string format
        context_str = self.table_formatter.docs2str(self.convert_docs_to_strings(res))
        return context_str
 
# Usage
if __name__ == "__main__":
    retriever = RedisDocumentRetriever(redis_url)
    question = "Which schools require high school GPA?"
    context = retriever.find_top_k_similar(question, k=3)
    print(context)
