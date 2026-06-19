import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config.settings import EMBEDDING_MODEL, VECTOR_DB_DIR, INTERNAL_POLICY_DIR

def inizializza_db_locale():
    if not os.path.exists(INTERNAL_POLICY_DIR):
        os.makedirs(INTERNAL_POLICY_DIR)
        print(f"📁 Creata la cartella '{INTERNAL_POLICY_DIR}'. Inserisci i tuoi .txt procedurali qui dentro.")
        return

    if not os.listdir(INTERNAL_POLICY_DIR):
        print(f"⚠️ La cartella '{INTERNAL_POLICY_DIR}' è vuota. Inserisci file di testo per popolare l'archivio.")
        return

    print("📖 Caricamento documenti interni...")
    loader = DirectoryLoader(INTERNAL_POLICY_DIR, glob="*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    documenti = loader.load()

    print("✂️ Frammentazione testi...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    frammenti = text_splitter.split_documents(documenti)

    print("🧠 Generazione vettoriale (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_db = FAISS.from_documents(frammenti, embeddings)
    
    vector_db.save_local(VECTOR_DB_DIR)
    print(f"✅ Database FAISS salvato con successo in '{VECTOR_DB_DIR}'.")

if __name__ == "__main__":
    inizializza_db_locale()