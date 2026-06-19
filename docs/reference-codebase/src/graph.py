from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.orchestrator import orchestrator_node

# Importazione delle nuove classi ingegnerizzate
from src.agents.agent_local import AgentLocal
from src.agents.agent_eu import AgentEU
from src.agents.agent_it import AgentIT
from src.agents.agent_gafi import AgentGAFI

# 1. Istanziazione degli oggetti e conversione automatica in nodi LangGraph
nodo_locale = AgentLocal().to_node()
nodo_eu = AgentEU().to_node()
nodo_it = AgentIT().to_node()
nodo_gafi = AgentGAFI().to_node()

# 2. Configurazione del Workflow
workflow = StateGraph(AgentState)

# Aggiunta dei nodi al grafo
workflow.add_node("orchestratore", orchestrator_node)
workflow.add_node("locale", nodo_locale)
workflow.add_node("eu", nodo_eu)
workflow.add_node("it", nodo_it)
workflow.add_node("gafi", nodo_gafi)

# Impostiamo l'ingresso sull'orchestratore
workflow.set_entry_point("orchestratore")

# 3. Logica del Conditional Routing basata sullo stato strutturato
def decisione_routing(state: AgentState):
    contributi = state.get("contributi_specialisti", {})
    
    if "Agente_Locale" not in contributi: return "locale"
    if "Agente_EU" not in contributi: return "eu"
    if "Agente_IT" not in contributi: return "it"
    if "Agente_GAFI" not in contributi: return "gafi"
    
    return "completo"

workflow.add_conditional_edges(
    "orchestratore",
    decisione_routing,
    {
        "locale": "locale",
        "eu": "eu",
        "it": "it",
        "gafi": "gafi",
        "completo": END
    }
)

# Chiusura dei nodi verso il riesame dell'orchestratore
workflow.add_edge("locale", "orchestratore")
workflow.add_edge("eu", "orchestratore")
workflow.add_edge("it", "orchestratore")
workflow.add_edge("gafi", "orchestratore")

app_compliance = workflow.compile()