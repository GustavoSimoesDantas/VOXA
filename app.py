import re
import unicodedata
from typing import List, Tuple, Optional, Set

import streamlit as st
from pydantic import BaseModel, validator


# Util: normalização de texto

def normalize(txt: str) -> str:
    if txt is None:
        return ""
    txt = txt.strip().lower()
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(ch for ch in txt if unicodedata.category(ch) != "Mn")
    return txt

def split_free_text(txt: str) -> List[str]:
    if not txt:
        return []
    parts = re.split(r"[\n,;]+", txt)  # quebra por linha, vírgula ou ponto-e-vírgula
    return [p.strip() for p in parts if p.strip()]


# Modelo de entrada / validação

class TriageInput(BaseModel):
    sintomas: List[str]                 
    outros_sintomas_texto: Optional[str] = ""  
    sbp: Optional[float] = None         
    dbp: Optional[float] = None          
    temp_c: Optional[float] = None       # temperatura (°C)
    dor_0a10: int = 0                    # escala de dor 0–10

    @validator("dor_0a10")
    def valida_dor(cls, v):
        if v < 0 or v > 10:
            raise ValueError("A dor deve estar entre 0 e 10.")
        return v


# Motor de regras (explicável)

RED_FLAGS: Set[str] = {
    "Dor no peito forte/pressão no peito",
    "Falta de ar importante",
    "Desmaio ou inconsciência",
    "Confusão mental intensa",
    "Sangramento intenso que não para",
    "Erupção que não some ao pressionar com um copo (não-esbranquiçável)",
    "Rigidez de nuca com febre",
    "Convulsão",
    "Perna Quebrada",
    "Braço Quebrado",
}

YELLOW_FLAGS: Set[str] = {
    "Falta de ar leve/moderada",
    "Dor abdominal forte",
    "Vômitos persistentes",
    "Dor de cabeça forte",
    "Dor moderada (7–8/10)",
    "Queda recente com dor",
}

def map_free_text_to_flags(texto: str, temp_c: Optional[float]) -> Tuple[Set[str], Set[str], List[str]]:
    """
    Converte sintomas digitados em correspondências canônicas (RED/YELLOW).
    Retorna (hits_red, hits_yellow, lista_original_limpa).
    """
    items = split_free_text(texto)
    norm_items = [normalize(i) for i in items]

    hits_red: Set[str] = set()
    hits_yellow: Set[str] = set()

    for raw, s in zip(items, norm_items):
        # Dor no peito
        if "dor no peito" in s or "pressao no peito" in s or "aperto no peito" in s:
            hits_red.add("Dor no peito forte/pressão no peito")

        # Falta de ar
        if "falta de ar" in s or "dispneia" in s:
            if any(w in s for w in ["grave", "importante", "muita", "sufoc", "repouso", "piorando"]):
                hits_red.add("Falta de ar importante")
            else:
                hits_yellow.add("Falta de ar leve/moderada")

        # Desmaio / inconsciência
        if "desmaio" in s or "desmai" in s or "inconscien" in s or "apagao" in s:
            hits_red.add("Desmaio ou inconsciência")

        # Confusão
        if "confus" in s or "desorient" in s or "delirio" in s:
            hits_red.add("Confusão mental intensa")

        # Sangramento
        if "sangram" in s or "hemorrag" in s:
            if any(w in s for w in ["nao para", "não para", "muito", "excessiv", "abundant"]):
                hits_red.add("Sangramento intenso que não para")
            else:
                hits_yellow.add("Sangramento (avaliar)")

        # Rigidez de nuca (+ febre preferencialmente)
        if ("rigidez" in s and ("nuca" in s or "pescoco" in s or "pescoço" in s)) or "pescoço duro" in s:
            if temp_c is not None and temp_c >= 38.0:
                hits_red.add("Rigidez de nuca com febre")
            else:
                hits_yellow.add("Rigidez de nuca (sem febre informada)")

        # Convulsão
        if "convuls" in s or "ataque epilept" in s:
            hits_red.add("Convulsão")

        # Dor abdominal
        if "dor abdominal" in s or ("dor" in s and "barriga" in s):
            hits_yellow.add("Dor abdominal forte")

        # Vômitos
        if "vomit" in s or "vômit" in s or "enjoo" in s or "enjo" in s:
            hits_yellow.add("Vômitos persistentes")

        # Dor de cabeça
        if "dor de cabeca" in s or "dor de cabeça" in raw.lower() or "cefaleia" in s:
            hits_yellow.add("Dor de cabeça forte")

        # Queda com dor
        if "queda" in s and "dor" in s:
            hits_yellow.add("Queda recente com dor")

    return hits_red, hits_yellow, items

