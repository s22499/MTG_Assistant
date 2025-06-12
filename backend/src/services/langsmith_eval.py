from langsmith import Client, wrappers
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
from openai import OpenAI
import os
from dotenv import load_dotenv
from chromadb_service import ChromaDBService
from llm_service import LLMService
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import chromadb

load_dotenv(r"D:\TEGPROJECT\MTG_Assistant\.env")


langsmith_tracing = os.getenv("LANGSMITH_TRACING")
langsmith_endpoint = os.getenv("LANGSMITH_ENDPOINT")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY_TEG")

llm_service = LLMService()
CHROMA_HOST = "http://localhost:8000"
client = chromadb.HttpClient(host="localhost", port=8000)

langsmith_client = Client(api_key=langsmith_api_key)

dataset = langsmith_client.create_dataset(dataset_name="Sample questions8", description="MTG questions for rag")


examples = [

    {
        "inputs": {"question" : "What are some good cat creature cards to use in commander deck?"},
        "outputs": {"answer": "Some strong Cat creature cards to consider for a Commander deck include Arahbo, Roar of the World, Jetmir, Nexus of Revels, and Ygra, Eater of All. Arahbo, Roar of the World is an excellent commander thanks to the eminence ability, which boosts Cats even while Arahbo is in the command zone. Jetmir, Nexus of Revels rewards you for going wide with creatures. Ygra, Eater of All is a mythic Cat creature that synergizes well with Food-based combos."},
    },

    {
        "inputs": {"question" : "What color of cards can I use if my commanders colors are blue and black? And why can't I use every color of the card?"},
        "outputs": {"answer": "If your commander's colors are blue and black, you can only use cards whose color identity is blue, black, or colorless. You cannot include cards that have white, red, or green in their color identity. This restriction exists because a Commander deck must only include cards whose color identities match the color identity of the commander. A card’s color identity includes its mana cost and any colored mana symbols in its rules text. This rule helps preserve balance and flavor in deck construction by tying the deck thematically and mechanically to its commander."},
    },

    {
        "inputs": {"question" : "Give me three examples of Elf Creature cards with cmc = 3.0"},
        "outputs": {"answer": """
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

                """},
    },

]


langsmith_client.create_examples(dataset_id=dataset.id, examples=examples)

openai_client = wrappers.wrap_openai(OpenAI(api_key=openai_api_key))

def target(inputs: dict) -> dict:
    user_query = inputs.get("input")
    result = llm_service.run_rag_pipeline(user_query)
    return {
        "output": result["response"],
        "original_question": result["original_question"],
        "refined_candidates": result["refined_candidates"],
        "best_query": result["best_query"]
    }


def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict):
    evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        model="openai:o3-mini",
        feedback_key="correctness"
    )
    eval_result = evaluator(
        inputs=inputs,
        outputs=outputs,
        reference_outputs=reference_outputs
    )
    return eval_result
#%%
experiment_results = langsmith_client.evaluate(
    target,
    data="Sample questions8",
    evaluators=[
        correctness_evaluator,
        # you can add multiple evaluators here
    ],
    experiment_prefix="first-eval-in-langsmith",
    max_concurrency=2,
)

langsmith_client.delete_dataset(dataset_name="Sample questions8")