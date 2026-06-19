import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config.settings import EMBEDDING_MODEL, VECTOR_DB_DIR

def carica_retriever_locale():
    """Inizializza il modello di embedding e carica l'indice FAISS locale se presente."""
    if not os.path.exists(VECTOR_DB_DIR):
        print(f"⚠️ [WARNING]: Database vettoriale '{VECTOR_DB_DIR}' non trovato. L'Agente Locale simulerà risposte vuote.")
        return None
        
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_db = FAISS.load_local(VECTOR_DB_DIR, embeddings, allow_dangerous_deserialization=True)
    return vector_db.as_retriever(search_kwargs={"k": 2})