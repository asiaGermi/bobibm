import sys
import os
import re

# Allineamento del path di sistema per l'import dei moduli interni
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph import app_compliance

# Import delle componenti grafiche di Rich
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.status import Status
from rich.text import Text

console = Console(log_time=True, log_time_format="[%H:%M:%S]")

def pulisci_nome_file(testo: str) -> str:
    """Genera un nome file sicuro ed evocativo basandosi sulla query dell'utente."""
    parole = re.findall(r'\b\w{4,}\b', testo.lower())
    parole_chiave = "-".join(parole[:3]) if parole else "analisi"
    return f"report_compliance_{parole_chiave}.md"

def main():
    console.print(Panel.fit(
        "[bold cyan]🧠 PIATTAFORMA INVESTIGATIVA AML / KYC[/bold cyan]\n"
        "[dim]Framework Agentico OOP basato su LangGraph & Ollama[/dim]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    while True:
        console.print("\n[bold white]📝 Inserisci il quesito investigativo da analizzare[/bold white]")
        console.print("[dim](oppure digita 'exit' per uscire dalla piattaforma)[/dim]")
        
        try:
            domanda_aml = input(" > ").strip()
        except (KeyboardInterrupt, EOFError):
            domanda_aml = "exit"
        
        if not domanda_aml:
            console.print("[yellow]⚠️ Il quesito non può essere vuoto. Riprova.[/yellow]")
            continue
            
        if domanda_aml.lower() in ['exit', 'quit', 'q']:
            console.print("\n[bold green]👋 Chiusura della piattaforma compliance in corso. Arrivederci![/bold green]\n")
            break
            
        # Configurazione dello stato iniziale strutturato
        inputs = {
            "query_originale": domanda_aml,
            "contributi_specialisti": {},
            "report_finale": "",
            "errori": []
        }
        
        console.print("\n[bold chevron]⚙️  Inizializzazione del grafo agentico...[/bold chevron]")
        console.log("[bold green]🚀 Avvio Workflow Investigativo del Grafo...[/bold green]")
        
        try:
            # Sfruttiamo lo Status di Rich per mostrare uno spinner animato durante l'inferenza
            with console.status("[bold country]Analisi in corso da parte degli agenti specialistici (Scraping live & Rag)...[/bold country]", spinner="dots2", spinner_style="cyan") as status:
                # Esecuzione del grafo LangGraph
                stato_finale = app_compliance.invoke(inputs)
            
            # Estrazione dei dati dallo stato
            report_testo = stato_finale.get("report_finale", "")
            errori_rilevati = stato_finale.get("errori", [])
            
            # Rendering grafico del Report Finale se presente
            if report_testo:
                console.print("\n")
                console.print(Panel(
                    "[bold green]📋 REPORT INVESTIGATIVO DI COMPLIANCE FINALE[/bold green]", 
                    style="green", 
                    expand=True
                ))
                
                # Questa riga trasforma la stringa Markdown grezza in un output renderizzato a colori nel terminale!
                console.print(Markdown(report_testo))
                console.print("[green]" + "="*console.width + "[/green]\n")
                
                # Scrittura del file Markdown di Audit dinamico
                nome_file = pulisci_nome_file(domanda_aml)
                with open(nome_file, "w", encoding="utf-8") as f:
                    f.write(report_testo)
                    
                console.print(Panel(f"💾 [bold green]SUCCESS:[/bold green] Report salvato in [bold white]'{nome_file}'[/bold white]", border_style="green"))
            else:
                console.print("\n[bold red]❌ ATTENZIONE: Il grafo ha terminato l'esecuzione senza produrre un report.[/bold red]")
                
            # Segnalazione elegante delle anomalie non bloccanti
            if errori_rilevati:
                console.print(Panel(
                    "\n".join([f"• {err}" for err in errori_rilevati]),
                    title="[bold yellow]⚠️ Anomalie Rilevate (Non Bloccanti)[/bold yellow]",
                    border_style="yellow"
                ))
            
        except Exception as e:
            console.print(f"\n[bold red]❌ [CRITICAL ERROR]: Fallimento dell'orchestrazione del grafo:[/bold red] {str(e)}\n")

if __name__ == "__main__":
    main()