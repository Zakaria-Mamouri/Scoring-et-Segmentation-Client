STATUS_COLORS = {'Good': '#0ca30c', 'Standard': '#fab219', 'Poor': '#d03b3b'}
CREDIT_SCORE_ORDER = ['Good', 'Standard', 'Poor']

ELASTICITY_COLORS = {'Baisse': '#d03b3b', 'Stable': '#fab219', 'Hausse': '#0ca30c'}
ELASTICITY_ORDER = ['Baisse', 'Stable', 'Hausse']

SEGMENT_COLORS = {
    'Salariés stables / clients matures': '#2a78d6',
    'Clients aisés à forte élasticité (premium)': '#0ca30c',
    'Jeunes clients en construction de crédit': '#fab219',
    'Clients endettés à risque': '#d03b3b',
}

RISQUE_ORDER = ['Faible', 'Moyen', 'Eleve']
RISQUE_COLORS = {'Faible': '#0ca30c', 'Moyen': '#fab219', 'Eleve': '#d03b3b'}

RECOMMANDATIONS = {
    ('Faible', 'Hausse'): "Client premium en croissance → cross-sell / upsell prioritaire",
    ('Faible', 'Stable'): "Client fidèle stable → programme de fidélisation, maintien de la relation",
    ('Faible', 'Baisse'): "Risque faible mais en dégradation → contact proactif pour anticiper",
    ('Moyen', 'Hausse'): "Potentiel en amélioration → accompagnement pour sécuriser la progression",
    ('Moyen', 'Stable'): "Profil neutre → suivi standard, pas d'action prioritaire",
    ('Moyen', 'Baisse'): "Vigilance accrue → risque de bascule, action de rétention à engager",
    ('Eleve', 'Hausse'): "Risque élevé mais en amélioration → encadrement rapproché, pas de restriction immédiate",
    ('Eleve', 'Stable'): "Risque élevé persistant → révision des conditions de crédit",
    ('Eleve', 'Baisse'): "Risque élevé et en dégradation → priorité absolue, provisionnement / recouvrement préventif",
}

SEQUENTIAL_BLUE = '#2a78d6'
PRIMARY_INK = '#0b0b0b'
SECONDARY_INK = '#52514e'
MUTED_INK = '#898781'
GRID_COLOR = '#e1e0d9'
SURFACE = '#fcfcfb'

MONTH_ORDER = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']
MONTH_NUM = {mois: i + 1 for i, mois in enumerate(MONTH_ORDER)}
