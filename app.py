import streamlit as st
import time
import random
import string

# =========================
# CONFIG BÁSICA (sem imagem)
# =========================
st.set_page_config(page_title="VOXA Triagem", layout="centered", page_icon="⚕️")

# =========================
# ESTILOS (UI/UX)
# =========================
st.markdown(
    """
    <style>
    :root{
      --primary:#7b5dd3;
      --primary-2:#8a60d8;
      --ink:#0f1720;
      --muted:#6b7280;
      --bg-glass: rgba(255,255,255,0.86);
      --ring: rgba(124,58,237,0.35);
    }
    #MainMenu, header, footer {display:none;}

    body { background: radial-gradient(1200px 600px at 20% 0%, #ffffff 0%, #f8fafc 60%, #f3f4f6 100%) !important; }

    .container-max {
      max-width: 1200px;
      margin: 0 auto;
      padding: 16px 12px 60px 12px;
      color: var(--ink);
      font-family: Inter, ui-sans-serif, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
    }

    .hero { text-align:center; margin: 6px auto 14px auto; }
    .hero .title { font-weight: 800; font-size: 40px; letter-spacing: -0.5px; }
    .hero .sub { color: var(--muted); margin-top: 2px; font-size: 14.5px; }

    .card {
      background: var(--bg-glass);
      border: 1px solid rgba(17, 25, 40, 0.08);
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 10px 30px rgba(2,12,27,0.06);
      -webkit-backdrop-filter: blur(8px) saturate(1.2);
      backdrop-filter: blur(8px) saturate(1.2);
    }

    .section-title{ font-size: 22px; font-weight: 700; margin: 8px 0 12px 0; }

    .stButton>button {
      background: linear-gradient(90deg, var(--primary), var(--primary-2));
      color: #fff; border: none; border-radius: 10px;
      padding: 10px 16px; font-weight: 700;
      box-shadow: 0 6px 18px rgba(123,93,211,0.25);
      transition: transform .05s, filter .15s;
    }
    .stButton>button:hover { filter: brightness(1.03); }
    .stButton>button:active { transform: translateY(1px); }

    .stTextInput>div>div>input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox>div>div>div {
      border-radius: 10px !important;
      border: 1px solid rgba(2,12,27,0.10) !important;
    }
    .stTextInput>div>div>input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
      outline: 2px solid var(--ring) !important;
      border-color: transparent !important;
      box-shadow: none !important;
    }

    [data-baseweb="slider"] div[role="slider"] {
      outline: none !important;
      border: 2px solid var(--primary) !important;
      box-shadow: 0 0 0 6px rgba(123,93,211,0.15) !important;
    }

    .badge { display:inline-block; padding:8px 12px; border-radius:10px; font-weight:700; }
    .badge-green { color:#065f46; background:#d1fae5; }
    .badge-yellow{ color:#854d0e; background:#fff7ed; }
    .badge-red{ color:#7f1d1d; background:#fee2e2; }

    .kpi-grid{ display:grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin: 10px 0 6px 0; }
    .kpi{ background:#fff; border:1px solid rgba(2,12,27,0.06); border-radius:14px; padding:14px; box-shadow: 0 6px 16px rgba(2,12,27,0.05); text-align:center; }
    .kpi .label{ color:var(--muted); font-size:12px; margin-bottom:4px;}
    .kpi .value{ font-size:22px; font-weight:800; letter-spacing:-0.3px;}

    .chips{ display:flex; flex-wrap:wrap; gap:8px; margin-top:8px;}
    .chip{ background:#f3f4f6; border:1px solid #e5e7eb; color:#111827; padding:6px 10px; border-radius:999px; font-size:13px; box-shadow: inset 0 -1px 0 rgba(0,0,0,0.02); }

    .anim { display:flex; align-items:center; justify-content:center; height:100px; margin: 0 0 8px 0; }
    .pulse { font-size:18px; padding:10px 14px; border-radius:12px; background: rgba(67,143,171,0.08); color:#1f2937; animation: pulse 2.4s infinite; border: 1px solid rgba(67,143,171,0.12); }
    @keyframes pulse { 0%{transform:translateY(0);opacity:.9} 50%{transform:translateY(-6px);opacity:1} 100%{transform:translateY(0);opacity:.9}}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HEADER / HERO
# =========================
st.markdown('<div class="container-max">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="hero">
      <div class="title">🩺 VOXA Triagem</div>
      <div class="sub">Protótipo educativo para <b>pré-triagem</b>. Ajuste às normas do serviço.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# CARD DO FORM
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

wait_markdown = st.markdown('<div class="anim"><div class="pulse">Carregando interface...</div></div>', unsafe_allow_html=True)
time.sleep(1.0)
wait_markdown.empty()

# ---------- Lógica ----------
def gerar_senha(prefix="IE"):
    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{token}"

def calcular_score_multiselect(sintomas, dor=0, duracao_dias=0):
    score = 0
    if "Falta de ar importante" in sintomas or "Dor no peito forte/pressão no peito" in sintomas:
        score += 8
    if "Sangramento intenso que não para" in sintomas:
        score += 8
    if "Desmaio ou perda de consciência" in sintomas or "Convulsão" in sintomas:
        score += 8
    score += int(dor / 2)
    if "Rigidez de nuca com febre" in sintomas or "Vômitos persistentes" in sintomas or "Queda recente com dor" in sintomas:
        score += 2
    if duracao_dias >= 3:
        score += 1
    return score

def score_para_categoria(score):
    if score >= 8:
        return "vermelho", "grave"
    elif score >= 5:
        return "amarelo", "moderado"
    else:
        return "verde", "leve"

# ---------- Form ----------
st.markdown('<div class="section-title">Informações iniciais</div>', unsafe_allow_html=True)
with st.form("triagem_form"):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome completo")
        idade = st.number_input("Idade", min_value=0, max_value=120, value=1)
        telefone = st.text_input("Telefone (opcional)")
    with col2:
        dor = st.slider("Dor agora (0 = sem dor, 10 = pior possível)", 0, 10, 3)
        duracao_dias = st.number_input("Há quantos dias você apresenta sintomas?", min_value=0, max_value=365, value=1)

    st.markdown('<div class="section-title">Selecione sintomas que se aplicam</div>', unsafe_allow_html=True)
    sintomas = st.multiselect(
        "Sintomas",
        [
            "Dor no peito forte/pressão no peito",
            "Falta de ar importante",
            "Falta de ar leve/moderada",
            "Desmaio ou perda de consciência",
            "Confusão mental intensa",
            "Sangramento intenso que não para",
            "Erupção que não some ao pressionar com um copo (não-esbranquiçável)",
            "Rigidez de nuca com febre",
            "Convulsão",
            "Dor abdominal forte",
            "Vômitos persistentes",
            "Dor de cabeça forte",
            "Coriza",
            "Dor de garganta",
            "Tosse",
            "Queda recente com dor",
        ],
    )

    outros_sintomas = st.text_area(
        "Digite outros sintomas (um por linha ou separados por vírgulas)",
        placeholder="Ex.: tontura, rigidez no pescoço, sangramento que não para, dor na barriga, vômitos...",
        height=90,
    )

    submitted = st.form_submit_button("Enviar triagem")

st.markdown('</div>', unsafe_allow_html=True)  # fecha .card

# =========================
# RESULTADO
# =========================
if submitted:
    outros_sintomas_lista = []
    if outros_sintomas:
        for item in outros_sintomas.replace("\n", ",").split(","):
            item = item.strip()
            if item:
                outros_sintomas_lista.append(item)
    todos_sintomas = sintomas + outros_sintomas_lista

    score = calcular_score_multiselect(todos_sintomas, dor=dor, duracao_dias=duracao_dias)
    categoria_cor, categoria_label = score_para_categoria(score)
    senha = gerar_senha("IE")

    if categoria_cor == "vermelho":
        espera_min = 1
    elif categoria_cor == "amarelo":
        espera_min = random.randint(6, 10)
    else:
        espera_min = random.randint(10, 15)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Resultado da triagem")

    if categoria_cor == "vermelho":
        st.markdown(f'<span class="badge badge-red">GRAU: VERMELHO — {categoria_label.upper()}</span>', unsafe_allow_html=True)
    elif categoria_cor == "amarelo":
        st.markdown(f'<span class="badge badge-yellow">GRAU: AMARELO — {categoria_label.upper()}</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="badge badge-green">GRAU: VERDE — {categoria_label.upper()}</span>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="kpi-grid">
          <div class="kpi"><div class="label">Pontuação (interno)</div><div class="value">{score}</div></div>
          <div class="kpi"><div class="label">Senha de atendimento</div><div class="value">{senha}</div></div>
          <div class="kpi"><div class="label">Estimativa de espera</div><div class="value">{espera_min} min</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if todos_sintomas:
        chips = "".join([f"<span class='chip'>{s}</span>" for s in todos_sintomas])
        st.markdown("#### Sintomas informados")
        st.markdown(f"<div class='chips'>{chips}</div>", unsafe_allow_html=True)
    else:
        st.write("Nenhum sintoma informado.")

    with st.expander("⏱ Cronômetro de atendimento (demonstração)"):
        st.write(f"Tempo estimado real (não automático): **{espera_min} minutos**")
        countdown_placeholder = st.empty()
        countdown_notify = st.empty()
        total_segundos = espera_min * 60
        for remaining in range(total_segundos, -1, -1):
            m = remaining // 60
            s = remaining % 60
            countdown_placeholder.markdown(
                f"Contagem: **{m:02d}:{s:02d}** — Tempo estimado real: **{espera_min} min**"
            )
            countdown_notify.markdown("✅ Atenção: contagem demonstrativa. O tempo real é gerenciado pela equipe.")
            time.sleep(1)

st.markdown('</div>', unsafe_allow_html=True)  # fecha .container-max
