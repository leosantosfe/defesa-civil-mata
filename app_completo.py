import streamlit as st
import folium
import requests
import time
from streamlit_folium import st_folium

# --- CONFIGURAÇÃO DA INTERFACE WEB ---
st.set_page_config(page_title="Defesa Civil Command Center", layout="centered")

# --- FUNÇÃO CORRIGIDA COM SCRIPT NATIVO (BURLA O BLOQUEIO DE ÁUDIO) ---
def disparar_som_sirene():
    # Injeta um código JavaScript puro no navegador para soltar o bipe nativo do sistema
    js_alarme = """
    <script>
        // Dispara o som de bipe nativo do processador do celular/PC
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var osc = context.createOscillator();
        osc.type = 'sawtooth'; // Som estilo sirene eletrônica
        osc.frequency.setValueAtTime(800, context.currentTime); // Frequência do alarme
        osc.connect(context.destination);
        osc.start();
        
        // Faz o alarme apitar por 2 segundos e para sozinho
        setTimeout(function(){ osc.stop(); }, 2000);
        
        // Abre o aviso visual na tela do operador
        alert("🚨 ALERTA GERAL DE EVACUAÇÃO: RISCO IMINENTE DE INUNDAÇÃO!");
    </script>
    """
    st.components.v1.html(js_alarme, height=0)

# --- BANCO DE DADOS DE LICENÇAS ---
CHAVES_SISTEMA = {
    "ALAG75": {"municipio": "Alagoinhas - BA", "lat_centro": -12.135, "lon_centro": -38.423, "setor_1": "Centro Urbano", "lat_1": -12.135, "lon_1": -38.423, "setor_2": "Bairro Silva Jardim", "lat_2": -12.142, "lon_2": -38.431, "padrao_chuva": 35.0, "padrao_umidade": 65},
    "CAMA71": {"municipio": "Camaçari - BA", "lat_centro": -12.697, "lon_centro": -38.324, "setor_1": "Centro Urbano", "lat_1": -12.697, "lon_1": -38.324, "setor_2": "Bairro Gleba C", "lat_2": -12.685, "lon_2": -38.330, "padrao_chuva": 25.0, "padrao_umidade": 60},
    "DIAS71": {"municipio": "Dias d'Ávila - BA", "lat_centro": -12.611, "lon_centro": -38.296, "setor_1": "Centro Sede", "lat_1": -12.611, "lon_1": -38.296, "setor_2": "Bairro Imbassay", "lat_2": -12.602, "lon_2": -38.305, "padrao_chuva": 30.0, "padrao_umidade": 65},
    "MATA71": {"municipio": "Mata de São João - BA", "lat_centro": -12.550, "lon_centro": -38.150, "setor_1": "Sede Urbana (Centro)", "lat_1": -12.530, "lon_1": -38.300, "setor_2": "Litoral (Praia do Forte)", "lat_2": -12.571, "lon_2": -38.001, "padrao_chuva": 40.0, "padrao_umidade": 70},
    "SALV71": {"municipio": "Salvador - BA", "lat_centro": -12.971, "lon_centro": -38.510, "setor_1": "Centro Histórico", "lat_1": -12.971, "lon_1": -38.510, "setor_2": "Bairro Cidade Baixa", "lat_2": -12.935, "lon_2": -38.501, "padrao_chuva": 30.0, "padrao_umidade": 65}
}

st.title("⛈️ Centro de Comando e Alarmes - Defesa Civil")

# --- TELA DE LOGIN POR CHAVE DE LICENÇA ---
st.sidebar.header("🔑 Autenticação de Licença")
chave_digitada = st.sidebar.text_input("Código de Acesso do Município:", type="password")

if chave_digitada == "":
    st.info("💡 Por favor, insira o Código de Licença para ativar o painel.")
    st.stop()

if chave_digitada not in CHAVES_SISTEMA:
    st.error("❌ Código de Licença inválido.")
    st.stop()

dados_foco = CHAVES_SISTEMA[chave_digitada]
st.success(f"✅ Conectado com sucesso para {dados_foco['municipio']}!")

