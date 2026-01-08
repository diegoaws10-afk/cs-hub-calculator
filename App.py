import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pyotp
import time
import os
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DO PRODUTO (WHITE-LABEL) ---
NOME_PRODUTO = "CS Master"
ICONE_APP = "🚀"

st.set_page_config(page_title=f"{NOME_PRODUTO} | Intelligence", layout="wide", page_icon=ICONE_APP)

# ==================================================
# 🎨 DESIGN SYSTEM (NEUTRO & MODERNO)
# ==================================================
def local_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Montserrat:wght@600;700&display=swap');

        .stApp {
            background: linear-gradient(135deg, #111827 0%, #1f2937 100%); /* Cinza Chumbo Profundo */
            font-family: 'Inter', sans-serif;
            color: #f3f4f6;
        }
        
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #374151;
        }

        h1, h2, h3 {
            font-family: 'Montserrat', sans-serif !important;
            color: #ffffff !important;
        }

        /* Cards Modernos */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(31, 41, 55, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            backdrop-filter: blur(10px);
            padding: 20px;
        }

        /* Botão de Ação (Gradiente Roxo - Tech) */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #7c3aed 0%, #6d28d9 100%);
            color: white;
            border: none;
            padding: 14px 24px;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
            transition: transform 0.2s;
        }
        div.stButton > button:first-child:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
        }

        [data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            text-align: center;
        }
        
        /* Box de Diagnóstico */
        .diag-box {
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            background-color: rgba(255,255,255,0.05);
            border-left: 4px solid;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# ==================================================
# 🔐 SEGURANÇA (GENÉRICA)
# ==================================================
def check_authentication():
    if st.session_state.get("authenticated", False): return True

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container(border=True):
            st.markdown(f"<h2 style='text-align: center;'>🔐 {NOME_PRODUTO} Login</h2>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")
                token_mfa = st.text_input("Token MFA") 
                st.write("")
                if st.form_submit_button("ACESSAR DASHBOARD"):
                    if username in st.secrets["passwords"] and password == st.secrets["passwords"][username]:
                        totp = pyotp.TOTP(st.secrets["mfa"]["secret_key"])
                        if totp.verify(token_mfa.replace(" ", "")):
                            st.session_state["authenticated"] = True
                            st.session_state["user_logado"] = username
                            st.rerun()
                        else: st.error("Token MFA Inválido.")
                    else: st.error("Acesso Negado.")
    return False

if not check_authentication(): st.stop()

# ==================================================
# 💾 PERSISTÊNCIA DE DADOS
# ==================================================
def salvar_no_banco(dados):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_atual = conn.read(worksheet="Página1", ttl=0)
        nova_linha = pd.DataFrame([dados])
        df_atualizado = pd.concat([df_atual, nova_linha], ignore_index=True)
        conn.update(worksheet="Página1", data=df_atualizado)
        return True
    except Exception as e:
        if "200" in str(e) or "Response" in str(e): return True
        else: st.error(f"Erro DB: {str(e)}"); return False

# ==================================================
# 📊 VISUALIZAÇÃO
# ==================================================
def create_radar(tec, eng, nps):
    val_nps = nps if isinstance(nps, (int, float)) else (tec + eng)/2
    cat = ['Técnico', 'Engajamento', 'NPS']
    val = [tec, eng, val_nps]; val += [val[0]]; cat += [cat[0]]
    fig = go.Figure(go.Scatterpolar(r=val, theta=cat, fill='toself', line=dict(color='#8b5cf6'), fillcolor='rgba(139, 92, 246, 0.3)'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showline=False)), paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=220, margin=dict(t=20, b=20, l=40, r=40))
    return fig

def create_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={'font': {'size': 40, 'color': "white"}, 'suffix': "%"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "rgba(255,255,255,0.3)"}, 
               'steps': [{'range': [0, 60], 'color': "#ef4444"}, {'range': [60, 75], 'color': "#f97316"}, {'range': [75, 100], 'color': "#10b981"}]}
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=200, margin=dict(t=10, b=10, l=20, r=20))
    return fig

