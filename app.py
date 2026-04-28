

import re
import uuid
import base64
from datetime import date, datetime, timedelta
from collections import defaultdict

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

from supabase import create_client, Client

# =============================================================================
# CONFIGURAÇÃO DO SUPABASE
# -----------------------------------------------------------------------------
# Substitua os valores abaixo pelos que você copiou em:
#   Supabase → seu projeto → Settings → API
#
#   SUPABASE_URL → "Project URL"   (ex: https://abcdefghij.supabase.co)
#   SUPABASE_KEY → "anon / public" (começa com eyJhbGciOiJIUzI1NiIs...)
#
# Dica de segurança: em produção, use st.secrets ou variáveis de ambiente
# em vez de colocar as chaves diretamente no código.
# =============================================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# =============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
# st.set_page_config DEVE ser a primeira chamada do Streamlit.
# layout="wide" -> ocupa toda a largura disponível (essencial p/ o dashboard).
# =============================================================================
st.set_page_config(
    page_title="Controle de Publicações | MLB",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# 2. PALETA DE CORES — tokens centralizados
# -----------------------------------------------------------------------------
# Mantém a identidade visual em sintonia com o resto do ecossistema da empresa
# (mesmas cores, mesmos gradientes, mesmas bordas).
# =============================================================================
COR = {
    # Fundos
    "bg_principal":   "#0b1120",
    "bg_sidebar_top": "#0a0f1f",
    "bg_sidebar_bot": "#0f172a",
    "bg_card":        "#0f172a",
    "borda":          "#1e293b",
    # Texto
    "txt_principal":  "#ffffff",
    "txt_secundario": "#94a3b8",
    "txt_terciario":  "#64748b",
    # Acentos
    "roxo_primario":  "#8b5cf6",
    "roxo_secundario":"#7c3aed",
    "rosa":           "#ec4899",
    "laranja":        "#f97316",
    "verde":          "#22c55e",
    "vermelho":       "#ef4444",
    "amarelo":        "#eab308",
    # Gradientes
    "grad_ativo":  "linear-gradient(90deg, #8b5cf6 0%, #ec4899 50%, #f97316 100%)",
    "grad_tabela": "linear-gradient(90deg, #6366f1 0%, #ec4899 55%, #f97316 100%)",
}


# =============================================================================
# 3. CONSTANTES DE NEGÓCIO
# =============================================================================
META_MENSAL_DEFAULT = 220       # anúncios/mês por funcionário (regra do escopo)
SENHA_PADRAO        = "123"     # senha inicial dos usuários pré-cadastrados

# Nomes dos meses em PT-BR para exibição
MESES_PT = {
    1: "Janeiro",  2: "Fevereiro", 3: "Março",     4: "Abril",
    5: "Maio",     6: "Junho",     7: "Julho",     8: "Agosto",
    9: "Setembro", 10: "Outubro",  11: "Novembro", 12: "Dezembro",
}

def aplicar_css_global():
    st.markdown(f"""
    <style>
    /* ---------- Reset do chrome do Streamlit ---------- */
    #MainMenu, footer, header {{ visibility: hidden; }}

    .block-container {{
        padding-top:    1.5rem !important;
        padding-bottom: 2rem   !important;
        padding-left:   2rem   !important;
        padding-right:  2rem   !important;
        max-width: 100% !important;
    }}

    /* ---------- Background ---------- */
    .stApp {{
        background:
            radial-gradient(circle at 85% 0%, rgba(124,58,237,0.08), transparent 40%),
            radial-gradient(circle at 0% 100%, rgba(236,72,153,0.05), transparent 40%),
            linear-gradient(135deg, #020617 0%, {COR["bg_principal"]} 100%);
        color: {COR["txt_principal"]};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COR["bg_sidebar_top"]} 0%,
                                            {COR["bg_sidebar_bot"]} 100%);
        border-right: 1px solid {COR["borda"]};
        padding-top: 0 !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {{
        display: none;
    }}

    /* ---------- Logo (cabeçalho da sidebar) ---------- */
    .app-logo {{
        display: flex; align-items: center; gap: 12px;
        padding: 0 18px 24px 18px;
        border-bottom: 1px solid rgba(30,41,59,0.5);
        margin-bottom: 14px;
    }}
    .app-logo .mark {{
        font-size: 30px;
        font-weight: 900;
        letter-spacing: -1px;
        color: white;
        line-height: 1;
        position: relative;
    }}
    .app-logo .mark::after {{
        content: "";
        position: absolute;
        left: 0; right: 0; bottom: -6px;
        height: 2px;
        background: {COR["grad_ativo"]};
        border-radius: 2px;
    }}
    .app-logo .divider {{
        width: 2px; height: 38px;
        background: linear-gradient(180deg, #8b5cf6, #f97316);
        border-radius: 2px;
    }}
    .app-logo .text {{
        font-size: 11px; font-weight: 700; color: #cbd5e1;
        letter-spacing: 1px; line-height: 1.3;
    }}

    /* ---------- Card do usuário logado (rodapé sidebar) ---------- */
    .user-card {{
        background: {COR["bg_card"]};
        border: 1px solid {COR["borda"]};
        border-radius: 12px;
        padding: 14px;
        margin: 8px 12px;
        display: flex; align-items: center; gap: 12px;
    }}
    .user-card .avatar {{
        width: 38px; height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 16px; font-weight: 700;
        flex-shrink: 0; overflow: hidden;
    }}
    .user-card .avatar img {{
        width: 100%; height: 100%; object-fit: cover;
    }}
    .user-card .greeting {{ font-size: 11px; color: {COR["txt_secundario"]}; line-height: 1.2; }}
    .user-card .username {{ font-size: 14px; font-weight: 700; color: white; line-height: 1.2; }}
    .user-card .role     {{ font-size: 11px; color: {COR["txt_terciario"]}; line-height: 1.4; }}

    /* ---------- Botão padrão ---------- */
    .stButton > button {{
        background: {COR["bg_card"]};
        color: white;
        border: 1px solid {COR["borda"]};
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 500;
        width: 100%;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background: #1e293b;
        border-color: #334155;
        transform: translateY(-1px);
    }}
    /* Botão "primário" — usado para confirmar ações */
    .stButton button[kind="primary"] {{
        background: {COR["grad_ativo"]} !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 6px 20px rgba(236,72,153,0.25);
    }}
    .stButton button[kind="primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(236,72,153,0.35);
    }}

    /* ---------- Footer da sidebar ---------- */
    .sidebar-footer {{
        text-align: center;
        padding: 18px 12px;
        color: {COR["txt_terciario"]};
        font-size: 12px;
        border-top: 1px solid rgba(30,41,59,0.4);
        margin-top: 24px;
    }}
    .sidebar-footer .brand {{ color: {COR["txt_secundario"]}; font-weight: 600; }}

    /* ---------- Cabeçalho de página ---------- */
    .page-header {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 22px;
    }}
    .page-header .title-wrap h1 {{
        font-size: 30px; font-weight: 700; color: white;
        margin: 0; line-height: 1.1;
    }}
    .page-header .title-wrap p {{
        font-size: 14px; color: {COR["txt_secundario"]}; margin: 4px 0 0 0;
    }}

    /* "Pílula" de filtro/info no canto direito do cabeçalho */
    .filter-pill {{
        background: {COR["bg_card"]};
        border: 1px solid {COR["borda"]};
        border-radius: 10px;
        padding: 10px 18px;
        color: white;
        font-size: 13px;
        display: inline-flex; align-items: center; gap: 10px;
    }}

    /* ---------- KPI Cards ---------- */
    .kpi-card {{
        background: {COR["bg_card"]};
        border: 1px solid {COR["borda"]};
        border-radius: 16px;
        padding: 22px;
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        display: flex; align-items: center; gap: 18px;
    }}
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }}
    .kpi-icon {{
        width: 56px; height: 56px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0; color: white; font-size: 22px;
    }}
    .kpi-icon.purple1 {{ background: {COR["roxo_primario"]}; }}
    .kpi-icon.purple2 {{ background: {COR["roxo_secundario"]}; }}
    .kpi-icon.pink    {{ background: {COR["rosa"]}; }}
    .kpi-icon.orange  {{ background: {COR["laranja"]}; }}
    .kpi-icon.green   {{ background: {COR["verde"]}; }}
    .kpi-icon.red     {{ background: {COR["vermelho"]}; }}
    .kpi-icon.yellow  {{ background: {COR["amarelo"]}; }}
    .kpi-content {{ flex: 1; min-width: 0; }}
    .kpi-label {{ font-size: 13px; color: {COR["txt_secundario"]}; margin: 0 0 4px 0; font-weight: 500; }}
    .kpi-value {{ font-size: 24px; font-weight: 700; color: white; margin: 0; line-height: 1.1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .kpi-sub   {{ font-size: 11px; color: {COR["txt_terciario"]}; margin: 6px 0 0 0; }}

    /* ---------- Painéis ---------- */
    .panel {{
        background: {COR["bg_card"]};
        border: 1px solid {COR["borda"]};
        border-radius: 16px;
        padding: 22px;
        margin-top: 20px;
    }}
    .panel-header {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 16px;
    }}
    .panel-title {{ font-size: 17px; font-weight: 600; color: white; margin: 0; }}
    .panel-subtitle {{ font-size: 12px; color: {COR["txt_secundario"]}; margin-top: 2px; }}

    /* ---------- Barra de progresso da meta ---------- */
    .progress-wrap {{
        margin: 8px 0 4px 0;
    }}
    .progress-track {{
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid {COR["borda"]};
        border-radius: 99px;
        height: 14px;
        overflow: hidden;
        position: relative;
    }}
    .progress-fill {{
        height: 100%;
        border-radius: 99px;
        transition: width 0.4s ease;
    }}
    .progress-fill.below {{ background: linear-gradient(90deg, #f97316, #ef4444); }}
    .progress-fill.ontrack {{ background: linear-gradient(90deg, #eab308, #f97316); }}
    .progress-fill.above {{ background: linear-gradient(90deg, #22c55e, #10b981); }}
    .progress-meta {{
        display: flex; justify-content: space-between;
        font-size: 11px; color: {COR["txt_terciario"]};
        margin-top: 6px;
    }}

    /* ---------- Badge de status ---------- */
    .status-pill {{
        display: inline-block;
        padding: 5px 12px;
        border-radius: 99px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    .status-pill.above {{ background: rgba(34,197,94,0.18); color: #22c55e; border: 1px solid rgba(34,197,94,0.4); }}
    .status-pill.ontrack {{ background: rgba(234,179,8,0.18); color: #facc15; border: 1px solid rgba(234,179,8,0.4); }}
    .status-pill.below {{ background: rgba(239,68,68,0.18); color: #ef4444; border: 1px solid rgba(239,68,68,0.4); }}

    /* ---------- Tabela custom ---------- */
    .tabela-custom {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 4px;
    }}
    .tabela-custom thead th {{
        background: {COR["grad_tabela"]};
        color: white;
        padding: 14px 18px;
        font-size: 13px;
        font-weight: 600;
        text-align: left;
    }}
    .tabela-custom thead th:first-child {{ border-top-left-radius: 10px; }}
    .tabela-custom thead th:last-child  {{ border-top-right-radius: 10px; text-align: right; }}
    .tabela-custom thead th:not(:first-child):not(:last-child) {{ text-align: right; }}
    .tabela-custom tbody td {{
        padding: 13px 18px;
        border-bottom: 1px solid rgba(30,41,59,0.5);
        font-size: 14px;
        color: white;
    }}
    .tabela-custom tbody tr:hover td {{ background: rgba(30,41,59,0.3); }}
    .tabela-custom tbody td:not(:first-child):not(:last-child) {{
        text-align: right; color: {COR["txt_secundario"]};
    }}
    .tabela-custom tbody td:last-child {{ text-align: right; }}

    /* ---------- Cards de Funcionário (página Equipe) ---------- */
    .func-card {{
        background: {COR["bg_card"]};
        border: 1px solid {COR["borda"]};
        border-radius: 16px;
        padding: 22px 18px 18px 18px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 8px;
    }}
    .func-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }}
    .func-foto {{
        border-radius: 50%; object-fit: cover;
        margin: 0 auto 14px auto; display: block;
        outline: 3px solid #8b5cf6; outline-offset: 2px;
        box-shadow: 0 4px 20px rgba(139,92,246,0.3);
    }}
    .func-foto-placeholder {{
        border-radius: 50%;
        background: linear-gradient(135deg, #8b5cf6, #ec4899, #f97316);
        color: white; font-weight: 700;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 14px auto;
        box-shadow: 0 4px 20px rgba(236,72,153,0.3);
        letter-spacing: 1px;
    }}
    .func-nome {{ font-size: 17px; font-weight: 700; color: white; margin: 0 0 2px 0; }}
    .func-cargo {{ font-size: 12px; color: {COR["txt_secundario"]}; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 1px; }}
    .func-mini-kpis {{
        display: flex; justify-content: space-around;
        padding: 12px 0;
        border-top: 1px solid rgba(30,41,59,0.6);
        border-bottom: 1px solid rgba(30,41,59,0.6);
        margin-bottom: 12px;
    }}
    .func-mini-kpi {{ text-align: center; flex: 1; }}
    .func-mini-kpi .lbl {{
        font-size: 9px; color: {COR["txt_terciario"]};
        text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;
    }}
    .func-mini-kpi .val {{ font-size: 14px; font-weight: 700; color: white; margin-top: 2px; }}

    /* ---------- Hero do perfil ---------- */
    .profile-hero {{
        background:
            radial-gradient(circle at 0% 0%, rgba(139,92,246,0.18), transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(249,115,22,0.10), transparent 50%),
            {COR["bg_card"]};
        border: 1px solid {COR["borda"]};
        border-radius: 20px;
        padding: 30px 32px;
        margin-bottom: 22px;
        display: flex; align-items: center; gap: 30px;
    }}
    .profile-hero-info {{ flex: 1; }}
    .profile-hero-nome {{ font-size: 30px; font-weight: 700; color: white; margin: 0 0 4px 0; line-height: 1.1; }}
    .profile-hero-cargo {{
        font-size: 13px; color: #cbd5e1;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin-bottom: 18px; font-weight: 600;
    }}
    .profile-hero-stats {{ display: flex; gap: 28px; flex-wrap: wrap; }}
    .profile-stat-label {{ font-size: 10px; color: {COR["txt_terciario"]}; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 2px; }}
    .profile-stat-value {{ font-size: 19px; font-weight: 700; color: white; }}

    /* ---------- Inputs em dark mode ---------- */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stDateInput"] input {{
        background-color: {COR["bg_card"]} !important;
        border: 1px solid {COR["borda"]} !important;
        color: white !important;
        border-radius: 10px !important;
    }}
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {{
        border-color: {COR["roxo_primario"]} !important;
        box-shadow: 0 0 0 1px {COR["roxo_primario"]} !important;
    }}

    /* Selectbox dark */
    div[data-baseweb="select"] > div {{
        background-color: {COR["bg_card"]} !important;
        border-color: {COR["borda"]} !important;
        border-radius: 10px !important;
        color: white !important;
        cursor: pointer !important;
    }}

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px dashed #334155 !important;
        border-radius: 10px !important;
    }}
    [data-testid="stFileUploaderDropzone"] small {{ color: {COR["txt_secundario"]} !important; }}
    [data-testid="stFileUploaderDropzone"] button {{
        background: linear-gradient(90deg, #8b5cf6, #ec4899) !important;
        color: white !important;
        border: none !important;
    }}

    /* Expander dark */
    [data-testid="stExpander"] {{
        background: transparent !important;
        border: 1px solid {COR["borda"]} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stExpander"] summary {{ color: {COR["txt_secundario"]} !important; }}

    /* ---------- Tela de Login ---------- */
    .login-wrap {{
        max-width: 460px; margin: 60px auto 0 auto;
        background: {COR["bg_card"]};
        border: 1px solid {COR["borda"]};
        border-radius: 20px;
        padding: 40px 36px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }}
    .login-logo {{
        text-align: center; margin-bottom: 26px;
    }}
    .login-logo .ico {{
        font-size: 44px; margin-bottom: 6px;
    }}
    .login-logo h1 {{
        font-size: 24px; color: white; margin: 0; font-weight: 700;
    }}
    .login-logo p {{
        font-size: 13px; color: {COR["txt_secundario"]}; margin: 4px 0 0 0;
    }}
    .login-help {{
        margin-top: 16px;
        padding: 12px 14px;
        background: rgba(139,92,246,0.08);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 10px;
        font-size: 12px;
        color: {COR["txt_secundario"]};
        line-height: 1.5;
    }}
    .login-help b {{ color: #cbd5e1; }}

    /* ---------- Publicações: textarea de MLBs com fonte mono ---------- */
    .stTextArea textarea {{
        font-family: 'Fira Code', 'Courier New', monospace !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
    }}

    /* Chips de MLB no preview */
    .mlb-chip {{
        display: inline-block;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 99px;
        background: rgba(139,92,246,0.18);
        color: #cbd5e1;
        font-size: 11px;
        font-family: 'Fira Code', monospace;
        border: 1px solid rgba(139,92,246,0.3);
    }}
    .mlb-chip.dup {{
        background: rgba(239,68,68,0.15);
        color: #fca5a5;
        border-color: rgba(239,68,68,0.3);
        text-decoration: line-through;
    }}

    /* Box de feedback de inserção */
    .insight-box {{
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid {COR["borda"]};
        border-radius: 12px;
        padding: 16px 18px;
        margin-top: 14px;
    }}
    .insight-box .row {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 6px 0;
    }}
    .insight-box .row .lbl {{ color: {COR["txt_secundario"]}; font-size: 13px; }}
    .insight-box .row .val {{ color: white; font-weight: 700; font-size: 15px; }}
    .insight-box .row .val.green  {{ color: {COR["verde"]}; }}
    .insight-box .row .val.red    {{ color: {COR["vermelho"]}; }}
    .insight-box .row .val.yellow {{ color: {COR["amarelo"]}; }}

    /* Tabela Plotly: fundo transparente */
    .js-plotly-plot .plotly .modebar {{ display: none !important; }}

    /* Mensagem vazia */
    .empty-msg {{
        background: {COR["bg_card"]};
        border: 1px dashed {COR["borda"]};
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        color: {COR["txt_secundario"]};
        margin-top: 20px;
    }}
    .empty-msg .ico {{ font-size: 36px; display:block; margin-bottom: 10px; }}

    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# 6. DATA LAYER — Supabase como banco persistente
# -----------------------------------------------------------------------------
# Arquitetura de dados:
#
#   Supabase (fonte de verdade permanente):
#     • tabela `usuarios`    → login, nome, senha, perfil
#     • tabela `publicacoes` → data, login, loja, mlb
#
#   st.session_state (cache em memória por sessão):
#     • "users"       : dict[login] → {nome, role, senha, ...}
#     • "publicacoes" : pd.DataFrame com colunas id | data | login | empresa | cust_id | mlb
#     • "meta_mensal" : int
#     • "logado"      : bool
#     • "user_atual"  : str | None
#
#   Estratégia de sincronização:
#     – Leitura: carregada do Supabase uma vez por sessão (início).
#     – Escrita: sempre vai ao Supabase PRIMEIRO; em sucesso, atualiza o cache.
#     – Fallback: se o Supabase estiver indisponível, o app exibe aviso e usa
#       os dados em memória até a reconexão.
# =============================================================================

# --------------------------------------------------------------------------
# 6a. Helpers de conversão entre o modelo do Supabase e o modelo interno
# --------------------------------------------------------------------------

def _sb_usuario_para_dict(row: dict) -> dict:
    """Converte uma linha da tabela `usuarios` do Supabase para o dict interno.

    Mapeamento de colunas:
        Supabase          →  Interno
        perfil            →  role
        (sem cargo)       →  cargo (inferido pelo perfil)
        (sem email)       →  email (string vazia, editável em Meu Perfil)
        (sem foto_b64)    →  foto_b64 (None; foto é mantida só em sessão)
    """
    perfil = row.get("perfil", "employee")
    return {
        "nome":     row.get("nome", row.get("login", "")),
        "cargo":    "Gestor" if perfil == "admin" else "Anunciante MLB",
        "role":     perfil,
        "senha":    row.get("senha", ""),
        "email":    row.get("email", "") or "",
        "foto_b64": row.get("foto_b64") or None,   # persistido no Supabase
    }


def _sb_publicacoes_para_df(rows: list) -> pd.DataFrame:
    """Converte lista de linhas de `publicacoes` do Supabase para DataFrame interno.

    Mapeamento de colunas:
        Supabase   →  Interno
        loja       →  empresa
        (ausente)  →  cust_id  (string vazia — não existe na tabela Supabase)
        id         →  _seq     (preserva ordem de inserção p/ "últimos lançamentos")
        (ausente)  →  id       (UUID gerado localmente p/ compatibilidade com remover_publicacao)
    """
    # Ordena por id ASC para que os mais recentes fiquem no final do DataFrame.
    # Como o id no Supabase é BIGSERIAL, ele reflete a ordem de inserção.
    rows_sorted = sorted(rows, key=lambda r: r.get("id", 0))
    registros = []
    for seq, r in enumerate(rows_sorted):
        registros.append({
            "id":      str(uuid.uuid4()),
            "data":    pd.to_datetime(r["data"]).date(),
            "login":   r["login"],
            "empresa": r.get("loja", ""),
            "cust_id": "",
            "mlb":     str(r["mlb"]),
            "_seq":    seq,  # ordem de inserção (0 = mais antigo, N = mais recente)
        })
    return pd.DataFrame(
        registros,
        columns=["id", "data", "login", "empresa", "cust_id", "mlb", "_seq"],
    )

# --------------------------------------------------------------------------
# 6b. Seed inicial — popula o Supabase quando encontrado vazio
# --------------------------------------------------------------------------

def _seed_publicacoes_supabase(df: pd.DataFrame) -> None:
    """Insere o histórico mock no Supabase quando a tabela `publicacoes` está vazia.

    Opera em lotes de 500 linhas para respeitar o limite de payload do Supabase
    (máx. ~1 MB por request). Erros são silenciados para não bloquear o app —
    o histórico mock já está disponível no session_state como fallback.
    """
    try:
        rows = [
            {
                "data":  str(r["data"]),
                "login": r["login"],
                "loja":  r["empresa"],
                "mlb":   r["mlb"],
            }
            for _, r in df.iterrows()
        ]
        BATCH = 500
        for i in range(0, len(rows), BATCH):
            supabase.table("publicacoes").insert(rows[i:i + BATCH]).execute()
    except Exception:
        pass  # fallback silencioso


def usuarios_iniciais():
    """Cria a tabela inicial de usuários (admin + 4 funcionários)."""
    return {
        "adm": {
            "nome": "Administrador",
            "cargo": "Gestor",
            "role": "admin",
            "senha": SENHA_PADRAO,
            "email": "adm@empresa.com",
            "foto_b64": None,
        },
        "ruben": {
            "nome": "Ruben",
            "cargo": "Anunciante MLB",
            "role": "employee",
            "senha": SENHA_PADRAO,
            "email": "ruben@empresa.com",
            "foto_b64": None,
        },
        "bruno": {
            "nome": "Bruno",
            "cargo": "Anunciante MLB",
            "role": "employee",
            "senha": SENHA_PADRAO,
            "email": "bruno@empresa.com",
            "foto_b64": None,
        },
        "kaio": {
            "nome": "Kaio",
            "cargo": "Anunciante MLB",
            "role": "employee",
            "senha": SENHA_PADRAO,
            "email": "kaio@empresa.com",
            "foto_b64": None,
        },
        "maycon": {
            "nome": "Maycon",
            "cargo": "Anunciante MLB",
            "role": "employee",
            "senha": SENHA_PADRAO,
            "email": "maycon@empresa.com",
            "foto_b64": None,
        },
    }


def load_initial_data():
    """
    Converte _MOCK_HISTORY no DataFrame analítico do app.

    Cada item `(empresa, cust_id, [mlb1, mlb2, ...])` vira N linhas — uma por
    código MLB — porque a regra de negócio é "1 MLB = 1 publicação realizada".

    Distribuímos as datas dentro do mês de forma determinística (varremos os
    dias úteis do mês uniformemente) para que os gráficos por dia tenham
    granularidade real, em vez de tudo cair no dia 1.
    """
    rows = []

    for login, meses in _MOCK_HISTORY.items():
        for ym, grupos in meses.items():
            ano, mes = int(ym[:4]), int(ym[5:7])
            # Coleta a lista total de MLBs do mês para distribuir entre dias úteis
            todos_mlbs = []
            for empresa, cust_id, mlbs in grupos:
                for m in mlbs:
                    todos_mlbs.append((empresa, cust_id, m))

            if not todos_mlbs:
                continue

            # Dias úteis do mês (segunda a sexta). Para o mês corrente, usamos
            # apenas os dias úteis decorridos (até hoje); para meses passados,
            # o mês inteiro.
            primeiro = date(ano, mes, 1)
            if mes == 12:
                ultimo = date(ano + 1, 1, 1) - timedelta(days=1)
            else:
                ultimo = date(ano, mes + 1, 1) - timedelta(days=1)

            hoje = date.today()
            if (ano, mes) == (hoje.year, hoje.month):
                ultimo = min(ultimo, hoje)

            dias_uteis = []
            d = primeiro
            while d <= ultimo:
                if d.weekday() < 5:    # 0..4 = Seg..Sex
                    dias_uteis.append(d)
                d += timedelta(days=1)
            if not dias_uteis:
                dias_uteis = [primeiro]

            # Distribui os N MLBs entre os K dias úteis disponíveis (round-robin).
            for i, (empresa, cust_id, mlb) in enumerate(todos_mlbs):
                d = dias_uteis[i % len(dias_uteis)]
                rows.append({
                    "id": str(uuid.uuid4()),
                    "data": d,
                    "login": login,
                    "empresa": empresa,
                    "cust_id": cust_id or "",
                    "mlb": mlb,
                })

    df = pd.DataFrame(rows, columns=["id", "data", "login", "empresa", "cust_id", "mlb"])
    df["data"] = pd.to_datetime(df["data"]).dt.date
    df["_seq"] = range(len(df))   # ordem de inserção p/ ordenar "últimos"
    return df


def init_session_state():
    """Inicializa o session_state na primeira execução de cada sessão do navegador.

    Usuários e publicações são carregados do Supabase uma única vez por sessão.
    Escritas (inserções, remoções, troca de senha) vão sempre ao Supabase primeiro
    e depois atualizam o cache local — assim o F5 nunca perde dados.

    Fluxo de carga:
        usuarios    → SELECT * FROM usuarios  → dict interno
        publicacoes → SELECT * FROM publicacoes → DataFrame interno
            └─ se a tabela estiver vazia na primeira execução, semeia o histórico mock.

    Fallback: se o Supabase estiver inacessível (URL/KEY errados, sem internet),
    o app exibe um aviso e opera com os dados mock em memória.
    """
    # ── Usuários ──────────────────────────────────────────────────────────────
    if "users" not in st.session_state:
        try:
            resp = supabase.table("usuarios").select("*").execute()
            rows = resp.data or []
            if rows:
                users = {r["login"]: _sb_usuario_para_dict(r) for r in rows}
            else:
                # Supabase vazio: usa defaults e tenta inserir os usuários base
                users = usuarios_iniciais()
                _seed_usuarios_supabase(users)
            st.session_state["users"] = users
        except Exception as e:
            st.warning(
                f"⚠️ Supabase inacessível — operando com dados locais. ({e})"
            )
            st.session_state["users"] = usuarios_iniciais()

    # ── Publicações ───────────────────────────────────────────────────────────
    if "publicacoes" not in st.session_state:
        try:
            resp = supabase.table("publicacoes").select("*").execute()
            rows = resp.data or []
            if rows:
                df = _sb_publicacoes_para_df(rows)
            else:
                # Tabela vazia: carrega o histórico mock e o envia ao Supabase
                df = load_initial_data()
                _seed_publicacoes_supabase(df)
            st.session_state["publicacoes"] = df
        except Exception as e:
            st.warning(
                f"⚠️ Supabase inacessível — publicações carregadas do histórico local. ({e})"
            )
            st.session_state["publicacoes"] = load_initial_data()

    # ── Demais flags de sessão ─────────────────────────────────────────────────
    if "meta_mensal" not in st.session_state:
        st.session_state["meta_mensal"] = META_MENSAL_DEFAULT
    if "logado" not in st.session_state:
        st.session_state["logado"] = False
    if "user_atual" not in st.session_state:
        st.session_state["user_atual"] = None
    if "perfil_visualizando" not in st.session_state:
        st.session_state["perfil_visualizando"] = None


def _seed_usuarios_supabase(users: dict) -> None:
    """Insere os usuários padrão no Supabase quando a tabela `usuarios` está vazia."""
    try:
        rows = [
            {
                "login":  login,
                "nome":   u["nome"],
                "senha":  u["senha"],
                "perfil": u["role"],
            }
            for login, u in users.items()
        ]
        supabase.table("usuarios").insert(rows).execute()
    except Exception:
        pass  # fallback silencioso


def adicionar_publicacoes(login: str, data_pub: date, empresa: str,
                          cust_id: str, mlbs: list) -> int:
    """Insere N publicações no Supabase e atualiza o cache local.

    Fluxo:
      1. Verifica duplicatas no cache local E no Supabase (outra sessão pode ter
         inserido MLBs enquanto esta aba estava aberta).
      2. Envia os novos registros para o Supabase via INSERT.
      3. Em sucesso, adiciona as linhas ao DataFrame em session_state.

    Retorna a quantidade de publicações efetivamente inseridas.
    """
    df_atual = st.session_state["publicacoes"]
    existentes = set(df_atual["mlb"].astype(str))

    # Consulta duplicatas no Supabase para evitar conflitos entre sessões abertas
    try:
        resp_dup = (
            supabase.table("publicacoes")
            .select("mlb")
            .in_("mlb", [str(m) for m in mlbs])
            .execute()
        )
        existentes |= {str(r["mlb"]) for r in (resp_dup.data or [])}
    except Exception:
        pass  # se falhar, a verificação local já cobre o essencial

    rows_supabase = []
    rows_local    = []
    # Próximo _seq local (maior que todos os existentes, garante que novos
    # lançamentos apareçam como "últimos" mesmo na mesma data).
    proximo_seq = int(df_atual["_seq"].max()) + 1 if "_seq" in df_atual.columns and not df_atual.empty else 0
    for mlb in mlbs:
        if str(mlb) in existentes:
            continue
        rows_supabase.append({
            "data":  str(data_pub),
            "login": login,
            "loja":  empresa.strip(),
            "mlb":   str(mlb),
        })
        rows_local.append({
            "id":      str(uuid.uuid4()),
            "data":    data_pub,
            "login":   login,
            "empresa": empresa.strip(),
            "cust_id": (cust_id or "").strip(),
            "mlb":     str(mlb),
            "_seq":    proximo_seq,
        })
        proximo_seq += 1
        existentes.add(str(mlb))

    if not rows_supabase:
        return 0

    try:
        supabase.table("publicacoes").insert(rows_supabase).execute()
    except Exception as e:
        st.error(f"❌ Erro ao salvar no Supabase: {e}")
        return 0

    # Persiste no Supabase com sucesso → atualiza cache local
    df_novos = pd.DataFrame(rows_local)
    st.session_state["publicacoes"] = pd.concat(
        [df_atual, df_novos], ignore_index=True
    )
    return len(rows_supabase)


def remover_publicacao(id_: str) -> bool:
    """Remove uma publicação do Supabase e do cache local.

    O `id_` é um UUID gerado localmente (não existe no Supabase). Por isso,
    primeiro localizamos o código MLB correspondente no cache e usamos o MLB
    como chave natural para a deleção no Supabase.

    Retorna True se a remoção foi bem-sucedida.
    """
    df = st.session_state["publicacoes"]
    linha = df[df["id"] == id_]
    if linha.empty:
        return False

    mlb_val = str(linha.iloc[0]["mlb"])

    try:
        supabase.table("publicacoes").delete().eq("mlb", mlb_val).execute()
    except Exception as e:
        st.error(f"❌ Erro ao remover publicação do Supabase: {e}")
        return False

    novo = df[df["id"] != id_]
    st.session_state["publicacoes"] = novo.reset_index(drop=True)
    return True


# =============================================================================
# 7. UTILITÁRIOS DE NEGÓCIO
# =============================================================================
def hoje() -> date:
    """Date wrapper para facilitar mock em testes futuros."""
    return date.today()


def primeiro_e_ultimo_dia_do_mes(ref: date):
    """Retorna (primeiro, ultimo) dia do mês de `ref`."""
    primeiro = ref.replace(day=1)
    if ref.month == 12:
        proximo = date(ref.year + 1, 1, 1)
    else:
        proximo = date(ref.year, ref.month + 1, 1)
    ultimo = proximo - timedelta(days=1)
    return primeiro, ultimo


def dias_uteis_entre(inicio: date, fim: date) -> int:
    """
    Conta dias úteis (seg-sex) entre `inicio` e `fim`, inclusivos.
    Retorna 0 quando inicio > fim. Usa numpy.busday_count para performance
    (a planilha original usava esse mesmo critério: dias úteis sem feriados).
    """
    if inicio > fim:
        return 0
    # busday_count é meio-aberto à direita -> incluímos +1 dia
    return int(np.busday_count(
        inicio.isoformat(),
        (fim + timedelta(days=1)).isoformat(),
    ))


def calcular_kpis(df_pubs: pd.DataFrame, login: str, ref: date,
                  meta: int) -> dict:
    """
    Calcula todos os KPIs do mês de `ref` para um funcionário (`login`).

    Quando `login is None`, calcula CONSOLIDADO da equipe (soma todos), e
    a meta passada deve ser a meta global (meta * n_funcionarios).

    Retorna um dict com:
        meta, feito, faltantes,
        media_diaria_atual, media_diaria_alvo,
        projecao, status, status_classe, percentual,
        dias_uteis_decorridos, dias_uteis_restantes, dias_uteis_total
    """
    primeiro, ultimo = primeiro_e_ultimo_dia_do_mes(ref)

    # Filtra publicações do mês de referência
    df = df_pubs.copy()
    if df.empty:
        feito = 0
    else:
        df["data"] = pd.to_datetime(df["data"]).dt.date
        mask_mes = (df["data"] >= primeiro) & (df["data"] <= ultimo)
        if login is not None:
            mask = mask_mes & (df["login"] == login)
        else:
            mask = mask_mes
        feito = int(mask.sum())

    faltantes = max(meta - feito, 0)

    # Datas de referência para "dias úteis"
    today = hoje()
    # Se a referência é o mês corrente, "decorridos" vai até HOJE.
    # Se for um mês passado/futuro, usamos o mês inteiro como decorrido (passado)
    # ou 0 (futuro).
    if (ref.year, ref.month) == (today.year, today.month):
        dias_decorridos = dias_uteis_entre(primeiro, today)
        dias_restantes  = dias_uteis_entre(today + timedelta(days=1), ultimo)
    elif (ref.year, ref.month) < (today.year, today.month):
        dias_decorridos = dias_uteis_entre(primeiro, ultimo)
        dias_restantes  = 0
    else:
        dias_decorridos = 0
        dias_restantes  = dias_uteis_entre(primeiro, ultimo)
    dias_total = dias_decorridos + dias_restantes
    if dias_total == 0:
        dias_total = 1   # blindagem matemática

    # Média Diária Atual: anúncios feitos por dia útil decorrido
    media_atual = (feito / dias_decorridos) if dias_decorridos > 0 else 0.0

    # Média Diária Alvo: o ritmo necessário para BATER A META a partir de
    # amanhã (ou hoje, se não houver decorrido). Se a meta já foi batida,
    # alvo = 0.
    if dias_restantes > 0:
        media_alvo = max(faltantes / dias_restantes, 0)
    else:
        # Já não há mais dias úteis no mês — alvo é zero por definição
        media_alvo = 0.0

    # Projeção do mês: se mantiver o ritmo atual, quanto fecha o mês?
    projecao = round(media_atual * dias_total)

    # Status visual
    percentual = (feito / meta * 100) if meta > 0 else 0
    if feito >= meta:
        status, status_classe = "Acima da meta", "above"
    elif projecao >= meta * 0.95:    # vai bater dentro de 5% se mantiver o ritmo
        status, status_classe = "No alvo", "ontrack"
    else:
        status, status_classe = "Abaixo da meta", "below"

    return {
        "meta": meta,
        "feito": feito,
        "faltantes": faltantes,
        "media_diaria_atual": media_atual,
        "media_diaria_alvo": media_alvo,
        "projecao": projecao,
        "percentual": percentual,
        "status": status,
        "status_classe": status_classe,
        "dias_uteis_decorridos": dias_decorridos,
        "dias_uteis_restantes": dias_restantes,
        "dias_uteis_total": dias_total,
    }


# Regex que extrai códigos MLB de qualquer texto.
# Aceita "MLB12345678", "mlb12345678", "12345678" (com 7-13 dígitos), com ou
# sem espaços/quebras de linha. Toda a "magia" do paste em massa mora aqui.
_MLB_PATTERN = re.compile(r"\bMLB[\s-]*?(\d{7,13})\b|\b(\d{9,13})\b", re.IGNORECASE)


def extrair_mlbs(texto: str) -> list:
    """
    Extrai todos os códigos MLB de um texto livre (paste em massa).

    Aceita os formatos típicos:
      - "MLB1234567890" / "mlb1234567890"
      - "MLB-1234567890" / "MLB 1234567890"
      - Apenas o número, sem prefixo: "1234567890"
      - Separados por vírgula, ponto-e-vírgula, espaço, tab ou quebra de linha
      - Misturados com lixo (aspas, colchetes, links etc)

    Retorna lista DEDUPLICADA, preservando a ordem da primeira ocorrência.
    """
    if not texto:
        return []
    vistos = set()
    encontrados = []
    for m in _MLB_PATTERN.finditer(texto):
        # group 1 = casado com prefixo MLB; group 2 = casado sem prefixo
        codigo = m.group(1) or m.group(2)
        if not codigo:
            continue
        codigo = codigo.strip()
        # Validação de tamanho (MLBs reais têm 9-13 dígitos)
        if len(codigo) < 9 or len(codigo) > 13:
            continue
        mlb = f"MLB{codigo}"
        if mlb in vistos:
            continue
        vistos.add(mlb)
        encontrados.append(mlb)
    return encontrados


def fmt_int(n) -> str:
    """Formata inteiro como '1.234' (separador de milhar PT-BR)."""
    if pd.isna(n):
        return "—"
    return f"{int(round(n)):,}".replace(",", ".")


def fmt_dec(n, casas=1) -> str:
    """Formata decimal com vírgula (1,5)."""
    if pd.isna(n):
        return "—"
    return f"{n:.{casas}f}".replace(".", ",")


def fmt_data(d) -> str:
    """Formata date/datetime como 'DD/MM/AAAA'."""
    if d is None or pd.isna(d):
        return "—"
    if isinstance(d, str):
        d = pd.to_datetime(d).date()
    return d.strftime("%d/%m/%Y")


def iniciais_de(nome: str) -> str:
    """JS -> 'João Silva'  -> 'JS'."""
    partes = [p for p in (nome or "").split() if p]
    if len(partes) >= 2:
        return (partes[0][0] + partes[-1][0]).upper()
    if partes:
        return partes[0][:2].upper()
    return "??"


def html_avatar(login: str, tamanho: int = 80) -> str:
    """
    Renderiza o avatar do usuário. Se houver foto (b64) -> <img>, caso
    contrário -> círculo com gradiente + iniciais.
    """
    user = st.session_state["users"].get(login, {})
    nome = user.get("nome", login)
    foto = user.get("foto_b64")
    if foto:
        return (
            f'<img src="{foto}" class="func-foto" '
            f'style="width:{tamanho}px;height:{tamanho}px;" alt="Foto de {nome}" />'
        )
    return (
        f'<div class="func-foto-placeholder" '
        f'style="width:{tamanho}px;height:{tamanho}px;'
        f'font-size:{int(tamanho * 0.34)}px;">'
        f'{iniciais_de(nome)}</div>'
    )


def arquivo_para_data_uri(arquivo) -> str:
    """Converte um UploadedFile em data URI base64 para embutir no HTML."""
    extensao = arquivo.name.rsplit(".", 1)[-1].lower()
    mime = "jpeg" if extensao in ("jpg", "jpeg") else extensao
    b64 = base64.b64encode(arquivo.getbuffer()).decode()
    return f"data:image/{mime};base64,{b64}"


def mlb_link(mlb: str) -> str:
    """Renderiza um código MLB como link clicável para o anúncio no Mercado Livre.

    O banco armazena o código no formato `MLB6574794814` (sem hífen), mas a URL
    pública do ML usa `MLB-6574794814` (com hífen). Essa função faz a conversão.
    """
    mlb_clean = str(mlb).strip()
    # Converte MLB6574794814 → MLB-6574794814 (apenas para a URL)
    mlb_url = mlb_clean if mlb_clean.startswith("MLB-") else mlb_clean.replace("MLB", "MLB-", 1)
    return (
        f'<a href="https://produto.mercadolivre.com.br/{mlb_url}" '
        f'target="_blank" rel="noopener noreferrer" '
        f'style="color:#a78bfa; text-decoration:none; font-family:Fira Code,monospace; '
        f'font-size:13px; font-weight:500;" '
        f'title="Abrir anúncio no Mercado Livre">'
        f'{mlb_clean} <span style="font-size:10px; opacity:.7;">↗</span></a>'
    )


# =============================================================================
# 8. COMPONENTES DE UI (HTML helpers)
# =============================================================================
def html_logo() -> str:
    """Logo do app, mostrado no topo da sidebar e na tela de login."""
    return (
        '<div class="app-logo">'
            '<div class="mark">📦</div>'
            '<div class="divider"></div>'
            '<div class="text">CONTROLE<br>DE PUBLICAÇÕES</div>'
        '</div>'
    )


def render_page_header(titulo: str, subtitulo: str, pill_html: str = ""):
    """Cabeçalho padrão da página: título à esquerda, pílula opcional à direita."""
    html = (
        '<div class="page-header">'
            '<div class="title-wrap">'
                f'<h1>{titulo}</h1>'
                f'<p>{subtitulo}</p>'
            '</div>'
            f'<div>{pill_html}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def html_kpi(label: str, valor: str, sublabel: str, icone: str, classe_cor: str) -> str:
    """Card de KPI no estilo do mockup."""
    return (
        '<div class="kpi-card">'
            f'<div class="kpi-icon {classe_cor}">{icone}</div>'
            '<div class="kpi-content">'
                f'<p class="kpi-label">{label}</p>'
                f'<p class="kpi-value">{valor}</p>'
                f'<p class="kpi-sub">{sublabel}</p>'
            '</div>'
        '</div>'
    )


def html_progress(percentual: float, classe: str) -> str:
    """Barra de progresso colorida pela performance."""
    pct_clamped = max(0, min(100, percentual))
    return (
        '<div class="progress-wrap">'
            '<div class="progress-track">'
                f'<div class="progress-fill {classe}" style="width:{pct_clamped:.1f}%;"></div>'
            '</div>'
        '</div>'
    )


def html_status_pill(status: str, classe: str) -> str:
    return f'<span class="status-pill {classe}">{status}</span>'


def render_painel_tabela(titulo: str, cabecalhos: list, linhas_dados: list,
                         subtitulo: str = "", html_acao_direita: str = ""):
    """
    Painel com título + tabela estilizada.
    O HTML é montado como UMA STRING contínua para não acionar o parser de
    bloco de código do Streamlit (que reage à indentação de 4 espaços).
    """
    th_html = "".join(f"<th>{c}</th>" for c in cabecalhos)
    if not linhas_dados:
        tr_html = (
            f'<tr><td colspan="{len(cabecalhos)}" '
            f'style="text-align:center; color:{COR["txt_terciario"]}; padding:30px;">'
            'Nenhum registro encontrado.'
            '</td></tr>'
        )
    else:
        tr_html = "".join(
            "<tr>" + "".join(f"<td>{cel}</td>" for cel in linha) + "</tr>"
            for linha in linhas_dados
        )

    sub_html = f'<div class="panel-subtitle">{subtitulo}</div>' if subtitulo else ""
    html = (
        '<div class="panel">'
            '<div class="panel-header">'
                f'<div><h3 class="panel-title">{titulo}</h3>{sub_html}</div>'
                f'<div>{html_acao_direita}</div>'
            '</div>'
            '<table class="tabela-custom">'
                f'<thead><tr>{th_html}</tr></thead>'
                f'<tbody>{tr_html}</tbody>'
            '</table>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# Ícones SVG inline — escolha consciente para não depender de CDN externo
SVG_TARGET = """<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><circle cx='12' cy='12' r='6'/><circle cx='12' cy='12' r='2'/></svg>"""

SVG_CHECK = """<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><path d='M20 6L9 17l-5-5'/></svg>"""

SVG_REMAINING = """<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>"""

SVG_TREND = """<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='23 6 13.5 15.5 8.5 10.5 1 18'/><polyline points='17 6 23 6 23 12'/></svg>"""

SVG_USER = """<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/><circle cx='12' cy='7' r='4'/></svg>"""

SVG_PACKAGE = """<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'/><polyline points='3.27 6.96 12 12.01 20.73 6.96'/><line x1='12' y1='22.08' x2='12' y2='12'/></svg>"""

SVG_CALENDAR = """<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>"""

SVG_FIRE = """<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z'/></svg>"""


# =============================================================================
# 9. GRÁFICOS PLOTLY (helpers)
# =============================================================================
def grafico_evolucao_diaria(df_dia: pd.DataFrame, altura: int = 320) -> go.Figure:
    """
    Gráfico de barras + linha cumulativa para a evolução diária do mês.
    Espera df com colunas: data, total_dia, acumulado.
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_dia["data"],
        y=df_dia["total_dia"],
        name="Anúncios no dia",
        marker=dict(
            color=df_dia["total_dia"],
            colorscale=[[0, "#7c3aed"], [0.5, "#ec4899"], [1, "#f97316"]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x|%d/%m}</b><br>%{y} anúncio(s)<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df_dia["data"],
        y=df_dia["acumulado"],
        name="Acumulado",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color="#22c55e", width=3, shape="spline", smoothing=0.6),
        marker=dict(size=7, color="#22c55e",
                    line=dict(width=2, color=COR["bg_card"])),
        hovertemplate="<b>%{x|%d/%m}</b><br>Acumulado: %{y}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Inter", size=12),
        height=altura,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(color="#cbd5e1", size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color="#94a3b8", size=11),
            tickformat="%d/%m",
        ),
        yaxis=dict(
            title="Anúncios no dia",
            gridcolor="rgba(30,41,59,0.6)",
            tickfont=dict(color="#94a3b8", size=11),
            zeroline=False,
        ),
        yaxis2=dict(
            title="Acumulado",
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#94a3b8", size=11),
            zeroline=False,
        ),
        hovermode="x unified",
    )
    return fig


def grafico_ranking_funcionarios(df_rank: pd.DataFrame, meta: int,
                                 altura: int = 340) -> go.Figure:
    """
    Barras horizontais comparando o "feito" de cada funcionário com a meta.
    Espera df com: nome, feito, meta.
    """
    fig = go.Figure()

    cores = []
    for v in df_rank["feito"]:
        if v >= meta:
            cores.append("#22c55e")
        elif v >= meta * 0.85:
            cores.append("#eab308")
        else:
            cores.append("#ef4444")

    fig.add_trace(go.Bar(
        x=df_rank["feito"],
        y=df_rank["nome"],
        orientation="h",
        marker=dict(color=cores, line=dict(width=0)),
        text=df_rank["feito"].apply(lambda v: f"{int(v)}"),
        textposition="outside",
        textfont=dict(color="#cbd5e1", size=12, family="Inter"),
        hovertemplate="<b>%{y}</b><br>Feito: %{x}<extra></extra>",
        name="Feito",
    ))

    # Linha vertical da meta
    fig.add_vline(
        x=meta,
        line=dict(color="#8b5cf6", width=2, dash="dash"),
        annotation_text=f"Meta: {meta}",
        annotation_position="top",
        annotation_font_color="#8b5cf6",
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Inter", size=12),
        height=altura,
        margin=dict(l=10, r=40, t=20, b=10),
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(30,41,59,0.6)",
            tickfont=dict(color="#94a3b8", size=11),
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color="white", size=13),
            zeroline=False,
            categoryorder="total ascending",
        ),
    )
    return fig


def grafico_evolucao_mensal(df_mes: pd.DataFrame, altura: int = 320) -> go.Figure:
    """
    Linhas suaves comparando totais mensais (até 12 meses).
    Espera df com colunas: mes_label (str), total (int).
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_mes["mes_label"],
        y=df_mes["total"],
        mode="lines+markers",
        line=dict(color="#8b5cf6", width=3, shape="spline", smoothing=0.7),
        marker=dict(size=10, color="#ec4899",
                    line=dict(width=2, color=COR["bg_card"])),
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.15)",
        hovertemplate="<b>%{x}</b><br>%{y} anúncios<extra></extra>",
        name="Anúncios",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cbd5e1", family="Inter", size=12),
        height=altura,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color="#94a3b8", size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(30,41,59,0.6)",
            tickfont=dict(color="#94a3b8", size=11),
            zeroline=False,
        ),
    )
    return fig


