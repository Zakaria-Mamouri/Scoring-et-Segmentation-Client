import os

# Chemin du dossier de ce projet FastAPI
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dossier contenant les artefacts de modeles
# 1) Variable d'environnement EURAFRIC_MODELS_DIR
# 2) Un dossier models/ cote de ce projet
# 3) Le dossier models/ du projet principal (voisin)
DEFAULT_MODELS_CANDIDATES = [
    os.environ.get('EURAFRIC_MODELS_DIR', ''),
    os.path.join(BASE_DIR, 'models'),
    os.path.join(os.path.dirname(BASE_DIR), 'Projet_Eurafric', 'models'),
    os.path.join(os.path.dirname(BASE_DIR), 'Projet_Eurafric-20260726T133855Z-1-001', 'Projet_Eurafric', 'models'),
]

MODELS_DIR = next((p for p in DEFAULT_MODELS_CANDIDATES if p and os.path.isdir(p)), DEFAULT_MODELS_CANDIDATES[1])

# Dossier des donnees (train_segments.csv etc.) - facultatif
DEFAULT_DATA_CANDIDATES = [
    os.environ.get('EURAFRIC_DATA_DIR', ''),
    os.path.join(BASE_DIR, 'data'),
    os.path.join(os.path.dirname(BASE_DIR), 'Projet_Eurafric', 'data'),
    os.path.join(os.path.dirname(BASE_DIR), 'Projet_Eurafric-20260726T133855Z-1-001', 'Projet_Eurafric', 'data'),
]

DATA_DIR = next((p for p in DEFAULT_DATA_CANDIDATES if p and os.path.isdir(p)), DEFAULT_DATA_CANDIDATES[1])

# Fichiers modeles attendus
MODEL_FILES = {
    'stats_ref_nettoyage': 'reference_stats_nettoyage.joblib',
    'stats_ref_elasticite': 'reference_stats_elasticite.joblib',
    'kmeans': 'kmeans_segmentation.joblib',
    'scaler_segmentation': 'scaler_segmentation.joblib',
    'segmentation_columns': 'segmentation_feature_columns.joblib',
    'rf_credit': 'random_forest_credit_score_production.joblib',
    'xgb_elasticity': 'elasticity_direction_model.pkl',
    'le_elasticity': 'elasticity_label_encoder.pkl',
    'elasticity_columns': 'elasticity_feature_columns.pkl',
    'seuils_risque': 'risque_categorie_seuils.joblib',
}
