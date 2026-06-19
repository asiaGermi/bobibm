import warnings
warnings.filterwarnings("ignore", message=".*deprecated.*")

from langchain_community.llms import Ollama
from config.settings import OLLAMA_BASE_URL, LLM_MODEL
from src.state import AgentState

llm = Ollama(base_url=OLLAMA_BASE_URL, model=LLM_MODEL, temperature=0)

def orchestrator_node(state: AgentState):
    print("\n🧠 [ORCHESTRATORE]: Analisi dello stato e pianificazione dei presidi...")
    
    contributi = state.get("contributi_specialisti", {})
    
    # 1. Routing sequenziale deterministico basato sulle chiavi del dizionario strutturato
    if "Agente_Locale" not in contributi: 
        return {"prossimo_passo": "locale"}
    if "Agente_EU" not in contributi: 
        return {"prossimo_passo": "eu"}
    if "Agente_IT" not in contributi: 
        return {"prossimo_passo": "it"}
    if "Agente_GAFI" not in contributi: 
        return {"prossimo_passo": "gafi"}
    
    # 2. Se tutti gli specialisti sono presenti, procediamo alla sintesi finale
    print("\n✍️ [ORCHESTRATORE]: Tutti gli specialisti hanno risposto. Generazione del report finale...")
    
    cronologia = ""
    # Cicliamo in modo esplicito sulla mappa ordinata per mantenere la coerenza espositiva
    mappa_nomi = {
        "Agente_Locale": "VALUTAZIONE POLICIES INTERNE (Vector DB)",
        "Agente_EU": "CONTESTO NORMATIVO EUROPEO (BCE / EBA)",
        "Agente_IT": "ADEMPIMENTI NAZIONALI ITALIANI (Banca d'Italia / UIF)",
        "Agente_GAFI": "RISCHIO GEOPOLITICO INTERNAZIONALE (FATF / GAFI)"
    }
    
    for chiave_agente, etichetta in mappa_nomi.items():
        testo_contributo = contributi.get(chiave_agente, "Nessun dato raccolto.")
        cronologia += f"--- {etichetta} ---\n{testo_contributo}\n\n"
            
    prompt_sintesi = (
        f"Sei il Capo della Compliance della banca. Redigi il report investigativo finale integrando i contributi dei tuoi analisti.\n\n"
        f"DATI RACCOLTI DAGLI AGENTI:\n{cronologia}\n"
        f"STRUTTURA OBBLIGATORIA DEL REPORT:\n"
        f"1. VALUTAZIONE INTERNA (Fonti: Procedure Interne)\n"
        f"2. QUADRO NORMATIVO EUROPEO (Fonti: BCE / EBA)\n"
        f"3. REQUISITI E ADEMPIMENTI NAZIONALI (Fonti: Banca d'Italia / UIF)\n"
        f"4. RISCHIO INTERNAZIONALE GEOPOLITICO (Fonti: GAFI / FATF)\n"
        f"5. CONCLUSIONI E AZIONI DI REMEDIATION OPERATIVE\n\n"
        f"Genera il report mantenendo un tono formale, rigoroso ed evidenziando con precisione chirurgica ogni singola fonte citata dagli agenti."
    )
    
    # Esecuzione dell'inferenza finale su Ollama
    risposta_llm = llm.invoke(prompt_sintesi)
    report_completo = risposta_llm.content if hasattr(risposta_llm, "content") else str(risposta_llm)
    
    # Valorizziamo il campo dedicato nello stato e dichiariamo il completamento
    return {
        "report_finale": report_completo,
        "prossimo_passo": "completo"
    }