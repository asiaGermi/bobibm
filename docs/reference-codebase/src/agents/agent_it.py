from src.agents.base import BaseComplianceAgent
from src.tools.web_crawler import esegui_ricerca_mirata

class AgentIT(BaseComplianceAgent):
    def __init__(self):
        super().__init__(name="Agente_IT", emoji="🇮🇹")

    def _execute_analysis(self, query: str) -> str:
        bankit_data = esegui_ricerca_mirata("bancaditalia.it", query)
        uif_data = esegui_ricerca_mirata("uif.bancaditalia.it", query)
        
        prompt = (
            f"Dati Bankit:\n{bankit_data}\n\n"
            f"Dati UIF:\n{uif_data}\n\n"
            f"Estrai gli indicatori di anomalia e i regolamenti italiani per: {query}"
        )
        
        risposta_llm = self.llm.invoke(prompt)
        return risposta_llm.content if hasattr(risposta_llm, "content") else str(risposta_llm)