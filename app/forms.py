from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_STYLE = """
  :root {
    --blue: #2a78d6; --blue-dark: #1e5ca8; --ink: #0b0b0b; --muted: #5f5f5a;
    --surface: #fcfcfb; --line: #e1e0d9; --green: #0ca30c; --amber: #d98a00;
    --red: #d03b3b; --blue-soft: #eef4fc;
  }
  * { box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background: #f5f6f8;
         color: var(--ink); line-height: 1.5; }
  .topbar { background: var(--ink); color: #fff; padding: 0 28px; height: 58px;
            display: flex; align-items: center; gap: 18px; }
  .topbar .brand { font-size: 17px; font-weight: 700; letter-spacing: .3px; }
  .topbar .brand span { color: var(--blue); }
  .topbar nav { display: flex; gap: 6px; margin-left: 18px; }
  .topbar nav a { color: #cfcfcf; text-decoration: none; padding: 7px 13px; border-radius: 6px;
                  font-size: 14px; }
  .topbar nav a:hover, .topbar nav a.active { background: #232323; color: #fff; }
  .wrap { max-width: 1040px; margin: 26px auto; padding: 0 22px; }
  .card { background: #fff; border: 1px solid var(--line); border-radius: 10px;
          padding: 22px 26px; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
  h1 { font-size: 24px; margin: 0 0 6px; }
  h2 { font-size: 16px; margin: 26px 0 10px; color: var(--muted); text-transform: uppercase;
       letter-spacing: .4px; }
  .sub { color: var(--muted); font-size: 14px; margin-top: 0; }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 13px 18px; }
  .grid.two { grid-template-columns: repeat(2, 1fr); }
  label { display: block; font-size: 12.5px; font-weight: 600; margin-bottom: 4px; }
  .req { color: var(--red); }
  input, select { width: 100%; padding: 8px 10px; border: 1px solid #c9c8c0; border-radius: 6px;
                  font-size: 14px; background: #fff; }
  input:focus, select:focus { outline: 2px solid var(--blue-soft); border-color: var(--blue); }
  .actions { margin-top: 24px; display: flex; gap: 12px; align-items: center; }
  button, .btn { background: var(--blue); color: #fff; border: none; padding: 11px 26px;
                 border-radius: 7px; font-size: 15px; font-weight: 600; cursor: pointer; }
  button:hover, .btn:hover { background: var(--blue-dark); }
  .btn.ghost { background: #fff; color: var(--blue); border: 1px solid var(--blue); }
  .btn.ghost:hover { background: var(--blue-soft); }
  .spin { display: none; font-size: 14px; color: var(--muted); }
  .spin.vis { display: inline; }
  .err { display: none; margin-top: 16px; padding: 13px 16px; border-radius: 8px;
         background: #fdecec; border: 1px solid #f2b8b8; color: #a02020; font-size: 14px; }
  .err.vis { display: block; }
  /* Résultats */
  .result { display: none; margin-top: 26px; }
  .result.vis { display: block; }
  .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
  .metric { background: #fff; border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; }
  .metric .k { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .3px; }
  .metric .v { font-size: 22px; font-weight: 700; margin-top: 4px; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 12px;
           font-weight: 700; }
  .b-green { background: #e4f5e4; color: #0a7a0a; }
  .b-amber { background: #fdf1dc; color: #9a6600; }
  .b-red { background: #fde8e8; color: #a02020; }
  .b-blue { background: var(--blue-soft); color: var(--blue-dark); }
  .reco { margin-top: 16px; padding: 16px 18px; background: var(--blue-soft);
          border-left: 5px solid var(--blue); border-radius: 8px; font-size: 15px; }
  .reco b { display: block; margin-bottom: 3px; color: var(--blue-dark); }
  table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 13.5px; }
  th { text-align: left; background: #f2f3f5; padding: 9px 10px; border-bottom: 2px solid var(--line); }
  td { padding: 8px 10px; border-bottom: 1px solid var(--line); }
  tr:hover td { background: #fafbfc; }
  .ok { color: var(--green); font-weight: 700; }
  .ko { color: var(--red); font-weight: 700; }
  .hint { font-size: 13px; color: var(--muted); margin-top: 14px; }
  code { background: #f0f0f0; padding: 1px 5px; border-radius: 3px; font-size: 12.5px; }
  .drop { border: 2px dashed #c9c8c0; border-radius: 12px; padding: 34px; text-align: center;
          background: #fafbfc; }
  .drop.on { border-color: var(--blue); background: var(--blue-soft); }
  .drop p { margin: 6px 0 0; font-size: 13px; color: var(--muted); }
  .hero { display: grid; grid-template-columns: repeat(2, 1fr); gap: 22px; margin-top: 20px; }
  .hero .card { padding: 30px; }
  .hero .card h3 { margin: 0 0 8px; font-size: 19px; }
  .hero .card p { color: var(--muted); font-size: 14px; margin: 0 0 18px; }
  .icon { font-size: 34px; }
  .fileinfo { font-size: 13px; color: var(--muted); margin-top: 10px; }
  @media (max-width: 820px) { .grid, .grid.two, .metrics, .hero { grid-template-columns: 1fr; } }
"""

