from typing import TypedDict, Dict, List, Annotated
import operator

class AgentState(TypedDict):
    # Il quesito investigativo iniziale passato dall'utente
    query_originale: str
    # Dizionario incrementale dei contributi. 
    # Usiamo Annotated e operator.ior (In-place OR) per unire i dizionari ad ogni passaggio del grafo
    contributi_specialisti: Annotated[Dict[str, str], operator.ior]
    # Il Markdown definitivo generato dall'Orchestratore alla fine del flusso
    report_finale: str
    # Tracciamento centralizzato di eventuali anomalie o timeout nei nodi
    errori: Annotated[List[str], operator.add]