# ==================================================
# 🧠 CORE INTELLIGENCE (MOTOR HÍBRIDO SAAS/SERVIÇOS)
# ==================================================
class CSMasterModel:
    def __init__(self, tipo_negocio):
        self.tipo_negocio = tipo_negocio
        # Pesos podem variar por tipo, aqui mantive padronizado para simplicidade inicial
        self.regras = {
            'Onboarding': {'eng': 0.60, 'tec': 0.20, 'nps': 0.20},
            'Adoção':     {'eng': 0.30, 'tec': 0.40, 'nps': 0.30},
            'Retenção':   {'eng': 0.20, 'tec': 0.50, 'nps': 0.30}
        }
        self.sla_targets = {'Ouro': 99.0, 'Prata': 98.0, 'Bronze': 95.0}

    def calcular_engajamento(self, d):
        # LÓGICA HÍBRIDA
        if self.tipo_negocio == "SaaS (Software)":
            # 1. Frequência de Login (Peso 60%)
            # Diário (100), Semanal (70), Quinzenal (40), Mensal (10)
            map_login = {'Diário': 100, 'Semanal': 70, 'Quinzenal': 40, 'Mensal/Raro': 10}
            score_freq = map_login.get(d['freq_login'], 0)
            
            # 2. Uso de Licenças (Peso 40%)
            # >80% (100), 50-80% (70), <50% (30)
            licencas = d['uso_licencas']
            score_lic = 100 if licencas >= 80 else (70 if licencas >= 50 else 30)
            
            # QBR bônus
            qbr = 100 if d['qbr'] == 'Sim' else 0
            
            # Cálculo SaaS
            final_eng = (score_freq * 0.6) + (score_lic * 0.3) + (qbr * 0.1)
            return min(final_eng, 100.0)

        else: 
            # LÓGICA SERVIÇOS (Original Strati)
            meta = 1 if d['fase'] == 'Adoção' else (2 if d['fase'] == 'Onboarding' else 0.5)
            
            # Verifica local para definir meta principal
            if d['local'] == "Remoto":
                presenca = min((d['online']/2)*100, 100) # Meta 2 calls online
                bonus = 10 if d['visitas'] > 0 else 0
            else:
                presenca = 100 if meta==0 else min((d['visitas']/meta)*100, 100)
                bonus = min(d['online']*2, 10)
            
            book = 100 if d['book']=='Apresentado' else (50 if d['book']=='Enviado' else 0)
            qbr = 100 if d['qbr'] == 'Sim' else 0
            
            final_eng = (presenca * 0.5) + ((book + qbr)/2 * 0.5) + bonus
            return min(final_eng, 100.0)

    def calcular(self, d):
        # Técnico (Igual para ambos)
        target = self.sla_targets.get(d['tier'], 98.0)
        ratio = 1.0 if d['abertos'] == 0 else d['fechados'] / d['abertos']
        backlog = min(ratio, 1.0) * 100
        sla_sc = 100 if d['sla'] >= target else ((d['sla']/target)**5)*100
        tec = (sla_sc * 0.7) + (backlog * 0.3)

        # Engajamento (Híbrido)
        eng = self.calcular_engajamento(d)

        # Final
        w = self.regras[d['fase'].split()[0]] # Pega só a primeira palavra da fase
        
        if d['nps'] is None:
            nps_val = 0
            tot = w['tec'] + w['eng']
            final = (eng * (w['eng']/tot)) + (tec * (w['tec']/tot))
            msg_nps = "N/A"
        else:
            nps_val = d['nps'] * 10
            final = (eng * w['eng']) + (tec * w['tec']) + (nps_val * w['nps'])
            msg_nps = nps_val

        if final < 60: stt, cor, icon = "CRÍTICO", "red", "🚨"
        elif final < 75: stt, cor, icon = "ATENÇÃO", "orange", "⚠️"
        else: stt, cor, icon = "SAUDÁVEL", "green", "✅"

        return {"Score": round(final, 1), "Status": stt, "Cor": cor, "Icon": icon, "Tec": int(tec), "Eng": int(eng), "NPS": msg_nps}

    def gerar_playbook(self, res, d):
        acoes = []
        # Lógica Genérica de Playbook
        if res['Status'] == "CRÍTICO":
            strat = "🚨 PROTOCOLO DE RISCO: Risco severo de cancelamento."
            acoes.append("Liderança: Escalonamento Executivo Imediato.")
            if self.tipo_negocio == "SaaS (Software)":
                if res['Eng'] < 50: acoes.append("CSM: Investigar motivo do baixo login (Problema de UX ou Falta de Treinamento?)")
            else:
                 acoes.append("CSM: Agendar visita de crise presencial.")
        elif res['Status'] == "ATENÇÃO":
            strat = "⚠️ ALERTA DE SAÚDE: Sinais de estagnação."
            acoes.append("CSM: Plano de Ação de 30 dias.")
            if res['Eng'] < 70 and self.tipo_negocio == "SaaS (Software)":
                acoes.append("CSM: Oferecer retreinamento da plataforma para usuários chave.")
        else:
            strat = "🚀 OPORTUNIDADE: Cliente engajado."
            acoes.append("Comercial: Mapear expansão.")
            if res['NPS'] != "N/A" and res['NPS'] >= 90: acoes.append("Mkt: Solicitar Case de Sucesso.")
            
        return strat, acoes