_HEADER = """
  <div class="topbar">
    <div class="brand">EURAFRIC <span>Crédit</span></div>
    <nav>
      <a href="/">Accueil</a>
      <a href="/form" class="{m1}">Saisie manuelle</a>
      <a href="/form/csv" class="{m2}">Import CSV</a>
    </nav>
  </div>
"""


def _page(title: str, body: str, menu1: str = "", menu2: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - Eurafric Crédit</title>
<style>{_STYLE}</style>
</head>
<body>
{_HEADER.format(m1=menu1, m2=menu2)}
<div class="wrap">
{body}
</div>
</body>
</html>"""


def _landing_html() -> str:
    body = """
    <div class="card">
      <h1>Bienvenue sur l'outil de scoring crédit</h1>
      <p class="sub">Scoring de nouveaux clients : score crédit, risque, segment,
      élasticité et recommandation business — à partir du pipeline Eurafric.</p>
    </div>
    <div class="hero">
      <div class="card">
        <div class="icon">🖊️</div>
        <h3>Saisie manuelle</h3>
        <p>Saisissez les informations d'un client directement dans le formulaire
        et obtenez immédiatement son profil complet.</p>
        <a class="btn" href="/form">Saisir un client</a>
      </div>
      <div class="card">
        <div class="icon">📁</div>
        <h3>Import par fichier CSV</h3>
        <p>Scorez plusieurs clients d'un coup en téléversant un fichier CSV au
        format des données d'entraînement.</p>
        <a class="btn" href="/form/csv">Importer un fichier</a>
      </div>
    </div>
    <div class="card" style="margin-top:22px">
      <h3 style="margin:0 0 6px">Documentation technique</h3>
      <p class="sub" style="margin:0">L'API expose aussi des endpoints JSON pour une
      intégration système : <a href="/docs">Swagger UI</a> · <a href="/schema">Schéma</a> ·
      <a href="/health">État des modèles</a></p>
    </div>
    """
    return _page("Accueil", body, menu1="", menu2="")


def _manual_html() -> str:
    body = """
    <div class="card">
      <h1>Saisie manuelle d'un client</h1>
      <p class="sub">Renseignez les informations du client (1 relevé mensuel).
      Les champs marqués d'un <span class="req">*</span> sont obligatoires.</p>
      <form id="form" autocomplete="off">
        <h2>Identité et revenus</h2>
        <div class="grid">
          <div><label>Customer_ID <span class="req">*</span></label>
            <input name="Customer_ID" placeholder="Ex : CUST001" required></div>
          <div><label>Mois du relevé</label>
            <select name="Month">
              <option value="">— Non précisé —</option>
              <option>January</option><option>February</option><option>March</option>
              <option>April</option><option>May</option><option>June</option>
              <option>July</option><option>August</option>
            </select>
          </div>
          <div><label>Âge <span class="req">*</span></label>
            <input name="Age" type="number" min="18" max="90" required></div>
          <div><label>Revenu annuel (€) <span class="req">*</span></label>
            <input name="Annual_Income" type="number" step="any" min="0" required></div>
          <div><label>Salaire mensuel net (€) <span class="req">*</span></label>
            <input name="Monthly_Inhand_Salary" type="number" step="any" min="0" required></div>
          <div><label>Dette en cours (€) <span class="req">*</span></label>
            <input name="Outstanding_Debt" type="number" step="any" min="0" required></div>
          <div><label>Taux d'utilisation du crédit <span class="req">*</span></label>
            <input name="Credit_Utilization_Ratio" type="number" step="0.01" min="0" max="1" required></div>
          <div><label>Total EMI mensuel (€) <span class="req">*</span></label>
            <input name="Total_EMI_per_month" type="number" step="any" min="0" required></div>
          <div><label>Montant investi mensuel (€) <span class="req">*</span></label>
            <input name="Amount_invested_monthly" type="number" step="any" min="0" required></div>
          <div><label>Solde mensuel (€) <span class="req">*</span></label>
            <input name="Monthly_Balance" type="number" step="any" required></div>
          <div><label>Ancienneté du crédit <span class="req">*</span></label>
            <input name="Credit_History_Age" placeholder="Ex : 10 Years and 3 Months" required></div>
        </div>

        <h2>Comptes et crédit</h2>
        <div class="grid">
          <div><label>Nb comptes bancaires <span class="req">*</span></label>
            <input name="Num_Bank_Accounts" type="number" min="0" required></div>
          <div><label>Nb cartes de crédit <span class="req">*</span></label>
            <input name="Num_Credit_Card" type="number" min="0" required></div>
          <div><label>Taux d'intérêt (%) <span class="req">*</span></label>
            <input name="Interest_Rate" type="number" step="any" min="0" required></div>
          <div><label>Nb de prêts <span class="req">*</span></label>
            <input name="Num_of_Loan" type="number" min="0" required></div>
          <div><label>Jours de retard <span class="req">*</span></label>
            <input name="Delay_from_due_date" type="number" min="0" required></div>
          <div><label>Nb paiements en retard <span class="req">*</span></label>
            <input name="Num_of_Delayed_Payment" type="number" step="any" min="0" required></div>
          <div><label>Changement limite de crédit <span class="req">*</span></label>
            <input name="Changed_Credit_Limit" type="number" step="any" required></div>
          <div><label>Nb demandes de crédit <span class="req">*</span></label>
            <input name="Num_Credit_Inquiries" type="number" step="any" min="0" required></div>
          <div><label>Mix de crédit <span class="req">*</span></label>
            <select name="Credit_Mix"><option>Good</option><option>Standard</option><option>Bad</option></select></div>
          <div><label>Paiement du minimum <span class="req">*</span></label>
            <select name="Payment_of_Min_Amount"><option>Yes</option><option>No</option></select></div>
        </div>

        <h2>Profil et comportement</h2>
        <div class="grid">
          <div><label>Type de prêt <span class="req">*</span></label>
            <input name="Type_of_Loan" value="Personal Loan, Auto Loan"></div>
          <div><label>Occupation <span class="req">*</span></label>
            <select name="Occupation">
              <option>Accountant</option><option>Architect</option><option>Developer</option>
              <option>Doctor</option><option>Engineer</option><option>Entrepreneur</option>
              <option>Journalist</option><option>Lawyer</option><option>Manager</option>
              <option>Mechanic</option><option>Media_Manager</option><option>Musician</option>
              <option>Scientist</option><option>Teacher</option><option>Writer</option>
            </select></div>
          <div><label>Comportement de paiement <span class="req">*</span></label>
            <select name="Payment_Behaviour">
              <option>High_spent_Large_value_payments</option>
              <option>High_spent_Medium_value_payments</option>
              <option>High_spent_Small_value_payments</option>
              <option>Low_spent_Large_value_payments</option>
              <option>Low_spent_Medium_value_payments</option>
              <option>Low_spent_Small_value_payments</option>
            </select></div>
        </div>

        <div class="actions">
          <button type="submit">Scorer le client</button>
          <span class="spin" id="spin">⏳ Analyse en cours...</span>
        </div>
      </form>
      <div class="err" id="err"></div>

      <div class="result" id="result">
        <h2 style="margin-top:8px">Résultat du scoring</h2>
        <div class="metrics">
          <div class="metric"><div class="k">Score crédit</div>
            <div class="v" id="r_score"></div></div>
          <div class="metric"><div class="k">Risque</div>
            <div class="v" id="r_risque"></div></div>
          <div class="metric"><div class="k">Segment</div>
            <div class="v" id="r_segment"></div></div>
          <div class="metric"><div class="k">Élasticité</div>
            <div class="v" id="r_elasticite"></div></div>
        </div>
        <div class="metrics" style="margin-top:14px">
          <div class="metric"><div class="k">Risk Score (0-100)</div>
            <div class="v" id="r_riskscore"></div></div>
          <div class="metric"><div class="k">P(Good)</div>
            <div class="v" id="r_pgood"></div></div>
          <div class="metric"><div class="k">P(Standard)</div>
            <div class="v" id="r_pstd"></div></div>
          <div class="metric"><div class="k">P(Poor)</div>
            <div class="v" id="r_ppoor"></div></div>
        </div>
        <div class="reco"><b>Recommandation business</b><span id="r_reco"></span></div>
      </div>
    </div>

<script>
const BADGE = {
  'Good': 'b-green', 'Standard': 'b-amber', 'Poor': 'b-red',
  'Faible': 'b-green', 'Moyen': 'b-amber', 'Eleve': 'b-red',
  'Hausse': 'b-green', 'Stable': 'b-amber', 'Baisse': 'b-red',
};
document.getElementById('form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = {};
  for (const [k, v] of fd.entries()) payload[k] = v;
  const num = ['Age','Annual_Income','Monthly_Inhand_Salary','Outstanding_Debt',
               'Credit_Utilization_Ratio','Total_EMI_per_month','Amount_invested_monthly',
               'Monthly_Balance','Num_Bank_Accounts','Num_Credit_Card','Interest_Rate',
               'Num_of_Loan','Delay_from_due_date','Num_of_Delayed_Payment',
               'Changed_Credit_Limit','Num_Credit_Inquiries'];
  for (const k of num) if (payload[k] !== '') payload[k] = Number(payload[k]);
  if (payload.Month === '') delete payload.Month;
  const errEl = document.getElementById('err');
  const spin = document.getElementById('spin');
  errEl.className = 'err'; spin.className = 'spin vis';
  try {
    const r = await fetch('/score', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ releves: [payload] })
    });
    const data = await r.json();
    spin.className = 'spin';
    if (!r.ok) {
      const d = Array.isArray(data.detail) ? data.detail.map(x => x.msg).join('; ')
                : (data.detail || 'Erreur inconnue');
      errEl.textContent = 'Erreur : ' + d; errEl.className = 'err vis'; return;
    }
    const c = data[0];
    const b = (v) => '<span class="badge ' + (BADGE[v] || 'b-blue') + '">' + v + '</span>';
    document.getElementById('r_score').innerHTML = b(c.Credit_Score_Predit);
    document.getElementById('r_risque').innerHTML = b(c.Risque_Categorie);
    document.getElementById('r_segment').innerHTML = '<span class="badge b-blue">' + c.Segment + '</span>';
    document.getElementById('r_elasticite').innerHTML = b(c.Elasticity_Direction);
    document.getElementById('r_riskscore').textContent = c.Risk_Score;
    document.getElementById('r_pgood').textContent = (c.Proba_Good * 100).toFixed(1) + ' %';
    document.getElementById('r_pstd').textContent = (c.Proba_Standard * 100).toFixed(1) + ' %';
    document.getElementById('r_ppoor').textContent = (c.Proba_Poor * 100).toFixed(1) + ' %';
    document.getElementById('r_reco').textContent = c.Recommandation_Business;
    document.getElementById('result').className = 'result vis';
    window.scrollTo({ top: document.getElementById('result').offsetTop - 20, behavior: 'smooth' });
  } catch (err) {
    spin.className = 'spin';
    errEl.textContent = 'Erreur réseau : ' + err; errEl.className = 'err vis';
  }
});
</script>
"""
    return _page("Saisie manuelle", body, menu1="active")


def _csv_html() -> str:
    body = """
    <div class="card">
      <h1>Scoring par fichier CSV</h1>
      <p class="sub">Téléversez un fichier CSV au format des données d'entraînement
      (<code>train.csv</code>) pour scorer plusieurs clients d'un coup.</p>
      <form id="form">
        <div class="drop" id="drop">
          <p><strong>Cliquez pour choisir un fichier CSV</strong><br>
             ou déposez-le ici</p>
          <input type="file" name="file" accept=".csv" id="file" hidden>
          <div class="actions" style="justify-content:center">
            <button type="button" id="pick">Choisir un fichier</button>
            <button type="submit" id="go">Scorer le fichier</button>
          </div>
          <div class="fileinfo" id="finfo"></div>
        </div>
      </form>
      <div class="spin" id="spin" style="margin-top:14px">⏳ Traitement en cours...</div>
      <div class="err" id="err"></div>

      <div class="result" id="result">
        <h2 style="margin-top:8px">Résultats (<span id="nres">0</span> clients)</h2>
        <div class="actions" style="margin-top:6px">
          <button type="button" id="dl">Télécharger le CSV des résultats</button>
        </div>
        <div style="overflow-x:auto">
        <table id="tbl"></table>
        </div>
      </div>
    </div>

