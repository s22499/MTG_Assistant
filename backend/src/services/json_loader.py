from langchain_community.document_loaders import JSONLoader
from langchain.schema import Document
from langchain_text_splitters import RecursiveJsonSplitter
from typing import List
import json

def load_json_documents(json_path: str) -> List[Document]:

    loader = JSONLoader(
        file_path=json_path,
        jq_schema=".[]",
        text_content=False,
    )

    documents = loader.load()
    print(f"Loaded {len(documents)} JSON documents from {json_path}")
    return documents


def split_json_documents(documents: List[Document], max_chunk_size: int = 1000) -> List[Document]:

    print(f"Processing {len(documents)} JSON documents...")
    
    all_cards = []
    error_count = 0
    
    for i, doc in enumerate(documents):
        try:
           
            json_obj = json.loads(doc.page_content)
            
            
            if isinstance(json_obj, list):
                for card in json_obj:
                    new_doc = Document(
                        page_content=json.dumps(card, ensure_ascii=False),
                        metadata=doc.metadata.copy()  # Preserve original metadata
                    )
                    all_cards.append(new_doc)
            else:
                # Single card case
                new_doc = Document(
                    page_content=json.dumps(json_obj, ensure_ascii=False),
                    metadata=doc.metadata.copy()
                )
                all_cards.append(new_doc)
                
        except Exception as e:
            error_count += 1
            print(f"Error processing document at index {i}: {e}")
            print(f"Problematic document content: {doc.page_content[:200]}...")  # Truncate for readability

    print(f"Processed {len(documents)} input documents into {len(all_cards)} card documents.")
    if error_count > 0:
        print(f"Encountered errors with {error_count} documents.")
    
    return all_cards

