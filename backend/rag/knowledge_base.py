from pathlib import Path

DOCUMENTS_PATH = Path(__file__).parent / "documents"


def load_documents():
    documents = []

    for file in DOCUMENTS_PATH.glob("*.txt"):
        content = file.read_text(encoding="utf-8")

        documents.append({
            "source": file.name,
            "content": content
        })

    return documents