import os

# Configurazione LLM e Infrastruttura Locale (Mancavano queste righe o erano errate!)
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "mistral"
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"

# Configurazione Database Vettoriale e Policy Interna
VECTOR_DB_DIR = "faiss_index_banca"
INTERNAL_POLICY_DIR = "./normativa_interna"

# Configurazione Parametri di Rete e Compliance per i Crawler
CRAWL_DELAY_DEFAULT = 2
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Mappatura dei Crawl-Delay espliciti e consigliati per il perimetro AML/CFT
DOMAINS_CRAWL_DELAY = {
    "bancaditalia.it": 5,        
    "uif.bancaditalia.it": 5,    
    "fatf-gafi.org": 3,          
    "eba.europa.eu": 2,          
    "ecb.europa.eu": 2,          
    "fiusenet.europa.eu": 5      
}