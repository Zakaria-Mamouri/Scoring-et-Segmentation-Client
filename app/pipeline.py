import numpy as np
import pandas as pd

from app.constants import MONTH_ORDER, MONTH_NUM, RISQUE_ORDER, RECOMMANDATIONS


def nettoyer_nouveaux_clients(df_source, stats_ref):
    df = df_source.copy()
    df = df.replace(stats_ref['placeholders'], np.nan)

    def nettoyer_numerique(serie):
        return pd.to_numeric(serie.astype(str).str.replace('_', '', regex=False).str.strip(), errors='coerce')

    for col in stats_ref['colonnes_numeriques_underscore']:
        if col in df.columns:
            df[col] = nettoyer_numerique(df[col])

    def corriger_aberrantes(dataframe, colonne, borne_min, borne_max, mediane_reference):
        serie = dataframe[colonne].copy()
        hors_plage = ~serie.between(borne_min, borne_max) & serie.notna()
        serie[hors_plage] = np.nan
        valeurs_valides = serie.where(serie.between(borne_min, borne_max))
        mediane_client = valeurs_valides.groupby(dataframe['Customer_ID']).transform('median')
        serie = serie.fillna(mediane_client)
        serie = serie.fillna(mediane_reference)
        return serie

    for col, (lo, hi) in stats_ref['plages_valides'].items():
        if col in df.columns:
            df[col] = corriger_aberrantes(df, col, lo, hi, stats_ref['medianes_globales_plages_valides'][col])

    for col in stats_ref['colonnes_ffill_bfill_client']:
        if col in df.columns:
            df[col] = df.groupby('Customer_ID')[col].transform(lambda s: s.ffill().bfill())

    if 'Monthly_Inhand_Salary' in df.columns:
        df['Monthly_Inhand_Salary'] = df['Monthly_Inhand_Salary'].fillna(
            stats_ref['mediane_globale_monthly_inhand_salary'])

    for col, mode_ref in stats_ref['modes_globaux_ffill_bfill_client'].items():
        if col in df.columns:
            df[col] = df[col].fillna(mode_ref)

    if 'Type_of_Loan' in df.columns:
        df['Type_of_Loan'] = df['Type_of_Loan'].fillna('No Loan')

    def convertir_en_mois(valeur):
        if pd.isna(valeur):
            return np.nan
        match = pd.Series([valeur]).str.extract(r'(\d+)\s+Years?\s+and\s+(\d+)\s+Months?')
        annees, mois = match.iloc[0]
        if pd.isna(annees) or pd.isna(mois):
            return np.nan
        return int(annees) * 12 + int(mois)

    if 'Credit_History_Age' in df.columns:
        df['Credit_History_Age_Months'] = df['Credit_History_Age'].apply(convertir_en_mois)
        df['Credit_History_Age_Months'] = df.groupby('Customer_ID')['Credit_History_Age_Months'].transform(
            lambda s: s.ffill().bfill())
        df['Credit_History_Age_Months'] = df['Credit_History_Age_Months'].fillna(
            stats_ref['mediane_globale_credit_history_age_months'])

    for col in stats_ref['colonnes_mediane_client']:
        if col in df.columns:
            implausibles = df[col].abs() > stats_ref['seuil_plausibilite']
            df.loc[implausibles, col] = np.nan
            mediane_client = df.groupby('Customer_ID')[col].transform('median')
            df[col] = df[col].fillna(mediane_client)
            df[col] = df[col].fillna(stats_ref['medianes_globales_mediane_client'][col])

    col_mode = stats_ref['colonne_mode_client']
    if col_mode in df.columns:
        def _mode_ou_nan(s):
            m = s.mode(dropna=True)
            return m.iloc[0] if not m.empty else np.nan
        mode_client = df.groupby('Customer_ID')[col_mode].transform(_mode_ou_nan)
        df[col_mode] = df[col_mode].fillna(mode_client)
        df[col_mode] = df[col_mode].fillna(stats_ref['mode_global_mode_client'])

    return df