<script>
const drop = document.getElementById('drop');
const input = document.getElementById('file');
const finfo = document.getElementById('finfo');
document.getElementById('pick').addEventListener('click', () => input.click());
input.addEventListener('change', () => {
  finfo.textContent = input.files.length ? 'Fichier : ' + input.files[0].name : '';
});
['dragover','dragenter'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.className='drop on'; }));
['dragleave','drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.className='drop'; }));
drop.addEventListener('drop', e => {
  if (e.dataTransfer.files.length) { input.files = e.dataTransfer.files;
    finfo.textContent = 'Fichier : ' + input.files[0].name; }
});
let lastData = null;

document.getElementById('form').addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!input.files.length) { alert('Veuillez choisir un fichier CSV.'); return; }
  const fd = new FormData();
  fd.append('file', input.files[0]);
  const spin = document.getElementById('spin');
  const errEl = document.getElementById('err');
  spin.style.display = 'block'; errEl.className = 'err';
  try {
    const r = await fetch('/score/csv?format=json', { method: 'POST', body: fd });
    const data = await r.json();
    spin.style.display = 'none';
    if (!r.ok) {
      const d = Array.isArray(data.detail) ? data.detail.join('; ') : (data.detail || 'Erreur');
      errEl.textContent = 'Erreur : ' + d; errEl.className = 'err vis'; return;
    }
    lastData = data;
    renderTable(data);
    document.getElementById('result').className = 'result vis';
    window.scrollTo({ top: document.getElementById('result').offsetTop - 20, behavior: 'smooth' });
  } catch (err) {
    spin.style.display = 'none';
    errEl.textContent = 'Erreur réseau : ' + err; errEl.className = 'err vis';
  }
});

