import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

# --- CONFIGURAÇÃO DA INTERFACE WEB ---
st.set_page_config(page_title="Defesa Civil Bahia Enterprise", layout="centered")

# --- BANCO DE DADOS DE LICENÇAS DAS 12 CIDADES DA BAHIA ---
# Cada cidade agora tem suas coordenadas reais de Centro e seus 2 bairros/setores configurados!
CHAVES_SISTEMA = {
    "ALAG75": {
        "municipio": "Alagoinhas - BA", "lat_centro": -12.135, "lon_centro": -38.423,
        "setor_1": "Centro Urbano", "lat_1": -12.135, "lon_1": -38.423,
        "setor_2": "Bairro Silva Jardim", "lat_2": -12.142, "lon_2": -38.431,
        "padrao_chuva": 35.0, "padrao_umidade": 65
    },
    "BARA77": {
        "municipio": "Barreiras - BA", "lat_centro": -12.152, "lon_centro": -45.003,
        "setor_1": "Centro Sede", "lat_1": -12.152, "lon_1": -45.003,
        "setor_2": "Bairro Barreirinhas", "lat_2": -12.145, "lon_2": -44.991,
        "padrao_chuva": 40.0, "padrao_umidade": 70
    },
    "CAMA71": {
        "municipio": "Camaçari - BA", "lat_centro": -12.697, "lon_centro": -38.324,
        "setor_1": "Centro Urbano", "lat_1": -12.697, "lon_1": -38.324,
        "setor_2": "Bairro Gleba C", "lat_2": -12.685, "lon_2": -38.330,
        "padrao_chuva": 25.0, "padrao_umidade": 60
    },
    "DIAS71": {
        "municipio": "Dias d'Ávila - BA", "lat_centro": -12.611, "lon_centro": -38.296,
        "setor_1": "Centro Sede", "lat_1": -12.611, "lon_1": -38.296,
        "setor_2": "Bairro Imbassay", "lat_2": -12.602, "lon_2": -38.305,
        "padrao_chuva": 30.0, "padrao_umidade": 65
    },
    "FEIR75": {
        "municipio": "Feira de Santana - BA", "lat_centro": -12.266, "lon_centro": -38.962,
        "setor_1": "Centro Centro", "lat_1": -12.266, "lon_1": -38.962,
        "setor_2": "Bairro Baraúnas", "lat_2": -12.253, "lon_2": -38.971,
        "padrao_chuva": 30.0, "padrao_umidade": 65
    },
    "ILHE73": {
        "municipio": "Ilhéus - BA", "lat_centro": -14.793, "lon_centro": -39.046,
        "setor_1": "Zona Costeira Centro", "lat_1": -14.793, "lon_1": -39.046,
        "setor_2": "Bairro Malhado", "lat_2": -14.778, "lon_2": -39.039,
        "padrao_chuva": 35.0, "padrao_umidade": 70
    },
    "ITAR73": {
        "municipio": "Itabuna - BA", "lat_centro": -14.791, "lon_centro": -39.280,
        "setor_1": "Centro Sede", "lat_1": -14.791, "lon_1": -39.280,
        "setor_2": "Bairro Mangabinha", "lat_2": -14.797, "lon_2": -39.291,
        "padrao_chuva": 35.0, "padrao_umidade": 65
    },
    "JACO74": {
        "municipio": "Jacobina - BA", "lat_centro": -11.180, "lon_centro": -40.518,
        "setor_1": "Centro Urbano", "lat_1": -11.180, "lon_1": -40.518,
        "setor_2": "Bairro Serrinha (Encosta)", "lat_2": -11.189, "lon_2": -40.511,
        "padrao_chuva": 20.0, "padrao_umidade": 60
    },
    "JUAF74": {
        "municipio": "Juazeiro - BA", "lat_centro": -9.411, "lon_centro": -40.503,
        "setor_1": "Centro Urbano", "lat_1": -9.411, "lon_1": -40.503,
        "setor_2": "Bairro Angari (Ribeirinho)", "lat_2": -9.406, "lon_2": -40.509,
        "padrao_chuva": 40.0, "padrao_umidade": 70
    },
    "MATA71": {
        "municipio": "Mata de São João - BA", "lat_centro": -12.550, "lon_centro": -38.150,
        "setor_1": "Sede Urbana (Centro)", "lat_1": -12.530, "lon_1": -38.300,
        "setor_2": "Litoral (Praia do Forte)", "lat_2": -12.571, "lon_2": -38.001,
        "padrao_chuva": 40.0, "padrao_umidade": 70
    },
    "PORT73": {
        "municipio": "Porto Seguro - BA", "lat_centro": -16.449, "lon_centro": -39.064,
        "setor_1": "Centro Histórico", "lat_1": -16.449, "lon_1": -39.064,
        "setor_2": "Bairro Baianão", "lat_2": -16.438, "lon_2": -39.082,
        "padrao_chuva": 35.0, "padrao_umidade": 65
    },
    "SALV71": {
        "municipio": "Salvador - BA", "lat_centro": -12.971, "lon_centro": -38.510,
        "setor_1": "Centro Histórico", "lat_1": -12.971, "lon_1": -38.510,
        "setor_2": "Bairro Cidade Baixa", "lat_2": -12.935, "lon_2": -38.501,
        "padrao_chuva": 30.0, "padrao_umidade": 65
    },
    "VITO77": {
        "municipio": "Vitória da Conquista - BA", "lat_centro": -14.861, "lon_centro": -40.844,
        "setor_1": "Centro Sede", "lat_1": -14.861, "lon_1": -40.844,
        "setor_2": "Bairro Brasil", "lat_2": -14.852, "lon_2": -40.857,
        "padrao_chuva": 35.0, "padrao_umidade": 70
    }
}

st.title("⛈️ Centro de Comando e Simulação - Defesa Civil BA")

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

# --- LÓGICA DE GATILHO DO SISTEMA ---
def calcular_risco(chuva, umidade, lim_chuva, lim_umid):
    if chuva >= lim_chuva and umidade >= lim_umid: return "🚨 ALERTA MÁXIMO", "red"
    elif chuva >= (lim_chuva / 2) or umidade >= (lim_umid - 15): return "⚠️ ATENÇÃO", "orange"
    else: return "✅ SEGURO", "green"

status_1, cor_1 = calcular_risco(chuva_1, umidade_1, dados_foco["padrao_chuva"], dados_foco["padrao_umidade"])
status_2, cor_2 = calcular_risco(chuva_2, umidade_2, dados_foco["padrao_chuva"], dados_foco["padrao_umidade"])

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
mapa = folium.Map(location=[dados_foco["lat_centro"], dados_foco["lon_centro"]], zoom_start=13)

folium.CircleMarker(location=[dados_foco["lat_1"], dados_foco["lon_1"]], radius=25, color=cor_1, fill=True, fill_color=cor_1, fill_opacity=0.6).add_to(mapa)
folium.CircleMarker(location=[dados_foco["lat_2"], dados_foco["lon_2"]], radius=25, color=cor_2, fill=True, fill_color=cor_2, fill_opacity=0.6).add_to(mapa)

st_folium(mapa, width=700, height=400)