import sys
import os
import time
import sqlite3
from urllib.parse import urlparse
from rich.console import Console

# Silenziamo i warning interni di ddgs
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*duckduckgo_search.*")

from ddgs import DDGS

console = Console(log_time=True, log_time_format="[%H:%M:%S]")
DB_PATH = "crawler_cache.db"

def init_db():
    """Inizializza la cache persistente su SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS aml_web_cache (
                chiave_ricerca TEXT PRIMARY KEY,
                contenuto_testuale TEXT,
                timestamp REAL
            )
        """)
init_db()

def recupera_da_cache_persistente(chiave: str, validita_secondi: int = 86400) -> str:
    """Controlla se la ricerca è presente sul disco ed è stata fatta nelle ultime 24 ore."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT contenuto_testuale, timestamp FROM aml_web_cache WHERE chiave_ricerca = ?", (chiave,))
        row = cursor.fetchone()
        if row:
            contenuto, timestamp = row
            if (time.time() - timestamp) < validita_secondi:
                return contenuto
    return None

def salva_in_cache_persistente(chiave: str, contenuto: str):
    """Archivia il risultato sul database SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO aml_web_cache (chiave_ricerca, contenuto_testuale, timestamp) VALUES (?, ?, ?)",
            (chiave, contenuto, time.time())
        )

def esegui_ricerca_mirata(dominio: str, query: str) -> str:
    """
    Esegue una ricerca mirata su un dominio istituzionale sfruttando l'indice di DDG.
    Evita i blocchi HTTP 403/404 e garantisce persistenza incrementale e velocità.
    """
    # Creiamo una chiave univoca per la cache basata su dominio e query
    chiave_cache = f"{dominio}:{query.lower().strip()}"
    
    # 1. LIVELLO INCREMENTALE: Check della Cache su Disco
    contenuto_archiviato = recupera_da_cache_persistente(chiave_cache)
    if contenuto_archiviato:
        console.print(f"  [bold green]⚡ [CACHE HIT]:[/bold green] Informazioni per [white]{dominio}[/white] caricate istantaneamente da disco.")
        return contenuto_archiviato

    console.print(f"  [dim]🌐 [CRAWLER ETICO]:[/dim] Ricerca dati normativi live su [cyan]{dominio}[/cyan]...")
    
    # Costruiamo la query mirata per costringere il motore a cercare solo in quel perimetro
    query_strutturata = f"site:{dominio} {query}"
    corpo_testuale_raccolto = []
    
    try:
        # Applichiamo un throttling minimo etico pre-chiamata (0.5s) per non stressare il network
        time.sleep(0.5)
        
        with DDGS() as ddgs:
            # Estraiamo i primi 4 risultati comprensivi di titolo e snippet (riassunto)
            risultati = ddgs.text(query_strutturata, max_results=4)
            
            for idx, r in enumerate(risultati, 1):
                titolo = r.get('title', 'Nessun Titolo')
                url = r.get('href', '')
                snippet = r.get('body', '')
                
                corpo_testuale_raccolto.append(f"[Fonte {idx}]: {url}\nTitolo: {titolo}\nContenuto: {snippet}\n")
                
        if corpo_testuale_raccolto:
            testo_finale = "\n".join(corpo_testuale_raccolto)
            
            # 2. SALVATAGGIO IN CACHE: Se abbiamo trovato dati, li persistiamo sul DB
            salva_in_cache_persistente(chiave_cache, testo_finale)
            console.print(f"  [bold green]✓ [CACHE SALVATA]:[/bold green] Indicizzati dati normativi da DDG per {dominio}.")
            return testo_finale
        else:
            # Fallback se il sito non restituisce dati per quella specifica keyword
            msg_vuoto = f"Nessuna direttiva specifica trovata di recente su {dominio} per la query inserita."
            salva_in_cache_persistente(chiave_cache, msg_vuoto)
            return msg_vuoto
            
    except Exception as e:
        error_msg = f"Errore durante l'interrogazione dell'indice per {dominio}: {str(e)}"
        console.print(f"  [bold red]✕ [ERRORE RETE]:[/bold red] {error_msg}")
        return f"Impossibile recuperare aggiornamenti live da {dominio} a causa di un problema di rete."