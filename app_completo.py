import streamlit as st
import folium
from streamlit_folium import st_folium

# --- CONFIGURAÇÃO DA INTERFACE WEB ---
st.set_page_config(page_title="Defesa Civil Avançada", layout="centered")

st.title("⛈️ Inteligência Climática - Mata de São João / BA")
st.write("Monitoramento multi-setorial em tempo real para o município.")

# --- CONTROLES INDEPENDENTES NA BARRA LATERAL ---
st.sidebar.header("⚙️ Sensores por Setor")

# Setor 1: Sede Urbana (Centro)
st.sidebar.subheader("🏙️ Setor 1: Sede Urbana")
chuva_sede = st.sidebar.slider("Chuva na Sede (mm)", 0, 100, 25)
umidade_sede = st.sidebar.slider("Umidade Solo Sede (%)", 0, 100, 50)

# Setor 2: Litoral (Praia do Forte)
st.sidebar.subheader("🌊 Setor 2: Litoral")
chuva_litoral = st.sidebar.slider("Chuva no Litoral (mm)", 0, 100, 25)
umidade_litoral = st.sidebar.slider("Umidade Solo Litoral (%)", 0, 100, 50)

# --- LÓGICA DE ALERTA INDEPENDENTE ---
# Nível de risco para a Sede Urbana
if chuva_sede > 40 and umidade_sede > 70:
    status_sede = "🚨 ALERTA MÁXIMO"
    cor_sede = "red"
elif chuva_sede > 20 or umidade_sede > 60:
    status_sede = "⚠️ ATENÇÃO"
    cor_sede = "orange"
else:
    status_sede = "✅ SEGURO"
    cor_sede = "green"

# Nível de risco para o Litoral (Praia do Forte)
if chuva_litoral > 40 and umidade_litoral > 70:
    status_litoral = "🚨 ALERTA MÁXIMO"
    cor_litoral = "red"
elif chuva_litoral > 20 or umidade_litoral > 60:
    status_litoral = "⚠️ ATENÇÃO"
    cor_litoral = "orange"
else:
    status_litoral = "✅ SEGURO"
    cor_litoral = "green"

# --- 5. EXIBIÇÃO DOS PAINÉIS DE STATUS ---
st.subheader("📊 Painel de Risco Operacional")
col1, col2 = st.columns(2)

with col1:
    st.metric("Sede Urbana (Centro)", status_sede)
    if cor_sede == "red": st.error("Risco alto de alagamento!")
    elif cor_sede == "orange": st.warning("Condições instáveis.")
    else: st.success("Área urbana segura.")

with col2:
    st.metric("Litoral (Praia do Forte)", status_litoral)
    if cor_litoral == "red": st.error("Risco alto de alagamento!")
    elif cor_litoral == "orange": st.warning("Condições instáveis.")
    else: st.success("Área litorânea segura.")

# --- 6. MAPA DE MONITORAMENTO COM OS DOIS PONTOS ---
st.subheader("🗺️ Painel de Monitoramento Geográfico")

# Centraliza o mapa entre a Sede e o Litoral
mapa = folium.Map(location=[-12.550, -38.150], zoom_start=11)

# Bolinha 1: Sede Urbana Centro
folium.CircleMarker(
    location=[-12.530, -38.300],
    radius=20,
    popup=f"Sede Centro: {status_sede}",
    color=cor_sede, fill=True, fill_color=cor_sede, fill_opacity=0.6
).add_to(mapa)

# Bolinha 2: Litoral Praia do Forte
folium.CircleMarker(
    location=[-12.571, -38.001],
    radius=20,
    popup=f"Praia do Forte: {status_litoral}",
    color=cor_litoral, fill=True, fill_color=cor_litoral, fill_opacity=0.6
).add_to(mapa)

st_folium(mapa, width=700, height=400)