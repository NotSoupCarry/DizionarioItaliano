import os
import json
import requests
from tqdm import tqdm
from datetime import datetime, timedelta

from config import (
    OLLAMA_URL, MODEL_NAME, INPUT_FILE, BATCH_SIZE,
    CHECKPOINT_FILE, REQUEST_TIMEOUT, CHECKPOINT_INTERVAL,
    OUTPUT_ESCLUSE, OUTPUT_VALIDE, OUTPUT_ERRORI,
    MODEL_OPTIONS, PROMPT_TEMPLATE
)


def load_checkpoint():
    """Carica il checkpoint se esiste, altrimenti ritorna lo stato iniziale."""
    try:
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "last_index": 0,
            "parole_da_escludere": [],
            "parole_valide": [],
            "errori": []
        }


def save_checkpoint(checkpoint):
    """Salva lo stato corrente su file per permettere la ripresa."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def analyze_words_batch(words_batch):
    """
    Invia un batch di parole al modello LLM e restituisce una lista di booleani.
    True = da escludere | False = valida | None = errore/risposta non interpretabile
    """
    words_list = "\n".join([f"{i+1}. {word}" for i, word in enumerate(words_batch)])
    prompt = PROMPT_TEMPLATE.format(words_list=words_list)

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                **MODEL_OPTIONS,
                "num_predict": len(words_batch) * 5
            }
        }, timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            answer_text = response.json()['response'].strip()
            answers = answer_text.split('\n')

            results = []
            for answer in answers[:len(words_batch)]:
                cleaned = answer.strip().lower()
                if 'true' in cleaned:
                    results.append(True)
                elif 'false' in cleaned:
                    results.append(False)

            while len(results) < len(words_batch):
                results.append(None)

            return results[:len(words_batch)]
        else:
            return [None] * len(words_batch)

    except Exception as e:
        print(f"\nErrore: {e}")
        return [None] * len(words_batch)


def main():
    start_time = datetime.now()

    print("Caricamento parole...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        parole = [line.strip() for line in f if line.strip()]
    print(f"✅ Caricate {len(parole):,} parole")

    checkpoint = load_checkpoint()
    start_index = checkpoint["last_index"]
    parole_da_escludere = checkpoint["parole_da_escludere"]
    parole_valide = checkpoint["parole_valide"]
    errori = checkpoint["errori"]

    if start_index > 0:
        print(f"🔄 Ripresa da parola #{start_index:,}")

    total_batches = (len(parole) - start_index + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"📊 Batch totali: {total_batches:,}\n")

    batch_count = 0

    for i in tqdm(range(start_index, len(parole), BATCH_SIZE), total=total_batches):
        batch = parole[i:i + BATCH_SIZE]
        risultati = analyze_words_batch(batch)

        for parola, risultato in zip(batch, risultati):
            if risultato is None:
                errori.append(parola)
            elif risultato:
                parole_da_escludere.append(parola)
            else:
                parole_valide.append(parola)

        batch_count += 1

        if batch_count % CHECKPOINT_INTERVAL == 0:
            checkpoint = {
                "last_index": i + BATCH_SIZE,
                "parole_da_escludere": parole_da_escludere,
                "parole_valide": parole_valide,
                "errori": errori
            }
            save_checkpoint(checkpoint)

            elapsed = (datetime.now() - start_time).total_seconds()
            rate = batch_count / elapsed
            remaining = total_batches - batch_count
            eta_sec = remaining / rate
            eta = datetime.now() + timedelta(seconds=eta_sec)
            print(f"\nCheckpoint | {batch_count}/{total_batches} | ETA: {eta.strftime('%H:%M')}")

    # Salva risultati finali
    with open(OUTPUT_ESCLUSE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parole_da_escludere))

    with open(OUTPUT_VALIDE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parole_valide))

    if errori:
        with open(OUTPUT_ERRORI, 'w', encoding='utf-8') as f:
            f.write('\n'.join(errori))

    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

    elapsed = datetime.now() - start_time
    print(f"\nCOMPLETATO in {elapsed}!")
    print(f"Da escludere: {len(parole_da_escludere):,}")
    print(f"Valide: {len(parole_valide):,}")
    print(f"Errori: {len(errori):,}")


if __name__ == "__main__":
    main()