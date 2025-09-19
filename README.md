# Membres du groupes:

```
Nephtalie 
Cindy
Adja 
```


# Benchmark IA - Évaluation de modèles sur QCM

## Structure du projet

```
benchmark-ia/
├── data/
│   ├── questions_raw.csv      # Dataset d'entrée
│   └── benchmark_results.csv     # Résultats générés
├── scripts/
│   └── enrich_dataset.py              # Script pour prendre les reponses en fonction de l'ia
    └── question_py                     #script principal qui permet de recueillir les questions
├── notebooks/
│   └── analyse_resultats.ipynb   # Analyse des résultats
└── README.md
```

## Installation

```bash
git clone https://github.com/adjafatou/performances.git
cd evaluations

# Installer les dépendances
pip install pandas ollama Matplotlib

# Installer Ollama et télécharger un modèle
ollama pull llama3.2
ollama pull gemma:2.b


## Utilisation
# Exécuter
python scripts/benchmark.py
```

### 2. Tester plusieurs modèles

```bash
# Modifier MODELE dans benchmark.py puis relancer
python scripts/benchmark.py  # avec llama3.2
python scripts/benchmark.py  # avec gemma:2b
```

### 3. Analyser les résultats

Ouvrir `notebooks/analyse_resultats.ipynb` et exécuter les cellules :

1. **Imports et configuration**
2. **Chargement des données**
3. **Performance globale** 
4. **Analyse par catégorie** 
5. **Analyse par difficulté** 
6. **Temps de réponse** 
7. **Questions difficiles/faciles** 

## Résultats générés

Le script produit un fichier `data/benchmark_results.csv` avec :

- Colonnes originales du dataset
- `reponse_ia_[MODELE]` : Réponse donnée par l'IA
- `ia_correct_[MODELE]` : True/False selon correction
- `temps_reponse_[MODELE]` : Temps de traitement en secondes

