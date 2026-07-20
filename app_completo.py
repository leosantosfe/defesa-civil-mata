import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

# --- CONFIGURAÇÃO DA INTERFACE WEB ---
st.set_page_config(page_title="Defesa Civil Command Center", layout="centered")

# --- BANCO DE DADOS DE LICENÇAS ---
CHAVES_SISTEMA = {
    "MATA71": {
        "municipio": "Mata de São João - BA", "lat_centro": -12.550, "lon_centro": -38.150,
        "setor_1": "Sede Urbana (Centro)", "lat_1": -12.530, "lon_1": -38.300,
        "setor_2": "Litoral (Praia do Forte)", "lat_2": -12.571, "lon_2": -38.001
    },
    "CAMA71": {
        "municipio": "Camaçari - BA", "lat_centro": -12.697, "lon_centro": -38.324,
        "setor_1": "Centro Urbano", "lat_1": -12.697, "lon_1": -38.324,
        "setor_2": "Bairro Gleba C", "lat_2": -12.685, "lon_2": -38.330
    }
}

st.title("⛈️ Centro de Comando e Simulação - Defesa Civil")

# --- TELA DE LOGIN POR CHAVE DE LICENÇA ---
st.sidebar.header("🔑 Autenticação de Licença")
chave_digitada = st.sidebar.text_input("Código de Acesso do Município:", type="password")

if chave_digitada == "":
    st.info("💡 Por favor, insira o Código de Licença da sua cidade na barra lateral esquerda para ativar o painel.")
    st.stop()

if chave_digitada not in CHAVES_SISTEMA:
    st.error("❌ Código de Licença inválido ou expirado. Entre em contato com o suporte comercial.")
    st.stop()

dados_foco = CHAVES_SISTEMA[chave_digitada]
st.success(f"✅ Conectado com sucesso para {dados_foco['municipio']}!")

# --- 🛰️ CHAVE SELETORA: AUTOMÁTICO VS MANUAL ---
st.sidebar.markdown("---")
st.sidebar.header("📡 Modo de Operação")
modo_operacao = st.sidebar.radio("Selecione a Origem dos Dados:", ("Satélite (Tempo Real)", "Simulador (Manual)"))

# --- SE O MODO FOR MANUAL, LIBERA AS BARRAS PARA ARRUSTAR OS MM ---
if modo_operacao == "Simulador (Manual)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🕹️ Controles do Simulador")
    st.sidebar.write("Arraste para simular cenários de risco:")
    
    chuva_1 = st.sidebar.slider(f"Chuva {dados_foco['setor_1']} (mm)", 0.0, 100.0, 25.0)
    umidade_1 = st.sidebar.slider(f"Solo {dados_foco['setor_1']} (%)", 0, 100, 50)
    
    chuva_2 = st.sidebar.slider(f"Chuva {dados_foco['setor_2']} (mm)", 0.0, 100.0, 25.0)
    umidade_2 = st.sidebar.slider(f"Solo {dados_foco['setor_2']} (%)", 0, 100, 50)

# --- SE O MODO FOR AUTOMÁTICO, BUSCA DIRETO NA INTERNET PELO SATÉLITE ---
else:
    def buscar_dados_tempo_real(lat, lon):
        try:
            url = f"https://open-meteo.com{lat}&longitude={lon}&current=precipitation,soil_moisture_27_to_81cm&timezone=America%2FSao_Paulo"
            resposta = requests.get(url).json()
            return resposta['current']['precipitation'], min(int(resposta['current']['soil_moisture_27_to_81cm'] * 100), 100)
        except:
            return 0.0, 50

    chuva_1, umidade_1 = buscar_dados_tempo_real(dados_foco["lat_1"], dados_foco["lon_1"])
    chuva_2, umidade_2 = buscar_dados_tempo_real(dados_foco["lat_2"], dados_foco["lon_2"])

# --- LÓGICA DE GATILHO FIXA DO SISTEMA ---
def calcular_risco(chuva, umidade):
    if chuva >= 40.0 and umidade >= 70: return "🚨 ALERTA MÁXIMO", "red"
    elif chuva >= 15.0 or umidade >= 60: return "⚠️ ATENÇÃO", "orange"
    else: return "✅ SEGURO", "green"

status_1, cor_1 = calcular_risco(chuva_1, umidade_1)
status_2, cor_2 = calcular_risco(chuva_2, umidade_2)

# --- PAINÉIS DE STATUS ---
st.subheader(f"📊 Telemetria Operacional: {dados_foco['municipio']}")
col1, col2 = st.columns(2)

with col1:
    st.metric(dados_foco["setor_1"], status_1, f"{chuva_1:.1f} mm")
    if cor_1 == "red": st.error("Risco alto de alagamento!")
    elif cor_1 == "orange": st.warning("Condições instáveis.")
    else: st.success("Área segura.")
    st.caption(f"Solo local: {umidade_1}% de umidade.")

with col2:
    st.metric(dados_foco["setor_2"], status_2, f"{chuva_2:.1f} mm")
    if cor_2 == "red": st.error("Risco alto de alagamento!")
    elif cor_2 == "orange": st.warning("Condições instáveis.")
    else: st.success("Área segura.")
    st.caption(f"Solo local: {umidade_2}% de umidade.")

# --- MAPA DINÂMICO ---
st.subheader("🗺️ Radar Geográfico Local")
mapa = folium.Map(location=[dados_foke := dados_foco["lat_centro"], dados_foco["lon_centro"]], zoom_start=13)

folium.CircleMarker(location=[dados_foco["lat_1"], dados_foco["lon_1"]], radius=25, color=cor_1, fill=True, fill_color=cor_1, fill_opacity=0.6).add_to(mapa)
folium.CircleMarker(location=[dados_foco["lat_2"], dados_foco["lon_2"]], radius=25, color=cor_2, fill=True, fill_color=cor_2, fill_opacity=0.6).add_to(mapa)

st_folium(mapa, width=700, height=400)