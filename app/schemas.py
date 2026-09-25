from typing import List, Optional, Union

from pydantic import BaseModel, Field

# Champs attendus pour une ligne de releve mensuel (schema de train.csv,
# sans ID/Name/SSN qui ne sont pas utilises par le pipeline).
COLONNES_INPUT = [
    'Customer_ID', 'Month', 'Age', 'Annual_Income', 'Monthly_Inhand_Salary',
    'Num_Bank_Accounts', 'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan',
    'Type_of_Loan', 'Delay_from_due_date', 'Num_of_Delayed_Payment',
    'Changed_Credit_Limit', 'Num_Credit_Inquiries', 'Credit_Mix',
    'Outstanding_Debt', 'Credit_Utilization_Ratio', 'Credit_History_Age',
    'Payment_of_Min_Amount', 'Total_EMI_per_month', 'Amount_invested_monthly',
    'Payment_Behaviour', 'Occupation', 'Monthly_Balance',
]

COLONNES_OBLIGATOIRES = [
    'Customer_ID', 'Age', 'Annual_Income', 'Monthly_Inhand_Salary',
    'Num_Bank_Accounts', 'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan',
    'Type_of_Loan', 'Delay_from_due_date', 'Num_of_Delayed_Payment',
    'Changed_Credit_Limit', 'Num_Credit_Inquiries', 'Credit_Mix',
    'Outstanding_Debt', 'Credit_Utilization_Ratio', 'Credit_History_Age',
    'Payment_of_Min_Amount', 'Total_EMI_per_month', 'Amount_invested_monthly',
    'Payment_Behaviour', 'Occupation', 'Monthly_Balance',
]


class ReleveMensuel(BaseModel):
    """Un relevé mensuel d'un client (une ligne du CSV d'entrée)."""
    Customer_ID: str = Field(..., description="Identifiant du client")
    Month: Optional[str] = Field(None, description="Mois du relevé (January à August)")
    Age: int = Field(..., description="Âge du client")
    Annual_Income: float = Field(..., description="Revenu annuel")
    Monthly_Inhand_Salary: float = Field(..., description="Salaire mensuel net")
    Num_Bank_Accounts: int = Field(..., description="Nombre de comptes bancaires")
    Num_Credit_Card: int = Field(..., description="Nombre de cartes de crédit")
    Interest_Rate: int = Field(..., description="Taux d'intérêt")
    Num_of_Loan: int = Field(..., description="Nombre de prêts")
    Type_of_Loan: str = Field(..., description="Types de prêts (séparés par des virgules)")
    Delay_from_due_date: int = Field(..., description="Jours de retard")
    Num_of_Delayed_Payment: float = Field(..., description="Nombre de paiements en retard")
    Changed_Credit_Limit: float = Field(..., description="Changement de limite de crédit")
    Num_Credit_Inquiries: float = Field(..., description="Nombre de demandes de crédit")
    Credit_Mix: str = Field(..., description="Mix de crédit (Good/Standard/Bad)")
    Outstanding_Debt: float = Field(..., description="Dette en cours")
    Credit_Utilization_Ratio: float = Field(..., description="Taux d'utilisation du crédit")
    Credit_History_Age: str = Field(..., description="Ancienneté du crédit (ex: '10 Years and 3 Months')")
    Payment_of_Min_Amount: str = Field(..., description="Paiement du minimum (Yes/No)")
    Total_EMI_per_month: float = Field(..., description="Total EMI mensuel")
    Amount_invested_monthly: float = Field(..., description="Montant investi mensuel")
    Payment_Behaviour: str = Field(..., description="Comportement de paiement")
    Occupation: str = Field(..., description="Profession du client")
    Monthly_Balance: float = Field(..., description="Solde mensuel")


class ScoreResponse(BaseModel):
    Customer_ID: str
    Segment: str
    Credit_Score_Predit: str
    Proba_Good: float
    Proba_Standard: float
    Proba_Poor: float
    Risk_Score: float
    Risque_Categorie: str
    Elasticity_Direction: str
    Proba_Elasticity_Baisse: float
    Proba_Elasticity_Stable: float
    Proba_Elasticity_Hausse: float
    Recommandation_Business: str


class ScoreRequest(BaseModel):
    """Requête de scoring : une liste de relevés mensuels (1 client = 1+ relevés)."""
    releves: List[ReleveMensuel] = Field(
        ...,
        description="Liste des relevés mensuels à scorer. Plusieurs relevés d'un même client "
                    "sont agrégés automatiquement (1 à 8 relevés par client).",
    )


class HealthResponse(BaseModel):
    status: str
    models_dir: str
    models_loaded: List[str]
