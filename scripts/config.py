# ==========================================
# CONFIGURAZIONE GENERALE
# ==========================================

# URL dell'API di Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"

# Modello LLM da utilizzare
MODEL_NAME = "deepseek-r1:1.5b"

# File di input contenente le parole (una per riga)
INPUT_FILE = "dizionarioEsteso.txt"

# Numero di parole per batch inviate al modello
BATCH_SIZE = 55

# File di checkpoint per riprendere l'elaborazione
CHECKPOINT_FILE = "checkpoint.json"

# Timeout per le richieste HTTP (secondi)
REQUEST_TIMEOUT = 120

# Ogni quanti batch salvare un checkpoint
CHECKPOINT_INTERVAL = 100

# ==========================================
# FILE DI OUTPUT
# ==========================================

OUTPUT_ESCLUSE = "parole_da_escludere.txt"
OUTPUT_VALIDE = "parole_valide.txt"
OUTPUT_ERRORI = "parole_con_errori.txt"

# ==========================================
# PARAMETRI DEL MODELLO
# ==========================================

MODEL_OPTIONS = {
    "temperature": 0,
}

# ==========================================
# PROMPT
# ==========================================

PROMPT_TEMPLATE = """Per ognuna delle seguenti parole italiane, dimmi se appartiene a una di queste categorie:
- Un verbo all'infinito
- Una coniugazione verbale
- Un nome proprio di persona
- Una parola arcaica non più usata

Lista parole:
{words_list}

Rispondi SOLO con "true" o "false" (uno per riga) SOLO SE SEI SICURO AL 100%, NESSUNA altra parola.
Esempio:
true
false
true"""