#%%
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
import openai
import os
import shutil

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


DATA_PATH = r"data/Articles"
OPEN_AI_KEY = os.environ['OPENAI_API_KEY_TEG']
def load_documents():
    loader = DirectoryLoader(
        DATA_PATH,
        glob="**/*.md",       
        recursive=True       
    )
    documents =  loader.load()
    return documents

docs = load_documents()
#wrapped_docs = [Document(page_content=doc, metadata={}) for doc in docs]
#print(wrapped_docs[1].page_content)
#%%
def split_text(documents: list[Document]):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks

chunks = split_text(documents=docs)

#%%

CHROMA_PATH = "chroma"
def createChromaDB(chunks):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    db = Chroma.from_documents(chunks, OpenAIEmbeddings(api_key=OPEN_AI_KEY), persist_directory=CHROMA_PATH)
    db.persist()
    print(f"Saved")

createChromaDB(chunks)
#%%
embedding_function = OpenAIEmbeddings(api_key=OPEN_AI_KEY)
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
query_text = "Which instants work well in a control deck in black and blue colors?"
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


#%%