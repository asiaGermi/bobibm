from src.agents.base import BaseComplianceAgent
from src.tools.vector_db import carica_retriever_locale

class AgentLocal(BaseComplianceAgent):
    def __init__(self):
        super().__init__(name="Agente_Locale", emoji="🔍")
        self.retriever = carica_retriever_locale()

    def _execute_analysis(self, query: str) -> str:
        if self.retriever is None:
            return "Nessuna procedura interna rilevata (Vector DB non inizializzato)."
            
        documenti = self.retriever.invoke(query)
        contesto_db = "\n".join([f"- Fonte Interna [{d.metadata.get('source')}]: {d.page_content}" for d in documenti])
        
        prompt = f"Contesto aziendale interno:\n{contesto_db}\n\nEstrai le policy interne applicabili a: {query}"
        risposta_llm = self.llm.invoke(prompt)
        return risposta_llm.content if hasattr(risposta_llm, "content") else str(risposta_llm)