# =============================================================================
# 10. SIDEBAR — diferente para admin vs employee
# =============================================================================
def render_sidebar() -> str:
    """Renderiza a sidebar e retorna a página selecionada."""
    user_atual = st.session_state["user_atual"]
    user = st.session_state["users"][user_atual]
    is_admin = user["role"] == "admin"

    with st.sidebar:
        # Logo
        st.markdown(html_logo(), unsafe_allow_html=True)

        # Menu — diferente entre admin (visão consolidada da equipe) e
        # employee (visão pessoal + Publicações). A escolha do menu é a
        # principal manifestação do RBAC na UI.
        if is_admin:
            opcoes = ["Controle Geral", "Equipe", "Histórico", "Configurações"]
            icones = ["speedometer2", "people-fill", "clock-history", "gear-fill"]
        else:
            opcoes = ["Meu Painel", "Publicações", "Meu Histórico", "Meu Perfil"]
            icones = ["bar-chart-fill", "plus-circle-fill", "clock-history", "person-fill"]

        pagina = option_menu(
            menu_title=None,
            options=opcoes,
            icons=icones,
            default_index=0,
            styles={
                "container": {"padding": "0 12px", "background-color": "transparent"},
                "nav-link": {
                    "font-size": "14px", "font-weight": "500",
                    "color": "#cbd5e1", "text-align": "left",
                    "margin": "4px 0", "padding": "12px 16px",
                    "border-radius": "10px",
                    "background-color": "transparent",
                    "--hover-color": "#1e293b",
                },
                "nav-link-selected": {
                    "background-image": COR["grad_ativo"],
                    "color": "white", "font-weight": "600",
                    "box-shadow": "0 6px 20px rgba(236,72,153,0.25)",
                },
                "icon": {"font-size": "16px", "margin-right": "10px"},
            },
        )

        # Empurra o card do usuário para o rodapé
        st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

        # Card do usuário logado — com avatar (foto ou iniciais)
        foto = user.get("foto_b64")
        if foto:
            avatar_html = f'<div class="avatar"><img src="{foto}" /></div>'
        else:
            avatar_html = f'<div class="avatar">{iniciais_de(user["nome"])}</div>'

        user_card = (
            '<div class="user-card">'
                f'{avatar_html}'
                '<div>'
                    '<div class="greeting">Bem-vindo,</div>'
                    f'<div class="username">{user["nome"]}</div>'
                    f'<div class="role">{"Administrador" if is_admin else user.get("cargo", "Funcionário")}</div>'
                '</div>'
            '</div>'
        )
        st.markdown(user_card, unsafe_allow_html=True)

        # Botão sair
        if st.button("⎋  Sair", key="btn_sair"):
            st.session_state["logado"] = False
            st.session_state["user_atual"] = None
            st.session_state["perfil_visualizando"] = None
            st.rerun()

        # Footer
        footer_html = (
            '<div class="sidebar-footer">'
                '<div class="brand">Controle de Publicações</div>'
                '<div>Versão 1.0.0</div>'
            '</div>'
        )
        st.markdown(footer_html, unsafe_allow_html=True)

    return pagina


