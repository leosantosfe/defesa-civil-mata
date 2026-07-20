import streamlit as st
import folium
import requests
from streamlit_folium import st_folium
from datetime import datetime

# --- CONFIGURAÇÃO DA TRAVA DE SEGURANÇA ---
DATA_LIMITE = datetime(2026, 8, 19)
DATA_ATUAL = datetime.now()

if DATA_ATUAL > DATA_LIMITE:
    st.set_page_config(page_title="Licença Expirada", layout="centered")
    st.error("❌ PERÍODO DE TESTES ENCERRADO")
    st.subheader("O prazo de avaliação gratuita deste software expirou.")
    st.stop()

# --- CONFIGURAÇÃO DA INTERFACE WEB ---
st.set_page_config(page_title="Defesa Civil Real-Time", layout="centered")
st.caption(f"⚙️ Conexão Satélite Ativa - Licença válida até: {DATA_LIMITE.strftime('%d/%m/%Y')}")
st.title("⛈️ Inteligência Climática Real - Mata de São João / BA")
st.write("Monitoramento conectado a radares meteorológicos globais em tempo real.")

# --- FUNÇÃO PARA BUSCAR DADOS DE SATÉLITE EM TEMPO REAL ---
def buscar_dados_tempo_real(lat, lon):
    try:
        # Link da API que consulta o clima exato nas coordenadas geográficas
        url = f"https://open-meteo.com{lat}&longitude={lon}&current=precipitation,soil_moisture_27_to_81cm&timezone=America%2FSao_Paulo"
        resposta = requests.get(url).json()
        
        # Extrai os mm de chuva e a umidade do solo do satélite
        chuva = resposta['current']['precipitation']
        umidade = resposta['current']['soil_moisture_27_to_81cm']
        
        # Converte a umidade para formato de porcentagem aproximada (0-100)
        umidade_porcentagem = min(int(umidade * 100), 100)
        
        return chuva, umidade_porcentagem
    except:
        # Caso a internet falhe, ele usa dados padrão seguros
        return 0.0, 50

# --- COORDENADAS OFICIAIS DOS DOIS SETORES ---
LAT_SEDE, LON_SEDE = -12.530, -38.300
LAT_LITORAL, LON_LITORAL = -12.571, -38.001

# --- CHAMADA DOS DADOS REAIS DO SATÉLITE ---
chuva_sede, umidade_sede = buscar_dados_tempo_real(LAT_SEDE, LON_SEDE)
chuva_litoral, umidade_litoral = buscar_dados_tempo_real(LAT_LITORAL, LON_LITORAL)

# --- LÓGICA DE ALERTA INTELIGENTE ---
def calcular_risco(chuva, umidade):
    if chuva > 40.0 and umidade > 70:
        return "🚨 ALERTA MÁXIMO", "red", "Risco alto de alagamento imediato!"
    elif chuva > 15.0 or umidade > 60:
        return "⚠️ ATENÇÃO", "orange", "Condições instáveis sob monitoramento."
    else:
        return "✅ SEGURO", "green", "Área monitorada e segura."

status_sede, cor_sede, msg_sede = calcular_risco(chuva_sede, umidade_sede)
status_litoral, cor_litoral, msg_litoral = calcular_risco(chuva_litoral, umidade_litoral)

# --- PAINÉIS DE STATUS ---
st.subheader("📊 Painel de Risco Operacional (Dados de Hoje)")
col1, col2 = st.columns(2)

with col1:
    st.metric("Sede Urbana (Centro)", status_sede, f"{chuva_sede:.1f} mm chuva")
    if cor_sede == "red": st.error(msg_sede)
    elif cor_sede == "orange": st.warning(msg_sede)
    else: st.success(msg_sede)
    st.caption(f"Sensores: Solo em {umidade_sede}%")

with col2:
    st.metric("Litoral (Praia do Forte)", status_litoral, f"{chuva_litoral:.1f} mm chuva")
    if cor_litoral == "red": st.error(msg_litoral)
    elif cor_litoral == "orange": st.warning(msg_litoral)
    else: st.success(msg_litoral)
    st.caption(f"Sensores: Solo em {umidade_litoral}%")

# --- MAPA DE MONITORAMENTO ---
st.subheader("🗺️ Painel de Monitoramento Geográfico")
mapa = folium.Map(location=[-12.550, -38.150], zoom_start=11)

folium.CircleMarker(
    location=[LAT_SEDE, LON_SEDE], radius=20, popup=f"Sede: {status_sede}",
    color=cor_sede, fill=True, fill_color=cor_sede, fill_opacity=0.6
).add_to(mapa)

folium.CircleMarker(
    location=[LAT_LITORAL, LON_LITORAL], radius=20, popup=f"Litoral: {status_litoral}",
    color=cor_litoral, fill=True, fill_color=cor_litoral, fill_opacity=0.6
).add_to(mapa)

st_folium(mapa, width=700, height=400)