# Account di Test — Financial Risk Management Demo

Dataset: `data/raw/HI-Small_Trans_sample.csv` (28.374 righe, 2.5MB)  
Aggiornato: 24 giugno 2026

---

## Tabella Account di Test

| Account ID | Risk Score | Level | Pattern AML | Caratteristiche |
|---|---|---|---|---|
| `100428A51` | 70.0% | **HIGH** | fan-out | 13.073 tx tutte in Bitcoin, 1.147 destinatari diversi |
| `812D22980` | 53.9% | **MEDIUM** | circular | 25/27 tx laundering (93%), flussi circolari |
| `808B1C350` | 42.4% | **MEDIUM** | fan-out + circular | 12/17 tx laundering (71%), 13 destinatari |
| `100428660` | 34.2% | LOW | fan-out + smurfing | 267 tx, 122 destinatari, 9 tx sotto $10k — account principale demo |
| `8000EBD30` | ~0% | LOW | nessuno | Transazioni normali — confronto "account pulito" |

---

## Workflow Demo Consigliato

### Scenario 1 — Account Sospetto (HIGH risk)
```
Account ID: 100428A51
Periodo:    90 giorni
Risultato:  70% HIGH, fan-out verso 1.147 account, 100% Bitcoin
Messaggio:  "Il sistema ha rilevato un account che opera esclusivamente
             in Bitcoin con oltre 1.000 destinatari diversi"
```

### Scenario 2 — Money Laundering (MEDIUM risk)
```
Account ID: 812D22980
Periodo:    90 giorni
Risultato:  54% MEDIUM, flussi circolari, 93% transazioni flaggate
Messaggio:  "93% delle transazioni risultano sospette di riciclaggio"
```

### Scenario 3 — Pattern multipli (LOW ma sospetto)
```
Account ID: 100428660
Periodo:    30 giorni
Risultato:  34% LOW, fan-out + smurfing
Messaggio:  "Basso score complessivo ma 2 pattern AML critici rilevati:
             fan-out verso 122 account e strutturazione sotto $10k"
```

### Scenario 4 — Confronto account pulito
```
Account ID: 8000EBD30
Periodo:    30 giorni
Risultato:  ~0% LOW, 0 pattern
Messaggio:  "Nessun pattern anomalo — profilo di rischio normale"
```

---

## Note Tecniche

- **`100428A51`**: alta frequenza (145 tx/giorno) + 100% Bitcoin = HIGH anche con bassa % laundering
- **`812D22980`**: alta % laundering (93%) + circular flow = MEDIUM
- Il dataset sample include tutte le righe di `100428A51` dal dataset completo (HI-Small_Trans.csv)
- I pattern AML rilevati dipendono dal periodo di analisi (`lookback_days`)
- Per il demo usare `lookback_days=90` per massimizzare i pattern visibili
