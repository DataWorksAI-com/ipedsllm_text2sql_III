# Author: Liran
# Description: The first step is to create an in-memory database for embedding documents by reading the JSON file data in the init method.
# This is the initial setup.
# Then, we have a class that has already loaded the "database". Now we can query the database to get the top k similar documents.
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from apps.langchain_bot.phases.context.table_formatter import TableFormatter
import os
class DocumentRetriever:
    # initialize the retriever by loading the custom model (fine-tuned in Google Colab) and the data, the model should be downloaded from Readme file
    # Create an in memory database
    def __init__(self, json_file_path = './data/data_for_embedding/tableinfo.json', model_name='dataWorksAI/embedding_model_tabledescriptions_questions_iped6tables'):

        # Load the model and the JSON data
        
        self.model = SentenceTransformer(model_name, token=os.environ.get("HF_TOKEN"))
        self.documents = self.load_json(json_file_path)
        #Generate embeddings for each document's table description
        self.doc_embeddings = self.create_doc_embeddings()
        self.table_formatter = TableFormatter()


    def load_json(self, json_file_path):
        # Load the JSON file containing documents
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        return data
 
    def create_doc_embeddings(self):
        # Create embeddings for "table_description" in each document and store the entire document
        embeddings = {}
        for doc in self.documents:
            table_info = doc.get('Table_Info')
            if table_info:
                table_description=table_info[0]['Table_Description']
                embedding = self.model.encode(table_description, convert_to_tensor=True).cpu().numpy()
                
                 # Store the embedding and associated metadata in the embeddings dictionary
                embeddings[table_info[0]['Table_Name']] = {
                    'embedding': embedding,
                   'metadata': self.metadata_func(table_info[0],{})
                }
        return embeddings
        
    # functiom to retrieve metadata for a given document to be stored alongside the embedding
    def metadata_func(self, record: dict, metadata: dict) -> dict:
        def column_retriever(ls):
            cname = []
            dtype = []
            cdesc = []
            for i in range(len(ls)):
                cname.append(record.get("Columns")[i].get("Column_Name"))
                dtype.append(record.get("Columns")[i].get("Data_Type"))
                cdesc.append(record.get("Columns")[i].get("Column_Description"))
            return cname, dtype, cdesc
            
        # Extract column metadata (names, data types, descriptions)
        cname, dtype, cdesc = column_retriever(record.get("Columns"))

        metadata["Table_Name"] = record.get("Table_Name")
        metadata["Table_Description"] = record.get("Table_Description")
        metadata["Column_Names"] = str(cname)
        metadata["Data_Type"] = str(dtype)
        metadata["Column_Description"] = str(cdesc)
        # metadata["share"] = record.get("share")
        return metadata

    # function to find the top k most similar documents to a given question based on their table descriptions.

    def find_top_k_similar(self, question:str, k=4) -> str:
        # Encode the input question
        question_embedding = self.model.encode(question, convert_to_tensor=True).cpu().numpy()
        
        # Calculate cosine similarities between the question and each document's "table_description"
        similarities = {}
        for doc_id, doc_info in self.doc_embeddings.items():
            doc_embedding = doc_info['embedding']
            similarity = cosine_similarity(
                [question_embedding], [doc_embedding])[0][0]
            similarities[doc_id] = similarity
        
        # Sort documents by similarity and return the top k
        sorted_docs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        top_k_docs = [self.doc_embeddings[doc_id]['metadata'] for doc_id, _ in sorted_docs[:k]]

        context_str =  self.table_formatter.docs2str(top_k_docs)
        return context_str

 
# Usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    retriever = DocumentRetriever()
    question = "Which schools require high school GPA?"
    context = retriever.find_top_k_similar(question, k=3)
    print(context)