def feature_engineering_nouveaux_clients(df_source, stats_ref_elast):
    df = df_source.copy()

    df['Ratio_Dette_Revenu'] = df['Outstanding_Debt'] / df['Annual_Income']
    df['Ratio_EMI_Salaire'] = df['Total_EMI_per_month'] / df['Monthly_Inhand_Salary']
    df['Taux_Investissement'] = df['Amount_invested_monthly'] / df['Monthly_Inhand_Salary']
    df['Nb_produits'] = df['Num_Bank_Accounts'] + df['Num_Credit_Card'] + df['Num_of_Loan']

    for col in ['Ratio_Dette_Revenu', 'Ratio_EMI_Salaire', 'Taux_Investissement', 'Nb_produits']:
        df.loc[np.isinf(df[col]), col] = np.nan

    stats_balance = df.groupby('Customer_ID')['Monthly_Balance'].agg(['mean', 'std'])
    stats_balance['CV_Balance'] = stats_balance['std'] / stats_balance['mean']
    cas_degeneres_cv = (stats_balance['mean'] <= 0) | stats_balance['CV_Balance'].isna()
    stats_balance.loc[cas_degeneres_cv, 'CV_Balance'] = stats_ref_elast['mediane_cv_balance']
    df = df.merge(stats_balance['CV_Balance'], on='Customer_ID', how='left')

    if 'Month' in df.columns:
        df['Month_num'] = df['Month'].map(MONTH_NUM)
        df = df.sort_values(['Customer_ID', 'Month_num'])

    def regression_log_lineaire(groupe):
        solde = groupe['Monthly_Balance'].to_numpy()
        t = np.arange(len(solde))
        valide = solde > 0
        if valide.sum() < 3:
            return pd.Series({'Elasticite_Tendance': np.nan, 'Volatilite_Residuelle': np.nan})
        log_solde = np.log(solde[valide])
        t_valide = t[valide]
        beta, alpha = np.polyfit(t_valide, log_solde, 1)
        residus = log_solde - (alpha + beta * t_valide)
        return pd.Series({
            'Elasticite_Tendance': beta,
            'Volatilite_Residuelle': residus.std(ddof=1) if valide.sum() > 1 else 0.0,
        })

    elasticite_v2 = (
        df.groupby('Customer_ID')[['Monthly_Balance']]
        .apply(regression_log_lineaire)
        .reset_index()
    )
    df = df.merge(elasticite_v2, on='Customer_ID', how='left')

    df['Elasticite_Tendance'] = df['Elasticite_Tendance'].fillna(stats_ref_elast['mediane_elasticite_tendance'])
    df['Volatilite_Residuelle'] = df['Volatilite_Residuelle'].fillna(stats_ref_elast['mediane_volatilite_residuelle'])

    TYPES_PRET_CIBLES = ['Auto Loan', 'Personal Loan', 'Credit-Builder Loan', 'Home Equity Loan',
                          'Mortgage Loan', 'Student Loan', 'Debt Consolidation Loan', 'Payday Loan']

    def parser_types_prets(valeur):
        if pd.isna(valeur):
            return set()
        items = [x.strip() for x in str(valeur).split(',')]
        items = [x[4:].strip() if x.lower().startswith('and ') else x for x in items]
        return set(items)

    types_par_ligne = df['Type_of_Loan'].apply(parser_types_prets)
    types_par_client = types_par_ligne.groupby(df['Customer_ID']).agg(lambda s: set.union(*s))
    colonnes_prets = ['Loan_' + t.replace(' ', '_').replace('-', '_') for t in TYPES_PRET_CIBLES]
    loan_features = pd.DataFrame(index=types_par_client.index)
    for type_pret, colonne in zip(TYPES_PRET_CIBLES, colonnes_prets):
        loan_features[colonne] = types_par_client.apply(lambda s, t=type_pret: int(t in s))
    loan_features['Loan_No_Loan'] = (loan_features[colonnes_prets].sum(axis=1) == 0).astype(int)

    if 'Month' in df.columns:
        df['Month'] = pd.Categorical(df['Month'], categories=MONTH_ORDER, ordered=True)
        df = df.sort_values(['Customer_ID', 'Month'])

    colonnes_numeriques = [
        'Age', 'Annual_Income', 'Monthly_Inhand_Salary', 'Num_Bank_Accounts',
        'Num_Credit_Card', 'Interest_Rate', 'Num_of_Loan', 'Delay_from_due_date',
        'Num_of_Delayed_Payment', 'Changed_Credit_Limit', 'Num_Credit_Inquiries',
        'Outstanding_Debt', 'Credit_Utilization_Ratio', 'Total_EMI_per_month',
        'Amount_invested_monthly', 'Monthly_Balance', 'Credit_History_Age_Months',
        'Ratio_Dette_Revenu', 'Ratio_EMI_Salaire', 'Taux_Investissement',
        'Nb_produits', 'CV_Balance', 'Elasticite_Tendance', 'Volatilite_Residuelle',
    ]
    colonnes_categorielles = ['Occupation', 'Credit_Mix', 'Payment_of_Min_Amount', 'Payment_Behaviour']
    colonnes_numeriques = [c for c in colonnes_numeriques if c in df.columns]
    colonnes_categorielles = [c for c in colonnes_categorielles if c in df.columns]

    def mode_ou_nan(s):
        m = s.mode(dropna=True)
        return m.iloc[0] if not m.empty else np.nan

    agg_numerique = df.groupby('Customer_ID')[colonnes_numeriques].mean()
    agg_categorielle = df.groupby('Customer_ID')[colonnes_categorielles].agg(mode_ou_nan)
    df_client = agg_numerique.join(agg_categorielle).join(loan_features).reset_index()

    CREDIT_MIX_ORDRE = {'Bad': 0, 'Standard': 1, 'Good': 2}
    df_client['Credit_Mix'] = df_client['Credit_Mix'].map(CREDIT_MIX_ORDRE)
    PAYMENT_MIN_ORDRE = {'No': 0, 'Yes': 1}
    df_client['Payment_of_Min_Amount'] = df_client['Payment_of_Min_Amount'].map(PAYMENT_MIN_ORDRE)
    df_client = pd.get_dummies(df_client, columns=['Occupation', 'Payment_Behaviour'],
                                prefix=['Occupation', 'Payment_Behaviour'])
    colonnes_dummies = [c for c in df_client.columns
                        if c.startswith('Occupation_') or c.startswith('Payment_Behaviour_')]
    df_client[colonnes_dummies] = df_client[colonnes_dummies].astype(int)

    colonnes_a_supprimer = [c for c in ['ID', 'Name', 'SSN', 'Month', 'Monthly_Inhand_Salary']
                            if c in df_client.columns]
    df_client = df_client.drop(columns=colonnes_a_supprimer)
    return df_client


