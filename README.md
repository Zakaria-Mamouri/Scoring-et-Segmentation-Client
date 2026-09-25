# Eurafric - API de scoring credit (FastAPI)

Variante FastAPI du projet Streamlit Eurafric. L'API permet a l'entreprise de
scorer de nouveaux clients en **saisie manuelle** (JSON) ou **par fichier CSV**,
et d'obtenir en sortie : score credit, probabilites, risque, segment,
elasticite et recommandation business.

Pipeline complet reutilise : nettoyage → feature engineering → segmentation
(K-Means) → scoring credit (Random Forest) → elasticite (XGBoost) → recommandations.

> **Archive autonome** : ce projet est fourni avec son dossier `models/` inclus.
> Il fonctionne tel quel sur n'importe quelle machine (aucun chemin absolu,
> aucune dependance vers le projet principal). Il suffit d'executer
> `lancer_serveur.bat`.

## Pre-requis

- Python 3.10+ (installe et ajoute au PATH)
- Le dossier `models/` est fourni avec le projet

## Installation

```bash
pip install -r requirements.txt
```

## Lancement (une seule commande)

Sur Windows, double-cliquer sur **`lancer_serveur.bat`** :

- cree un environnement virtuel `venv/` au premier lancement ;
- installe automatiquement les dependances ;
- demarre le serveur sur `http://localhost:8000`.

Ou manuellement :

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

L'API est alors accessible sur `http://localhost:8000`.

## Endpoints

| Methode | Route | Description |
|---------|-------|-------------|
| GET  | `/` | Page d'accueil (interface utilisateur) |
| GET  | `/form` | Formulaire web de saisie manuelle d'un client |
| GET  | `/form/csv` | Formulaire web d'import CSV (avec apercu des resultats) |
| GET  | `/health` | Etat des modeles (charges ou non) |
| GET  | `/schema` | Colonnes d'entree / sortie + exemple |
| POST | `/score` | Scoring manuel (JSON) |
| POST | `/score/json` | Variante flexible du scoring JSON |
| POST | `/score/csv` | Scoring par fichier CSV (upload, `?format=json` pour JSON) |
| GET  | `/docs` | Documentation interactive Swagger |

## Exemple de saisie manuelle (POST /score)

```json
{
  "releves": [
    {
      "Customer_ID": "CUST001",
      "Month": "March",
      "Age": 35,
      "Annual_Income": 85000,
      "Monthly_Inhand_Salary": 5400,
      "Num_Bank_Accounts": 3,
      "Num_Credit_Card": 2,
      "Interest_Rate": 12,
      "Num_of_Loan": 2,
      "Type_of_Loan": "Personal Loan, Auto Loan",
      "Delay_from_due_date": 5,
      "Num_of_Delayed_Payment": 2,
      "Changed_Credit_Limit": 1200,
      "Num_Credit_Inquiries": 3,
      "Credit_Mix": "Standard",
      "Outstanding_Debt": 12000,
      "Credit_Utilization_Ratio": 0.35,
      "Credit_History_Age": "10 Years and 3 Months",
      "Payment_of_Min_Amount": "Yes",
      "Total_EMI_per_month": 850,
      "Amount_invested_monthly": 600,
      "Payment_Behaviour": "High_spent_Large_value_payments",
      "Occupation": "Engineer",
      "Monthly_Balance": 3200
    }
  ]
}
```

Un client peut avoir de 1 a 8 releves mensuels (liste). Plusieurs clients
peuvent etre envoyes dans le meme appel.

## Exemple d'import CSV (POST /score/csv)

Le CSV doit contenir les memes colonnes que `train.csv` :

```
Customer_ID,Month,Age,Annual_Income,Monthly_Inhand_Salary,Num_Bank_Accounts,Num_Credit_Card,Interest_Rate,Num_of_Loan,Type_of_Loan,Delay_from_due_date,Num_of_Delayed_Payment,Changed_Credit_Limit,Num_Credit_Inquiries,Credit_Mix,Outstanding_Debt,Credit_Utilization_Ratio,Credit_History_Age,Payment_of_Min_Amount,Total_EMI_per_month,Amount_invested_monthly,Payment_Behaviour,Occupation,Monthly_Balance
```

Upload avec curl :

```bash
curl -X POST -F "file=@clients.csv" http://localhost:8000/score/csv -o resultats.csv
```

## Colonnes de sortie

`Customer_ID`, `Segment`, `Credit_Score_Predit` (Good/Standard/Poor),
`Proba_Good`, `Proba_Standard`, `Proba_Poor`, `Risk_Score` (0-100),
`Risque_Categorie` (Faible/Moyen/Eleve), `Elasticity_Direction`
(Baisse/Stable/Hausse), `Proba_Elasticity_Baisse`, `Proba_Elasticity_Stable`,
`Proba_Elasticity_Hausse`, `Recommandation_Business`.

## Interface utilisateur (pour les employes)

L'API inclut des pages HTML simples destinees aux employes non techniques.
Apres lancement, ouvrir `http://localhost:8000` :

- **Saisie manuelle** (`/form`) : formulaire de saisie d'un client avec
  resultats immediats (score credit, risque, segment, elasticite,
  probabilites et recommandation) affiches sous forme de cartes colorees.
- **Import CSV** (`/form/csv`) : glisser-deposer un fichier CSV, apercu des
  resultats dans un tableau et telechargement du CSV de resultats.

## Structure du projet

```
eurafric_fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py          Application FastAPI (endpoints)
│   ├── config.py        Chemins des modeles / donnees
│   ├── schemas.py       Schemas Pydantic (entree / sortie)
│   ├── service.py       Service de scoring (chargement + pipeline)
│   ├── pipeline.py      Pipeline complet (nettoyage → scoring)
│   ├── constants.py     Constantes (recommandations, ordres, mois)
│   └── forms.py         Formulaires web HTML
├── models/              Artefacts de modeles (fournis)
├── requirements.txt
├── lancer_serveur.bat   Lancement en un clic (Windows)
└── README.md
```

## Notes

- Les modeles sont charges une seule fois (cache) au demarrage.
- Le projet est **autonome** : les modeles sont inclus dans `models/`, le code
  n'utilise aucun chemin absolu ni aucun fichier du projet principal. Deployer
  = extraire l'archive et lancer `lancer_serveur.bat`.
- Le pipeline est identique a celui des notebooks et de l'application Streamlit.
- La categorie de risque utilise les seuils fixes appris sur l'entrainement
  (artefact `risque_categorie_seuils.joblib`), ce qui permet de scorer
  un nombre quelconque de clients (y compris un seul).
