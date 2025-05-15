#%%
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
import openai 
from dotenv import load_dotenv
import os
import shutil

OPEN_AI_KEY = os.environ['OPENAI_API_KEY_TEG']
CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

embedding_function = OpenAIEmbeddings(api_key=OPEN_AI_KEY)
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
query_text = "Provide types of potential strategies for a commander deck."
results = db.similarity_search_with_relevance_scores(query=query_text, k=3)
if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        
context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
prompt = prompt_template.format(context=context_text, question=query_text)
print(prompt)

model = ChatOpenAI(api_key=OPEN_AI_KEY)
response_text = model.predict(prompt)

sources = [doc.metadata.get("source", None) for doc, _score in results]
formatted_response = f"Response: {response_text}\nSources: {sources}"
print(formatted_response)