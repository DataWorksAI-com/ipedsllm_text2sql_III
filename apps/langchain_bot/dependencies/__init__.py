#Author: Liran
#This file is used to import all the dependencies that are used in the langchain_bot app. This is done to make the code more modular and easy to read. This file is imported in the main file of the app to use the dependencies in the app.
import os
from apps.langchain_bot.env import db_url
from apps.langchain_bot.phases.context.vectors_store_sentence_transformer import DocumentRetriever
from apps.langchain_bot.utils.db_information.database_information_retrieval import DatabaseInformationRetrieval
from apps.langchain_bot.utils.llm_provider.llm_provider import LLMProvider
# Create an instance of the Postgres database class
database_information_retrieval = DatabaseInformationRetrieval(db_url=db_url).db
document_retriever = DocumentRetriever()
llm = LLMProvider(provider=os.getenv("LLM_PROVIDER",None))
