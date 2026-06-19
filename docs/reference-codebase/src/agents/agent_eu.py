from src.agents.base import BaseComplianceAgent
from src.tools.web_crawler import esegui_ricerca_mirata

class AgentEU(BaseComplianceAgent):
    def __init__(self):
        super().__init__(name="Agente_EU", emoji="🌍")

    def _execute_analysis(self, query: str) -> str:
        bce_data = esegui_ricerca_mirata("ecb.europa.eu", query)
        eba_data = esegui_ricerca_mirata("eba.europa.eu", query)
        
        prompt = (
            f"Dati live BCE:\n{bce_data}\n\n"
            f"Dati live EBA:\n{eba_data}\n\n"
            f"Estrai le direttive europee e le linee guida applicabili a: {query}"
        )
        
        risposta_llm = self.llm.invoke(prompt)
        return risposta_llm.content if hasattr(risposta_llm, "content") else str(risposta_llm)