def classify_triage(inp: TriageInput) -> Tuple[str, List[str], List[str]]:
    reasons: List[str] = []

    # Mapeia texto livre para flags
    free_red, free_yellow, free_list = map_free_text_to_flags(inp.outros_sintomas_texto or "", inp.temp_c)

    # Conjunto final de sintomas (multiselect + mapeamento texto)
    sintomas_set = set(inp.sintomas) | free_red | (free_yellow & YELLOW_FLAGS)

    # -------- Vermelha --------
    red_hits = sorted(list(sintomas_set & RED_FLAGS))
    if red_hits:
        reasons.append(f"Sintomas de alto risco: {', '.join(red_hits)}")

    if inp.sbp is not None and (inp.sbp >= 180):
        reasons.append("Pressão sistólica muito elevada (≥180).")
    if inp.dbp is not None and (inp.dbp >= 120):
        reasons.append("Pressão diastólica muito elevada (≥120).")
    if inp.sbp is not None and (inp.sbp < 90):
        reasons.append("Pressão sistólica muito baixa (<90).")
    if inp.temp_c is not None and inp.temp_c >= 39.5:
        reasons.append("Febre muito alta (≥39,5 °C).")

    if reasons:
        return "vermelha", reasons, free_list

    # -------- Amarela --------
    y_reasons: List[str] = []
    if inp.temp_c is not None and inp.temp_c >= 38.0:
        y_reasons.append("Febre (≥38,0 °C).")
    if inp.sbp is not None and 160 <= inp.sbp < 180:
        y_reasons.append("Pressão sistólica elevada (160–179).")
    if inp.dbp is not None and 100 <= inp.dbp < 120:
        y_reasons.append("Pressão diastólica elevada (100–119).")
    if inp.sbp is not None and 90 <= inp.sbp < 100:
        y_reasons.append("Pressão sistólica baixa-limítrofe (90–99).")

    yellow_hits = sorted(list((sintomas_set & YELLOW_FLAGS) | (free_yellow - YELLOW_FLAGS)))
    if yellow_hits:
        y_reasons.append(f"Sintomas com prioridade: {', '.join(yellow_hits)}")
    if inp.dor_0a10 >= 8:
        y_reasons.append("Dor intensa (≥8/10).")

    if y_reasons:
        return "amarela", y_reasons, free_list

    # -------- Verde --------
    return "verde", ["Sem sinais imediatos de alto risco detectados."], free_list


# UI (Streamlit)

st.set_page_config(page_title="Chatbot de Triagem (MVP)", page_icon="🩺", layout="centered")

st.markdown("## 🩺 VOXA Triagem")
st.caption("Protótipo educativo para **pré-triagem**. Ajuste às normas do serviço.")

with st.form("triage_form"):
    st.markdown("### Informe sintomas e sinais")

    sintomas = st.multiselect(
        "Sintomas (selecione os que se aplicam)",
        [
            "Dor no peito forte/pressão no peito",
            "Falta de ar importante",
            "Falta de ar leve/moderada",
            "Desmaio ou inconsciência",
            "Confusão mental intensa",
            "Sangramento intenso que não para",
            "Erupção que não some ao pressionar com um copo (não-esbranquiçável)",
            "Rigidez de nuca com febre",
            "Convulsão",
            "Dor abdominal forte",
            "Vômitos persistentes",
            "Dor de cabeça forte",
            "Dor moderada (7–8/10)",
            "Queda recente com dor",
        ],
    )

    outros_sintomas = st.text_area(
        "Digite outros sintomas (um por linha ou separados por vírgulas)",
        placeholder="Ex.: tontura, rigidez no pescoço, sangramento que não para, dor na barriga, vômitos...",
        height=90,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        sbp = st.number_input("Pressão sistólica (SBP, mmHg)", min_value=0, max_value=300, value=120)
    with col2:
        dbp = st.number_input("Pressão diastólica (DBP, mmHg)", min_value=0, max_value=200, value=80)
    with col3:
        temp_c = st.number_input("Temperatura (°C)", min_value=30.0, max_value=43.0, value=36.5, step=0.1, format="%.1f")

    dor = st.slider("Escala de dor (0–10)", 0, 10, 0)

    submitted = st.form_submit_button("Classificar")

if submitted:
    try:
        entry = TriageInput(
            sintomas=sintomas,
            outros_sintomas_texto=outros_sintomas,
            sbp=sbp,
            dbp=dbp,
            temp_c=temp_c,
            dor_0a10=dor,
        )
        cor, motivos, livres = classify_triage(entry)

        cor_badge = {
            "vermelha": "🔴 **PULSEIRA VERMELHA**",
            "amarela": "🟡 **PULSEIRA AMARELA**",
            "verde": "🟢 **PULSEIRA VERDE**",
        }[cor]

        st.markdown("---")
        st.markdown(cor_badge)
        st.markdown("**Motivos detectados:**")
        for m in motivos:
            st.markdown(f"- {m}")

        if livres:
            st.caption("Sintomas digitados: " + "; ".join(livres))

        

    except Exception as e:
        st.error(f"Entrada inválida: {e}")
