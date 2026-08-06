from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = Path(__file__).resolve().parents[3] / "data" / "chroma"
CHROMA_PATH.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(CHROMA_PATH))

embedding_fn = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="run_memory",
    embedding_function=embedding_fn,
)

def add_memory(run_id: int, task: str, final_output: str):
    collection.add(
        ids=[str(run_id)],
        documents=[f"Task: {task}\n\nOutput: {final_output}"],
        metadatas=[{"task": task}],
    )

def query_memory(query: str, n_results: int = 3, max_distance: float = 1.2):
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )
    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    relevant = [
        doc for doc, dist in zip(documents, distances)
        if dist <= max_distance
    ]
    return relevant