from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
import chromadb.utils.embedding_functions as embedding_function
import chromadb
import os

# === Setup ===
OPEN_AI_KEY = os.environ["OPENAI_API_KEY"]
CHROMA_HOST = "http://localhost:8000"  # or use host.docker.internal

COLLECTIONS = ["Cards", "Articles"]
QUERY = "Can you provide card details of Mizzix's Mastery?"
TOP_K = 3

# === LangChain tools ===
embedding_function = embedding_function.OpenAIEmbeddingFunction(api_key=OPEN_AI_KEY)
model = ChatOpenAI(api_key=OPEN_AI_KEY)

# === Connect to remote Chroma via HttpClient ===
client = chromadb.HttpClient(host="localhost", port=8000)

all_results = []

# === Query each collection ===
for collection_name in COLLECTIONS:
    collection = client.get_collection(name=collection_name, embedding_function=embedding_function)
    query_result = collection.query(query_texts=[QUERY], n_results=TOP_K)

    for i in range(len(query_result["documents"][0])):
        doc = query_result["documents"][0][i]
        metadata = query_result["metadatas"][0][i]
        distance = query_result["distances"][0][i]
        all_results.append((Document(page_content=doc, metadata=metadata or {}), distance, collection_name))


# === Sort & filter top results ===
all_results = sorted(all_results, key=lambda x: x[1])[:TOP_K]

if not all_results:
    print("No matching results found.")
    exit()

# === Build prompt ===
context_text = "\n\n---\n\n".join([doc.page_content for doc, _, _ in all_results])
prompt_template = ChatPromptTemplate.from_template("""
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
""")
prompt = prompt_template.format(context=context_text, question=QUERY)

# === Call LLM ===
response_text = model.predict(prompt)
sources = [f"{doc.metadata.get('source', 'unknown')} (from: {collection})" for doc, _, collection in all_results]

# === Output ===
print(f"Response: {response_text}")
print(f"Sources: {sources}")