# ==================================================
# 🖥️ UI PRINCIPAL
# ==================================================
with st.sidebar:
    st.markdown(f"<h1>{NOME_PRODUTO}</h1>", unsafe_allow_html=True)
    st.caption("Intelligence System v1.0")
    st.write("---")
    
    # SELETOR DO MODELO DE NEGÓCIO (A MÁGICA ACONTECE AQUI)
    st.markdown("### 🏢 Configuração")
    modelo_negocio = st.selectbox("Modelo do Cliente", ["Serviços (Consultoria)", "SaaS (Software)"])
    
    st.write("---")
    if st.button("🚪 Logout"): st.session_state.clear(); st.rerun()

    # Inputs Comuns
    st.markdown("### 1. Perfil")
    nome = st.text_input("Cliente")
    c1, c2 = st.columns(2)
    tier = c1.selectbox("Tier", ["Ouro", "Prata", "Bronze"])
    fase = c2.selectbox("Fase", ['Onboarding', 'Adoção', 'Retenção'])

    st.markdown("### 2. Técnico")
    sla = st.slider("SLA (%)", 80.0, 100.0, 98.0)
    c_in = st.number_input("Tickets Abertos", 5)
    c_out = st.number_input("Tickets Fechados", 5)

# HEADER
st.markdown(f"<h1>{ICONE_APP} {NOME_PRODUTO} <span style='color:#8b5cf6'>Intelligence</span></h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#9ca3af'>Análise: <b>{nome if nome else 'Novo Cliente'}</b> | Modo: <b>{modelo_negocio}</b></p>", unsafe_allow_html=True)

c_eng, c_nps = st.columns(2)

# COLUNA 1: ENGAJAMENTO (DINÂMICA)
with c_eng:
    with st.container(border=True):
        st.markdown(f"### ⚡ Engajamento ({'Uso' if 'SaaS' in modelo_negocio else 'Relacionamento'})")
        
        # INPUTS VARIÁVEIS BASEADOS NO MODELO
        if modelo_negocio == "SaaS (Software)":
            freq_login = st.select_slider("Frequência de Login (Usuários Chave)", options=["Mensal/Raro", "Quinzenal", "Semanal", "Diário"], value="Semanal")
            uso_licencas = st.slider("Utilização de Licenças Contratadas (%)", 0, 100, 70)
            qbr = st.radio("QBR Realizada?", ["Sim", "Não"], horizontal=True)
            
            # Variáveis nulas para o outro modelo
            local, visitas, online, book = "N/A", 0, 0, "N/A"
            
        else: # SERVIÇOS
            local = st.radio("Localização", ["Local", "Remoto"], horizontal=True)
            if local == "Local":
                visitas = st.slider("Visitas Presenciais", 0, 5, 1)
                online = st.slider("Calls Online (Bônus)", 0, 10, 2)
            else:
                st.info("✈️ Modo Remoto Ativo")
                online = st.slider("Calls Online (Meta: 2)", 0, 10, 2)
                visitas = 0
            
            book = st.selectbox("Book de Serviços", ["Apresentado", "Enviado", "Não realizado"])
            qbr = st.radio("QBR Realizada?", ["Sim", "Não"], horizontal=True)
            
            # Variáveis nulas SaaS
            freq_login, uso_licencas = "N/A", 0