document.getElementById('dl').addEventListener('click', () => {
  if (!lastData) return;
  const cols = Object.keys(lastData[0]);
  const rows = lastData.map(r => cols.map(c => {
    const v = r[c]; return (v === null || v === undefined) ? '' : String(v).replace(/"/g,'""');
  }).join(','));
  const csv = cols.join(',') + '\\n' + rows.join('\\n');
  const blob = new Blob(['\\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'resultats_scoring.csv';
  document.body.appendChild(a); a.click(); a.remove();
});

function renderTable(data) {
  document.getElementById('nres').textContent = data.length;
  const cols = ['Customer_ID','Credit_Score_Predit','Risk_Score','Risque_Categorie',
                'Segment','Elasticity_Direction','Recommandation_Business'];
  let html = '<thead><tr><th>' + cols.join('</th><th>') + '</th></tr></thead><tbody>';
  for (const r of data) {
    html += '<tr><td>' + cols.map(c => {
      if (c === 'Risk_Score') return r[c];
      const v = r[c] ?? '—';
      if (c === 'Credit_Score_Predit') {
        const cls = v === 'Good' ? 'ok' : (v === 'Poor' ? 'ko' : '');
        return '<b class="' + cls + '">' + v + '</b>';
      }
      return v;
    }).join('</td><td>') + '</td></tr>';
  }
  html += '</tbody>';
  document.getElementById('tbl').innerHTML = html;
}
</script>
"""
    return _page("Import CSV", body, menu2="active")


@router.get("/", response_class=HTMLResponse)
def accueil():
    return _landing_html()


@router.get("/form", response_class=HTMLResponse)
def formulaire():
    return _manual_html()


@router.get("/form/csv", response_class=HTMLResponse)
def formulaire_csv():
    return _csv_html()
