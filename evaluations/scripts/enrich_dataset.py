import time
import pandas as pd
import ollama
import re
import os

# Configuration
FICHIER_ENTREE = "./data/questions_trivia.csv"
FICHIER_SORTIE = "./data/benchmark_results.csv"
MODELE = "gemma:2b"  
NOMBRE_TEST = 1000      

def normaliser(texte):
    return re.sub(r"[^\w\s]", "", str(texte).strip().lower())

def verifier_correct(reponse_ia, reponse_correcte):
    ia_norm = normaliser(reponse_ia)
    correcte_norm = normaliser(reponse_correcte)
    return (ia_norm == correcte_norm or 
            correcte_norm in ia_norm or 
            ia_norm in correcte_norm)

# Charger dataset de base
donnees = pd.read_csv(FICHIER_ENTREE)
if NOMBRE_TEST:
    donnees = donnees.head(NOMBRE_TEST)

# Colonnes en fonction de le modèle
col_reponse = f"reponse_ia_{MODELE.replace(':','_')}"
col_correct = f"ia_correct_{MODELE.replace(':','_')}"
col_temps = f"temps_reponse_{MODELE.replace(':','_')}"

reponses_ia, ia_corrects, temps_reponse = [], [], []

for idx, ligne in donnees.iterrows():
    question = ligne["question"]
    reponse_correcte = ligne["reponse_correcte"]
    options = ligne["toutes_reponses"].split("|")

    prompt = f"{question}\n" + "\n".join([f"- {opt}" for opt in options]) + \
             "\n\nRéponds uniquement par le mot exact de la bonne réponse."

    debut_temps = time.time()
    try:
        reponse = ollama.chat(model=MODELE, messages=[{"role": "user", "content": prompt}])
        reponse_ia = reponse["message"]["content"].strip()
    except Exception as e:
        reponse_ia = f"ERREUR: {e}"

    duree = round(time.time() - debut_temps, 3)
    ia_correct = verifier_correct(reponse_ia, reponse_correcte) if not reponse_ia.startswith("ERREUR") else False

    reponses_ia.append(reponse_ia)
    ia_corrects.append(ia_correct)
    temps_reponse.append(duree)

    print(f"[{idx+1}/{len(donnees)}] {reponse_ia} | {ia_correct} | {duree}s")

if os.path.exists(FICHIER_SORTIE):
    donnees_resultats = pd.read_csv(FICHIER_SORTIE)
    if len(donnees_resultats) != len(donnees):
        donnees_resultats = donnees.copy()
else:
    donnees_resultats = donnees.copy()

donnees_resultats[col_reponse] = reponses_ia
donnees_resultats[col_correct] = ia_corrects
donnees_resultats[col_temps] = temps_reponse

donnees_resultats.to_csv(FICHIER_SORTIE, index=False)

nombre_correct = sum(ia_corrects)
precision = (nombre_correct / len(donnees)) * 100
temps_moyen = sum(temps_reponse) / len(temps_reponse)

print(f"\nRésultats sauvegardés dans {FICHIER_SORTIE}")
print(f"Questions totales: {len(donnees)}")
print(f"Réponses correctes ({MODELE}): {nombre_correct}")
print(f"Précision: {precision:.1f}%")
print(f"Temps moyen: {temps_moyen:.2f}s")