# COLUNA 2: NPS
with c_nps:
    with st.container(border=True):
        st.markdown("### ❤️ Satisfação")
        tem_nps = st.toggle("Possui pesquisa recente?", value=True)
        nps = st.slider("Nota (0-10)", 0, 10, 9) if tem_nps else None
        if not tem_nps: st.warning("Peso redistribuído automaticamente.")

st.write("")

if st.button("GERAR DIAGNÓSTICO"):
    if not nome: st.toast("Preencha o nome do cliente.", icon="⚠️")
    else:
        # Processamento
        with st.spinner("Processando algoritmos..."):
            time.sleep(1) # Efeito visual
            
            # Inputs unificados
            data_inputs = {
                'modelo': modelo_negocio, 'tier': tier, 'fase': fase, 'nps': nps,
                'sla': sla, 'abertos': c_in, 'fechados': c_out,
                'freq_login': freq_login, 'uso_licencas': uso_licencas, # SaaS
                'local': local, 'visitas': visitas, 'online': online, 'book': book, # Serviço
                'qbr': qbr
            }
            
            engine = CSMasterModel(modelo_negocio)
            res = engine.calcular(data_inputs)
            strat, acoes = engine.gerar_playbook(res, data_inputs)

        st.markdown("---")
        
        # Dashboard
        c1, c2 = st.columns([1, 1.5])
        with c1:
            with st.container(border=True):
                st.markdown("<p style='text-align:center; color:#9ca3af'>Equilíbrio dos Pilares</p>", unsafe_allow_html=True)
                st.plotly_chart(create_radar(res['Tec'], res['Eng'], res['NPS']), use_container_width=True)
        
        with c2:
            with st.container(border=True):
                c_gauge, c_txt = st.columns([1, 1])
                with c_gauge: st.plotly_chart(create_gauge(res['Score']), use_container_width=True)
                with c_txt:
                    st.markdown(f"<h1 style='color:{res['Cor']}; font-size:3rem !important'>{res['Score']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h3>{res['Icon']} {res['Status']}</h3>", unsafe_allow_html=True)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Técnico", f"{res['Tec']}%")
                m2.metric("Engajamento", f"{res['Eng']}%")
                m3.metric("NPS", res['NPS'] if res['NPS'] != "N/A" else "-")

        # Playbook
        st.write("")
        with st.container(border=True):
            st.markdown("### 📋 Diagnóstico Inteligente")
            if res['Cor'] == 'green': st.success(strat, icon="✅")
            elif res['Cor'] == 'orange': st.warning(strat, icon="⚠️")
            else: st.error(strat, icon="🚨")
            
            st.markdown("**Plano de Ação Sugerido:**")
            for a in acoes:
                st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:8px; border-radius:4px; margin-bottom:4px; border-left:3px solid #8b5cf6'>{a}</div>", unsafe_allow_html=True)

        # Salvar (Tratamento para colunas vazias)
        db_row = {
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Cliente": nome, "Modelo": modelo_negocio,
            "Score": res['Score'], "Status": res['Status'], "Playbook": strat,
            "Login_Freq": freq_login, "Licencas": uso_licencas, # Colunas SaaS
            "Visitas": visitas, "Online": online # Colunas Serviço
        }
        salvar_no_banco(db_row)
        st.toast("Dados salvos na nuvem.", icon="☁️")
