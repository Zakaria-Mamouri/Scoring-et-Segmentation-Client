import os
import time

import joblib
import numpy as np
import pandas as pd

from app.config import MODELS_DIR, MODEL_FILES
from app.pipeline import run_pipeline

_models = None
_load_time = None


def load_models(force=False):
    """Charge (et met en cache) tous les artefacts de modèles."""
    global _models, _load_time
    if _models is not None and not force:
        return _models

    if not os.path.isdir(MODELS_DIR):
        raise FileNotFoundError(
            f"Dossier des modèles introuvable : {MODELS_DIR}\n"
            "Définissez la variable d'environnement EURAFRIC_MODELS_DIR "
            "ou placez les fichiers .joblib/.pkl dans un dossier models/."
        )

    models = {}
    for key, filename in MODEL_FILES.items():
        path = os.path.join(MODELS_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Artefact manquant : {path}")
        models[key] = joblib.load(path)

    _models = models
    _load_time = time.time()
    return models


def get_models():
    return load_models()


def _to_dataframe(releves):
    """Convertit une liste de relevés (dict) en DataFrame pandas."""
    df = pd.DataFrame([r if isinstance(r, dict) else r.model_dump() for r in releves])
    df['Customer_ID'] = df['Customer_ID'].astype(str)
    return df


def valider_colonnes(df):
    """Vérifie que toutes les colonnes obligatoires sont présentes."""
    from app.schemas import COLONNES_OBLIGATOIRES
    manquantes = [c for c in COLONNES_OBLIGATOIRES if c not in df.columns]
    return manquantes


def score_releves(releves):
    """Exécute le pipeline complet sur une liste de relevés mensuels.

    Retourne une liste de dicts avec les résultats par client.
    """
    models = get_models()
    df = _to_dataframe(releves)

    manquantes = valider_colonnes(df)
    if manquantes:
        raise ValueError(
            f"Colonnes obligatoires absentes de l'entrée : {manquantes}. "
            "Rappel des colonnes attendues : "
            "Customer_ID, Age, Annual_Income, Monthly_Inhand_Salary, Num_Bank_Accounts, "
            "Num_Credit_Card, Interest_Rate, Num_of_Loan, Type_of_Loan, Delay_from_due_date, "
            "Num_of_Delayed_Payment, Changed_Credit_Limit, Num_Credit_Inquiries, Credit_Mix, "
            "Outstanding_Debt, Credit_Utilization_Ratio, Credit_History_Age, "
            "Payment_of_Min_Amount, Total_EMI_per_month, Amount_invested_monthly, "
            "Payment_Behaviour, Monthly_Balance."
        )

    clients, _ = run_pipeline(df, models)

    colonnes_sortie = [
        'Customer_ID', 'Segment', 'Credit_Score_Predit',
        'Proba_Good', 'Proba_Standard', 'Proba_Poor', 'Risk_Score',
        'Risque_Categorie', 'Elasticity_Direction',
        'Proba_Elasticity_Baisse', 'Proba_Elasticity_Stable', 'Proba_Elasticity_Hausse',
        'Recommandation_Business',
    ]

    resultats = clients[colonnes_sortie].copy()

    # Nettoyage des valeurs NaN pour une sérialisation JSON propre
    resultats = resultats.replace({np.nan: None})
    return resultats


def score_dataframe(df_source):
    """Exécute le pipeline complet sur un DataFrame brut (cas fichier CSV)."""
    models = get_models()
    df = df_source.copy()

    if 'Customer_ID' not in df.columns:
        raise ValueError("La colonne 'Customer_ID' est absente du fichier.")

    df['Customer_ID'] = df['Customer_ID'].astype(str)

    manquantes = valider_colonnes(df)
    if manquantes:
        raise ValueError(
            f"Colonnes obligatoires absentes du fichier : {manquantes}. "
            "Le CSV doit contenir les mêmes colonnes que train.csv."
        )

    clients, _ = run_pipeline(df, models)

    colonnes_sortie = [
        'Customer_ID', 'Segment', 'Credit_Score_Predit',
        'Proba_Good', 'Proba_Standard', 'Proba_Poor', 'Risk_Score',
        'Risque_Categorie', 'Elasticity_Direction',
        'Proba_Elasticity_Baisse', 'Proba_Elasticity_Stable', 'Proba_Elasticity_Hausse',
        'Recommandation_Business',
    ]

    resultats = clients[colonnes_sortie].copy()
    resultats = resultats.replace({np.nan: None})
    return resultats