def identifier_segments(profil):
    restants = list(profil.index)
    noms = {}
    c_endettes = profil.loc[restants, 'Ratio_Dette_Revenu'].idxmax()
    noms[c_endettes] = 'Clients endettés à risque'
    restants.remove(c_endettes)
    c_instables = profil.loc[restants, 'Volatilite_Residuelle'].idxmax()
    noms[c_instables] = 'Clients aisés à forte élasticité (premium)'
    restants.remove(c_instables)
    c_salaries = profil.loc[restants, 'Credit_History_Age_Months'].idxmax()
    noms[c_salaries] = 'Salariés stables / clients matures'
    restants.remove(c_salaries)
    noms[restants[0]] = 'Jeunes clients en construction de crédit'
    return noms


def run_pipeline(df_brut, models):
    stats_ref_nettoyage = models['stats_ref_nettoyage']
    stats_ref_elasticite = models['stats_ref_elasticite']
    kmeans = models['kmeans']
    scaler_seg = models['scaler_segmentation']
    seg_cols = models['segmentation_columns']
    rf_credit = models['rf_credit']
    xgb_elast = models['xgb_elasticity']
    le_elast = models['le_elasticity']
    elast_cols = models['elasticity_columns']
    seuils_risque = models.get('seuils_risque')

    df_nettoye = nettoyer_nouveaux_clients(df_brut, stats_ref_nettoyage)
    clients = feature_engineering_nouveaux_clients(df_nettoye, stats_ref_elasticite)

    centroides_originaux = pd.DataFrame(
        scaler_seg.inverse_transform(kmeans.cluster_centers_),
        columns=seg_cols,
    )
    noms_segments = identifier_segments(centroides_originaux)

    X_seg = clients[seg_cols]
    X_seg_scaled = scaler_seg.transform(X_seg)
    clients['Cluster'] = kmeans.predict(X_seg_scaled)
    clients['Segment'] = clients['Cluster'].map(noms_segments)

    colonnes_a_exclure_credit = [c for c in clients.columns
                                  if c == 'Customer_ID' or c.startswith('Cluster') or c.startswith('Segment')]
    X_credit = clients.drop(columns=[c for c in colonnes_a_exclure_credit if c in clients.columns])
    X_credit = X_credit.reindex(columns=rf_credit.feature_names_in_, fill_value=0)

    proba_credit = pd.DataFrame(
        rf_credit.predict_proba(X_credit), columns=rf_credit.classes_, index=clients.index,
    )
    clients['Credit_Score_Predit'] = rf_credit.predict(X_credit)
    for classe in ['Good', 'Standard', 'Poor']:
        clients[f'Proba_{classe}'] = proba_credit[classe].values

    RISK_WEIGHTS = {'Good': 0, 'Standard': 1, 'Poor': 2}
    score_brut = sum(proba_credit[classe] * poids for classe, poids in RISK_WEIGHTS.items())
    clients['Risk_Score'] = (score_brut / max(RISK_WEIGHTS.values()) * 100).round(2)

    X_elasticity = clients.drop(columns=[c for c in ['Volatilite_Residuelle', 'Cluster'] if c in clients.columns])
    X_elasticity = pd.get_dummies(X_elasticity, columns=['Segment'], prefix='Segment')
    X_elasticity = X_elasticity.reindex(columns=elast_cols, fill_value=0)

    proba_elasticity = pd.DataFrame(
        xgb_elast.predict_proba(X_elasticity), columns=le_elast.classes_, index=clients.index,
    )
    clients['Elasticity_Direction'] = le_elast.inverse_transform(xgb_elast.predict(X_elasticity))
    for classe in ['Baisse', 'Stable', 'Hausse']:
        clients[f'Proba_Elasticity_{classe}'] = proba_elasticity[classe].values

    if seuils_risque is not None and len(seuils_risque) == len(RISQUE_ORDER) + 1:
        def _categorie_risque(score):
            if pd.isna(score):
                return 'Eleve'
            for cat, borne in zip(RISQUE_ORDER, seuils_risque[1:]):
                if score <= borne:
                    return cat
            return 'Eleve'

        clients['Risque_Categorie'] = clients['Risk_Score'].apply(_categorie_risque)
    else:
        clients['Risque_Categorie'] = pd.qcut(
            clients['Risk_Score'], q=3, labels=RISQUE_ORDER,
        )
    clients['Recommandation_Business'] = clients.apply(
        lambda ligne: RECOMMANDATIONS[(ligne['Risque_Categorie'], ligne['Elasticity_Direction'])],
        axis=1,
    )

    return clients, X_credit
