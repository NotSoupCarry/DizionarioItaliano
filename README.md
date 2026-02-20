# Italian Dictionary

Un dizionario italiano pulito, **senza verbi, nomi propri e parole arcaiche**, generato filtrando un dizionario grezzo da ~320k parole tramite un LLM locale.

## Il Dizionario

Il file **`result.txt`** contiene il dizionario filtrato, pronto all'uso — una parola per riga. Viene aggiornato periodicamente con correzioni e miglioramenti.

> **Nota sull'accuratezza**: il dizionario è stato generato con un modello molto piccolo (1.5B parametri) ed è accurato circa al **~90%**. Alcune parole valide potrebbero essere state escluse e qualche verbo o nome proprio potrebbe essere sfuggito al filtro. Se trovi errori, apri pure una issue o una PR.

---

## Come è Stato Ottenuto

### Il Problema

I dizionari italiani reperibili online contengono centinaia di migliaia di voci, ma includono indiscriminatamente tutte le coniugazioni verbali (*mangiavo, corremmo, andassero...*), nomi propri di persona (*Giuseppe, Maria, Alessandro...*) e parole arcaiche ormai fuori dall'uso comune. Per applicazioni come word game, analisi testuale o NLP serve un sottoinsieme più pulito.

Non esistono filtri deterministici affidabili per questo tipo di classificazione: una parola come *rosa* è sia un nome proprio che un sostantivo, *porto* è sia un verbo che un nome. Serve un modello linguistico in grado di valutare il contesto d'uso più comune.

### Il Processo

Ho utilizzato **DeepSeek R1 1.5B**, un modello mini self-hostato tramite [Ollama](https://ollama.com), per classificare ogni parola del dizionario grezzo. La scelta è caduta su un modello piccolo per poterlo eseguire interamente in locale su CPU, senza GPU dedicata.

Lo script `filter_words.py` prende il dizionario grezzo e lo invia al modello in **batch da 55 parole**, chiedendo per ciascuna se è:

- un verbo all'infinito
- una coniugazione verbale
- un nome proprio di persona
- una parola arcaica non più usata

```
dizionarioEsteso.txt (~320k parole)
        │
        ▼
┌───────────────────────────────┐
│     filter_words.py           │
│                               │
│  1. Carica le parole          │
│  2. Le divide in batch da 55  │
│  3. Per ogni batch chiede     │
│     al modello LLM:           │
│     "Questa parola è un       │
│      verbo / nome proprio /   │
│      parola arcaica?"         │
│  4. Salva checkpoint ogni     │
│     100 batch                 │
└───────────────────────────────┘
        │
        ▼
    result.txt (dizionario pulito)
```

Il modello risponde con `true` (da escludere) o `false` (da tenere) per ciascuna parola. La temperatura è impostata a **0** per massimizzare il determinismo delle risposte.

### Numeri

| Metrica | Valore |
|---|---|
| Parole in input | ~320.000 |
| Tempo totale di elaborazione | **~30 ore** |
| Batch size | 55 parole |
| Tasso di errore | **~10%** |
| Accuratezza stimata | **~90%** |

### Sistema di Checkpoint

Elaborare ~320k parole richiede molte ore. Per evitare di perdere il progresso in caso di crash o interruzione, lo script salva automaticamente un **checkpoint** (file JSON) ogni 100 batch. Al riavvio, riparte esattamente da dove si era fermato.

---

## Rieseguire il Filtro

Se vuoi rieseguire il processo da zero o su un dizionario diverso, ecco come fare.

### Requisiti

- Python 3.8+
- [Ollama](https://ollama.com) installato e in esecuzione
- Il modello DeepSeek scaricato: `ollama pull deepseek-r1:1.5b`

```bash
pip install requests tqdm
```

### Utilizzo

1. **Installa Ollama** e scarica il modello:
   ```bash
   ollama pull deepseek-r1:1.5b
   ```

2. **Configura** `config.py` se necessario (modello, batch size, URL di Ollama...).

3. **Avvia**:
   ```bash
   python filter_words.py
   ```

4. Se lo script viene interrotto, basta rilanciarlo: ripartirà dall'ultimo checkpoint.

---

## Struttura del Progetto

```
.
├── result.txt                          # Dizionario pulito (output finale)
├── scripts/config.py                   # Variabili di configurazione e prompt
├── scripts/filter_words.py             # Script di filtraggio
├── scripts/dizionarioEsteso.txt        # Dizionario grezzo di input
└── README.md
```

Tutte le variabili sono in `config.py` con già la configurazione di default usata da me


<br>


###
Questo dizionario è il cuore di [**TUFFGramma**](https://tuffgramma.com/) — la mia app di giochi sulle parole italiane.
