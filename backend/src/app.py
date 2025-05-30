from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.config.config_manager import ConfigManager
from src.services.chromadb_service import ChromaDBService
from src.services.llm_service import LLMService


app = FastAPI()
chroma_service = ChromaDBService()
llm_service = LLMService()

# Load configuration
config = ConfigManager("config.yaml")
chroma_host = config.get_value("chroma.host", "localhost")
chroma_port = config.get_value("chroma.port", 8000)


@app.get("/")
def root():
    return {
        "message": "Backend is running",
        "chroma_host": chroma_host,
        "chroma_port": chroma_port
    }


@app.post("/add")
async def add_document(request: Request):
    data = await request.json()
    text = data.get("text")
    doc_id = data.get("id", None)
    metadata = data.get("metadata", {})
    
    if not text:
        return {"error": "Missing 'text' field"}
    
    chroma_service.add_documents(
        collection_name="default",
        documents=[text],
        ids=[doc_id] if doc_id else None,
        metadatas=[metadata] if metadata else None
    )
    return {"status": "added"}


@app.post("/query")
async def query_chroma(request: Request):
    data = await request.json()
    query = data.get("query")
    
    if not query:
        return {"error": "Missing 'query' field"}
    
    collection = chroma_service.get_collection("default")
    results = collection.similarity_search(query, k=5)
    
    return {
        "results": [
            {"text": doc.page_content, "metadata": doc.metadata}
            for doc in results
        ]
    }


@app.post("/reset")
def reset_chroma():
    try:
        chroma_service.reset_collection(name="default")
        return {"status": "Collection reset successfully."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    question = data.get("question")
    context = data.get("context")
    if not question or not context:
        return {"error": "Missing 'question' or 'context'"}
    response = llm_service.generate_answer(context=context, question=question)
    return {"response": response}


@app.post("/refine")
async def refine(request: Request):
    data = await request.json()
    question = data.get("question")
    if not question:
        return {"error": "Missing 'question'"}
    refined = llm_service.refine_query(question)
    return {"refined_query": refined}

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    user_question = data.get("question")
    if not user_question:
        return {"error": "Missing 'question'"}
    
    refined_query = llm_service.refine_query(user_question)

    # Testowy kontekst
    context = """Lightning Bolt is a red instant card that deals 3 damage to any target. It costs {R} to cast and is often included in burn decks for its efficiency.

Counterspell is a blue instant card counters any spell. It's commonly used in control decks to stop opponent threats.

Control decks typically aim to prolong the game, counter spells, and win with a few powerful finishers like planeswalkers or hard-to-remove creatures.

In formats like Modern and Legacy, black-blue (Dimir) control decks use cards like Fatal Push, Thoughtseize, and Jace, the Mind Sculptor.

Instant-speed interaction is crucial for control decks to respond during the opponent's turn. Cards like Mana Leak, Cryptic Command, and Hero's Downfall are popular options.

Against aggro decks, control players prioritize early removal and card advantage through cantrips or card draw engines like Think Twice and Fact or Fiction.
"""

# TODO: Usunąć testowy kontekst i zastąpić contekstem stowrzonym przez Chromę

    answer = llm_service.generate_answer(context=context, question=user_question)

    return {
        "refined_query": refined_query,
        "response": answer,
        # "context_sources": [doc.metadata for doc in search_results]
    }