from src.agents.base import BaseComplianceAgent
from src.tools.web_crawler import esegui_ricerca_mirata

class AgentGAFI(BaseComplianceAgent):
    def __init__(self):
        super().__init__(name="Agente_GAFI", emoji="🌐")

    def _execute_analysis(self, query: str) -> str:
        gafi_data = esegui_ricerca_mirata("fatf-gafi.org", f"high risk jurisdictions blacklist grey list {query}")
        
        prompt = (
            f"Dati FATF/GAFI:\n{gafi_data}\n\n"
            f"Verifica se la richiesta coinvolge giurisdizioni a rischio secondo gli standard globali: {query}"
        )
        
        risposta_llm = self.llm.invoke(prompt)
        return risposta_llm.content if hasattr(risposta_llm, "content") else str(risposta_llm)