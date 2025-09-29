import streamlit as st
from PIL import Image
import time
import random
import string

st.set_page_config(page_title="VOXA Triagem", layout="centered", page_icon="⚕️")

st.markdown(
    """
    <style>
    /* geral */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        background: linear-gradient(180deg, rgba(255,255,255,1) 0%, rgba(250,250,250,1) 100%);
        padding: 24px;
        border-radius: 8px;
        font-family: 'Poppins', 'Playfair Display', serif;
        color: #0f1720;
    }
    .title { font-size: 48px; text-align: center; font-weight: 600; }
    .panel { background: rgba(255,255,255,0.9); padding: 22px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.06); }
    .stButton>button { background: linear-gradient(90deg,#7b5dd3,#8a60d8); color: white; border-radius: 8px; padding: 10px 16px; font-weight: 600; }
    .anim { display:flex; align-items:center; justify-content:center; height:120px; margin-bottom: 12px; }
    .pulse { font-size:22px; padding:12px 18px; border-radius:12px; background: rgba(67,143,171,0.08); color: #1f2937; animation: pulse 2.4s infinite; border: 1px solid rgba(67,143,171,0.12); }
    @keyframes pulse { 0% { transform: translateY(0px); opacity: 0.9; } 50% { transform: translateY(-6px); opacity: 1; } 100% { transform: translateY(0px); opacity: 0.9; } }
    .badge-green { color: #065f46; background: #d1fae5; padding:8px 12px; border-radius:8px; }
    .badge-yellow { color: #854d0e; background: #fff7ed; padding:8px 12px; border-radius:8px; }
    .badge-red { color: #7f1d1d; background: #fee2e2; padding:8px 12px; border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown('<div class="main">', unsafe_allow_html=True)
  
image_path = "VOXA.PNG"
try:
    loaded_img = Image.open(image_path)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(loaded_img, width=400)
except Exception:
    st.markdown("<h1 class='title'>VOXA</h1>", unsafe_allow_html=True)

st.markdown('<div class="panel">', unsafe_allow_html=True)

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

wait_markdown = st.markdown('<div class="anim"><div class="pulse">Por favor, aguarde — você será redirecionado para as perguntas...</div></div>', unsafe_allow_html=True)
time.sleep(2.2)

wait_markdown.empty()

st.markdown("## 🩺 VOXA Triagem")
st.caption("Protótipo educativo para **pré-triagem**. Ajuste às normas do serviço.")

st.markdown("### Informações iniciais")
with st.form("triagem_form"):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome completo")
        idade = st.number_input("Idade", min_value=0, max_value=120, value=1)
        telefone = st.text_input("Telefone (opcional)")
    with col2:
        dor = st.slider("Em uma escala de 0 (sem dor) a 10 (pior dor imaginável), qual sua dor agora?", 0, 10, 3)
        duracao_dias = st.number_input("Há quantos dias você apresenta sintomas?", min_value=0, max_value=365, value=1)

    st.markdown("### Selecione sintomas que se aplicam")
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

    st.markdown("### Resultado da triagem")
    if categoria_cor == "vermelho":
        st.markdown(f'<div class="badge-red"><strong>GRAU: VERMELHO — {categoria_label.upper()}</strong></div>', unsafe_allow_html=True)
    elif categoria_cor == "amarelo":
        st.markdown(f'<div class="badge-yellow"><strong>GRAU: AMARELO — {categoria_label.upper()}</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="badge-green"><strong>GRAU: VERDE — {categoria_label.upper()}</strong></div>', unsafe_allow_html=True)

    st.write(f"Pontuação (interno): {score}")
    st.write(f"Senha de atendimento: **{senha}**")
    st.write(f"Estimativa de espera: **{espera_min} minutos**")


    if todos_sintomas:
        st.markdown("#### Sintomas informados:")
        for s in todos_sintomas:
            st.markdown(f"- {s}")
    else:
        st.write("Nenhum sintoma informado.")


    st.markdown("#### Cronômetro de atendimento")
    st.write("Tempo estimado real (não automático):")
    st.write(f"**{espera_min} minutos**")

    countdown_placeholder = st.empty()
    countdown_notify = st.empty()
    total_segundos = espera_min * 60
    for remaining in range(total_segundos, -1, -1):
        m = remaining // 60
        s = remaining % 60
        countdown_placeholder.markdown(
            f"Contagem: **{m:02d}:{s:02d}** — Tempo estimado real: **{espera_min} min**"
        )
        countdown_notify.markdown(
        "✅ Atenção: esta é uma contagem demonstrativa. O tempo real é gerenciado pela equipe."
        )   
        time.sleep(1) 

