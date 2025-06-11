from ragas import EvaluationDataset
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness
from chromadb_service import ChromaDBService
from llm_service import LLMService
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
import chromadb

# chroma_service = ChromaDBService()
llm_service = LLMService()
CHROMA_HOST = "http://localhost:8000"
client = chromadb.HttpClient(host="localhost", port=8000)

api_key = os.environ["OPENAI_API_KEY_TEG"]

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=api_key
)

embedding_function = OpenAIEmbeddings(
    model="text-embedding-ada-002",  # Ensure this is correct
    openai_api_key=api_key
)

sample_queries = [
    "What are some good cat creature cards to use in commander deck?",
    "What color of cards can I use if my commanders colors are blue and black? And why can't I use every color of the card?",
    "Give me three examples of Elf Creature cards with cmc = 3.0"

]

expected_responses = [
    "Some strong Cat creature cards to consider for a Commander deck include Arahbo, Roar of the World, Jetmir, Nexus of Revels, and Ygra, Eater of All. Arahbo, Roar of the World is an excellent commander thanks to the eminence ability, which boosts Cats even while Arahbo is in the command zone. Jetmir, Nexus of Revels rewards you for going wide with creatures. Ygra, Eater of All is a mythic Cat creature that synergizes well with Food-based combos.",
    "If your commander's colors are blue and black, you can only use cards whose color identity is blue, black, or colorless. You cannot include cards that have white, red, or green in their color identity. This restriction exists because a Commander deck must only include cards whose color identities match the color identity of the commander. A card’s color identity includes its mana cost and any colored mana symbols in its rules text. This rule helps preserve balance and flavor in deck construction by tying the deck thematically and mechanically to its commander.",
    """
    Greenweaver Druid

    CMC: 3
    Type: Creature — Elf Druid
    Ability: {T}: Add {G}{G}.
    Set: Zendikar

    Elvish Harbinger

    CMC: 3
    Type: Creature — Elf Druid
    Ability: When this creature enters, you may search your library for an Elf card, reveal it, then shuffle and put that card on top. {T}: Add one mana of any color.
    Set: Duel Decks Anthology: Elves vs. Goblins
    
    (Possible bonus) Llanowar Envoy
    
    CMC: 3
    Type: Creature — Elf
    Ability: {T}: Add one mana of any color.
    Set: Dominaria
    """
]


def query_collections(query_text: str, collections_to_query: list[str]) -> list[str]:
    query_embedding = embedding_function.embed_query(query_text)
    retrieved_docs = []
    
    for name in collections_to_query:
        collection = client.get_collection(name)
        results = collection.query(query_embeddings=[query_embedding], n_results=10)
        documents = results.get("documents", [[]])[0]  # List of lists
        retrieved_docs.extend(documents)
    
    return retrieved_docs


def eval_refined_query(queries, references):
    dataset = []
    
    for query, reference in zip(queries, references):
        refined_query = llm_service.refine_query(query)
        docs = query_collections(refined_query, ["Articles", "Cards"])
        context = "\n".join(docs)
        
        answer = llm_service.generate_answer(context=context, question=query)
        print(answer)
        dataset.append({
            "user_input": query,
            "retrieved_contexts": docs,
            "response": answer,
            "reference": reference
        })
    
    evaluation_dataset = EvaluationDataset.from_list(dataset)
    evaluator_llm = LangchainLLMWrapper(llm)
    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],
        llm=evaluator_llm
    )
    return result


def eval_query(queries, references):
    dataset = []
    
    for query, reference in zip(queries, references):
        docs = query_collections(query, ["Articles", "Cards"])
        context = "\n".join(docs)
        
        answer = llm_service.generate_answer(context=context, question=query)
        print(answer)
        dataset.append({
            "user_input": query,
            "retrieved_contexts": docs,
            "response": answer,
            "reference": reference
        })
    
    evaluation_dataset = EvaluationDataset.from_list(dataset)
    evaluator_llm = LangchainLLMWrapper(llm)
    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],
        llm=evaluator_llm
    )
    return result


if __name__ == "__main__":
    print("Running evaluation with refined queries:")
    refined_result = eval_refined_query(sample_queries, expected_responses)
    print(refined_result)
    
    print("\nRunning evaluation with raw queries:")
    raw_result = eval_query(sample_queries, expected_responses)
    print(raw_result)
