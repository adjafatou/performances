import requests
import csv
import time
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

URL_API = "https://opentdb.com/api.php"
MAX_PAR_REQUETE = 50
OBJECTIF_QUESTIONS = 4500
NB_WORKERS = 6
TIMEOUT = 15
DELAI_RETRY = 2
MAX_TENTATIVES = 3

def recuperer_questions(nb_questions=MAX_PAR_REQUETE):
    """Récupère un batch de questions depuis l'API"""
    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            reponse = requests.get(
                URL_API,
                params={"amount": nb_questions, "type": "multiple", "encode": "url3986"},
                timeout=TIMEOUT
            )
            donnees = reponse.json()
            
            if donnees["response_code"] == 0:
                # Décoder toutes les données
                for question in donnees["results"]:
                    question['question'] = unquote(question['question'])
                    question['correct_answer'] = unquote(question['correct_answer'])
                    question['category'] = unquote(question['category'])
                    question['incorrect_answers'] = [unquote(reponse) for reponse in question['incorrect_answers']]
                return donnees["results"]
            else:
                print(f" Erreur API - tentative {tentative}")
                
        except Exception as e:
            print(f" Erreur {e} - tentative {tentative}")
            
        time.sleep(DELAI_RETRY)
    
    return []

def convertir_en_ligne_csv(question):
    """Convertit une question en ligne CSV"""
    return {
        'categorie': question['category'],
        'type': question['type'],
        'difficulte': question['difficulty'],
        'question': question['question'],
        'reponse_correcte': question['correct_answer'],
        'reponses_incorrectes': '|'.join(question['incorrect_answers']),
        'toutes_reponses': '|'.join([question['correct_answer']] + question['incorrect_answers'])
    }

def scraper_questions():
    """Fonction principale de scraping"""
    total_questions = 0
    questions_vues = set()
    
    print(f" Objectif: {OBJECTIF_QUESTIONS} questions")
    
    #  fichier CSV
    with open("../data/questions_raw.csv", "w", newline='', encoding="utf-8") as fichier_csv:
        colonnes = [
            'categorie', 'type', 'difficulte', 'question', 
            'reponse_correcte', 'reponses_incorrectes', 'toutes_reponses'
        ]
        writer = csv.DictWriter(fichier_csv, fieldnames=colonnes)
        writer.writeheader()
        
        while total_questions < OBJECTIF_QUESTIONS:
            restant = OBJECTIF_QUESTIONS - total_questions
            nb_batches = min(restant, MAX_PAR_REQUETE * NB_WORKERS)
            batches_a_faire = (nb_batches + MAX_PAR_REQUETE - 1) // MAX_PAR_REQUETE
            
            with ThreadPoolExecutor(max_workers=NB_WORKERS) as executor:
                futures = [
                    executor.submit(recuperer_questions, min(MAX_PAR_REQUETE, restant)) 
                    for _ in range(batches_a_faire)
                ]
                
                for future in as_completed(futures):
                    batch = future.result()
                    for question in batch:
                        if question['question'] not in questions_vues:
                            questions_vues.add(question['question'])
                            
                            # Écrire dans le CSV
                            ligne_csv = convertir_en_ligne_csv(question)
                            writer.writerow(ligne_csv)
                            
                            total_questions += 1
                            
                            if total_questions >= OBJECTIF_QUESTIONS:
                                break
                    
                    print(f" Questions récupérées: {total_questions}")
                    
                    if total_questions >= OBJECTIF_QUESTIONS:
                        break
    
    print(f"\n fini {total_questions}")

if __name__ == "__main__":
    scraper_questions()