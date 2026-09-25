from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import ValidationError

from app.config import MODELS_DIR
from app.forms import router as forms_router
from app.schemas import (
    COLONNES_INPUT,
    HealthResponse,
    ReleveMensuel,
    ScoreRequest,
    ScoreResponse,
)
from app.service import get_models, load_models, score_dataframe, score_releves

app = FastAPI(
    title="Eurafric - API de scoring crédit",
    description=(
        "API de scoring crédit pour nouveaux clients : saisie manuelle (JSON) "
        "ou import par fichier CSV. Pipeline complet : nettoyage, feature engineering, "
        "segmentation (K-Means), scoring crédit (Random Forest), élasticité (XGBoost) "
        "et recommandations business."
    ),
    version="1.0.0",
)

app.include_router(forms_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales de cache des modèles


@app.on_event("startup")
def _startup():
    try:
        load_models()
    except Exception:
        pass


@app.get("/accueil-api", response_class=HTMLResponse)
def accueil_api():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
      <meta charset="utf-8">
      <title>Eurafric - API de scoring crédit</title>
      <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px auto; max-width: 760px;
               color: #0b0b0b; line-height: 1.6; }
        h1 { color: #0b0b0b; border-bottom: 3px solid #2a78d6; padding-bottom: 8px; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; }
        li { margin: 6px 0; }
      </style>
    </head>
    <body>
      <h1>Eurafric - API de scoring crédit</h1>
      <p>Pipeline complet : nettoyage → feature engineering → segmentation (K-Means)
         → scoring crédit (Random Forest) → élasticité (XGBoost) → recommandations.</p>
      <p>Interface utilisateur : <a href="/form">saisie manuelle</a> ·
         <a href="/form/csv">import CSV</a> · <a href="/">accueil</a></p>
      <h3>Endpoints</h3>
      <ul>
        <li><code>GET  /health</code> — état des modèles</li>
        <li><code>GET  /schema</code> — colonnes d'entrée / sortie attendues</li>
        <li><code>POST /score</code> — scoring manuel (JSON)</li>
        <li><code>POST /score/csv</code> — scoring par fichier CSV</li>
      </ul>
      <h3>Documentation interactive</h3>
      <p><a href="/docs">Swagger UI</a> — <a href="/redoc">ReDoc</a></p>
    </body>
    </html>
    """)


@app.get("/health", response_model=HealthResponse)
def health():
    try:
        models = get_models()
        ok = True
    except Exception:
        models = {}
        ok = False
    return HealthResponse(
        status="ok" if ok else "error",
        models_dir=MODELS_DIR,
        models_loaded=list(models.keys()),
    )


@app.get("/schema")
def schema_endpoint():
    from app.schemas import COLONNES_OBLIGATOIRES
    return {
        "colonnes_entree": COLONNES_INPUT,
        "colonnes_obligatoires": COLONNES_OBLIGATOIRES,
        "colonnes_sortie": [
            "Customer_ID", "Segment", "Credit_Score_Predit",
            "Proba_Good", "Proba_Standard", "Proba_Poor", "Risk_Score",
            "Risque_Categorie", "Elasticity_Direction",
            "Proba_Elasticity_Baisse", "Proba_Elasticity_Stable", "Proba_Elasticity_Hausse",
            "Recommandation_Business",
        ],
        "exemple_entree": {
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
                    "Monthly_Balance": 3200,
                }
            ]
        },
    }


@app.post("/score", response_model=List[ScoreResponse])
def score_manuel(payload: ScoreRequest):
    """Scoring de nouveaux clients à partir d'une liste de relevés mensuels (JSON).

    - Un client peut avoir de 1 à 8 relevés mensuels (agrégés automatiquement).
    - Plusieurs clients peuvent être envoyés dans le même appel.
    """
    if not payload.releves:
        raise HTTPException(status_code=422, detail="La liste 'releves' est vide.")
    try:
        resultats = score_releves(payload.releves)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return resultats.to_dict(orient="records")


@app.post("/score/json")
def score_json_payload(payload: dict):
    """Variante flexible : envoi d'un JSON brut (list ou dict avec clé 'releves')."""
    releves_data = payload.get("releves") if isinstance(payload, dict) and "releves" in payload else payload
    if isinstance(releves_data, dict):
        releves_data = [releves_data]
    if not isinstance(releves_data, list) or not releves_data:
        raise HTTPException(status_code=422, detail="Payload invalide : attendu une liste de relevés.")
    try:
        validated = [ReleveMensuel(**r) for r in releves_data]
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())
    try:
        resultats = score_releves(validated)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return resultats.to_dict(orient="records")


@app.post("/score/csv")
def score_csv(file: UploadFile = File(...), format: str = "csv"):
    """Scoring de nouveaux clients à partir d'un fichier CSV.

    Le CSV doit contenir les mêmes colonnes que train.csv
    (Customer_ID, Month, Age, Annual_Income, etc.).

    - `format=csv` (défaut) : renvoie un fichier CSV de résultats à télécharger.
    - `format=json` : renvoie les résultats en JSON (pour les formulaires web).
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=422, detail="Le fichier doit être un CSV.")

    import io

    import pandas as pd

    try:
        content = file.file.read().decode("utf-8")
        df_brut = pd.read_csv(io.StringIO(content), low_memory=False)
    except UnicodeDecodeError:
        file.file.seek(0)
        df_brut = pd.read_csv(file.file, encoding="latin-1", low_memory=False)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Erreur de lecture du CSV : {exc}")

    try:
        resultats = score_dataframe(df_brut)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    if format == "json":
        return resultats.to_dict(orient="records")

    return Response(
        content=resultats.to_csv(index=False),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=resultats_scoring.csv"},
    )