# --- CONFIGURAÇÃO DO MODO DE OPERAÇÃO ---
st.sidebar.markdown("---")
st.sidebar.header("📡 Origem dos Dados")
modo_operacao = st.sidebar.radio("Selecione:", ("Satélite (Tempo Real)", "Simulador (Manual)"))

# --- LÓGICA DE DADOS REAIS OU SIMULADOS ---
if modo_operacao == "Simulador (Manual)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🕹️ Controles do Simulador")
    chuva_1 = st.sidebar.slider(f"Chuva {dados_foco['setor_1']} (mm)", 0.0, 100.0, 25.0)
    umidade_1 = st.sidebar.slider(f"Solo {dados_foco['setor_1']} (%)", 0, 100, 50)
    chuva_2 = st.sidebar.slider(f"Chuva {dados_foco['setor_2']} (mm)", 0.0, 100.0, 25.0)
    umidade_2 = st.sidebar.slider(f"Solo {dados_foco['setor_2']} (%)", 0, 100, 50)
else:
    def buscar_dados_tempo_real(lat, lon):
        try:
            url = f"https://open-meteo.com{lat}&longitude={lon}&current=precipitation,soil_moisture_27_to_81cm&timezone=America%2FSao_Paulo"
            resposta = requests.get(url).json()
            return resposta['current']['precipitation'], min(int(resposta['current']['soil_moisture_27_to_81cm'] * 100), 100)
        except: return 0.0, 50

    chuva_1, umidade_1 = buscar_dados_tempo_real(dados_foco["lat_1"], dados_foco["lon_1"])
    chuva_2, umidade_2 = buscar_dados_tempo_real(dados_foco["lat_2"], dados_foco["lon_2"])

# --- CÁLCULO DE RISCO ---
def calcular_risco(chuva, umidade, lim_chuva, lim_umid):
    if chuva >= lim_chuva and umidade >= lim_umid: return "🚨 ALERTA MÁXIMO", "red"
    elif chuva >= (lim_chuva / 2) or umidade >= (lim_umid - 15): return "⚠️ ATENÇÃO", "orange"
    else: return "✅ SEGURO", "green"

status_1, cor_1 = calcular_risco(chuva_1, umidade_1, dados_foco["padrao_chuva"], dados_foco["padrao_umidade"])
status_2, cor_2 = calcular_risco(chuva_2, umidade_2, dados_foco["padrao_chuva"], dados_foco["padrao_umidade"])

# --- DISPARADOR DA SIRENE ---
if cor_1 == "red" or cor_2 == "red":
    st.error("🚨 CRÍTICO: CONDIÇÃO DE INUNDAÇÃO ATINGIDA!")
    if st.button("🔊 ACIONAR ALARME DE EMERGÊNCIA"):
        disparar_som_sirene()

# --- PAINÉIS DE STATUS ---
st.subheader(f"📊 Telemetria Operacional: {dados_foco['municipio']}")
col1, col2 = st.columns(2)

with col1:
    st.metric(dados_foco["setor_1"], status_1, f"{chuva_1:.1f} mm")
    if cor_1 == "red": st.error("Risco alto de alagamento!")
    elif cor_1 == "orange": st.warning("Condições instáveis.")
    else: st.success("Área segura.")

with col2:
    st.metric(dados_foco["setor_2"], status_2, f"{chuva_2:.1f} mm")
    if cor_2 == "red": st.error("Risco alto de alagamento!")
    elif cor_2 == "orange": st.warning("Condições instáveis.")
    else: st.success("Área segura.")

# --- MAPA DINÂMICO ---
st.subheader("🗺️ Radar Geográfico Local")
mapa = folium.Map(location=[dados_foco["lat_centro"], dados_foco["lon_centro"]], zoom_start=13)
folium.CircleMarker(location=[dados_foco["lat_1"], dados_foco["lon_1"]], radius=25, color=cor_1, fill=True, fill_color=cor_1, fill_opacity=0.6).add_to(mapa)
folium.CircleMarker(location=[dados_foco["lat_2"], dados_foco["lon_2"]], radius=25, color=cor_2, fill=True, fill_color=cor_2, fill_opacity=0.6).add_to(mapa)
st_folium(mapa, width=700, height=400)

# --- RECARGA AUTOMÁTICA EM 10 SEGUNDOS ---
time.sleep(10)
st.rerun()