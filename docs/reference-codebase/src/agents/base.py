from abc import ABC, abstractmethod
import warnings
from langchain_community.llms import Ollama
from src.state import AgentState
from config.settings import OLLAMA_BASE_URL, LLM_MODEL

# Importiamo la console di Rich per uniformare lo stile visivo
from rich.console import Console
console = Console(log_time=True, log_time_format="[%H:%M:%S]")

warnings.filterwarnings("ignore", message=".*deprecated.*")

class BaseComplianceAgent(ABC):
    def __init__(self, name: str, emoji: str):
        self.name = name
        self.emoji = emoji
        self.llm = Ollama(base_url=OLLAMA_BASE_URL, model=LLM_MODEL, temperature=0)

    @abstractmethod
    def _execute_analysis(self, query: str) -> str:
        pass

    def to_node(self):
        def node(state: AgentState):
            # Log grafico e pulito: usa i tag di Rich per dare colore ed evitare interruzioni di linea brutte
            console.print(f"[bold cyan]{self.emoji} [{self.name.upper()}][/bold cyan] [dim]Scansione e analisi in corso...[/dim]")
            
            query = state.get("query_originale", "")
            if not query and state.get("messages"):
                query = state["messages"][0]
            
            try:
                risposta_testo = self._execute_analysis(query)
                
                # Log di successo sul terminale
                console.print(f"  [bold green]✓[/bold green] [dim]{self.name} completato con successo.[/dim]")
                return {
                    "contributi_specialisti": {self.name: risposta_testo}
                }
                
            except Exception as e:
                error_msg = f"Eccezione nel nodo {self.name}: {str(e)}"
                console.print(f"  [bold red]✕ [ERRORE {self.name}]:[/bold red] [dim]{str(e)}[/dim]")
                
                return {
                    "contributi_specialisti": {self.name: f"Rilevato fallimento tecnico durante l'analisi di {self.name}."},
                    "errori": [error_msg]
                }
                
        return node