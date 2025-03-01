# Author: Liran
# Description: This file contains the LLMProvider class which is used to interact with different LLM providers (ollama, openai, gemini)
import os
import ollama
import requests
from langchain_openai import ChatOpenAI

class LLMProvider:
    def __init__(self, provider: str):
        self.provider = provider
        # Select the appropriate LLM based on the provider
        self.llm = self.get_llm_chat(provider)

    # Select the LLM provider (openai, ollama, gemini)
    def get_llm_chat(self, provider: str):
        # If the provider is 'ollama', return None (No LLM)
        if provider == "ollama":
            ollama.pull("llama3.1")
            return None
            # Raise error for unsupported 'google' provider
        elif provider == "google":
            raise NotImplementedError()
            # If the provider is 'openai', return the OpenAI model (gpt-3.5-turbo)
        elif provider == "openai":
            return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        # If the provider is 'gemini', return None and let the invoke method handle it
        elif provider == "gemini":
            return None
        else:
            raise NotImplementedError()

    # Invoke the LLM (handles ollama, openai, and gemini)
    def invoke(self, prompt: str) -> str:
        if self.provider == "ollama":
            return self.invoke_ollama(prompt)
        elif self.provider == "openai":
            return self.invoke_openai(prompt)
        elif self.provider == "gemini":
            return self.invoke_gemini(prompt)
        else:
            raise NotImplementedError("Provider not supported")

    # Call Ollama API with the prompt
    def invoke_ollama(self, prompt):
        response = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': prompt}])
        return response["message"]["content"]

        # Call OpenAI model using the llm object
    def invoke_openai(self, prompt) -> str:
        response = self.llm.invoke(prompt).content
        return response

    # Call Gemini API using google.generativeai
    def invoke_gemini(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.environ['GEMINI_API_KEY']}"
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for a bad response
        # Extract the generated text from the response
        return response.json()['candidates'][0]['content']['parts'][0]['text']



# Usage example
if __name__ == "__main__":
    custom_llm = LLMProvider(provider="gemini")  # Use "gemini" for Gemini API

    instruction = """       
        Generate SQL query from the question, return ONLY SQL query.    
    """

    question = """       
        How many student learning on Boston ?      
    """

    context = """       
        table description: Table that describe student data        
        table name: Students       
        columns: Name     
    """

    final_prompt = f"""       
        Instruction: {instruction}        
        Context: {context}        
        Question: {question}        
        Answer:     
    """

    print(custom_llm.invoke(final_prompt))  # Should work with Gemini API if provider is set to 'gemini'