# =============================================================================
# 11. TELA DE LOGIN
# =============================================================================
def tela_login():
    """Tela de login centralizada com card escuro."""
    aplicar_css_global()
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown(
            '<div class="login-wrap">'
                '<div class="login-logo">'
                    '<div class="ico">📦</div>'
                    '<h1>Controle de Publicações</h1>'
                    '<p>Acesse para registrar e acompanhar seus anúncios MLB</p>'
                '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Renderizamos os inputs DEPOIS do card visual (Streamlit não permite
        # injetar inputs nativos dentro de um markdown). O CSS do .login-wrap
        # cria a impressão de continuidade.
        usuario = st.text_input("Usuário", placeholder="Ex: ruben",
                                key="login_user").strip().lower()
        senha = st.text_input("Senha", type="password",
                              placeholder="Sua senha", key="login_pass")

        if st.button("Entrar", type="primary", key="btn_entrar"):
            if not usuario:
                st.error("Informe o usuário.")
            else:
                try:
                    # Consulta o Supabase: login E senha têm que bater
                    resp = (
                        supabase.table("usuarios")
                        .select("login, nome, senha, perfil")
                        .eq("login", usuario)
                        .eq("senha", senha)
                        .execute()
                    )
                    if resp.data:
                        row = resp.data[0]
                        # Atualiza o cache local com os dados mais recentes do DB
                        st.session_state["users"][usuario] = _sb_usuario_para_dict(row)
                        st.session_state["logado"]     = True
                        st.session_state["user_atual"] = usuario
                        st.rerun()
                    else:
                        st.error("Usuário ou senha inválidos.")
                except Exception as e:
                    # Fallback local para quando o Supabase está inacessível
                    users = st.session_state.get("users", {})
                    if usuario in users and users[usuario]["senha"] == senha:
                        st.session_state["logado"]     = True
                        st.session_state["user_atual"] = usuario
                        st.rerun()
                    else:
                        st.error(
                            f"Usuário ou senha inválidos. "
                            f"(Supabase inacessível — verifique URL/KEY. Detalhe: {e})"
                        )

        # Dica de logins (apenas para demonstração)
        st.markdown(
            '<div class="login-help">'
                '<b>🔑 Acessos de demonstração</b><br>'
                'Senha padrão: <b>123</b><br>'
                '<b>Admin:</b> adm &nbsp;|&nbsp; '
                '<b>Funcionários:</b> ruben, bruno, kaio, maycon'
            '</div>',
            unsafe_allow_html=True,
        )


# =============================================================================
# 12. PÁGINA — CONTROLE GERAL (ADMIN)
# -----------------------------------------------------------------------------
# Replica e estende o "Controle Geral" da planilha original, agora com
# gráficos, ranking e drill-down individual.
# =============================================================================
def pagina_controle_geral():
    """Visão consolidada da equipe (apenas admin)."""
    df_pubs   = st.session_state["publicacoes"]
    users     = st.session_state["users"]
    meta_ind  = st.session_state["meta_mensal"]
    funcionarios = [u for u in users if users[u]["role"] == "employee"]

    today  = hoje()
    nome_mes = MESES_PT[today.month]
    pill = (
        f'<div class="filter-pill">'
        f'<span style="color:{COR["txt_secundario"]};">📅 Mês de referência:</span>'
        f'<b style="color:white;">{nome_mes} / {today.year}</b>'
        f'</div>'
    )
    render_page_header(
        "Controle Geral",
        f"Consolidado da equipe • {len(funcionarios)} funcionários • Meta individual: {meta_ind}/mês",
        pill_html=pill,
    )

    # ---------------- KPIs do consolidado ----------------
    meta_geral = meta_ind * len(funcionarios)
    kpi_geral = calcular_kpis(df_pubs, login=None, ref=today, meta=meta_geral)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(html_kpi(
            "Meta da Equipe", fmt_int(kpi_geral["meta"]),
            f'{len(funcionarios)} funcionários × {meta_ind}',
            SVG_TARGET, "purple1",
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(html_kpi(
            "Feito no mês", fmt_int(kpi_geral["feito"]),
            f'{kpi_geral["percentual"]:.0f}% da meta',
            SVG_CHECK, "green",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(html_kpi(
            "Faltam", fmt_int(kpi_geral["faltantes"]),
            f'{kpi_geral["dias_uteis_restantes"]} dias úteis restantes',
            SVG_REMAINING, "orange",
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(html_kpi(
            "Projeção", fmt_int(kpi_geral["projecao"]),
            "no ritmo atual",
            SVG_TREND, "pink",
        ), unsafe_allow_html=True)

    # ---------------- Barra de progresso global ----------------
    st.markdown(
        '<div class="panel">'
            '<div class="panel-header">'
                '<div>'
                    '<h3 class="panel-title">Progresso da Equipe</h3>'
                    f'<div class="panel-subtitle">Média diária atual: <b style="color:white;">{fmt_dec(kpi_geral["media_diaria_atual"])}</b> anúncios/dia · '
                    f'Alvo para bater a meta: <b style="color:white;">{fmt_dec(kpi_geral["media_diaria_alvo"])}</b> anúncios/dia</div>'
                '</div>'
                f'<div>{html_status_pill(kpi_geral["status"], kpi_geral["status_classe"])}</div>'
            '</div>'
            f'{html_progress(kpi_geral["percentual"], kpi_geral["status_classe"])}'
            '<div class="progress-meta">'
                f'<span>0</span><span>Meta: {fmt_int(kpi_geral["meta"])}</span>'
            '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ---------------- Linha 2: gráfico evolução diária + ranking ----------------
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        # Evolução diária do mês (consolidado)
        primeiro, ultimo = primeiro_e_ultimo_dia_do_mes(today)
        df_mes = df_pubs.copy()
        if not df_mes.empty:
            df_mes["data"] = pd.to_datetime(df_mes["data"]).dt.date
            df_mes = df_mes[(df_mes["data"] >= primeiro) & (df_mes["data"] <= ultimo)]
        if df_mes.empty:
            df_dia = pd.DataFrame({"data": [today], "total_dia": [0], "acumulado": [0]})
        else:
            agg = df_mes.groupby("data").size().reset_index(name="total_dia")
            agg = agg.sort_values("data")
            agg["acumulado"] = agg["total_dia"].cumsum()
            df_dia = agg

        st.markdown(
            '<div class="panel">'
                '<div class="panel-header">'
                    '<div>'
                        f'<h3 class="panel-title">Evolução Diária • {nome_mes}/{today.year}</h3>'
                        '<div class="panel-subtitle">Anúncios publicados por dia + curva acumulada</div>'
                    '</div>'
                '</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(grafico_evolucao_diaria(df_dia, altura=320),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # Ranking dos funcionários no mês
        ranking = []
        for login in funcionarios:
            k = calcular_kpis(df_pubs, login=login, ref=today, meta=meta_ind)
            ranking.append({"nome": users[login]["nome"], "feito": k["feito"]})
        df_rank = pd.DataFrame(ranking).sort_values("feito", ascending=True)

        st.markdown(
            '<div class="panel">'
                '<div class="panel-header">'
                    '<div>'
                        '<h3 class="panel-title">Ranking do Mês</h3>'
                        f'<div class="panel-subtitle">Linha tracejada = meta individual ({meta_ind})</div>'
                    '</div>'
                '</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(grafico_ranking_funcionarios(df_rank, meta_ind, altura=320),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- Tabela detalhada por funcionário ----------------
    linhas = []
    for login in funcionarios:
        k = calcular_kpis(df_pubs, login=login, ref=today, meta=meta_ind)
        nome = users[login]["nome"]
        linhas.append([
            f'<b>{nome}</b><br><span style="color:{COR["txt_terciario"]}; font-size:11px;">@{login}</span>',
            fmt_int(k["meta"]),
            f'<b style="color:white;">{fmt_int(k["feito"])}</b>',
            fmt_int(k["faltantes"]),
            fmt_dec(k["media_diaria_atual"]),
            fmt_dec(k["media_diaria_alvo"]),
            fmt_int(k["projecao"]),
            html_status_pill(k["status"], k["status_classe"]),
        ])
    render_painel_tabela(
        titulo="Detalhamento por Funcionário",
        subtitulo=f"Mês de {nome_mes}/{today.year} · Dias úteis decorridos: "
                  f"{kpi_geral['dias_uteis_decorridos']} de {kpi_geral['dias_uteis_total']}",
        cabecalhos=["Funcionário", "Meta", "Feito", "Faltam",
                    "Média Atual", "Média Alvo", "Projeção", "Status"],
        linhas_dados=linhas,
    )

    # ---------------- Histórico mensal (12 meses) ----------------
    df_all = df_pubs.copy()
    if not df_all.empty:
        df_all["data"] = pd.to_datetime(df_all["data"])
        df_all["ym"] = df_all["data"].dt.to_period("M").astype(str)
        agg_mes = (df_all.groupby("ym").size().reset_index(name="total")
                   .sort_values("ym").tail(12))
        agg_mes["mes_label"] = agg_mes["ym"].apply(
            lambda s: f"{MESES_PT[int(s[5:7])][:3]}/{s[2:4]}"
        )
        st.markdown(
            '<div class="panel">'
                '<div class="panel-header">'
                    '<div>'
                        '<h3 class="panel-title">Evolução Histórica da Equipe</h3>'
                        '<div class="panel-subtitle">Total consolidado de anúncios publicados nos últimos meses</div>'
                    '</div>'
                '</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(grafico_evolucao_mensal(agg_mes, altura=290),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# 13. PÁGINA — EQUIPE (ADMIN)
# -----------------------------------------------------------------------------
# Grid de cards dos funcionários, cada um com mini-KPIs + botão "Ver detalhes".
# =============================================================================
def pagina_equipe():
    """Lista de funcionários (cards). Admin pode clicar para ver perfil."""
    df_pubs  = st.session_state["publicacoes"]
    users    = st.session_state["users"]
    meta_ind = st.session_state["meta_mensal"]
    today    = hoje()

    # Se o admin já clicou em "Ver detalhes", redirecionamos ao perfil
    if st.session_state.get("perfil_visualizando"):
        return pagina_perfil_funcionario(st.session_state["perfil_visualizando"])

    funcionarios = [u for u in users if users[u]["role"] == "employee"]
    pill = (
        f'<div class="filter-pill">'
        f'👥 <b style="color:white;">{len(funcionarios)}</b> funcionários ativos'
        f'</div>'
    )
    render_page_header(
        "Equipe",
        f"Performance individual em {MESES_PT[today.month]}/{today.year}",
        pill_html=pill,
    )

    # Renderiza em grid de 4 colunas (responsivo via st.columns)
    cols = st.columns(4)
    for i, login in enumerate(funcionarios):
        user = users[login]
        k = calcular_kpis(df_pubs, login=login, ref=today, meta=meta_ind)
        with cols[i % 4]:
            # Card HTML — sem botão (botão renderiza fora pelo limite do streamlit)
            card_html = (
                '<div class="func-card">'
                    f'{html_avatar(login, 90)}'
                    f'<div class="func-nome">{user["nome"]}</div>'
                    f'<div class="func-cargo">{user["cargo"]}</div>'
                    '<div class="func-mini-kpis">'
                        '<div class="func-mini-kpi">'
                            '<div class="lbl">Feito</div>'
                            f'<div class="val">{fmt_int(k["feito"])}</div>'
                        '</div>'
                        '<div class="func-mini-kpi">'
                            '<div class="lbl">Meta</div>'
                            f'<div class="val">{fmt_int(k["meta"])}</div>'
                        '</div>'
                        '<div class="func-mini-kpi">'
                            '<div class="lbl">Status</div>'
                            f'<div class="val" style="font-size:11px;">'
                            f'{html_status_pill(k["status"], k["status_classe"])}'
                            '</div>'
                        '</div>'
                    '</div>'
                    f'{html_progress(k["percentual"], k["status_classe"])}'
                    '<div class="progress-meta">'
                        f'<span>{k["percentual"]:.0f}%</span>'
                        f'<span>Projeção: {fmt_int(k["projecao"])}</span>'
                    '</div>'
                '</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)
            # Botão de ação — fora do card por limitação do Streamlit
            if st.button("Ver detalhes →", key=f"ver_{login}",
                         use_container_width=True):
                st.session_state["perfil_visualizando"] = login
                st.rerun()


# =============================================================================
# 14. PÁGINA — PERFIL DETALHADO DE UM FUNCIONÁRIO
# -----------------------------------------------------------------------------
# Acessível pelo admin (drill-down a partir da Equipe) OU pelo próprio
# funcionário (sua página "Meu Painel" reutiliza praticamente o mesmo layout).
# =============================================================================
def pagina_perfil_funcionario(login: str, modo_self: bool = False):
    """
    Mostra o painel detalhado de um funcionário.

    Args:
        login: usuário a ser exibido
        modo_self: se True, é o próprio funcionário olhando seu painel
                   (esconde o botão "Voltar" e o botão "Editar perfil" do admin)
    """
    df_pubs  = st.session_state["publicacoes"]
    users    = st.session_state["users"]
    user     = users.get(login)
    if not user:
        st.error(f"Funcionário '{login}' não encontrado.")
        return

    meta_ind = st.session_state["meta_mensal"]
    today    = hoje()
    k = calcular_kpis(df_pubs, login=login, ref=today, meta=meta_ind)

    # Botão "Voltar" — apenas no modo admin
    if not modo_self:
        col_back, _ = st.columns([0.2, 0.8])
        with col_back:
            if st.button("← Voltar para Equipe", key="btn_voltar"):
                st.session_state["perfil_visualizando"] = None
                st.rerun()

    # Hero section com avatar + nome + KPIs principais
    hero_html = (
        '<div class="profile-hero">'
            f'{html_avatar(login, 120)}'
            '<div class="profile-hero-info">'
                f'<div class="profile-hero-nome">{user["nome"]}</div>'
                f'<div class="profile-hero-cargo">{user["cargo"]} • @{login}</div>'
                '<div class="profile-hero-stats">'
                    '<div>'
                        '<div class="profile-stat-label">Meta</div>'
                        f'<div class="profile-stat-value">{fmt_int(k["meta"])}</div>'
                    '</div>'
                    '<div>'
                        '<div class="profile-stat-label">Feito</div>'
                        f'<div class="profile-stat-value">{fmt_int(k["feito"])}</div>'
                    '</div>'
                    '<div>'
                        '<div class="profile-stat-label">Faltam</div>'
                        f'<div class="profile-stat-value">{fmt_int(k["faltantes"])}</div>'
                    '</div>'
                    '<div>'
                        '<div class="profile-stat-label">Status</div>'
                        f'<div class="profile-stat-value">{html_status_pill(k["status"], k["status_classe"])}</div>'
                    '</div>'
                '</div>'
            '</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    # Bloco de KPIs detalhados (linha única de 4 cards)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(html_kpi(
            "Média Diária Atual", fmt_dec(k["media_diaria_atual"]),
            f'em {k["dias_uteis_decorridos"]} dias úteis decorridos',
            SVG_FIRE, "purple1",
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(html_kpi(
            "Média Diária Alvo", fmt_dec(k["media_diaria_alvo"]),
            f'para os {k["dias_uteis_restantes"]} dias úteis restantes',
            SVG_TARGET, "purple2",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(html_kpi(
            "Projeção do Mês", fmt_int(k["projecao"]),
            "no ritmo atual",
            SVG_TREND, "pink",
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(html_kpi(
            "Dias Úteis Restantes", fmt_int(k["dias_uteis_restantes"]),
            f'de {k["dias_uteis_total"]} no mês',
            SVG_CALENDAR, "orange",
        ), unsafe_allow_html=True)

    # Barra de progresso individual
    st.markdown(
        '<div class="panel">'
            '<div class="panel-header">'
                '<div>'
                    '<h3 class="panel-title">Progresso da Meta</h3>'
                    f'<div class="panel-subtitle">{fmt_int(k["feito"])} de {fmt_int(k["meta"])} anúncios — {k["percentual"]:.1f}%</div>'
                '</div>'
                f'<div>{html_status_pill(k["status"], k["status_classe"])}</div>'
            '</div>'
            f'{html_progress(k["percentual"], k["status_classe"])}'
            '<div class="progress-meta">'
                f'<span>{k["percentual"]:.0f}% concluído</span>'
                f'<span>Faltam {fmt_int(k["faltantes"])}</span>'
            '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Linha 2: evolução diária do mês + top empresas
    primeiro, ultimo = primeiro_e_ultimo_dia_do_mes(today)
    df_mes = df_pubs[df_pubs["login"] == login].copy()
    if not df_mes.empty:
        df_mes["data"] = pd.to_datetime(df_mes["data"]).dt.date
        df_mes_atual = df_mes[(df_mes["data"] >= primeiro) & (df_mes["data"] <= ultimo)]
    else:
        df_mes_atual = df_mes

    col_g, col_t = st.columns([1.4, 1])

    with col_g:
        if df_mes_atual.empty:
            df_dia = pd.DataFrame({"data": [today], "total_dia": [0], "acumulado": [0]})
        else:
            agg = df_mes_atual.groupby("data").size().reset_index(name="total_dia")
            agg = agg.sort_values("data")
            agg["acumulado"] = agg["total_dia"].cumsum()
            df_dia = agg

        st.markdown(
            '<div class="panel">'
                '<div class="panel-header">'
                    '<div>'
                        f'<h3 class="panel-title">Sua Evolução em {MESES_PT[today.month]}</h3>'
                        '<div class="panel-subtitle">Anúncios publicados por dia + acumulado</div>'
                    '</div>'
                '</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(grafico_evolucao_diaria(df_dia, altura=300),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_t:
        # Top 5 empresas do mês
        if df_mes_atual.empty:
            linhas = []
        else:
            top = (df_mes_atual.groupby("empresa").size()
                   .reset_index(name="total")
                   .sort_values("total", ascending=False)
                   .head(5))
            linhas = [
                [f'<b>{r["empresa"]}</b>', fmt_int(r["total"])]
                for _, r in top.iterrows()
            ]
        render_painel_tabela(
            titulo=f"Top 5 Empresas",
            subtitulo="Maiores volumes do mês corrente",
            cabecalhos=["Empresa", "Anúncios"],
            linhas_dados=linhas,
        )

    # Histórico mensal pessoal (até 12 meses)
    if not df_pubs.empty:
        df_all = df_pubs[df_pubs["login"] == login].copy()
        if not df_all.empty:
            df_all["data"] = pd.to_datetime(df_all["data"])
            df_all["ym"] = df_all["data"].dt.to_period("M").astype(str)
            agg_mes = (df_all.groupby("ym").size().reset_index(name="total")
                       .sort_values("ym").tail(12))
            agg_mes["mes_label"] = agg_mes["ym"].apply(
                lambda s: f"{MESES_PT[int(s[5:7])][:3]}/{s[2:4]}"
            )
            st.markdown(
                '<div class="panel">'
                    '<div class="panel-header">'
                        '<div>'
                            '<h3 class="panel-title">Sua Evolução Histórica</h3>'
                            '<div class="panel-subtitle">Total mensal de anúncios publicados</div>'
                        '</div>'
                    '</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(grafico_evolucao_mensal(agg_mes, altura=270),
                            use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# 15. PÁGINA — MEU PAINEL (FUNCIONÁRIO)
# -----------------------------------------------------------------------------
# Reusa a página de perfil em "modo self".
# =============================================================================
def pagina_meu_painel():
    """Painel pessoal do funcionário logado."""
    user_atual = st.session_state["user_atual"]
    today = hoje()

    pill = (
        f'<div class="filter-pill">'
        f'<span style="color:{COR["txt_secundario"]};">📅</span>&nbsp; '
        f'<b style="color:white;">{MESES_PT[today.month]}/{today.year}</b>'
        f'</div>'
    )
    render_page_header(
        "Meu Painel",
        "Acompanhe sua produtividade do mês em tempo real",
        pill_html=pill,
    )
    pagina_perfil_funcionario(user_atual, modo_self=True)


# =============================================================================
# 16. PÁGINA — Publicações (FUNCIONÁRIO)
# -----------------------------------------------------------------------------
# A peça-chave do produto: substitui as "infinitas colunas MLB" da planilha
# por uma única caixa de texto onde o funcionário cola QUALQUER bloco de
# códigos. O sistema:
#   1) Detecta os MLBs via regex (com ou sem prefixo, separados por
#      espaço/vírgula/quebra-de-linha, com ou sem lixo entre eles).
#   2) Mostra um preview em tempo real com a contagem e os códigos.
#   3) Marca duplicatas (códigos que já existem no banco) com tachado em
#      vermelho — não bloqueia, mas avisa.
#   4) Ao confirmar, insere UMA LINHA POR MLB no banco em memória,
#      vinculando ao usuário logado.
# =============================================================================
def pagina_bater_ponto():
    user_atual = st.session_state["user_atual"]
    today = hoje()

    render_page_header(
        "Publicações",
        "Registre seus anúncios MLB — cole os códigos em qualquer formato e nós cuidamos do resto",
    )

    # ----- Formulário principal -----
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(
        '<h3 class="panel-title">📝 Novo Registro</h3>'
        '<div class="panel-subtitle">Você pode colar dezenas de MLBs de uma vez. '
        'O sistema detecta, deduplica e registra cada código como uma publicação separada.</div>'
        '<div style="height:18px;"></div>',
        unsafe_allow_html=True,
    )

    col_data, col_emp, col_cust = st.columns([1, 2, 1.3])
    with col_data:
        data_pub = st.date_input(
            "Data da publicação",
            value=today,
            max_value=today,
            format="DD/MM/YYYY",
            key="bp_data",
        )
    with col_emp:
        empresa = st.text_input(
            "Empresa / Loja",
            placeholder="Ex: CIA das Malas",
            key="bp_empresa",
        )
    with col_cust:
        cust_id = st.text_input(
            "Cust ID (opcional)",
            placeholder="Ex: 1234567890",
            key="bp_cust",
        )

    st.markdown(
        '<div style="margin-top: 8px; color:#94a3b8; font-size:13px;">'
        '🔢 <b>Códigos MLB</b> · cole o bloco aqui — qualquer formato:'
        '</div>',
        unsafe_allow_html=True,
    )
    texto_mlbs = st.text_area(
        label="Códigos MLB",
        placeholder=(
            "MLB1234567890\n"
            "MLB2345678901\n"
            "MLB3456789012\n\n"
            "ou\n"
            "MLB1234567890, MLB2345678901, MLB3456789012\n\n"
            "ou só os números:\n"
            "1234567890  2345678901  3456789012"
        ),
        height=200,
        key="bp_codigos",
        label_visibility="collapsed",
    )

    # ----- Preview em tempo real -----
    extraidos = extrair_mlbs(texto_mlbs)

    # Detecta duplicatas contra o banco
    df_atual = st.session_state["publicacoes"]
    existentes = set(df_atual["mlb"].astype(str).tolist())
    duplicatas = [m for m in extraidos if m in existentes]
    novos      = [m for m in extraidos if m not in existentes]

    # Caixa de feedback
    if texto_mlbs.strip():
        cls_total = "green" if extraidos else "red"
        cls_dup   = "yellow" if duplicatas else ""
        st.markdown(
            '<div class="insight-box">'
                '<div class="row">'
                    '<div class="lbl">🎯 Códigos detectados</div>'
                    f'<div class="val {cls_total}">{len(extraidos)}</div>'
                '</div>'
                '<div class="row">'
                    '<div class="lbl">✅ Novos (serão registrados)</div>'
                    f'<div class="val green">{len(novos)}</div>'
                '</div>'
                '<div class="row">'
                    '<div class="lbl">⚠️ Já existentes no banco (ignorados)</div>'
                    f'<div class="val {cls_dup}">{len(duplicatas)}</div>'
                '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Mostra os chips dos códigos (até 60 para não inflar a tela)
        if extraidos:
            with st.expander(f"👀 Preview dos {len(extraidos)} código(s) detectado(s)", expanded=False):
                chips = []
                for m in extraidos[:60]:
                    cls = "mlb-chip dup" if m in existentes else "mlb-chip"
                    chips.append(f'<span class="{cls}">{m}</span>')
                if len(extraidos) > 60:
                    chips.append(
                        f'<span style="color:{COR["txt_terciario"]}; font-size:12px;">'
                        f'+ {len(extraidos) - 60} mais...</span>'
                    )
                st.markdown(
                    '<div style="margin-top:10px;">' + " ".join(chips) + "</div>",
                    unsafe_allow_html=True,
                )

    # ----- Botão de confirmação -----
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        confirmar = st.button(
            f"✅ Registrar {len(novos)} anúncio(s)" if novos else "✅ Registrar",
            type="primary",
            disabled=(len(novos) == 0 or not empresa.strip()),
            use_container_width=True,
            key="bp_confirmar",
        )
    with col_info:
        if not empresa.strip():
            st.markdown(
                '<div style="color:#fca5a5; font-size:12px; padding-top:10px;">'
                '⚠️ Preencha o nome da empresa para registrar.'
                '</div>',
                unsafe_allow_html=True,
            )
        elif not novos:
            st.markdown(
                f'<div style="color:{COR["txt_terciario"]}; font-size:12px; padding-top:10px;">'
                'Cole pelo menos um código MLB válido para habilitar o registro.'
                '</div>',
                unsafe_allow_html=True,
            )

    if confirmar and novos and empresa.strip():
        n_inseridos = adicionar_publicacoes(
            login=user_atual,
            data_pub=data_pub,
            empresa=empresa.strip(),
            cust_id=cust_id.strip(),
            mlbs=novos,
        )
        st.success(
            f"🎉 {n_inseridos} anúncio(s) registrado(s) com sucesso para "
            f"**{empresa}** em **{fmt_data(data_pub)}**!"
        )
        st.balloons()
        # Limpa os campos para próximo lançamento
        for k_ in ["bp_empresa", "bp_cust", "bp_codigos"]:
            if k_ in st.session_state:
                st.session_state.pop(k_, None)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ----- Painel rápido de status do mês -----
    df_pubs  = st.session_state["publicacoes"]
    meta_ind = st.session_state["meta_mensal"]
    k = calcular_kpis(df_pubs, login=user_atual, ref=today, meta=meta_ind)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(html_kpi(
            "Feito Hoje", fmt_int(
                len(df_pubs[(df_pubs["login"] == user_atual) &
                            (pd.to_datetime(df_pubs["data"]).dt.date == today)])
            ),
            "anúncios registrados hoje",
            SVG_CHECK, "green",
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(html_kpi(
            "Feito no Mês", fmt_int(k["feito"]),
            f'{k["percentual"]:.0f}% da meta de {fmt_int(k["meta"])}',
            SVG_PACKAGE, "purple1",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(html_kpi(
            "Faltam", fmt_int(k["faltantes"]),
            f'{k["dias_uteis_restantes"]} dias úteis restantes',
            SVG_REMAINING, "orange",
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(html_kpi(
            "Ritmo Necessário", fmt_dec(k["media_diaria_alvo"]),
            "anúncios/dia útil para bater a meta",
            SVG_FIRE, "pink",
        ), unsafe_allow_html=True)

    # ----- Últimos 10 registros do funcionário -----
    df_meu = df_pubs[df_pubs["login"] == user_atual].copy()
    if not df_meu.empty:
        df_meu["data"] = pd.to_datetime(df_meu["data"]).dt.date
        # Ordena por data DESC e, dentro de cada data, pelo `_seq` DESC
        # para garantir que os últimos lançados aparecem primeiro mesmo
        # quando muitas linhas compartilham a mesma data.
        sort_cols = ["data"]
        sort_asc  = [False]
        if "_seq" in df_meu.columns:
            sort_cols.append("_seq")
            sort_asc.append(False)
        ultimos = df_meu.sort_values(sort_cols, ascending=sort_asc).head(10)
        linhas = [
            [
                fmt_data(r["data"]),
                f'<b>{r["empresa"]}</b>',
                r["cust_id"] or "—",
                mlb_link(r["mlb"]),
            ]
            for _, r in ultimos.iterrows()
        ]
        render_painel_tabela(
            titulo="🕘 Seus Últimos Lançamentos",
            subtitulo="Os 10 registros mais recentes",
            cabecalhos=["Data", "Empresa", "Cust ID", "MLB"],
            linhas_dados=linhas,
        )


# =============================================================================
# 17. PÁGINA — HISTÓRICO (com filtros)
# -----------------------------------------------------------------------------
# Tabela navegável com todas as publicações + filtros (mês, funcionário,
# empresa, busca por MLB). Visível para admin (vê todos) e funcionário
# (apenas seus próprios — controlado pelo modo).
# =============================================================================
def pagina_historico(escopo: str = "todos"):
    """
    escopo: "todos" (admin) ou "self" (apenas próprio funcionário).
    """
    df_pubs = st.session_state["publicacoes"].copy()
    users   = st.session_state["users"]

    if escopo == "self":
        user_atual = st.session_state["user_atual"]
        df_pubs = df_pubs[df_pubs["login"] == user_atual]
        titulo = "Meu Histórico"
        subtitulo = "Todas as publicações que você já registrou no sistema"
    else:
        titulo = "Histórico"
        subtitulo = "Visão completa de todas as publicações da equipe"

    render_page_header(titulo, subtitulo)

    if df_pubs.empty:
        st.markdown(
            '<div class="empty-msg">'
                '<span class="ico">📭</span>'
                '<b>Nenhuma publicação registrada.</b><br>'
                'Use a página "Publicações" para começar a registrar seus anúncios.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    df_pubs["data"] = pd.to_datetime(df_pubs["data"]).dt.date

    # ----- Filtros -----
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    if escopo == "todos":
        cols = st.columns([1.2, 1.2, 1.6, 1.6])
    else:
        cols = st.columns([1.2, 1.6, 1.6])

    # Lista de meses presentes nos dados (mais recente primeiro)
    meses_pres = sorted(
        {(d.year, d.month) for d in df_pubs["data"]},
        reverse=True,
    )
    opcoes_mes = ["Todos os meses"] + [
        f"{MESES_PT[m]} / {y}" for y, m in meses_pres
    ]

    with cols[0]:
        sel_mes = st.selectbox("Mês", opcoes_mes, key=f"hist_mes_{escopo}")

    idx_offset = 0
    if escopo == "todos":
        with cols[1]:
            opcoes_func = ["Todos os funcionários"] + [
                users[u]["nome"] for u in users if users[u]["role"] == "employee"
            ]
            sel_func = st.selectbox("Funcionário", opcoes_func,
                                     key=f"hist_func_{escopo}")
        idx_offset = 1
    else:
        sel_func = "Todos os funcionários"

    with cols[1 + idx_offset]:
        empresas_unicas = sorted(df_pubs["empresa"].dropna().unique().tolist())
        sel_empresa = st.selectbox(
            "Empresa",
            ["Todas as empresas"] + empresas_unicas,
            key=f"hist_emp_{escopo}",
        )
    with cols[2 + idx_offset]:
        sel_busca = st.text_input(
            "🔎 Buscar (MLB ou empresa)",
            placeholder="Digite para filtrar...",
            key=f"hist_busca_{escopo}",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ----- Aplica filtros -----
    df_filt = df_pubs.copy()

    if sel_mes != "Todos os meses":
        # Ex: "Setembro / 2025"
        nome_mes_sel, _, ano_sel = sel_mes.split()
        ano_sel = int(ano_sel)
        # Reverse-lookup do número do mês
        num_mes = next(num for num, n in MESES_PT.items() if n == nome_mes_sel)
        df_filt = df_filt[df_filt["data"].apply(
            lambda d: d.year == ano_sel and d.month == num_mes
        )]

    if sel_func != "Todos os funcionários":
        login_sel = next(u for u in users if users[u]["nome"] == sel_func)
        df_filt = df_filt[df_filt["login"] == login_sel]

    if sel_empresa != "Todas as empresas":
        df_filt = df_filt[df_filt["empresa"] == sel_empresa]

    if sel_busca:
        termo = sel_busca.strip().upper()
        mask = (
            df_filt["mlb"].str.contains(termo, case=False, na=False) |
            df_filt["empresa"].str.contains(termo, case=False, na=False) |
            df_filt["cust_id"].str.contains(termo, case=False, na=False)
        )
        df_filt = df_filt[mask]

    # KPI compacto da seleção
    n_total = len(df_filt)
    n_empresas = df_filt["empresa"].nunique()
    n_mlbs_unicos = df_filt["mlb"].nunique()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(html_kpi(
            "Registros na seleção", fmt_int(n_total),
            f"de {fmt_int(len(df_pubs))} no total",
            SVG_PACKAGE, "purple1",
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(html_kpi(
            "Empresas únicas", fmt_int(n_empresas),
            "lojas atendidas",
            SVG_USER, "pink",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(html_kpi(
            "MLBs únicos", fmt_int(n_mlbs_unicos),
            "códigos distintos",
            SVG_TARGET, "orange",
        ), unsafe_allow_html=True)

    # Tabela paginada (mostra primeiras 200 e oferece download CSV)
    sort_cols = ["data"]
    sort_asc  = [False]
    if "_seq" in df_filt.columns:
        sort_cols.append("_seq")
        sort_asc.append(False)
    df_show = df_filt.sort_values(sort_cols, ascending=sort_asc).head(200)
    linhas = []
    for _, r in df_show.iterrows():
        nome_func = users.get(r["login"], {}).get("nome", r["login"])
        linhas.append([
            fmt_data(r["data"]),
            f'<b>{nome_func}</b>' if escopo == "todos" else f'<b>{r["empresa"]}</b>',
            r["empresa"] if escopo == "todos" else (r["cust_id"] or "—"),
            r["cust_id"] or "—" if escopo == "todos" else "",
            mlb_link(r["mlb"]),
        ])

    if escopo == "todos":
        cabecalhos = ["Data", "Funcionário", "Empresa", "Cust ID", "MLB"]
    else:
        # No modo self, removemos as colunas vazias
        linhas = [[l[0], l[1], l[2], l[4]] for l in linhas]
        cabecalhos = ["Data", "Empresa", "Cust ID", "MLB"]

    sub = (
        f"Mostrando {len(df_show)} de {fmt_int(n_total)} registros"
        + (f" (filtro reduzido — exporte para ver todos)" if n_total > 200 else "")
    )

    # Botão de download CSV (visível também na header da tabela)
    csv_bytes = df_filt.drop(columns=["id"]).to_csv(
        index=False, encoding="utf-8-sig"
    ).encode("utf-8-sig")
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    col_dl, _ = st.columns([1, 4])
    with col_dl:
        st.download_button(
            "⬇️ Exportar CSV",
            data=csv_bytes,
            file_name=f"publicacoes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"dl_{escopo}",
        )

    render_painel_tabela(
        titulo="📋 Registros",
        subtitulo=sub,
        cabecalhos=cabecalhos,
        linhas_dados=linhas,
    )


# =============================================================================
# 18. PÁGINA — MEU PERFIL (FUNCIONÁRIO)
# -----------------------------------------------------------------------------
# Permite ao funcionário editar nome de exibição, foto e senha.
# =============================================================================
def pagina_meu_perfil():
    user_atual = st.session_state["user_atual"]
    user = st.session_state["users"][user_atual]

    render_page_header("Meu Perfil", "Atualize seus dados pessoais e foto")

    # Visualização atual + form
    col_avatar, col_form = st.columns([1, 2])

    with col_avatar:
        st.markdown(
            '<div class="panel" style="text-align:center;">'
                f'{html_avatar(user_atual, 140)}'
                f'<div class="func-nome" style="font-size:20px; margin-top:6px;">{user["nome"]}</div>'
                f'<div class="func-cargo">{user["cargo"]}</div>'
                f'<div style="color:{COR["txt_terciario"]}; font-size:12px; margin-top:4px;">@{user_atual}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with col_form:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(
            '<h3 class="panel-title">Editar dados</h3>'
            '<div class="panel-subtitle">Suas alterações ficam salvas durante a sessão</div>'
            '<div style="height:14px;"></div>',
            unsafe_allow_html=True,
        )

        novo_nome = st.text_input("Nome de exibição",
                                   value=user["nome"], key="perf_nome")
        novo_email = st.text_input("E-mail",
                                    value=user.get("email", ""), key="perf_email")
        nova_foto = st.file_uploader(
            "Atualizar foto de perfil (PNG ou JPG)",
            type=["png", "jpg", "jpeg"],
            key="perf_foto",
        )

        st.markdown(
            '<div style="margin: 14px 0 8px 0; color:#94a3b8; font-size:13px;">'
            '🔒 <b>Trocar de senha</b> (opcional)'
            '</div>',
            unsafe_allow_html=True,
        )
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            senha_atual = st.text_input("Senha atual", type="password",
                                         key="perf_senha_atual")
        with col_s2:
            nova_senha = st.text_input("Nova senha", type="password",
                                        key="perf_senha_nova")

        if st.button("💾 Salvar alterações", type="primary",
                     use_container_width=True, key="perf_save"):
            erros = []
            # Monta dict com tudo que mudou para enviar de uma vez ao Supabase
            updates_supabase = {}

            # ── Nome ───────────────────────────────────────────────────────────
            if novo_nome.strip() and novo_nome.strip() != user["nome"]:
                updates_supabase["nome"] = novo_nome.strip()

            # ── Email ──────────────────────────────────────────────────────────
            if novo_email.strip() != (user.get("email") or ""):
                updates_supabase["email"] = novo_email.strip()

            # ── Foto (precisa da coluna foto_b64 na tabela usuarios) ──────────
            nova_foto_b64 = None
            if nova_foto is not None:
                try:
                    nova_foto_b64 = arquivo_para_data_uri(nova_foto)
                    updates_supabase["foto_b64"] = nova_foto_b64
                except Exception as e:
                    erros.append(f"Erro ao processar foto: {e}")

            # ── Persiste mudanças (nome/email/foto) no Supabase ───────────────
            if updates_supabase:
                try:
                    supabase.table("usuarios") \
                        .update(updates_supabase) \
                        .eq("login", user_atual) \
                        .execute()
                    # Atualiza cache local SOMENTE após sucesso no banco
                    if "nome" in updates_supabase:
                        user["nome"] = updates_supabase["nome"]
                    if "email" in updates_supabase:
                        user["email"] = updates_supabase["email"]
                    if "foto_b64" in updates_supabase:
                        user["foto_b64"] = updates_supabase["foto_b64"]
                except Exception as e:
                    msg = str(e)
                    if "foto_b64" in msg or "column" in msg.lower():
                        erros.append(
                            "A coluna `foto_b64` não existe na tabela `usuarios`. "
                            "Rode no SQL Editor: "
                            "`ALTER TABLE usuarios ADD COLUMN foto_b64 TEXT;`"
                        )
                    else:
                        erros.append(f"Erro ao salvar no Supabase: {e}")

            # ── Senha (fluxo separado, com validação) ─────────────────────────
            if nova_senha:
                if senha_atual != user["senha"]:
                    erros.append("Senha atual incorreta.")
                elif len(nova_senha) < 3:
                    erros.append("A nova senha precisa de pelo menos 3 caracteres.")
                else:
                    try:
                        supabase.table("usuarios") \
                            .update({"senha": nova_senha}) \
                            .eq("login", user_atual) \
                            .execute()
                        user["senha"] = nova_senha
                    except Exception as e:
                        erros.append(f"Erro ao salvar nova senha: {e}")

            if erros:
                for e in erros:
                    st.error(e)
            else:
                st.success("✅ Perfil atualizado com sucesso!")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# =============================================================================
# 19. PÁGINA — CONFIGURAÇÕES (ADMIN)
# -----------------------------------------------------------------------------
# Permite ao admin alterar a meta global e (futuramente) cadastrar/remover
# funcionários. Para o protótipo, foco na meta.
# =============================================================================
def pagina_configuracoes():
    render_page_header(
        "Configurações",
        "Parâmetros globais do sistema",
    )

    users = st.session_state["users"]
    funcionarios = [u for u in users if users[u]["role"] == "employee"]

    # Card 1: meta mensal
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(
        '<h3 class="panel-title">🎯 Meta Mensal Individual</h3>'
        '<div class="panel-subtitle">Quantidade de anúncios que cada funcionário deve publicar por mês</div>'
        '<div style="height:14px;"></div>',
        unsafe_allow_html=True,
    )

    col_m, col_info = st.columns([1, 2])
    with col_m:
        nova_meta = st.number_input(
            "Meta (anúncios/mês)",
            min_value=10,
            max_value=2000,
            value=int(st.session_state["meta_mensal"]),
            step=10,
            key="cfg_meta",
        )
        if st.button("💾 Atualizar meta", type="primary",
                     use_container_width=True, key="cfg_save_meta"):
            st.session_state["meta_mensal"] = int(nova_meta)
            st.success(f"Meta atualizada para {fmt_int(nova_meta)} anúncios/mês.")
            st.rerun()
    with col_info:
        st.markdown(
            '<div class="insight-box" style="margin-top:0;">'
                '<div class="row">'
                    '<div class="lbl">Meta atual por funcionário</div>'
                    f'<div class="val green">{fmt_int(st.session_state["meta_mensal"])}</div>'
                '</div>'
                '<div class="row">'
                    '<div class="lbl">Funcionários ativos</div>'
                    f'<div class="val">{len(funcionarios)}</div>'
                '</div>'
                '<div class="row">'
                    '<div class="lbl">Meta da equipe (consolidada)</div>'
                    f'<div class="val green">{fmt_int(st.session_state["meta_mensal"] * len(funcionarios))}</div>'
                '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 2: cadastro de novo usuário
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(
        '<h3 class="panel-title">➕ Cadastrar Novo Usuário</h3>'
        '<div class="panel-subtitle">O novo usuário poderá fazer login imediatamente após o cadastro</div>'
        '<div style="height:14px;"></div>',
        unsafe_allow_html=True,
    )
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        new_login = st.text_input("Login (único)", placeholder="ex: joao",
                                  key="cfg_new_login").strip().lower()
    with col_b:
        new_nome = st.text_input("Nome completo", placeholder="ex: João Silva",
                                 key="cfg_new_nome").strip()
    with col_c:
        new_perfil = st.selectbox("Perfil", ["employee", "admin"],
                                  format_func=lambda x: "Funcionário" if x == "employee" else "Administrador",
                                  key="cfg_new_perfil")
    with col_d:
        new_senha = st.text_input("Senha inicial", value=SENHA_PADRAO,
                                  key="cfg_new_senha")

    if st.button("✅ Cadastrar usuário", type="primary", key="cfg_btn_new_user"):
        if not new_login:
            st.error("O campo Login é obrigatório.")
        elif not new_nome:
            st.error("O campo Nome é obrigatório.")
        elif len(new_senha) < 3:
            st.error("A senha deve ter pelo menos 3 caracteres.")
        elif new_login in st.session_state["users"]:
            st.error(f"O login **{new_login}** já existe. Escolha outro.")
        else:
            try:
                supabase.table("usuarios").insert({
                    "login":  new_login,
                    "nome":   new_nome,
                    "senha":  new_senha,
                    "perfil": new_perfil,
                }).execute()
                # Atualiza cache local
                st.session_state["users"][new_login] = {
                    "nome":     new_nome,
                    "cargo":    "Gestor" if new_perfil == "admin" else "Anunciante MLB",
                    "role":     new_perfil,
                    "senha":    new_senha,
                    "email":    "",
                    "foto_b64": None,
                }
                st.success(
                    f"✅ Usuário **{new_nome}** (@{new_login}) cadastrado com sucesso!"
                )
                st.rerun()
            except Exception as e:
                # Supabase retorna erro 409 se a PK (login) já existe
                msg = str(e)
                if "duplicate" in msg.lower() or "unique" in msg.lower() or "409" in msg:
                    st.error(
                        f"O login **{new_login}** já existe no banco de dados. Escolha outro."
                    )
                else:
                    st.error(f"Erro ao cadastrar usuário: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 3: usuários cadastrados (somente leitura)
    linhas = []
    for login in sorted(users.keys()):
        u = users[login]
        n_pub = int((st.session_state["publicacoes"]["login"] == login).sum())
        linhas.append([
            f'<b>{u["nome"]}</b><br><span style="color:{COR["txt_terciario"]}; font-size:11px;">@{login}</span>',
            "Administrador" if u["role"] == "admin" else u.get("cargo", "-"),
            u.get("email", "—"),
            fmt_int(n_pub),
        ])
    render_painel_tabela(
        titulo="👥 Usuários do Sistema",
        subtitulo=f"{len(users)} usuários cadastrados (alterações de senha podem ser feitas pelo próprio usuário)",
        cabecalhos=["Nome", "Cargo", "E-mail", "Publicações"],
        linhas_dados=linhas,
    )

    # Card 3: estatísticas gerais do banco
    df = st.session_state["publicacoes"]
    if not df.empty:
        primeira_data = pd.to_datetime(df["data"]).min().date()
        ultima_data   = pd.to_datetime(df["data"]).max().date()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(html_kpi(
                "Total de Publicações", fmt_int(len(df)),
                "no histórico completo",
                SVG_PACKAGE, "purple1",
            ), unsafe_allow_html=True)
        with c2:
            st.markdown(html_kpi(
                "Empresas Únicas", fmt_int(df["empresa"].nunique()),
                "lojas registradas",
                SVG_USER, "pink",
            ), unsafe_allow_html=True)
        with c3:
            st.markdown(html_kpi(
                "Primeira Data", fmt_data(primeira_data),
                "início do histórico",
                SVG_CALENDAR, "purple2",
            ), unsafe_allow_html=True)
        with c4:
            st.markdown(html_kpi(
                "Última Data", fmt_data(ultima_data),
                "registro mais recente",
                SVG_CALENDAR, "orange",
            ), unsafe_allow_html=True)


# =============================================================================
# 18. ROTEAMENTO PRINCIPAL
# =============================================================================
def main():
    """Ponto de entrada da aplicação.

    Estrutura do fluxo:
      1) Inicializa session_state (usuários, dados históricos, flags).
      2) Se o usuário não está autenticado, mostra a tela de login e encerra.
      3) Aplica o CSS global, renderiza a sidebar e captura a página
         selecionada no menu.
      4) Reseta `perfil_visualizando` sempre que o admin troca de página
         (caso contrário ficaria preso no perfil de um funcionário ao clicar
         em outra opção do menu).
      5) Despacha para a função de página correspondente, respeitando o
         RBAC (admin vs employee) e o escopo de cada página.
    """
    # 1) Estado inicial — só roda uma vez por sessão (controle interno
    #    via flag em init_session_state).
    init_session_state()

    # 2) Bloqueio de acesso — sem login válido, não passa daqui.
    if not st.session_state.get("logado", False):
        tela_login()
        return

    # 3) CSS global + navegação. O CSS precisa ser reaplicado a cada rerun
    #    porque o Streamlit re-renderiza tudo do zero.
    aplicar_css_global()
    pagina = render_sidebar()

    # 4) Detecta troca de página. Quando o admin abre o perfil de um
    #    funcionário (clicando em "Ver detalhes" na tela Equipe), o app
    #    salva o login em session_state["perfil_visualizando"]. Se ele
    #    em seguida clica em outra opção do menu, precisamos limpar essa
    #    flag — caso contrário a navegação ficaria "presa" no perfil.
    pagina_anterior = st.session_state.get("__pagina_atual")
    if pagina_anterior != pagina:
        st.session_state["__pagina_atual"] = pagina
        if pagina != "Equipe":
            st.session_state["perfil_visualizando"] = None

    user = st.session_state["users"][st.session_state["user_atual"]]
    is_admin = user["role"] == "admin"

    # 5) Despacho. As páginas admin e employee são totalmente disjuntas;
    #    os menus são renderizados de forma diferente em render_sidebar(),
    #    então em condições normais nunca caímos no else final.
    if is_admin:
        if pagina == "Controle Geral":
            pagina_controle_geral()
        elif pagina == "Equipe":
            pagina_equipe()
        elif pagina == "Histórico":
            pagina_historico(escopo="todos")
        elif pagina == "Configurações":
            pagina_configuracoes()
        else:
            pagina_controle_geral()
    else:
        if pagina == "Meu Painel":
            pagina_meu_painel()
        elif pagina == "Publicações":
            pagina_bater_ponto()
        elif pagina == "Meu Histórico":
            pagina_historico(escopo="self")
        elif pagina == "Meu Perfil":
            pagina_meu_perfil()
        else:
            pagina_meu_painel()


if __name__ == "__main__":
    main()
