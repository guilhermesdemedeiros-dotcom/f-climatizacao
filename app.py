import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import quote
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import copy
import uuid
import time
import hmac
import hashlib
import re
import secrets
from datetime import date, timedelta, time as horario_time
from contextlib import contextmanager

try:
    from streamlit_local_storage import LocalStorage
except Exception:
    LocalStorage = None

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Path as RLPath, Rect, Circle, Line

# =========================================================
# PÁGINA
# =========================================================

st.set_page_config(
    page_title="F Climatização",
    page_icon="F",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CONSTANTES
# =========================================================

OWNER = "guilhermesdemedeiros-dotcom"
CONFIG_REPO = "f-climatizacao"
DATA_REPO = st.secrets.get("DATA_GITHUB_REPO", "f-climatizacao-dados")
BRANCH = "main"

CONFIG_FILE = "config.json"
BUDGETS_FILE = "orcamentos.json"
FINANCE_FILE = "financeiro.json"
BUDGET_META_FILE = "orcamentos_meta.json"
AGENDA_FILE = "agenda_disponibilidade.json"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
ADMIN_KEY = st.secrets.get("ADMIN_KEY", "")

CAPACIDADES = ["9.000 BTUs", "12.000 BTUs", "18.000 BTUs", "24.000 BTUs"]
TIPOS_AR = ["Inverter", "Convencional"]
UNIDADES_ITEM = ["unidade", "metro", "km", "serviço", "equipamento"]
FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")

REFERENCIA_AREA = {
    "9.000 BTUs": "até 12 m²",
    "12.000 BTUs": "13 a 19 m²",
    "18.000 BTUs": "20 a 27 m²",
    "24.000 BTUs": "28 a 37 m²",
}

BTU_NUM = {
    "9.000 BTUs": 9000,
    "12.000 BTUs": 12000,
    "18.000 BTUs": 18000,
    "24.000 BTUs": 24000,
}

AREA_MIN_BTU = {
    "Até 12 m²": 9000,
    "13 a 19 m²": 12000,
    "20 a 27 m²": 18000,
    "28 a 37 m²": 24000,
}

OPCOES_AREA = [
    "Não sei",
    "Até 12 m²",
    "13 a 19 m²",
    "20 a 27 m²",
    "28 a 37 m²",
    "Acima de 37 m²",
]

# =========================================================
# VISUAL
# =========================================================

st.markdown(
    """
<style>
:root{
  --bg:#07090d;
  --card:#0e141e;
  --card2:#111a27;
  --border:#26354a;
  --blue:#0878e8;
  --blue2:#0f9fff;
  --navy:#05275d;
  --orange:#ff7a00;
  --white:#ffffff;
  --muted:#9caec4;
}
html,body,[class*="css"]{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
.stApp{
  background:
    radial-gradient(circle at top right,rgba(8,120,232,.13),transparent 28%),
    radial-gradient(circle at top left,rgba(255,122,0,.05),transparent 22%),
    linear-gradient(180deg,#07090d 0%,#090d14 55%,#07090d 100%);
  color:#fff;
}
#MainMenu, footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{
  max-width:780px;
  padding-top:.8rem;
  padding-left:1rem;
  padding-right:1rem;
  padding-bottom:4rem;
}
h1,h2,h3,h4,h5,h6,p,label,span{color:#fff;}
div[data-testid="stCaptionContainer"] p{color:var(--muted)!important;}
.brand-shell{
  display:flex;
  align-items:center;
  gap:13px;
  background:linear-gradient(135deg,#05275d 0%,#0878e8 120%);
  border:1px solid rgba(35,160,255,.35);
  border-radius:21px;
  padding:13px 16px;
  box-shadow:0 12px 30px rgba(0,0,0,.28);
  margin-bottom:10px;
}
.brand-logo{
  width:60px;height:60px;object-fit:contain;flex:0 0 60px;
}
.brand-name{font-size:21px;font-weight:900;line-height:1.05;color:#fff;}
.brand-sub{font-size:12.5px;color:#d4e5fa;margin-top:5px;}
.brand-admin{font-size:11px;color:#ff9a25;font-weight:800;letter-spacing:.8px;margin-bottom:3px;}
.quick-row{
  display:flex;gap:10px;flex-wrap:wrap;margin:7px 0 15px 0;
}
.quick-chip{
  display:inline-flex;align-items:center;gap:7px;
  border:1px solid #26354a;background:#0e141e;
  color:#cbd8e9!important;text-decoration:none!important;
  border-radius:999px;padding:8px 12px;font-size:12px;font-weight:650;
}
.quick-chip:hover{border-color:#0878e8;}
.section-wrap{margin-top:25px;margin-bottom:11px;}
.section-title{font-size:20px;font-weight:900;color:#fff;line-height:1.2;}
.section-sub{font-size:13px;color:#91a3b9;margin-top:4px;line-height:1.4;}
/* Navegação administrativa compacta com ícones e sinalização azul */
div[data-testid="stTabs"] [data-baseweb="tab-list"]{
  display:flex!important;
  gap:7px!important;
  overflow-x:auto!important;
  scrollbar-width:thin;
  padding:7px 3px 12px!important;
  border-bottom:1px solid #27384e;
}
div[data-testid="stTabs"] button[role="tab"]{
  background:#111b29!important;
  border:1px solid #2a3c54!important;
  border-radius:12px!important;
  color:#cbdcf0!important;
  font-size:12px!important;
  font-weight:750!important;
  padding:9px 13px!important;
  min-height:43px!important;
  white-space:nowrap!important;
  flex:0 0 auto!important;
  transition:background .15s ease,border-color .15s ease;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{
  background:linear-gradient(125deg,#064a93,#0878e8)!important;
  border-color:#36a7ff!important;
  color:#fff!important;
  box-shadow:0 5px 15px rgba(8,120,232,.24);
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:transparent!important;}
.section-wrap-pro{
  padding:11px 13px;
  border:1px solid #233c56;
  border-left:3px solid #0f9fff;
  border-radius:14px;
  background:linear-gradient(115deg,rgba(9,51,98,.32),rgba(14,20,30,.5));
}
.section-heading-row{display:flex;align-items:center;gap:12px;}
.section-heading-text{min-width:0;flex:1;}
.section-icon{
  display:flex;align-items:center;justify-content:center;
  flex:0 0 39px;width:39px;height:39px;
  border:1px solid rgba(58,162,244,.32);
  border-radius:12px;background:#122c4b;
  font-size:19px;line-height:1;
}
@media(max-width:600px){
  div[data-testid="stTabs"] button[role="tab"]{font-size:11.5px!important;padding:8px 10px!important;}
  .section-wrap-pro{padding:10px;}
  .section-icon{width:35px;height:35px;flex-basis:35px;font-size:17px;}
}
.info-card{
  background:linear-gradient(135deg,rgba(8,120,232,.17),rgba(14,20,30,.98));
  border:1px solid rgba(8,120,232,.4);
  border-left:4px solid #0878e8;
  border-radius:17px;padding:15px;margin:12px 0;
}
.orange-card{
  background:linear-gradient(135deg,rgba(255,122,0,.10),rgba(14,20,30,.98));
  border:1px solid rgba(255,122,0,.32);
  border-left:4px solid #ff7a00;
  border-radius:17px;padding:15px;margin:12px 0;
}
.card-title{font-weight:850;font-size:15px;color:#fff;margin-bottom:4px;}
.card-text{font-size:13px;color:#9caec4;line-height:1.5;}
div[data-testid="stWidgetLabel"] p{color:#fff!important;font-weight:650!important;}
div[data-testid="stRadio"]{
  background:#0e141e;border:1px solid #26354a;border-radius:16px;padding:11px 13px;
}
div[data-testid="stCheckbox"]{
  background:#0e141e;border:1px solid #223147;border-radius:12px;padding:6px 9px;margin-bottom:5px;
}
div[data-baseweb="select"]>div,
div[data-baseweb="input"]>div,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
textarea{
  background:#111824!important;
  border-color:#2b3a50!important;
  border-radius:13px!important;
  color:#fff!important;
}
input,textarea{color:#fff!important;caret-color:#ff7a00!important;}
input::placeholder,textarea::placeholder{color:#6f8197!important;}
ul[role="listbox"]{background:#111824!important;}
li[role="option"]{color:#fff!important;}
div[data-baseweb="tag"]{background:#0878e8!important;}
.stButton>button{
  width:100%;min-height:48px;border-radius:14px;font-weight:800;
  background:#111824;color:#fff;border:1px solid #2b3a50;
}
.stButton>button:hover{border-color:#0878e8;color:#fff;}
.stButton>button[kind="primary"]{
  background:linear-gradient(90deg,#0758b9,#0878e8);
  border:1px solid #1891ff;color:#fff;
  box-shadow:0 8px 19px rgba(8,120,232,.20);
}
.stLinkButton>a{
  border-radius:14px!important;min-height:48px!important;font-weight:800!important;
}
div[data-testid="stMetric"]{
  background:linear-gradient(135deg,rgba(8,120,232,.16),#0e141e);
  border:1px solid rgba(8,120,232,.38);border-radius:17px;padding:15px;
}
div[data-testid="stExpander"]{
  background:#0e141e;border:1px solid #26354a;border-radius:14px;overflow:hidden;
}
button[data-baseweb="tab"]{font-weight:750;color:#9aabc0!important;}
button[data-baseweb="tab"][aria-selected="true"]{color:#fff!important;}
div[data-baseweb="tab-highlight"]{background:#ff7a00!important;}
hr{border-color:#243147!important;}
.footer-box{
  margin-top:34px;padding-top:18px;border-top:1px solid #202c3d;text-align:center;
  color:#72849a;font-size:11px;
}
.budget-number{
  display:inline-block;background:#ff7a00;color:#fff;font-weight:900;
  padding:5px 10px;border-radius:999px;font-size:12px;margin-bottom:8px;
}
.capacity-ok{
  color:#45d483;
  font-size:12px;
  font-weight:750;
  margin-top:6px;
  line-height:1.35;
}
.capacity-warn{
  color:#ffad42;
  font-size:12px;
  font-weight:750;
  margin-top:6px;
  line-height:1.35;
}
.capacity-note{
  color:#8294aa;
  font-size:10.5px;
  margin-top:4px;
  line-height:1.35;
}
.finance-hero{
  background:
    linear-gradient(135deg,rgba(8,120,232,.30),rgba(5,39,93,.96) 58%,rgba(255,122,0,.14));
  border:1px solid rgba(24,145,255,.45);
  border-radius:22px;
  padding:18px;
  margin:8px 0 16px 0;
}
.finance-kicker{
  color:#8fc9ff;
  font-size:11px;
  font-weight:800;
  letter-spacing:.12em;
  text-transform:uppercase;
}
.finance-title{
  color:#fff;
  font-size:24px;
  font-weight:950;
  margin-top:3px;
  line-height:1.1;
}
.finance-sub{
  color:#c4d7eb;
  font-size:12.5px;
  margin-top:7px;
  line-height:1.45;
}
.finance-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:10px;
  margin:10px 0 16px 0;
}
.finance-card{
  background:linear-gradient(145deg,#0f1723,#111d2d);
  border:1px solid #263a54;
  border-radius:17px;
  padding:13px;
  min-width:0;
}
.finance-card-label{
  color:#8ca0b7;
  font-size:10.5px;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.06em;
}
.finance-card-value{
  color:#fff;
  font-size:20px;
  font-weight:900;
  margin-top:4px;
  overflow-wrap:anywhere;
}
.finance-card-value.positive{color:#45d483;}
.finance-card-value.orange{color:#ff9a36;}
.finance-card-value.blue{color:#54b4ff;}
.finance-bar-row{
  margin:10px 0;
}
.finance-bar-head{
  display:flex;
  justify-content:space-between;
  gap:10px;
  font-size:11px;
  color:#c7d3e2;
  margin-bottom:5px;
}
.finance-bar-track{
  width:100%;
  height:9px;
  background:#111824;
  border:1px solid #24344a;
  border-radius:999px;
  overflow:hidden;
}
.finance-bar-fill{
  height:100%;
  border-radius:999px;
  background:linear-gradient(90deg,#0878e8,#18a0fb);
}
.finance-pay{
  background:#0e141e;
  border:1px solid #26354a;
  border-left:4px solid #ff7a00;
  border-radius:14px;
  padding:11px 12px;
  margin:8px 0;
}
.finance-pay-name{
  color:#fff;
  font-size:12px;
  font-weight:800;
}
.finance-pay-meta{
  color:#8fa2b8;
  font-size:10.5px;
  margin-top:3px;
}
@media(max-width:520px){
  .finance-grid{grid-template-columns:1fr 1fr;}
  .finance-card-value{font-size:18px;}
}
.equipment-option{
  background:#0e141e;
  border:1px solid #26354a;
  border-left:4px solid #0878e8;
  border-radius:14px;
  padding:11px 13px;
  margin:8px 0;
}
.equipment-option-name{
  color:#fff;
  font-weight:800;
  font-size:13px;
  line-height:1.3;
}
.equipment-option-price{
  color:#45d483;
  font-weight:900;
  font-size:14px;
  margin-top:4px;
}
.equipment-option-total{
  color:#9caec4;
  font-size:11px;
  margin-top:3px;
}
@media(max-width:600px){
  .block-container{padding-left:.85rem;padding-right:.85rem;}
  .brand-logo{width:48px;height:48px;flex-basis:48px;}
  .brand-name{font-size:18px;}
  .section-title{font-size:18px;}
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# CONFIGURAÇÃO PADRÃO
# =========================================================

DEFAULT_CONFIG = {
    "empresa": {
        "nome": "F Climatização",
        "slogan": "Seu ambiente na temperatura ideal",
        "whatsapp": "5555999999999",
        "local_atendimento": "Não-Me-Toque/RS",
        "texto_atendimento": "Atendimento em Não-Me-Toque e região",
        "endereco": "",
        "cnpj": "",
    },
    "servicos": {
        "Instalação": {
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Instalação de ar-condicionado até 2 metros de linha. Materiais são cobrados separadamente quando necessários.",
            "precos": {
                "9.000 BTUs": 280.0,
                "12.000 BTUs": 280.0,
                "18.000 BTUs": 350.0,
                "24.000 BTUs": 400.0,
            },
        },
        "Carga de gás": {
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Carga de gás refrigerante conforme capacidade do equipamento.",
            "precos": {
                "9.000 BTUs": 280.0,
                "12.000 BTUs": 280.0,
                "18.000 BTUs": 400.0,
                "24.000 BTUs": 480.0,
            },
        },
        "Desinstalação": {
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Desinstalação do equipamento.",
            "precos": {
                "9.000 BTUs": 120.0,
                "12.000 BTUs": 120.0,
                "18.000 BTUs": 160.0,
                "24.000 BTUs": 200.0,
            },
        },
        "Higienização": {
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Limpeza e higienização do aparelho.",
            "precos": {
                "9.000 BTUs": 0.0,
                "12.000 BTUs": 0.0,
                "18.000 BTUs": 0.0,
                "24.000 BTUs": 0.0,
            },
        },
    },
    "materiais": {
        'Tubo de cobre 1/4"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        'Tubo de cobre 3/8"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        'Tubo de cobre 1/2"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        'Tubo de cobre 5/8"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        'Tubo de cobre 3/4"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        "Canaleta": {"unidade": "metro", "preco": 0.0, "ativo": True},
        "Cabo elétrico": {"unidade": "metro", "preco": 0.0, "ativo": True},
        "Mangueira de dreno": {"unidade": "metro", "preco": 0.0, "ativo": True},
        "Suporte para condensadora": {"unidade": "unidade", "preco": 0.0, "ativo": True},
    },
    "equipamentos": {},
    "regras": {
        "adicional_apartamento_2_mais": 0.0,
        "texto_variacao": "Esta é uma estimativa inicial. O valor final pode variar conforme materiais necessários, acesso, altura, condições do local e avaliação técnica.",
        "texto_equipamento": "O valor do equipamento é uma referência aproximada e pode variar conforme disponibilidade e cotação do fornecedor no dia. O valor final será confirmado antes do fechamento.",
    },
}

# =========================================================
# FUNÇÕES GERAIS
# =========================================================

def dinheiro(valor):
    valor = float(valor or 0)
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def completar_dict(base, padrao):
    if not isinstance(base, dict):
        return copy.deepcopy(padrao)
    out = copy.deepcopy(base)
    for k, v in padrao.items():
        if k not in out:
            out[k] = copy.deepcopy(v)
        elif isinstance(v, dict):
            out[k] = completar_dict(out[k], v)
    return out


def migrar_config(dados):
    """
    Completa somente a estrutura necessária sem recriar itens de catálogo
    que o administrador renomeou ou excluiu.

    Serviços, materiais e aparelhos são catálogos editáveis:
    se já existem no config.json, o conteúdo salvo pelo ADM é respeitado.
    """
    if not isinstance(dados, dict):
        return copy.deepcopy(DEFAULT_CONFIG)

    dados = copy.deepcopy(dados)

    # -----------------------------------------------------
    # EMPRESA E REGRAS: podem receber novos campos padrão
    # -----------------------------------------------------
    dados["empresa"] = completar_dict(
        dados.get("empresa", {}),
        DEFAULT_CONFIG["empresa"],
    )
    dados["regras"] = completar_dict(
        dados.get("regras", {}),
        DEFAULT_CONFIG["regras"],
    )

    # -----------------------------------------------------
    # SERVIÇOS: só usa os padrões se o catálogo inteiro
    # ainda não existir. Nunca recria um serviço excluído.
    # -----------------------------------------------------
    if "servicos" not in dados or not isinstance(dados.get("servicos"), dict):
        dados["servicos"] = copy.deepcopy(DEFAULT_CONFIG["servicos"])

    dados["servicos"].pop("Reinstalação", None)
    dados["servicos"].pop("Manutenção", None)

    servicos_normalizados = {}

    for nome, servico in dados.get("servicos", {}).items():
        if not isinstance(servico, dict):
            servico = {}

        item = copy.deepcopy(servico)
        item.setdefault("ativo", True)
        item.setdefault("mostrar_cliente", True)
        item.setdefault("descricao", "")
        item.setdefault("precos", {})

        if not isinstance(item["precos"], dict):
            item["precos"] = {}

        # Apenas garante que as capacidades existam.
        # Não substitui 0 por preço padrão.
        for cap in CAPACIDADES:
            item["precos"].setdefault(cap, 0.0)

        servicos_normalizados[nome] = item

    dados["servicos"] = servicos_normalizados

    # -----------------------------------------------------
    # MATERIAIS: preserva exatamente exclusões/renomes.
    # Padrões entram somente se nunca houve catálogo.
    # -----------------------------------------------------
    if "materiais" not in dados or not isinstance(dados.get("materiais"), dict):
        dados["materiais"] = copy.deepcopy(DEFAULT_CONFIG["materiais"])

    materiais_normalizados = {}

    for nome, material in dados.get("materiais", {}).items():
        if not isinstance(material, dict):
            material = {}

        item = copy.deepcopy(material)
        item.setdefault("unidade", "unidade")
        item.setdefault("preco", 0.0)
        item.setdefault("ativo", True)

        materiais_normalizados[nome] = item

    dados["materiais"] = materiais_normalizados

    # -----------------------------------------------------
    # APARELHOS: preserva catálogo atual e migra formato
    # antigo quando necessário.
    # -----------------------------------------------------
    if "equipamentos" not in dados or not isinstance(dados.get("equipamentos"), dict):
        dados["equipamentos"] = {}

    novos = {}

    for chave, eq in dados.get("equipamentos", {}).items():
        if not isinstance(eq, dict):
            continue

        eq2 = copy.deepcopy(eq)
        eq2.setdefault("id", chave)
        eq2.setdefault("marca", "")
        eq2.setdefault("capacidade", "9.000 BTUs")
        eq2.setdefault("tipo", "Inverter")
        eq2.setdefault("preco", 0.0)
        eq2.setdefault("ativo", False)

        if not eq.get("capacidade"):
            for cap in CAPACIDADES:
                if cap in str(chave):
                    eq2["capacidade"] = cap
                    break

        novos[str(eq2["id"])] = eq2

    dados["equipamentos"] = novos

    # Campo legado que não é mais usado.
    dados.pop("adicionais", None)

    return dados


@st.cache_data(ttl=600, max_entries=3, show_spinner=False)
def _config_local_processada(caminho, versao_arquivo):
    """Lê e normaliza a configuração local uma vez por versão do arquivo."""
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return migrar_config(json.load(arquivo))
    except Exception:
        return copy.deepcopy(DEFAULT_CONFIG)


def carregar_config_local():
    """Carrega o login sem rede e sem reprocessar o catálogo em cada rerun."""
    try:
        versao = os.path.getmtime(CONFIG_FILE)
    except OSError:
        versao = None
    return _config_local_processada(CONFIG_FILE, versao)


@st.cache_data(ttl=60, max_entries=8, show_spinner=False)
def _config_normalizada_cache(texto_json):
    """Não refaz a migração do catálogo quando o arquivo não mudou."""
    return migrar_config(json.loads(texto_json))


def carregar_config():
    # O dado publicado é obtido do GitHub (cache curto, invalidado após salvar).
    try:
        texto, _ = _consulta_sessao_github(CONFIG_REPO, CONFIG_FILE)
        if texto is not None:
            return _config_normalizada_cache(texto)
    except Exception:
        pass
    return carregar_config_local()



# =========================================================
# RASCUNHO TEMPORÁRIO DO CLIENTE
# =========================================================

DRAFT_STORAGE_KEY = "f_climatizacao_orcamento_rascunho_v1"
DRAFT_TTL_SECONDS = 7 * 24 * 60 * 60  # sete dias no mesmo navegador; apagado após salvar orçamento

CLIENT_DRAFT_FIELDS = [
    "cliente_possui",
    "cliente_equipamento",
    "cliente_capacidade_compra",
    "cliente_capacidade_compra_unico",
    "cliente_modo_compra",
    "cliente_equipamento_unico",
    "cliente_capacidade",
    "cliente_capacidade_existente",
    "cliente_servicos",
    "cliente_materiais",
    "cliente_tipo_imovel",
    "cliente_andar",
    "cliente_area",
    "cliente_adicional_sim",
    "cliente_adicional_desc",
    "cliente_observacoes",
    "cliente_nome",
    "cliente_telefone",
    "cliente_cidade",
    "cliente_deslocamento_cobrar_km",
    "cliente_deslocamento_km_rodados",
    "cliente_desconto_geral",
    "cliente_equipamentos_selecionados",
]

LOCAL_STORAGE = LocalStorage() if LocalStorage is not None else None


def _normalizar_payload_local(raw):
    if raw in (None, "", {}):
        return None
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None


def restaurar_rascunho_cliente():
    """
    Restaura um rascunho salvo no navegador por até sete dias.
    Os dados ficam somente no navegador até o orçamento ser confirmado.
    """
    if LOCAL_STORAGE is None:
        return

    if st.session_state.get("_rascunho_restaurado", False):
        return

    try:
        raw = LOCAL_STORAGE.getItem(
            DRAFT_STORAGE_KEY,
            key="fclima_draft_get",
        )
    except Exception:
        return

    payload = _normalizar_payload_local(raw)
    if not payload:
        # O componente de armazenamento pode devolver None enquanto o JS
        # inicializa. Evite sobrescrever um rascunho antigo na primeira leitura.
        # Depois de duas leituras vazias E uma edição humana real, habilite
        # a gravação de um novo rascunho (sem exigir rascunho anterior).
        vazias = st.session_state.get("_rascunho_leituras_vazias", 0) + 1
        st.session_state["_rascunho_leituras_vazias"] = vazias
        campos_preenchidos = any(
            str(st.session_state.get(campo, "") or "").strip()
            for campo in (
                "cliente_nome", "cliente_telefone", "cliente_cidade",
                "cliente_observacoes", "cliente_adicional_desc",
            )
        )
        if vazias >= 2 and campos_preenchidos:
            st.session_state["_rascunho_restaurado"] = True
        return

    try:
        expira_em = float(payload.get("expira_em", 0))
    except Exception:
        expira_em = 0

    if expira_em <= time.time():
        try:
            LOCAL_STORAGE.setItem(
                DRAFT_STORAGE_KEY,
                "",
                key="fclima_draft_expired_clear",
            )
        except Exception:
            pass
        st.session_state["_rascunho_restaurado"] = True
        return

    dados = payload.get("dados", {})
    if not isinstance(dados, dict):
        st.session_state["_rascunho_restaurado"] = True
        return

    alterou = False
    for campo, valor in dados.items():
        if (
            campo in CLIENT_DRAFT_FIELDS
            or str(campo).startswith((
                "cliente_eq_visivel_", "cliente_mat_qtd_", "cliente_pontos_",
                "cliente_desc_eq_", "cliente_desc_serv_",
            ))
        ) and campo not in st.session_state:
            st.session_state[campo] = valor
            alterou = True

    st.session_state["_rascunho_restaurado"] = True

    if alterou:
        st.session_state["_mostrar_aviso_rascunho"] = True
        st.rerun()


def salvar_rascunho_cliente():
    """
    Mantém o formulário por até sete dias no armazenamento local do navegador.
    Grava no início do rerun seguinte a cada interação concluída, para que
    cálculos/consultas posteriores não impeçam o backup.
    """
    if LOCAL_STORAGE is None:
        return

    dados = {}
    for campo in CLIENT_DRAFT_FIELDS:
        if campo in st.session_state:
            valor = st.session_state[campo]
            if isinstance(valor, tuple):
                valor = list(valor)
            dados[campo] = valor

    # Também preserva as seleções individuais de aparelhos.
    for campo, valor in st.session_state.items():
        nome_campo = str(campo)
        if nome_campo.startswith("cliente_eq_visivel_"):
            dados[campo] = bool(valor)
        elif nome_campo.startswith(("cliente_mat_qtd_", "cliente_pontos_", "cliente_desc_eq_", "cliente_desc_serv_")):
            dados[campo] = valor

    if not dados:
        return

    assinatura = json.dumps(
        dados,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )

    if assinatura == st.session_state.get("_rascunho_ultima_assinatura"):
        return

    payload = {
        "salvo_em": time.time(),
        "expira_em": time.time() + DRAFT_TTL_SECONDS,
        "dados": dados,
    }

    try:
        LOCAL_STORAGE.setItem(
            DRAFT_STORAGE_KEY,
            json.dumps(payload, ensure_ascii=False),
            key="fclima_draft_set",
        )
        st.session_state["_rascunho_ultima_assinatura"] = assinatura
    except Exception:
        pass


def limpar_rascunho_cliente():
    if LOCAL_STORAGE is not None:
        try:
            LOCAL_STORAGE.setItem(
                DRAFT_STORAGE_KEY,
                "",
                key="fclima_draft_clear",
            )
        except Exception:
            pass

    for campo in CLIENT_DRAFT_FIELDS:
        st.session_state.pop(campo, None)

    for campo in list(st.session_state.keys()):
        nome_campo = str(campo)
        if nome_campo.startswith((
            "cliente_eq_visivel_", "cliente_mat_qtd_", "cliente_pontos_",
            "cliente_desc_eq_", "cliente_desc_serv_",
        )):
            st.session_state.pop(campo, None)

    st.session_state.pop("cliente_equipamentos_selecionados", None)
    st.session_state.pop("_rascunho_ultima_assinatura", None)
    st.session_state["_rascunho_restaurado"] = True


def garantir_opcao_valida(chave, opcoes, multiplo=False):
    if chave not in st.session_state:
        return

    if multiplo:
        atual = st.session_state.get(chave, [])
        if not isinstance(atual, list):
            atual = list(atual) if isinstance(atual, tuple) else []
        st.session_state[chave] = [x for x in atual if x in opcoes]
    else:
        if st.session_state.get(chave) not in opcoes:
            st.session_state.pop(chave, None)


# =========================================================
# GITHUB API
# =========================================================

def github_request(url, method="GET", data=None):
    """Consultas curtas com segunda tentativa apenas em falha transitória.

    Gravações não são repetidas automaticamente para evitar operações em
    duplicidade. Falhas permanentes (403, 404) são retornadas imediatamente.
    """
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN não configurado nos Secrets.")

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "F-Climatizacao",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    tentativas = 2 if method == "GET" else 1
    for indice in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=9) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detalhes = ""
            try:
                detalhes = exc.read().decode("utf-8")
            except Exception:
                pass
            if indice + 1 < tentativas and exc.code in (429, 500, 502, 503, 504):
                time.sleep(0.3)
                continue
            raise RuntimeError(f"GitHub API {exc.code}: {detalhes or exc.reason}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if indice + 1 < tentativas:
                time.sleep(0.3)
                continue
            raise RuntimeError(f"Não foi possível conectar ao GitHub: {exc}") from exc


def github_get_file(repo, path):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{quote(path)}?ref={quote(BRANCH)}"
    try:
        obj = github_request(url)
        content = base64.b64decode(obj["content"]).decode("utf-8")
        return content, obj.get("sha")
    except RuntimeError as e:
        if "GitHub API 404" in str(e):
            return None, None
        raise


# Cache curto em memória: evita múltiplas consultas HTTPS ao GitHub a cada
# interação do Streamlit. O resultado é copiado pelo Streamlit, impedindo que
# uma edição em uma tela altere acidentalmente o conteúdo no cache.
@st.cache_data(ttl=60, max_entries=32, show_spinner=False)
def github_get_file_cache(repo, path):
    return github_get_file(repo, path)


@st.cache_data(ttl=60, max_entries=32, show_spinner=False)
def github_get_json_cache(repo, path):
    """Evita repetir base64/JSON parsing a cada clique ou troca de tela.

    O Streamlit devolve uma cópia independente do cache, portanto alterações
    de itens no ADM não modificam o objeto em cache inadvertidamente.
    """
    conteudo, _ = github_get_file_cache(repo, path)
    return json.loads(conteudo) if conteudo is not None else None


# Reaproveita leituras já feitas na mesma sessão, por um intervalo curto.
# Qualquer gravação bem-sucedida invalida as cópias imediatamente.
# Nenhum dado financeiro é armazenado no navegador do cliente.
def _consulta_sessao_github(repo, caminho, *, json_decodificado=False):
    cache_key = (repo, caminho, bool(json_decodificado))
    agora = time.monotonic()
    itens = st.session_state.setdefault("_fc_cache_remoto_sessao", {})
    item = itens.get(cache_key)
    duracao = 60 if caminho == CONFIG_FILE else 35
    if item is not None and agora - item[0] < duracao:
        return copy.deepcopy(item[1])

    if json_decodificado:
        resultado = github_get_json_cache(repo, caminho)
    else:
        resultado = github_get_file_cache(repo, caminho)
    itens[cache_key] = (agora, copy.deepcopy(resultado))
    return copy.deepcopy(resultado)


def github_put_file(repo, path, text_content, message, sha=None):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{quote(path)}"
    payload = {
        "message": message,
        "content": base64.b64encode(text_content.encode("utf-8")).decode("utf-8"),
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha
    resultado = github_request(url, method="PUT", data=payload)
    # Invalida somente após a API confirmar o salvamento. A próxima leitura
    # traz valores atualizados, inclusive em outras telas e no painel inicial.
    github_get_file_cache.clear()
    github_get_json_cache.clear()
    _config_normalizada_cache.clear()
    # Revalidar imediatamente depois de qualquer alteração, sem esperar o TTL.
    st.session_state.pop("_fc_cache_remoto_sessao", None)
    return resultado


# O login não precisa aguardar a rede. Após autenticação/restauração de
# sessão, o rerun carrega imediatamente o catálogo persistido do GitHub.
# Em qualquer sessão já autenticada, a configuração continua vindo do GitHub.
config = (
    carregar_config()
    if st.session_state.get("admin_logado", False)
    else carregar_config_local()
)


def salvar_config():
    """Salva o catálogo no GitHub, a fonte persistente das configurações.

    Não regrava config.json no filesystem do Streamlit Cloud: tal gravação
    pode acionar o observador de arquivos e recarregar o processo, além de
    não atualizar a cópia do GitHub clonada no deploy de modo confiável.
    No próximo rerun, carregar_config() lê o conteúdo mais recente via API.
    """
    texto = json.dumps(config, ensure_ascii=False, indent=2)
    _, sha = github_get_file(CONFIG_REPO, CONFIG_FILE)
    github_put_file(
        CONFIG_REPO,
        CONFIG_FILE,
        texto,
        "Atualiza configurações pelo painel ADM",
        sha=sha,
    )


def carregar_orcamentos():
    try:
        dados = _consulta_sessao_github(DATA_REPO, BUDGETS_FILE, json_decodificado=True)
        if not isinstance(dados, list):
            raise ValueError("Formato dos orçamentos inválido ou arquivo não encontrado")
        st.session_state["_orcamentos_ultima_leitura"] = dados
        st.session_state["_orcamentos_offline"] = False
        return dados
    except Exception as e:
        # Não transformar uma falha da rede em uma base vazia, pois uma próxima
        # gravação poderia sobrescrever os orçamentos verdadeiros.
        anterior = st.session_state.get("_orcamentos_ultima_leitura")
        if isinstance(anterior, list):
            st.session_state["_orcamentos_offline"] = True
            st.warning("Conexão instável: mostrando uma cópia dos orçamentos. O salvamento fica protegido até reconectar.")
            return copy.deepcopy(anterior)
        st.error(f"Não foi possível carregar os orçamentos: {e}")
        st.stop()


def salvar_orcamentos(lista):
    if st.session_state.get("_orcamentos_offline", False):
        raise RuntimeError("Sem conexão atualizada com os orçamentos. Reconecte antes de salvar para proteger os dados.")
    texto = json.dumps(lista, ensure_ascii=False, indent=2)
    _, sha = github_get_file(DATA_REPO, BUDGETS_FILE)
    github_put_file(
        DATA_REPO,
        BUDGETS_FILE,
        texto,
        "Atualiza histórico de orçamentos",
        sha=sha,
    )



FORMAS_PAGAMENTO = [
    "Pix",
    "Dinheiro à vista",
    "Débito",
    "Crédito à vista",
    "Crédito parcelado",
    "Dinheiro parcelado",
    "Transferência bancária",
    "Outro",
]


def pagamento_exige_parcelas(forma):
    return forma in (
        "Crédito parcelado",
        "Dinheiro parcelado",
    )


def nome_mes(numero):
    nomes = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }
    return nomes.get(int(numero), str(numero))


def extrair_mes_ano(data_texto):
    try:
        data = datetime.strptime(
            str(data_texto),
            "%d/%m/%Y %H:%M",
        )
        return data.month, data.year
    except Exception:
        return None, None


def carregar_financeiro():
    try:
        dados = _consulta_sessao_github(DATA_REPO, FINANCE_FILE, json_decodificado=True)

        if not isinstance(dados, dict):
            dados = {}

        dados.setdefault("custos_materiais", {})
        dados.setdefault("custos_equipamentos", {})
        dados.setdefault("movimentacoes", {})

        return dados
    except Exception as e:
        st.error(f"Não foi possível carregar os dados financeiros: {e}")
        return {
            "custos_materiais": {},
            "custos_equipamentos": {},
            "movimentacoes": {},
        }


def salvar_financeiro(dados):
    texto = json.dumps(dados, ensure_ascii=False, indent=2)
    _, sha = github_get_file(DATA_REPO, FINANCE_FILE)

    github_put_file(
        DATA_REPO,
        FINANCE_FILE,
        texto,
        "Atualiza dados privados de faturamento e custos",
        sha=sha,
    )



def assinatura_dados(dados):
    try:
        bruto = json.dumps(
            dados,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except Exception:
        bruto = repr(dados)
    return hashlib.sha256(bruto.encode("utf-8")).hexdigest()


def autosalvar_config_admin(chave="config_admin"):
    """
    Salva automaticamente alterações do ADM quando o conteúdo realmente muda.
    A primeira renderização apenas registra a assinatura atual.
    """
    assinatura = assinatura_dados(config)
    chave_estado = f"_autosave_sig_{chave}"
    anterior = st.session_state.get(chave_estado)

    if anterior is None:
        st.session_state[chave_estado] = assinatura
        return False

    if anterior != assinatura:
        salvar_config()
        st.session_state[chave_estado] = assinatura
        st.session_state["_autosave_ultima_config"] = datetime.now(
            FUSO_BRASILIA
        ).strftime("%d/%m/%Y %H:%M:%S")
        return True

    return False


def autosalvar_financeiro_admin(financeiro, chave):
    """
    Salva custos privados automaticamente e recalcula a Central para que
    custos/lucros dos pedidos e faturados usem os valores novos.
    """
    somente_custos = {
        "custos_materiais": financeiro.get("custos_materiais", {}),
        "custos_equipamentos": financeiro.get("custos_equipamentos", {}),
    }

    assinatura = assinatura_dados(somente_custos)
    chave_estado = f"_autosave_fin_sig_{chave}"
    anterior = st.session_state.get(chave_estado)

    if anterior is None:
        st.session_state[chave_estado] = assinatura
        return False

    if anterior != assinatura:
        salvar_financeiro(financeiro)

        # Recalcula faturados imediatamente com os novos custos.
        try:
            orcamentos_atualizados = carregar_orcamentos()
            financeiro_atualizado = carregar_financeiro()
            sincronizar_central_faturamento(
                orcamentos_atualizados,
                financeiro_atualizado,
            )
        except Exception:
            # O custo já foi salvo; se a sincronização falhar, o botão
            # "Atualizar dados da central" continua disponível como fallback.
            pass

        st.session_state[chave_estado] = assinatura
        st.session_state["_autosave_ultima_financeiro"] = datetime.now(
            FUSO_BRASILIA
        ).strftime("%d/%m/%Y %H:%M:%S")
        return True

    return False



def custo_material(financeiro, nome):
    return float(
        financeiro.get("custos_materiais", {})
        .get(nome, {})
        .get("custo", 0)
        or 0
    )


def custo_equipamento(financeiro, equipamento_id, descricao=None):
    custos = financeiro.get("custos_equipamentos", {})

    if equipamento_id is not None:
        direto = custos.get(str(equipamento_id), {})
        if direto:
            return float(direto.get("custo", 0) or 0)

    # Fallback para orçamentos antigos nos quais o ID do equipamento
    # não ficou gravado corretamente. Tenta localizar pelo texto do aparelho.
    texto = str(descricao or "").lower()
    texto = texto.replace(
        "• instalação inclusa até 2 m de linha",
        "",
    ).strip()

    if texto:
        for eid, eq in config.get("equipamentos", {}).items():
            nome = nome_equipamento(eq).lower().strip()
            if nome and (nome in texto or texto in nome):
                return float(
                    custos.get(str(eid), {}).get("custo", 0)
                    or 0
                )

    return 0.0


def total_item_liquido_financeiro(item):
    qtd = float(item.get("quantidade", 0) or 0)
    valor = float(item.get("valor_unitario", 0) or 0)
    desconto = limitar_percentual(item.get("desconto_percentual", 0))
    return aplicar_desconto(qtd * valor, desconto)


def estimar_resultado_pedido(orcamento, financeiro):
    """
    Estima receita, custo e lucro de um pedido ainda não faturado
    usando os custos privados atuais e o valor líquido do pedido.
    """
    receita = 0.0
    custo = 0.0

    for item in orcamento.get("itens", []):
        qtd = float(item.get("quantidade", 0) or 0)
        venda = total_item_liquido_financeiro(item)
        origem = item.get("origem", "manual")
        custo_unit = 0.0

        if origem == "material":
            custo_unit = custo_material(
                financeiro,
                item.get("descricao", ""),
            )

        elif origem == "equipamento":
            custo_unit = custo_equipamento(
                financeiro,
                orcamento.get("equipamento_id"),
                item.get("descricao", ""),
            )

        receita += venda
        custo += qtd * custo_unit

    opcoes = orcamento.get("opcoes_equipamentos", [])

    if len(opcoes) == 1:
        opcao = opcoes[0]

        receita += aplicar_desconto(
            float(opcao.get("preco", 0) or 0),
            opcao.get("desconto_percentual", 0),
        )

        custo += custo_equipamento(
            financeiro,
            opcao.get("id"),
            opcao.get("descricao", ""),
        )

        for servico in opcao.get("servicos", []):
            receita += aplicar_desconto(
                float(servico.get("valor", 0) or 0),
                servico.get("desconto_percentual", 0),
            )

    desconto_geral = limitar_percentual(
        orcamento.get("desconto_percentual", 0)
    )
    receita_final = aplicar_desconto(
        receita,
        desconto_geral,
    )

    return {
        "receita": receita_final,
        "custo": custo,
        "lucro": receita_final - custo,
        "margem": (
            ((receita_final - custo) / receita_final * 100)
            if receita_final > 0
            else 0.0
        ),
    }


def snapshot_faturamento(orcamento, financeiro, pagamento=None):
    """
    Cria um retrato financeiro do orçamento no momento do faturamento.
    Serviços geram receita, porém não custo de estoque.
    Materiais e equipamentos usam custo privado cadastrado.
    """
    linhas = []
    receita = 0.0
    custo = 0.0

    for item in orcamento.get("itens", []):
        qtd = float(item.get("quantidade", 0) or 0)
        venda = total_item_liquido_financeiro(item)
        origem = item.get("origem", "manual")
        custo_unit = 0.0

        if origem == "material":
            custo_unit = custo_material(
                financeiro,
                item.get("descricao", ""),
            )

        elif origem == "equipamento":
            custo_unit = custo_equipamento(
                financeiro,
                orcamento.get("equipamento_id"),
                item.get("descricao", ""),
            )

        custo_total = qtd * custo_unit

        linhas.append(
            {
                "descricao": item.get("descricao", ""),
                "origem": origem,
                "quantidade": qtd,
                "unidade": item.get("unidade", ""),
                "valor_venda": venda,
                "custo_unitario": custo_unit,
                "custo_total": custo_total,
            }
        )

        receita += venda
        custo += custo_total

    # Orçamento comparativo só deve ser faturado após restar uma opção escolhida.
    for opcao in orcamento.get("opcoes_equipamentos", []):
        preco_eq = aplicar_desconto(
            float(opcao.get("preco", 0) or 0),
            opcao.get("desconto_percentual", 0),
        )
        custo_eq = custo_equipamento(
            financeiro,
            opcao.get("id"),
            opcao.get("descricao", ""),
        )

        linhas.append(
            {
                "descricao": opcao.get("descricao", "Ar-condicionado"),
                "origem": "equipamento",
                "quantidade": 1.0,
                "unidade": "equipamento",
                "valor_venda": preco_eq,
                "custo_unitario": custo_eq,
                "custo_total": custo_eq,
            }
        )

        receita += preco_eq
        custo += custo_eq

        for servico in opcao.get("servicos", []):
            venda_servico = aplicar_desconto(
                float(servico.get("valor", 0) or 0),
                servico.get("desconto_percentual", 0),
            )

            linhas.append(
                {
                    "descricao": servico.get("descricao", "Serviço"),
                    "origem": "servico",
                    "quantidade": 1.0,
                    "unidade": "serviço",
                    "valor_venda": venda_servico,
                    "custo_unitario": 0.0,
                    "custo_total": 0.0,
                }
            )

            receita += venda_servico

    desconto_geral = limitar_percentual(
        orcamento.get("desconto_percentual", 0)
    )
    receita_final = aplicar_desconto(
        receita,
        desconto_geral,
    )

    return {
        "numero": str(orcamento.get("numero", "")).zfill(4),
        "cliente": copy.deepcopy(orcamento.get("cliente", {})),
        "data_faturamento": datetime.now(FUSO_BRASILIA).strftime(
            "%d/%m/%Y %H:%M"
        ),
        "linhas": linhas,
        "receita": receita_final,
        "custo": custo,
        "lucro": receita_final - custo,
        "desconto_geral": desconto_geral,
        "pagamento": copy.deepcopy(pagamento or {}),
    }


def alterar_status_orcamento(
    orcamentos,
    orcamento,
    novo_status,
    financeiro,
    pagamento=None,
):
    numero = str(orcamento.get("numero", "")).zfill(4)
    status_anterior = orcamento.get("status", "Orçamento")

    if novo_status in ("Pedido de venda", "Faturado / Concluído"):
        if len(orcamento.get("opcoes_equipamentos", [])) > 1:
            raise ValueError(
                "Antes de confirmar como pedido ou faturar, deixe somente uma opção de aparelho no orçamento."
            )

    agora_status = datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M")
    orcamento["status"] = novo_status
    orcamento["data_status"] = agora_status
    orcamento["atualizado_em"] = agora_status

    if novo_status == "Pedido de venda" and pagamento is not None:
        orcamento["pagamento_pedido"] = copy.deepcopy(pagamento)

    if novo_status == "Faturado / Concluído":
        # Registra execução na agenda, inclusive quando faturado pela aba Orçamentos.
        agendamento = orcamento.get("agendamento")
        if isinstance(agendamento, dict):
            agendamento["realizado"] = True
            agendamento.setdefault("realizado_em", agora_status)
        if pagamento is None:
            pagamento = copy.deepcopy(
                orcamento.get("pagamento_pedido", {})
            )
        orcamento["pagamento_faturamento"] = copy.deepcopy(
            pagamento or {}
        )
        financeiro.setdefault("movimentacoes", {})[
            numero
        ] = snapshot_faturamento(
            orcamento,
            financeiro,
            pagamento=pagamento,
        )

    elif status_anterior == "Faturado / Concluído":
        # Reversão: sai imediatamente da central de faturamento.
        financeiro.setdefault("movimentacoes", {}).pop(
            numero,
            None,
        )

    salvar_orcamentos(orcamentos)
    salvar_financeiro(financeiro)


def sincronizar_central_faturamento(orcamentos, financeiro):
    """
    Reconstrói a central financeira a partir da Gestão Comercial.
    Apenas registros atualmente marcados como Faturado / Concluído
    permanecem em movimentações. Registros antigos/excluídos são removidos.
    """
    movimentacoes_atuais = financeiro.get("movimentacoes", {})
    novas_movimentacoes = {}

    for orcamento in orcamentos:
        if orcamento.get("status", "Orçamento") != "Faturado / Concluído":
            continue

        numero = str(orcamento.get("numero", "")).zfill(4)

        pagamento = (
            orcamento.get("pagamento_faturamento")
            or orcamento.get("pagamento_pedido")
            or movimentacoes_atuais.get(numero, {}).get("pagamento")
            or {}
        )

        snapshot = snapshot_faturamento(
            orcamento,
            financeiro,
            pagamento=pagamento,
        )

        # Mantém a data original de faturamento, quando já existia.
        data_anterior = movimentacoes_atuais.get(numero, {}).get(
            "data_faturamento"
        )
        if data_anterior:
            snapshot["data_faturamento"] = data_anterior
        else:
            snapshot["data_faturamento"] = (
                orcamento.get("data_status")
                or orcamento.get("atualizado_em")
                or snapshot.get("data_faturamento")
            )

        novas_movimentacoes[numero] = snapshot

    removidos = len(
        set(movimentacoes_atuais.keys())
        - set(novas_movimentacoes.keys())
    )

    atualizados = len(novas_movimentacoes)

    financeiro["movimentacoes"] = novas_movimentacoes
    financeiro["ultima_sincronizacao"] = datetime.now(
        FUSO_BRASILIA
    ).strftime("%d/%m/%Y %H:%M")

    salvar_financeiro(financeiro)

    return {
        "atualizados": atualizados,
        "removidos": removidos,
        "ultima_sincronizacao": financeiro["ultima_sincronizacao"],
    }


def carregar_meta_orcamentos():
    try:
        content, _ = github_get_file_cache(DATA_REPO, BUDGET_META_FILE)
        if content is None:
            return {"ultimo_numero": 0}
        dados = json.loads(content)
        if not isinstance(dados, dict):
            return {"ultimo_numero": 0}
        dados.setdefault("ultimo_numero", 0)
        return dados
    except Exception:
        return {"ultimo_numero": 0}


def salvar_meta_orcamentos(meta):
    texto = json.dumps(meta, ensure_ascii=False, indent=2)
    _, sha = github_get_file(DATA_REPO, BUDGET_META_FILE)
    github_put_file(
        DATA_REPO,
        BUDGET_META_FILE,
        texto,
        "Atualiza contador permanente de orçamentos",
        sha=sha,
    )


def reservar_proximo_numero(lista):
    """
    Reserva um número novo e nunca reutiliza números apagados.
    """
    meta = carregar_meta_orcamentos()

    maior_existente = 0
    for o in lista:
        try:
            maior_existente = max(
                maior_existente,
                int(str(o.get("numero", "0")).lstrip("0") or "0"),
            )
        except Exception:
            pass

    ultimo = max(
        int(meta.get("ultimo_numero", 0) or 0),
        maior_existente,
    )
    proximo = ultimo + 1
    meta["ultimo_numero"] = proximo
    salvar_meta_orcamentos(meta)

    return f"{proximo:04d}"


def resetar_base_orcamentos():
    """
    Arquiva integralmente a base atual e reinicia a numeração em 0001.
    Nenhum número será reutilizado dentro do novo ciclo.
    """
    orcamentos = carregar_orcamentos()
    financeiro = carregar_financeiro()
    meta = carregar_meta_orcamentos()

    agora = datetime.now(FUSO_BRASILIA)
    carimbo = agora.strftime("%Y%m%d_%H%M%S")
    arquivo_backup = f"arquivos/reset_{carimbo}.json"

    pacote = {
        "criado_em": agora.strftime("%d/%m/%Y %H:%M"),
        "orcamentos": orcamentos,
        "financeiro": financeiro,
        "meta_orcamentos": meta,
    }

    github_put_file(
        DATA_REPO,
        arquivo_backup,
        json.dumps(pacote, ensure_ascii=False, indent=2),
        "Arquivo automático antes de resetar a base de orçamentos",
        sha=None,
    )

    salvar_orcamentos([])
    salvar_financeiro(
        {
            "custos_materiais": financeiro.get("custos_materiais", {}),
            "custos_equipamentos": financeiro.get("custos_equipamentos", {}),
            "movimentacoes": {},
        }
    )
    salvar_meta_orcamentos({"ultimo_numero": 0})

    return arquivo_backup


# =========================================================
# LOGO / CABEÇALHO
# =========================================================

def logo_path():
    for nome in ["logo_transparente.png", "logo_transparente.PNG", "logo.png", "logo.PNG"]:
        if os.path.exists(nome):
            return nome
    return None


@st.cache_data(show_spinner=False)
def logo_data_uri():
    """Evita reler e converter a imagem em base64 em cada rerun."""
    path = logo_path()
    if not path:
        return ""
    try:
        with open(path, "rb") as arquivo:
            dados = base64.b64encode(arquivo.read()).decode("ascii")
        return f"data:image/png;base64,{dados}"
    except Exception:
        return ""


def link_whatsapp(texto):
    numero = "".join(c for c in config["empresa"].get("whatsapp", "") if c.isdigit())
    return f"https://wa.me/{numero}?text={quote(texto)}"


def cabecalho(admin=False):
    logo = logo_data_uri()
    img = f'<img class="brand-logo" src="{logo}" alt="Logo F Climatização">' if logo else ""

    if admin:
        corpo = """
        <div>
          <div class="brand-admin">ADMINISTRAÇÃO</div>
          <div class="brand-name">F CLIMATIZAÇÃO</div>
          <div class="brand-sub">Agenda, orçamentos e gestão de serviços</div>
        </div>
        """
    else:
        nome = config["empresa"].get("nome", "F Climatização").upper()
        slogan = config["empresa"].get("slogan", "Seu ambiente na temperatura ideal")
        corpo = f"""
        <div>
          <div class="brand-name">{nome}</div>
          <div class="brand-sub">{slogan}</div>
        </div>
        """

    st.markdown(
        f'<div class="brand-shell">{img}{corpo}</div>',
        unsafe_allow_html=True,
    )

    if not admin:
        wa = link_whatsapp("Olá! Gostaria de falar com a F Climatização.")
        atendimento = config["empresa"].get(
            "texto_atendimento", "Atendimento em Não-Me-Toque e região"
        )
        st.markdown(
            f"""
            <div class="quick-row">
              <a class="quick-chip" href="{wa}" target="_blank">WhatsApp</a>
              <span class="quick-chip">{atendimento}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def secao(titulo, subtitulo=""):
    """Cabeçalho visual consistente para áreas operacionais e cadastros."""
    from html import escape
    icones = {
        "Novo orçamento": "📝", "Orçamentos": "📄",
        "Pedidos de venda": "📋", "Vendas concluídas": "✅",
        "Agenda": "📅", "Minha agenda": "📅",
        "Serviços realizados": "🛠️", "Gestão comercial": "📊",
        "Serviços": "🔧", "Materiais": "📦",
        "Aparelhos": "❄️", "Regras": "⚙️", "Empresa": "🏢",
        "Acesso restrito": "🔒", "Aparelho do cliente": "❄️",
        "Local do serviço": "📍", "Dados do cliente": "👤",
        "Descontos para este orçamento (%)": "🏷️",
    }
    icone = icones.get(str(titulo), "")
    marcador = (
        f'<span class="section-icon" aria-hidden="true">{icone}</span>'
        if icone else ""
    )
    st.markdown(
        f"""
        <div class="section-wrap section-wrap-pro">
          <div class="section-heading-row">{marcador}
            <div class="section-heading-text">
              <div class="section-title">{escape(str(titulo))}</div>
              <div class="section-sub">{escape(str(subtitulo))}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def tela_carregamento(texto="Carregando..."):
    placeholder = st.empty()
    logo = logo_data_uri()
    logo_html = (
        f'<img src="{logo}" style="width:42px;height:42px;object-fit:contain;">'
        if logo
        else '<div style="width:42px;height:42px;"></div>'
    )

    placeholder.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:12px;
            padding:13px 15px;
            margin:8px 0 12px 0;
            border-radius:16px;
            border:1px solid rgba(8,120,232,.38);
            background:linear-gradient(135deg,rgba(8,120,232,.15),rgba(14,20,30,.98));
        ">
          {logo_html}
          <div>
            <div style="font-size:12px;font-weight:850;color:#fff;">F CLIMATIZAÇÃO</div>
            <div style="font-size:11px;color:#8fc9ff;margin-top:2px;">{texto}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        placeholder.empty()



def compartilhar_pdf(pdf_bytes, nome_arquivo, titulo="Orçamento F Climatização"):
    """
    Tenta abrir o compartilhamento nativo do celular com o PDF anexado.
    Se o navegador/iframe não permitir Web Share com arquivos, oferece download como fallback.
    """
    pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")

    html = f"""
    <style>
      body {{
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}
      .wrap {{
        width: 100%;
      }}
      button {{
        width: 100%;
        min-height: 48px;
        border: 1px solid #1891ff;
        border-radius: 14px;
        background: linear-gradient(90deg,#0758b9,#0878e8);
        color: #fff;
        font-size: 15px;
        font-weight: 800;
        cursor: pointer;
        padding: 11px 14px;
      }}
      .fallback {{
        display: none;
        margin-top: 8px;
        text-align: center;
        font-size: 12px;
        color: #9caec4;
      }}
      .fallback a {{
        color: #46a9ff;
        font-weight: 700;
        text-decoration: none;
      }}
    </style>

    <div class="wrap">
      <button id="shareBtn" type="button">COMPARTILHAR PDF</button>
      <div id="fallback" class="fallback">
        O compartilhamento direto não está disponível neste navegador.
        <a id="downloadLink" download="{nome_arquivo}">Baixar PDF</a>
      </div>
    </div>

    <script>
      const b64 = "{pdf_b64}";
      const fileName = {json.dumps(nome_arquivo)};

      function base64ToBlob(base64, type) {{
        const binary = atob(base64);
        const len = binary.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {{
          bytes[i] = binary.charCodeAt(i);
        }}
        return new Blob([bytes], {{ type }});
      }}

      const blob = base64ToBlob(b64, "application/pdf");
      const file = new File([blob], fileName, {{ type: "application/pdf" }});
      const btn = document.getElementById("shareBtn");
      const fallback = document.getElementById("fallback");
      const downloadLink = document.getElementById("downloadLink");

      const objectUrl = URL.createObjectURL(blob);
      downloadLink.href = objectUrl;

      btn.addEventListener("click", async () => {{
        try {{
          if (
            navigator.share &&
            navigator.canShare &&
            navigator.canShare({{ files: [file] }})
          ) {{
            await navigator.share({{
              files: [file]
            }});
          }} else {{
            fallback.style.display = "block";
            downloadLink.click();
          }}
        }} catch (err) {{
          if (err && err.name === "AbortError") {{
            return;
          }}
          fallback.style.display = "block";
        }}
      }});

      window.addEventListener("beforeunload", () => URL.revokeObjectURL(objectUrl));
    </script>
    """

    components.html(html, height=72)



def mostrar_referencia_capacidade(capacidade):
    if capacidade not in REFERENCIA_AREA:
        return

    referencia = REFERENCIA_AREA[capacidade]
    st.markdown(
        f'<div class="capacity-ok">Referência prática: {capacidade} — {referencia}.</div>'
        '<div class="capacity-note">'
        'O dimensionamento pode variar conforme sol, pessoas, eletrônicos, isolamento e características do ambiente.'
        '</div>',
        unsafe_allow_html=True,
    )


def mostrar_compatibilidade_area(capacidade, area):
    if not capacidade or capacidade not in BTU_NUM or area == "Não sei":
        return

    if area == "Acima de 37 m²":
        st.markdown(
            '<div class="capacity-warn">'
            'Área acima da referência automática. Recomendamos confirmar o dimensionamento com a F Climatização.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    necessario = AREA_MIN_BTU.get(area)
    escolhido = BTU_NUM.get(capacidade)

    if necessario is None or escolhido is None:
        return

    if escolhido >= necessario:
        st.markdown(
            '<div class="capacity-ok">✓ Capacidade compatível com a área informada.</div>',
            unsafe_allow_html=True,
        )
    else:
        recomendada = next(
            (cap for cap, valor in BTU_NUM.items() if valor == necessario),
            "capacidade superior",
        )
        st.markdown(
            f'<div class="capacity-warn">'
            f'⚠ A capacidade selecionada pode ser insuficiente para esta área. '
            f'Referência mínima aproximada: {recomendada}.'
            f'</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# EQUIPAMENTOS
# =========================================================

def nome_equipamento(eq):
    marca = (eq.get("marca") or "").strip()
    partes = ["Ar-condicionado"]
    if marca:
        partes.append(marca)
    partes.append(eq.get("capacidade", ""))
    partes.append(eq.get("tipo", ""))
    return " • ".join([p for p in partes if p])


# =========================================================
# PDF
# =========================================================


def descricao_equipamento_com_instalacao(descricao):
    texto = str(descricao or "Ar-condicionado").strip()
    complemento = "Instalação inclusa até 2 m de linha"
    if complemento.lower() not in texto.lower():
        texto = f"{texto} • {complemento}"
    return texto


def situacao_tem_compra(situacao):
    return situacao in (
        "Não, quero comprar",
        "Já tenho um e também quero comprar outro",
    )


def situacao_tem_aparelho_existente(situacao):
    return situacao in (
        "Sim, já tenho o aparelho",
        "Já tenho um e também quero comprar outro",
        "Ainda estou avaliando",
    )

def icone_pdf(tipo, cor):
    """Ícones vetoriais simples e profissionais para o cabeçalho do orçamento."""
    d = Drawing(12, 12)

    if tipo == "casa":
        p = RLPath()
        p.moveTo(1.5, 5.5)
        p.lineTo(6, 10.5)
        p.lineTo(10.5, 5.5)
        p.strokeColor = cor
        p.strokeWidth = 1.4
        p.fillColor = None
        d.add(p)
        d.add(Rect(3, 1.8, 6, 4.3, strokeColor=cor, fillColor=None, strokeWidth=1.2))
        d.add(Rect(5.1, 1.8, 1.8, 2.8, strokeColor=cor, fillColor=None, strokeWidth=1.0))

    elif tipo == "documento":
        d.add(Rect(2.2, 1.5, 7.2, 9, strokeColor=cor, fillColor=None, strokeWidth=1.2))
        d.add(Line(3.7, 7.8, 8.0, 7.8, strokeColor=cor, strokeWidth=1.0))
        d.add(Line(3.7, 5.8, 8.0, 5.8, strokeColor=cor, strokeWidth=1.0))
        d.add(Line(3.7, 3.8, 7.0, 3.8, strokeColor=cor, strokeWidth=1.0))

    elif tipo == "local":
        d.add(Circle(6, 7.2, 3.2, strokeColor=cor, fillColor=None, strokeWidth=1.2))
        d.add(Circle(6, 7.2, 1.0, strokeColor=cor, fillColor=None, strokeWidth=1.0))
        p = RLPath()
        p.moveTo(3.8, 4.8)
        p.lineTo(6, 1.2)
        p.lineTo(8.2, 4.8)
        p.strokeColor = cor
        p.strokeWidth = 1.2
        p.fillColor = None
        d.add(p)

    return d


def rotulo_documento(orcamento):
    status = orcamento.get("status", "Orçamento")

    if status == "Pedido de venda":
        return "PEDIDO DE VENDA"

    if status == "Faturado / Concluído":
        return "VENDA CONCLUÍDA"

    return "ORÇAMENTO"


def pagamento_documento(orcamento):
    status = orcamento.get("status", "Orçamento")

    if status == "Pedido de venda":
        return copy.deepcopy(
            orcamento.get("pagamento_pedido", {})
        )

    if status == "Faturado / Concluído":
        return copy.deepcopy(
            orcamento.get("pagamento_faturamento")
            or orcamento.get("pagamento_pedido")
            or {}
        )

    return {}


def gerar_pdf(orcamento):
    buffer = BytesIO()

    azul = colors.HexColor("#05275D")
    azul2 = colors.HexColor("#0878E8")
    laranja = colors.HexColor("#FF7A00")
    cinza = colors.HexColor("#5F6B7A")
    cinza_claro = colors.HexColor("#E8EDF3")

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "FTitulo",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        textColor=azul,
        spaceAfter=3,
    )
    small = ParagraphStyle(
        "FSmall",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
        textColor=cinza,
    )
    normal = ParagraphStyle(
        "FNormal",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1A2430"),
    )
    right = ParagraphStyle(
        "FRight",
        parent=normal,
        alignment=TA_RIGHT,
    )

    story = []

    logo = logo_path()
    logo_flow = ""
    if logo:
        try:
            logo_flow = Image(logo, width=25 * mm, height=25 * mm)
        except Exception:
            logo_flow = ""

    empresa = config["empresa"]

    nome_empresa_style = ParagraphStyle(
        "FNomeEmpresa",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=21,
        textColor=azul,
        spaceAfter=1,
    )

    slogan_style = ParagraphStyle(
        "FSloganEmpresa",
        parent=small,
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=9.5,
        textColor=colors.HexColor("#12345B"),
    )

    detalhe_empresa_style = ParagraphStyle(
        "FDetalheEmpresa",
        parent=small,
        fontName="Helvetica",
        fontSize=8.1,
        leading=9.2,
        textColor=colors.HexColor("#17355A"),
    )

    bloco_empresa = [
        Paragraph(
            empresa.get("nome", "F Climatização"),
            nome_empresa_style,
        )
    ]

    if empresa.get("slogan"):
        bloco_empresa.append(
            Paragraph(
                empresa.get("slogan", ""),
                slogan_style,
            )
        )

    detalhes_empresa = []

    if empresa.get("endereco"):
        detalhes_empresa.append(
            [
                icone_pdf("casa", azul2),
                Paragraph(
                    empresa.get("endereco", ""),
                    detalhe_empresa_style,
                ),
            ]
        )

    if empresa.get("cnpj"):
        detalhes_empresa.append(
            [
                icone_pdf("documento", azul2),
                Paragraph(
                    f'CNPJ: {empresa.get("cnpj","")}',
                    detalhe_empresa_style,
                ),
            ]
        )

    if empresa.get("texto_atendimento"):
        detalhes_empresa.append(
            [
                icone_pdf("local", azul2),
                Paragraph(
                    empresa.get("texto_atendimento", ""),
                    detalhe_empresa_style,
                ),
            ]
        )

    if detalhes_empresa:
        detalhes_tbl = Table(
            detalhes_empresa,
            colWidths=[5 * mm, 92 * mm],
            rowHeights=[5.2 * mm] * len(detalhes_empresa),
        )
        detalhes_tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        bloco_empresa.append(Spacer(1, 1.2 * mm))
        bloco_empresa.append(detalhes_tbl)

    empresa_tbl = Table(
        [[bloco_empresa]],
        colWidths=[101 * mm],
    )
    empresa_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    cab_dados = [
        [
            logo_flow,
            empresa_tbl,
            Paragraph(
                f"<b>{rotulo_documento(orcamento)} Nº {orcamento['numero']}</b><br/>"
                f"<font size='8'>Data: {orcamento.get('data','')}</font>",
                right,
            ),
        ]
    ]

    cab = Table(
        cab_dados,
        colWidths=[28 * mm, 103 * mm, 43 * mm],
    )
    cab.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), 1.2, laranja),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story += [cab, Spacer(1, 5 * mm)]

    cliente = orcamento.get("cliente", {})
    story.append(Paragraph("<b>Cliente</b>", title_style))
    cliente_tbl = Table(
        [
            ["Nome", cliente.get("nome", "")],
            ["Contato", cliente.get("telefone", "")],
            ["Cidade", cliente.get("cidade", "")],
            ["Imóvel", orcamento.get("tipo_imovel", "")],
        ],
        colWidths=[30 * mm, 144 * mm],
    )
    cliente_tbl.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (0, -1), azul),
                ("GRID", (0, 0), (-1, -1), 0.4, cinza_claro),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F6F8FB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story += [cliente_tbl, Spacer(1, 6 * mm)]

    pagamento_pdf = pagamento_documento(orcamento)

    if pagamento_pdf:
        forma_pagamento_pdf = pagamento_pdf.get(
            "forma",
            "Não informado",
        )
        parcelas_pagamento_pdf = int(
            pagamento_pdf.get("parcelas", 1) or 1
        )
        observacao_pagamento_pdf = str(
            pagamento_pdf.get("observacao", "") or ""
        ).strip()

        linhas_pagamento = [
            ["Forma de pagamento", forma_pagamento_pdf],
        ]

        if parcelas_pagamento_pdf > 1:
            linhas_pagamento.append(
                ["Parcelamento", f"{parcelas_pagamento_pdf}x"]
            )

        if observacao_pagamento_pdf:
            linhas_pagamento.append(
                ["Observação", observacao_pagamento_pdf]
            )

        story.append(
            Paragraph(
                "<b>Condições de pagamento</b>",
                title_style,
            )
        )

        pagamento_tbl = Table(
            linhas_pagamento,
            colWidths=[42 * mm, 132 * mm],
        )
        pagamento_tbl.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TEXTCOLOR", (0, 0), (0, -1), azul),
                    ("GRID", (0, 0), (-1, -1), 0.4, cinza_claro),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F6F8FB")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story += [
            pagamento_tbl,
            Spacer(1, 6 * mm),
        ]

    itens_orcamento = orcamento.get("itens", [])
    opcoes_equipamentos_pdf = orcamento.get("opcoes_equipamentos", [])

    if itens_orcamento:
        titulo_itens = (
            "<b>Serviços e itens base</b>"
            if opcoes_equipamentos_pdf
            else "<b>Itens do orçamento</b>"
        )
        story.append(Paragraph(titulo_itens, title_style))
        dados = [["Descrição", "Qtd.", "Unidade", "Valor unit.", "Total"]]

        for item in itens_orcamento:
            qtd = float(item.get("quantidade", 0) or 0)
            vu = float(item.get("valor_unitario", 0) or 0)
            desconto_item = limitar_percentual(
                item.get("desconto_percentual", 0)
            )
            total_item_liquido = total_item(item)

            descricao_item = str(item.get("descricao", ""))
            if desconto_item > 0:
                descricao_item += (
                    f"<br/><font size='7' color='#5F6B7A'>"
                    f"Desconto: {desconto_item:g}%</font>"
                )

            dados.append(
                [
                    Paragraph(descricao_item, small),
                    f"{qtd:g}",
                    item.get("unidade", ""),
                    dinheiro(vu),
                    dinheiro(total_item_liquido),
                ]
            )

        itens_tbl = Table(
            dados,
            colWidths=[78 * mm, 18 * mm, 24 * mm, 27 * mm, 27 * mm],
            repeatRows=1,
        )
        itens_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), azul),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.4, cinza_claro),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFBFD")]),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story += [itens_tbl, Spacer(1, 5 * mm)]

    total = calcular_total(itens_orcamento)
    desconto_geral_pdf = limitar_percentual(
        orcamento.get("desconto_percentual", 0)
    )

    if opcoes_equipamentos_pdf:
        if total > 0:
            base_tbl = Table(
                [[
                    Paragraph(
                        "<b>ITENS COMUNS DO ORÇAMENTO</b>",
                        normal,
                    ),
                    Paragraph(
                        f"<b>{dinheiro(total)}</b>",
                        right,
                    ),
                ]],
                colWidths=[120 * mm, 54 * mm],
            )
            base_tbl.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor("#F4F7FB"),
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.7,
                            azul2,
                        ),
                        (
                            "PADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                    ]
                )
            )
            story += [
                base_tbl,
                Spacer(1, 5 * mm),
            ]

        story.append(
            Paragraph(
                "<b>Opções de equipamento</b>",
                title_style,
            )
        )
        story.append(
            Paragraph(
                (
                    "Orçamento comparativo. Cada alternativa apresenta seu próprio valor "
                    "com os serviços correspondentes, sem somar os aparelhos entre si."
                    + (
                        f" Desconto geral aplicado: {desconto_geral_pdf:g}%."
                        if desconto_geral_pdf > 0
                        else ""
                    )
                ),
                small,
            )
        )
        story.append(Spacer(1, 2 * mm))

        dados_opcoes = [["Equipamento", "Preço", "Total c/ serviços"]]

        for opcao in opcoes_equipamentos_pdf:
            preco_eq = float(opcao.get("preco", 0) or 0)
            desconto_eq = limitar_percentual(
                opcao.get("desconto_percentual", 0)
            )
            total_final_opcao = total_opcao_orcamento(
                orcamento,
                opcao,
            )

            descricao_opcao = str(
                opcao.get("descricao", "Ar-condicionado")
            )
            if orcamento.get("instalacao_inclusa_equipamento"):
                descricao_opcao = descricao_equipamento_com_instalacao(
                    descricao_opcao
                )

            if desconto_eq > 0:
                descricao_opcao += (
                    f"<br/><font size='7' color='#5F6B7A'>"
                    f"Desconto no aparelho: {desconto_eq:g}%</font>"
                )

            if opcao.get("servicos"):
                linhas_servico = "<br/>".join(
                    (
                        f'{s.get("descricao","")}: '
                        f'{dinheiro(aplicar_desconto(s.get("valor",0), s.get("desconto_percentual",0)))}'
                        + (
                            f' (desc. {limitar_percentual(s.get("desconto_percentual",0)):g}%)'
                            if limitar_percentual(s.get("desconto_percentual",0)) > 0
                            else ''
                        )
                    )
                    for s in opcao.get("servicos", [])
                )
                descricao_opcao += (
                    f"<br/><font size='7' color='#5F6B7A'>"
                    f"{linhas_servico}</font>"
                )

            dados_opcoes.append(
                [
                    Paragraph(descricao_opcao, small),
                    dinheiro(preco_eq),
                    dinheiro(total_final_opcao),
                ]
            )

        opcoes_tbl = Table(
            dados_opcoes,
            colWidths=[94 * mm, 38 * mm, 42 * mm],
            repeatRows=1,
        )
        opcoes_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), azul),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.4, cinza_claro),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFBFD")]),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story += [opcoes_tbl, Spacer(1, 6 * mm)]
    else:
        total_final_pdf = aplicar_desconto(
            total,
            desconto_geral_pdf,
        )

        linhas_total = []
        if desconto_geral_pdf > 0:
            linhas_total.append(
                [
                    Paragraph("Subtotal", normal),
                    Paragraph(dinheiro(total), right),
                ]
            )
            linhas_total.append(
                [
                    Paragraph(
                        f"<b>Desconto geral ({desconto_geral_pdf:g}%)</b>",
                        normal,
                    ),
                    Paragraph(
                        f"<b>- {dinheiro(total - total_final_pdf)}</b>",
                        right,
                    ),
                ]
            )

        linhas_total.append(
            [
                Paragraph("<b>TOTAL ESTIMADO</b>", normal),
                Paragraph(f"<b>{dinheiro(total_final_pdf)}</b>", right),
            ]
        )

        total_tbl = Table(
            linhas_total,
            colWidths=[120 * mm, 54 * mm],
        )
        total_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF4E8")),
                    ("BOX", (0, 0), (-1, -1), 0.8, laranja),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story += [total_tbl, Spacer(1, 6 * mm)]

    obs = orcamento.get("observacoes", "")
    adicional = orcamento.get("adicional", {})

    if obs:
        story += [
            Paragraph("<b>Observações</b>", title_style),
            Paragraph(obs.replace("\n", "<br/>"), normal),
            Spacer(1, 4 * mm),
        ]

    destaques = []

    if orcamento.get("instalacao_inclusa_equipamento"):
        destaques.append(
            [
                Paragraph(
                    "<b>Equipamento fornecido pela F Climatização:</b> "
                    "o preço do aparelho já inclui instalação padrão com até "
                    "2 metros de linha entre evaporadora e condensadora.",
                    normal,
                )
            ]
        )

    if adicional.get("solicitado"):
        desc = adicional.get("descricao", "").strip()
        if desc:
            texto_adicional = f"<b>Adicional informado pelo cliente:</b> {desc}. Valor sujeito à avaliação."
        else:
            texto_adicional = (
                "<b>Adicional informado pelo cliente.</b> "
                "O valor poderá ser ajustado após avaliação."
            )
        destaques.append([Paragraph(texto_adicional, normal)])

    status_documento = orcamento.get("status", "Orçamento")

    if status_documento == "Pedido de venda":
        destaques.append(
            [
                Paragraph(
                    "<b>Pedido de venda confirmado.</b> "
                    "Valores, itens e condições de pagamento estão registrados conforme este documento.",
                    normal,
                )
            ]
        )
        destaques.append(
            [
                Paragraph(
                    "<b>A conclusão da venda será registrada após o faturamento/conclusão do serviço.</b>",
                    normal,
                )
            ]
        )

    elif status_documento == "Faturado / Concluído":
        destaques.append(
            [
                Paragraph(
                    "<b>Venda concluída / faturada.</b> "
                    "Este documento apresenta os itens e as condições de pagamento registradas na venda.",
                    normal,
                )
            ]
        )

    else:
        destaques.append(
            [
                Paragraph(
                    "<b>Orçamento estimado.</b> "
                    "Valores podem variar conforme materiais, disponibilidade e condições do serviço.",
                    normal,
                )
            ]
        )

        destaques.append(
            [
                Paragraph(
                    "<b>Confirme o valor atualizado com a F Climatização antes do fechamento.</b>",
                    normal,
                )
            ]
        )

    destaque_tbl = Table(destaques, colWidths=[174 * mm])
    destaque_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7EE")),
                ("BOX", (0, 0), (-1, -1), 0.8, laranja),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#F3D8BE")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story += [Spacer(1, 2 * mm), destaque_tbl]

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# =========================================================
# ORÇAMENTO
# =========================================================

def limitar_percentual(valor):
    try:
        return max(0.0, min(100.0, float(valor or 0)))
    except Exception:
        return 0.0


def aplicar_desconto(valor, percentual):
    valor = float(valor or 0)
    percentual = limitar_percentual(percentual)
    return valor * (1 - percentual / 100.0)


def total_item(item):
    bruto = (
        float(item.get("quantidade", 0) or 0)
        * float(item.get("valor_unitario", 0) or 0)
    )
    return aplicar_desconto(
        bruto,
        item.get("desconto_percentual", 0),
    )


def calcular_total(itens):
    return sum(total_item(i) for i in itens)


def total_servicos_opcao(opcao):
    return sum(
        aplicar_desconto(
            float(servico.get("valor", 0) or 0),
            servico.get("desconto_percentual", 0),
        )
        for servico in opcao.get("servicos", [])
    )


def total_opcao_orcamento(orcamento, opcao):
    comuns = calcular_total(orcamento.get("itens", []))
    equipamento = aplicar_desconto(
        float(opcao.get("preco", 0) or 0),
        opcao.get("desconto_percentual", 0),
    )
    servicos = total_servicos_opcao(opcao)
    subtotal = comuns + equipamento + servicos
    return aplicar_desconto(
        subtotal,
        orcamento.get("desconto_percentual", 0),
    )


def total_orcamento(orcamento):
    subtotal = calcular_total(orcamento.get("itens", []))
    return aplicar_desconto(
        subtotal,
        orcamento.get("desconto_percentual", 0),
    )


def item_cobranca_km(km_total, tarifa_km):
    """Tarifa de deslocamento: distância total de ida e volta vezes preço por km."""
    km_total = float(km_total or 0)
    tarifa_km = float(tarifa_km or 0)
    if km_total <= 0 or tarifa_km <= 0:
        return None
    return montar_item(
        "Deslocamento (ida e volta)", km_total, "km", tarifa_km,
        origem="deslocamento",
    )


def controles_cobranca_km(prefixo, ativo=False, distancia=0.0):
    """Mesma experiência na criação e na edição; sem digitar formato específico."""
    cobrar = st.checkbox(
        "Cobrar km", value=bool(ativo), key=f"{prefixo}_cobrar_km",
        help="Ative para adicionar o deslocamento ao valor do orçamento.",
    )
    km = 0.0
    tarifa = float(config.get("regras", {}).get("valor_por_km", 0) or 0)
    if cobrar:
        km = st.number_input(
            "Quantos km serão rodados? (ida + volta)",
            min_value=0.0, max_value=100000.0,
            value=float(distancia or 0), step=1.0,
            format="%.1f", key=f"{prefixo}_km_rodados",
        )
        st.caption(
            f"Tarifa do ADM: {dinheiro(tarifa)} / km · "
            f"Total do deslocamento: {dinheiro(float(km) * tarifa)}"
        )
        if tarifa <= 0:
            st.warning("Defina o valor por km em ADM → Regras antes de cobrar deslocamento.")
    return cobrar, float(km), tarifa


def adicionar_cobranca_km(itens, cobrar, km, tarifa):
    if not cobrar:
        return
    if float(km or 0) <= 0:
        raise ValueError("Informe quantos km serão rodados (ida e volta).")
    if float(tarifa or 0) <= 0:
        raise ValueError("Configure o valor por km em ADM → Regras.")
    item = item_cobranca_km(km, tarifa)
    if item is not None:
        itens.append(item)


def montar_item(
    descricao,
    quantidade,
    unidade,
    valor_unitario,
    origem="manual",
    desconto_percentual=0,
):
    return {
        "id": uuid.uuid4().hex[:10],
        "descricao": descricao,
        "quantidade": float(quantidade),
        "unidade": unidade,
        "valor_unitario": float(valor_unitario),
        "desconto_percentual": limitar_percentual(desconto_percentual),
        "origem": origem,
    }


def servico_cobrado_por_ponto(nome):
    dados = config.get("servicos", {}).get(nome, {})
    return bool(dados.get("cobranca_por_ponto", "infraestrutura" in nome.lower()))


def servico_higienizacao(nome):
    """Inclui nomes personalizados como Limpeza e Higienização de ar-condicionado."""
    texto = str(nome or "").casefold()
    return "higieniza" in texto or "limpeza" in texto


def servico_com_quantidade(nome):
    """Todo serviço cadastrado pode ser contratado uma ou mais vezes."""
    return True


def unidade_servico_orcamento(nome):
    """Unidade indicada no orçamento e PDF, sem mudar o preço do catálogo."""
    if servico_cobrado_por_ponto(nome):
        return "ponto"
    texto = str(nome or "").casefold()
    if any(termo in texto for termo in (
        "higieniza", "limpeza", "instala", "desinstala", "gás", "gas",
        "manutenção", "manutencao",
    )):
        return "aparelho"
    return "serviço"


def descricao_servico_orcamento(nome, capacidade, quantidade):
    qtd = max(1, int(float(quantidade or 1)))
    unidade = unidade_servico_orcamento(nome)
    rotulo = {
        "ponto": "ponto(s)",
        "aparelho": "aparelho(s)",
        "serviço": "serviço(s)",
    }.get(unidade, "unidade(s)")
    descricao = f"{nome} • {qtd} {rotulo}"
    return f"{descricao} • {capacidade}" if capacidade else f"{descricao} • capacidade a confirmar"


# Estilo das linhas administrativas: expansão e lixeira na MESMA linha.
ESTILO_LINHAS_ADMIN = """
<style>
div[class*="st-key-fc_linha_material_"] div[data-testid="stHorizontalBlock"],
div[class*="st-key-fc_linha_registro_"] div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    align-items: flex-start !important;
    gap: .35rem !important;
    width: 100% !important;
}
div[class*="st-key-fc_linha_material_"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child,
div[class*="st-key-fc_linha_registro_"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
    min-width: 0 !important; flex: 1 1 0% !important; width: 0 !important;
}
div[class*="st-key-fc_linha_material_"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2),
div[class*="st-key-fc_linha_registro_"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
    min-width: 39px !important; flex: 0 0 42px !important; width: 42px !important;
}
div[class*="st-key-fc_linha_material_"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button,
div[class*="st-key-fc_linha_registro_"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) button {
    min-height: 40px !important; height: 40px !important;
    padding: 0 !important; color: #ff6666 !important;
    border: 1px solid #71404a !important; border-radius: 11px !important;
    background: #151923 !important;
}
</style>
"""

# =========================================================
# SESSÃO SEGURA E PERSISTENTE DO ADMINISTRADOR
# =========================================================

ADMIN_SESSION_STORAGE_KEY = "fclima_admin_session_v1"
ADMIN_SESSION_SECONDS = 14 * 24 * 60 * 60


def emitir_token_admin():
    """Token temporário assinado no servidor; não contém a senha."""
    validade = int(time.time()) + ADMIN_SESSION_SECONDS
    nonce = secrets.token_hex(12)
    corpo = f"{validade}.{nonce}"
    assinatura = hmac.new(
        str(ADMIN_KEY).encode("utf-8"), corpo.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"{corpo}.{assinatura}"


def verificar_token_admin(token):
    if not ADMIN_KEY or not isinstance(token, str):
        return False
    partes = token.split(".")
    if len(partes) != 3:
        return False
    try:
        validade = int(partes[0])
    except (ValueError, TypeError):
        return False
    if not (time.time() < validade <= time.time() + ADMIN_SESSION_SECONDS + 90):
        return False
    corpo = f"{partes[0]}.{partes[1]}"
    esperado = hmac.new(
        str(ADMIN_KEY).encode("utf-8"), corpo.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(partes[2], esperado)


def restaurar_sessao_admin():
    if st.session_state.get("admin_logado", False):
        return True
    if LOCAL_STORAGE is None:
        return False
    try:
        token = LOCAL_STORAGE.getItem(ADMIN_SESSION_STORAGE_KEY, key="fclima_auth_get")
        if isinstance(token, dict):
            token = token.get("token", "")
        if verificar_token_admin(token):
            st.session_state["admin_logado"] = True
            st.session_state["admin_token"] = token
            st.rerun()
            return True
    except Exception:
        pass
    return False


def persistir_sessao_admin():
    token = emitir_token_admin()
    st.session_state["admin_token"] = token
    if LOCAL_STORAGE is not None:
        try:
            LOCAL_STORAGE.setItem(
                ADMIN_SESSION_STORAGE_KEY, token, key="fclima_auth_set"
            )
        except Exception:
            st.warning("Login autorizado, mas o navegador não permitiu salvar a sessão.")


def encerrar_sessao_admin():
    st.session_state["admin_logado"] = False
    st.session_state.pop("admin_token", None)
    if LOCAL_STORAGE is not None:
        try:
            LOCAL_STORAGE.setItem(ADMIN_SESSION_STORAGE_KEY, "", key="fclima_auth_clear")
        except Exception:
            pass


# =========================================================
# AGENDA DE SERVIÇOS / PEDIDOS CONFIRMADOS
# =========================================================


# Disponibilidade e bloqueios ficam exclusivamente no repositório PRIVADO.
# Não existe regravação do config.json público para armazenar rotina pessoal.
AGENDA_DEFAULT = {
    "janelas_semanais": {
        str(i): [["08:00", "12:00"], ["13:00", "18:00"]] if i < 5 else []
        for i in range(7)
    },
    "excecoes": {},
    "duracao_servicos": {},
    "semanas_turnos": {},
    "passo_minutos": 30,
}
DIAS_SEMANA_AGENDA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def carregar_disponibilidade_agenda():
    dados = _consulta_sessao_github(DATA_REPO, AGENDA_FILE, json_decodificado=True)
    if dados is None:
        return copy.deepcopy(AGENDA_DEFAULT)
    if not isinstance(dados, dict):
        raise ValueError("Configuração privada da agenda inválida.")
    base = copy.deepcopy(AGENDA_DEFAULT)
    base.update(dados)
    return base


def salvar_disponibilidade_agenda(dados):
    _, sha = github_get_file(DATA_REPO, AGENDA_FILE)
    github_put_file(DATA_REPO, AGENDA_FILE, json.dumps(dados, ensure_ascii=False, indent=2),
                    "Atualiza disponibilidade e exceções da agenda", sha=sha)


def minutos_horario(hora):
    partes = str(hora).split(":")
    if len(partes) != 2:
        raise ValueError("Horário inválido")
    h, m = int(partes[0]), int(partes[1])
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError("Horário inválido")
    return 60*h+m


def formatar_minutos(valor):
    return f"{valor//60:02d}:{valor%60:02d}"


def janelas_de_texto(texto):
    """Exemplo: 08:00-12:00, 17:00-22:00."""
    if not str(texto).strip():
        return []
    resultado=[]
    for trecho in str(texto).split(','):
        pedacos = trecho.strip().replace('–','-').split('-')
        if len(pedacos) != 2:
            raise ValueError("Use o formato 08:00-12:00, 17:00-22:00")
        inicio, fim = (minutos_horario(v.strip()) for v in pedacos)
        if inicio >= fim:
            raise ValueError("O horário final precisa ser posterior ao inicial.")
        resultado.append([formatar_minutos(inicio), formatar_minutos(fim)])
    resultado.sort(key=lambda v: v[0])
    for atual, proxima in zip(resultado, resultado[1:]):
        if minutos_horario(atual[1]) > minutos_horario(proxima[0]):
            raise ValueError("As faixas de horários não podem se sobrepor.")
    return resultado


def texto_janelas(janelas):
    return ', '.join(f'{v[0]}-{v[1]}' for v in janelas)


def eh_instalacao_agenda(registro):
    desc = descricao_agendamento(registro).casefold()
    return 'instala' in desc or 'infraestrutura' in desc or 'infra ' in desc


def duracao_agendamento(registro, disponibilidade, quantidade=None, minutos_unitarios=None):
    ag = registro.get('agendamento') or {}
    if minutos_unitarios is None:
        minutos_unitarios = ag.get('minutos_por_aparelho')
    if quantidade is None:
        quantidade = ag.get('quantidade_aparelhos')
    desc = descricao_agendamento(registro).lower()
    duracoes = disponibilidade.get('duracao_servicos', {})
    if minutos_unitarios is None:
        nome = next((nome for nome in duracoes if nome.lower() in desc), None)
        minutos_unitarios = duracoes.get(nome) if nome else None
    if minutos_unitarios is None:
        minutos_unitarios = 60
    if quantidade is None:
        if 'higieniza' in desc or 'limpeza' in desc:
            quantidade = sum(
                max(1, int(float(i.get('quantidade',1) or 1)))
                for i in registro.get('itens', [])
                if 'higieniza' in str(i.get('descricao','')).lower() or 'limpeza' in str(i.get('descricao','')).lower()
            ) or 1
        else:
            quantidade = 1
    return max(30, int(minutos_unitarios)*max(1, int(quantidade)))


# Janelas que o prestador tem disponíveis no turno inverso ao trabalho principal.
JANELAS_TURNO = {
    'Primeiro turno': [['18:00', '21:30']],
    'Segundo turno': [['08:00', '11:30']],
}


def segunda_da_semana(dia):
    return dia - timedelta(days=dia.weekday())


def faixas_semana_disponiveis(dia, disponibilidade):
    """Semanas configuráveis individualmente, inclusive com semanas futuras diferentes."""
    semanas = disponibilidade.get('semanas_turnos', {})
    if not semanas:
        # Preserva a agenda anterior até o primeiro planejamento semanal.
        return disponibilidade.get('janelas_semanais', {}).get(str(dia.weekday()), [])
    plano = semanas.get(segunda_da_semana(dia).isoformat())
    if plano is None:
        # Semana ainda não configurada: não inventar disponibilidade.
        return []
    overrides = plano.get('dias_especiais', {})
    if dia.isoformat() in overrides:
        return overrides[dia.isoformat()]
    if dia.weekday() == 6:
        return []
    if dia.weekday() == 5:
        return plano.get('sabado', [])
    return plano.get('janelas', JANELAS_TURNO.get(plano.get('turno'), []))


def opcoes_hora_agenda():
    return [formatar_minutos(m) for m in range(0, 24 * 60, 30)] + ['23:59']


def selecionar_faixa_agenda(prefixo, *, inicio='08:00', fim='11:30'):
    """Seletores sem exigir texto com horários em formato especial."""
    opcoes = opcoes_hora_agenda()
    inicio = inicio if inicio in opcoes else '08:00'
    fim = fim if fim in opcoes else '11:30'
    coluna_ini, coluna_fim = st.columns(2, gap='small')
    with coluna_ini:
        hi = st.selectbox('Início', opcoes, index=opcoes.index(inicio), key=f'{prefixo}_ini')
    with coluna_fim:
        hf = st.selectbox('Fim', opcoes, index=opcoes.index(fim), key=f'{prefixo}_fim')
    return [hi, hf]


def normalizar_faixas_agenda(janelas):
    validadas=[]
    for ini, fim in janelas:
        if minutos_horario(ini) >= minutos_horario(fim):
            raise ValueError('O fim de cada intervalo deve ser posterior ao início.')
        validadas.append([ini, fim])
    validadas.sort(key=lambda v: v[0])
    for a,b in zip(validadas, validadas[1:]):
        if minutos_horario(a[1]) > minutos_horario(b[0]):
            raise ValueError('Os horários não podem se sobrepor.')
    return validadas


def disponibilidade_para_dia(dia, disponibilidade, instalacao=False):
    chave = dia.isoformat()
    excecao = disponibilidade.get('excecoes', {}).get(chave, {})
    if excecao.get('tipo') == 'indisponivel':
        return []
    if instalacao and excecao.get('tipo') == 'chuva':
        return []
    janelas = faixas_semana_disponiveis(dia, disponibilidade)
    if excecao.get('tipo') == 'horarios':
        janelas = excecao.get('janelas', [])
    return janelas


def horarios_livres_agenda(dia, duracao_min, registros, disponibilidade, registro_id=None,
                          instalacao=False, agora=None):
    if agora is None:
        agora = datetime.now(FUSO_BRASILIA).replace(tzinfo=None)
    reservas=[]
    for registro in registros:
        if str(registro.get('numero','')).zfill(4) == str(registro_id or '').zfill(4):
            continue
        if registro.get('status') != 'Pedido de venda' or servico_ja_realizado(registro):
            continue
        inicio = data_hora_agendamento(registro)
        if inicio and inicio.date() == dia:
            dur = duracao_agendamento(registro, disponibilidade)
            reservas.append((inicio.hour*60+inicio.minute, inicio.hour*60+inicio.minute+dur))
    passo = max(15, int(disponibilidade.get('passo_minutos',30) or 30))
    livres=[]
    for j_ini, j_fim in disponibilidade_para_dia(dia, disponibilidade, instalacao):
        inicio, fim = minutos_horario(j_ini), minutos_horario(j_fim)
        primeiro = ((inicio + passo - 1)//passo)*passo
        for instante in range(primeiro, fim-duracao_min+1, passo):
            candidato = datetime.combine(dia, horario_time(instante//60, instante%60))
            if candidato <= agora:
                continue
            if any(instante < fim_r and instante+duracao_min > ini_r for ini_r,fim_r in reservas):
                continue
            livres.append(formatar_minutos(instante))
    return livres


def proximo_dias_disponiveis(registros, disponibilidade, duracao, *,
                             registro_id=None, instalacao=False, dias=21):
    hoje = datetime.now(FUSO_BRASILIA).date()
    retorno={}
    for i in range(dias):
        dia = hoje + timedelta(days=i)
        livres = horarios_livres_agenda(dia, duracao, registros, disponibilidade,
                   registro_id=registro_id, instalacao=instalacao)
        if livres:
            retorno[dia]=livres
    return retorno


def seletor_horarios_agenda(numero, registro, registros, disponibilidade, prefixo,
                             *, permitir_pendente=False, selecao_inicial=True):
    """Retorna dicionário completo ou None quando não selecionado."""
    ag = registro.get('agendamento') or {}
    descricao = descricao_agendamento(registro).lower()
    higienizacao = 'higieniza' in descricao or 'limpeza' in descricao
    qtd_inicial = max(1, min(100, int(ag.get('quantidade_aparelhos') or (
        sum(max(1, int(float(i.get('quantidade', 1) or 1)))
            for i in registro.get('itens', [])
            if ('higieniza' in str(i.get('descricao','')).lower()
                or 'limpeza' in str(i.get('descricao','')).lower())) if higienizacao else 1
    ) or 1)))
    qtd = st.number_input('Quantidade de aparelhos / unidades', min_value=1, max_value=100,
                          value=qtd_inicial, step=1, key=f'{prefixo}_qtd_{numero}')
    if higienizacao:
        st.caption('Higienização: duração padrão de 1 hora por aparelho.')
    padrao = duracao_agendamento(registro, disponibilidade, quantidade=1, minutos_unitarios=None)
    minutos_salvos = ag.get('minutos_por_aparelho')
    alterar = st.checkbox('Ajustar duração por aparelho/unidade', value=bool(minutos_salvos and int(minutos_salvos)!=padrao),
                         key=f'{prefixo}_personalizar_{numero}')
    unidade_min = int(st.number_input('Minutos por aparelho/unidade', min_value=15, max_value=720,
                  value=int(minutos_salvos or padrao), step=15, key=f'{prefixo}_minutos_{numero}')) if alterar else padrao
    duracao = int(qtd) * unidade_min
    st.markdown(f'**Tempo reservado: {duracao//60}h{duracao%60:02d}** · {qtd} unidade(s) × {unidade_min} min')
    livres = proximo_dias_disponiveis(registros, disponibilidade, duracao,
                      registro_id=numero, instalacao=eh_instalacao_agenda(registro), dias=28)
    if not livres:
        st.warning('Não há intervalo livre nos próximos 28 dias. Configure seus turnos e bloqueios na aba Agenda.')
        return None
    datas=list(livres)
    dia = st.selectbox('Dia com horário livre', datas,
                       format_func=lambda d: f'{DIAS_SEMANA_AGENDA[d.weekday()]} · {d.strftime("%d/%m/%Y")}',
                       key=f'{prefixo}_dia_{numero}')
    hora = st.selectbox('Horário disponível', livres[dia], key=f'{prefixo}_hora_{numero}')
    st.caption(f'Início {hora} · término {formatar_minutos(minutos_horario(hora)+duracao)}')
    return {'data': dia.isoformat(), 'hora': hora, 'duracao_minutos': duracao,
            'quantidade_aparelhos': int(qtd), 'minutos_por_aparelho': unidade_min}


def painel_configuracao_agenda():
    secao('Horários de trabalho', 'Configure esta semana e as próximas. A Agenda fica somente para acompanhar e reagendar serviços.')
    st.caption('Selecione uma semana para definir o turno de segunda a sexta e os horários opcionais de sábado.')
    try:
        disponibilidade = carregar_disponibilidade_agenda()
    except Exception as e:
        st.error(f'Não foi possível carregar a disponibilidade privada: {e}')
        return

    hoje = datetime.now(FUSO_BRASILIA).date()
    inicio_atual = segunda_da_semana(hoje)
    # Até 16 semanas adiante; cada semana salva separadamente.
    semanas = [inicio_atual + timedelta(weeks=i) for i in range(17)]
    semana = st.selectbox(
        'Semana que deseja configurar', semanas,
        format_func=lambda d: (
            ('Esta semana' if d == inicio_atual else
             'Próxima semana' if d == inicio_atual + timedelta(weeks=1) else
             f'Semana de {d.strftime("%d/%m")}')
            + f' · {d.strftime("%d/%m")} a {(d + timedelta(days=4)).strftime("%d/%m/%Y")}'
            + (' · configurada' if d.isoformat() in disponibilidade.get('semanas_turnos', {}) else '')
        ),
        key='agenda_semana_escolhida',
    )
    chave_semana = semana.isoformat()
    plano_atual = disponibilidade.get('semanas_turnos', {}).get(chave_semana, {})
    turnos = ['Primeiro turno', 'Segundo turno']
    atual_turno = plano_atual.get('turno', 'Segundo turno')
    sabado_atual = plano_atual.get('sabado', [])
    modo_salvo = plano_atual.get('sabado_modo')
    if not modo_salvo:
        if not sabado_atual:
            modo_salvo = 'Não trabalhar'
        elif len(sabado_atual) == 1 and minutos_horario(sabado_atual[0][1]) <= 12 * 60:
            modo_salvo = 'Somente manhã'
        elif len(sabado_atual) == 1 and minutos_horario(sabado_atual[0][0]) >= 12 * 60:
            modo_salvo = 'Somente tarde'
        else:
            modo_salvo = 'Personalizar horários'
    modos_sabado = ['Não trabalhar', 'Somente manhã', 'Somente tarde', 'Personalizar horários']
    modo_sabado = st.selectbox(
        'Disponibilidade de sábado', modos_sabado,
        index=modos_sabado.index(modo_salvo) if modo_salvo in modos_sabado else 0,
        key=f'agenda_modo_sabado_{chave_semana}',
        help='É possível trabalhar apenas meio turno no sábado.',
    )
    qtd_sab = 0
    if modo_sabado == 'Personalizar horários':
        qtd_sab = st.number_input(
            'Quantidade de faixas no sábado', min_value=1, max_value=6,
            value=max(1, len(sabado_atual)), step=1,
            key=f'qtd_sab_{chave_semana}',
            help='Use + e − para adicionar ou remover horários.',
        )
    with st.form(f'agenda_semana_form_{chave_semana}'):
        turno = st.radio(
            'Turno do trabalho principal (segunda a sexta)', turnos,
            index=turnos.index(atual_turno) if atual_turno in turnos else 1,
            horizontal=True, key=f'turno_sem_{chave_semana}',
        )
        st.caption('Primeiro turno → disponível à tardinha (18:00–21:30). Segundo turno → disponível pela manhã (08:00–11:30).')
        personalizar = st.checkbox('Alterar manualmente o horário de segunda a sexta',
            value=bool(plano_atual.get('manual', False)), key=f'turno_man_{chave_semana}')
        horario_manual = None
        if personalizar:
            atual_janela = (plano_atual.get('janelas') or JANELAS_TURNO[atual_turno])[0]
            horario_manual = selecionar_faixa_agenda(f'sem_man_{chave_semana}',
                inicio=atual_janela[0], fim=atual_janela[1])
        st.markdown('**Sábado**')
        sabado = []
        if modo_sabado == 'Não trabalhar':
            st.caption('Sábado indisponível nesta semana.')
        elif modo_sabado in ('Somente manhã', 'Somente tarde'):
            # Um turno apenas; horários ajustáveis sem digitar formato especial.
            horario_padrao = (['08:00', '11:30'] if modo_sabado == 'Somente manhã'
                              else ['13:00', '17:00'])
            horario_anterior = sabado_atual[0] if (
                modo_salvo == modo_sabado and len(sabado_atual) == 1
            ) else horario_padrao
            st.caption('Ajuste início e fim caso necessário.')
            sabado.append(selecionar_faixa_agenda(
                f'sab_unico_{chave_semana}_{modo_sabado}',
                inicio=horario_anterior[0], fim=horario_anterior[1],
            ))
        else:
            for indice in range(int(qtd_sab)):
                st.caption(f'Faixa {indice+1} do sábado')
                janela = sabado_atual[indice] if indice < len(sabado_atual) else ['08:00', '11:30']
                sabado.append(selecionar_faixa_agenda(
                    f'sab_{chave_semana}_{indice}', inicio=janela[0], fim=janela[1],
                ))
        salvar_semana = st.form_submit_button('Salvar horários desta semana',
            type='primary', use_container_width=True)
    if salvar_semana:
        try:
            janelas_turno = normalizar_faixas_agenda(
                [horario_manual] if personalizar else JANELAS_TURNO[turno])
            sabado = normalizar_faixas_agenda(sabado)
            disponibilidade.setdefault('semanas_turnos', {})[chave_semana] = {
                'turno': turno, 'manual': bool(personalizar),
                'janelas': janelas_turno, 'sabado': sabado, 'sabado_modo': modo_sabado,
                'dias_especiais': copy.deepcopy(plano_atual.get('dias_especiais', {})),
            }
            salvar_disponibilidade_agenda(disponibilidade)
            st.success('Semana configurada. Os horários livres já usam essa programação.')
            st.rerun()
        except Exception as e:
            st.error(f'Não foi possível salvar os horários: {e}')
    st.caption('Semanas futuras ainda não configuradas não oferecem horários automaticamente.')
    st.markdown('**Exceção manual de um dia desta semana**')
    with st.form(f'excecao_semana_form_{chave_semana}'):
        dia_personalizado = st.selectbox('Dia', [semana + timedelta(days=i) for i in range(7)],
            format_func=lambda d: f'{DIAS_SEMANA_AGENDA[d.weekday()]} · {d.strftime("%d/%m")}',
            key=f'esc_dia_{chave_semana}')
        tipo_dia = st.radio('Disponibilidade', ['Horário personalizado', 'Dia indisponível', 'Voltar ao horário da semana'],
            key=f'esc_tipo_{chave_semana}')
        faixa_dia = selecionar_faixa_agenda(f'exc_{chave_semana}') if tipo_dia == 'Horário personalizado' else None
        confirmar_dia = st.form_submit_button('Salvar ajuste deste dia', use_container_width=True)
    if confirmar_dia:
        try:
            plano = disponibilidade.setdefault('semanas_turnos', {}).get(chave_semana)
            if plano is None:
                st.warning('Primeiro salve o turno desta semana.')
            else:
                especificos = plano.setdefault('dias_especiais', {})
                chave_dia = dia_personalizado.isoformat()
                if tipo_dia == 'Voltar ao horário da semana':
                    especificos.pop(chave_dia, None)
                elif tipo_dia == 'Dia indisponível':
                    especificos[chave_dia] = []
                else:
                    especificos[chave_dia] = normalizar_faixas_agenda([faixa_dia])
                salvar_disponibilidade_agenda(disponibilidade)
                st.success('Ajuste do dia salvo.')
                st.rerun()
        except Exception as e:
            st.error(f'Não foi possível salvar o ajuste: {e}')
    st.divider()
    st.markdown('**Tempo padrão de cada serviço**')
    st.caption('Configure a duração estimada por unidade. Higienização usa 60 minutos por aparelho quando não houver personalização.')
    duracoes_novas = {}
    with st.form('agenda_duracoes_form'):
        for nome_servico in sorted(config.get('servicos', {}), key=str.casefold):
            padrao = 60
            atual = int(disponibilidade.get('duracao_servicos', {}).get(nome_servico, padrao))
            duracoes_novas[nome_servico] = int(st.number_input(
                f'{nome_servico} · minutos por unidade', min_value=15, max_value=720,
                value=max(15, min(720, atual)), step=15,
                key=f'ag_dur_serv_{hashlib.sha1(nome_servico.encode()).hexdigest()[:12]}'))
        salvar_duracoes = st.form_submit_button('Salvar tempos dos serviços', use_container_width=True)
    if salvar_duracoes:
        try:
            disponibilidade['duracao_servicos'] = duracoes_novas
            salvar_disponibilidade_agenda(disponibilidade)
            st.success('Tempos padrão salvos.')
            st.rerun()
        except Exception as e:
            st.error(f'Não foi possível salvar os tempos: {e}')
    st.divider()
    st.markdown('**Bloquear ou liberar uma data específica**')
    d = st.date_input('Data da exceção', value=datetime.now(FUSO_BRASILIA).date(), key='agenda_exc_dia')
    tipo=st.selectbox('Regra para esta data',
           ['Indisponível para todos os serviços', 'Chuva: bloquear apenas instalações', 'Horários especiais', 'Remover bloqueio'],
           key='agenda_exc_tipo')
    faixa_especial = selecionar_faixa_agenda('agenda_excecao_data') if tipo=='Horários especiais' else None
    nota=st.text_input('Motivo (opcional)', key='agenda_exc_motivo')
    if st.button('Salvar bloqueio / exceção', key='agenda_exc_salvar'):
        try:
            if tipo=='Remover bloqueio':
                disponibilidade.setdefault('excecoes',{}).pop(d.isoformat(),None)
            else:
                regra={'Indisponível para todos os serviços':'indisponivel',
                        'Chuva: bloquear apenas instalações':'chuva','Horários especiais':'horarios'}[tipo]
                excecao={'tipo':regra,'motivo':nota.strip()}
                if regra=='horarios':
                    excecao['janelas']=normalizar_faixas_agenda([faixa_especial])
                disponibilidade.setdefault('excecoes',{})[d.isoformat()]=excecao
            # Não remove agendamentos existentes. A agenda destaca os afetados
            # para reagendamento com nova data/hora e preserva o histórico.
            salvar_disponibilidade_agenda(disponibilidade)
            afetados=reagendar_registros_bloqueados(carregar_orcamentos(), disponibilidade, d, excecao.get('tipo') if tipo!='Remover bloqueio' else '')
            if afetados:
                st.warning(f'{len(afetados)} pedido(s) precisam ser reagendados para outro horário.')
            st.success('Disponibilidade atualizada.')
            st.rerun()
        except Exception as e:
            st.error(f'Não foi possível salvar a exceção: {e}')
    excecoes = disponibilidade.get('excecoes', {})
    if excecoes:
        st.caption('Exceções cadastradas:')
        for chave, val in sorted(excecoes.items()):
            st.caption(f"{chave} · {val.get('tipo','')} · {val.get('motivo','')}")


def reagendar_registros_bloqueados(registros, disponibilidade, data_bloqueada, tipo):
    """Registros afetados continuam agendados até receber novo horário confirmado.
    Assim um bloqueio não transforma um pedido válido em pendente involuntariamente.
    """
    afetados=[]
    for registro in registros:
        dt=data_hora_agendamento(registro)
        if (registro.get('status')=='Pedido de venda' and not servico_ja_realizado(registro)
            and dt is not None and dt.date()==data_bloqueada and
            (tipo=='indisponivel' or (tipo=='chuva' and eh_instalacao_agenda(registro)))):
            afetados.append(registro)
    return afetados

def data_hora_agendamento(registro):
    ag = registro.get("agendamento") or {}
    dia = str(ag.get("data", ""))
    horario = str(ag.get("hora", ""))
    try:
        return datetime.strptime(f"{dia} {horario}", "%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return None


def descricao_agendamento(registro):
    ag = registro.get("agendamento") or {}
    if str(ag.get("servico", "")).strip():
        return str(ag["servico"]).strip()
    nomes = [str(item.get("descricao", "")).strip() for item in registro.get("itens", [])]
    for opcao in registro.get("opcoes_equipamentos", []):
        nomes.append(str(opcao.get("descricao", "")).strip())
        nomes.extend(str(sv.get("descricao", "")).strip() for sv in opcao.get("servicos", []))
    nomes = [n for n in nomes if n]
    return ", ".join(nomes[:3]) + ("…" if len(nomes) > 3 else "") if nomes else "Serviço conforme pedido"


def servico_ja_realizado(registro):
    """Venda faturada ou execução explicitamente confirmada."""
    if registro.get("status") == "Faturado / Concluído":
        return True
    return bool((registro.get("agendamento") or {}).get("realizado", False))


def agenda_admin(registros, *, compacta=False):
    """Agenda operacional: próximos, atrasados, realizados e histórico."""
    agora = datetime.now(FUSO_BRASILIA)
    hoje = agora.date()
    proximos, atrasados, realizados, sem_data = [], [], [], []

    for registro in registros:
        if registro.get("status") not in ("Pedido de venda", "Faturado / Concluído"):
            continue
        momento = data_hora_agendamento(registro)
        if momento is None:
            if registro.get("status") == "Pedido de venda":
                sem_data.append(registro)
            continue
        entrada = (momento, registro)
        if servico_ja_realizado(registro):
            realizados.append(entrada)
        elif momento.date() < hoje:
            atrasados.append(entrada)
        else:
            proximos.append(entrada)

    proximos.sort(key=lambda p: (p[0], str(p[1].get("numero", ""))))
    atrasados.sort(key=lambda p: p[0], reverse=True)
    realizados.sort(key=lambda p: p[0], reverse=True)

    st.markdown("### Minha agenda")
    st.caption("Serviços por data e horário • marque o que já foi executado")
    if st.button('Configurar turnos e horários da semana', icon=':material/schedule:',
                 key='agenda_abrir_horarios', use_container_width=True):
        st.session_state['admin_view'] = 'horarios'
        st.rerun()
    try:
        disponibilidade_agenda=carregar_disponibilidade_agenda()
        inconsistentes=[]
        for r in registros:
            dt=data_hora_agendamento(r)
            if (r.get('status')=='Pedido de venda' and not servico_ja_realizado(r) and dt and
                not disponibilidade_para_dia(dt.date(), disponibilidade_agenda, eh_instalacao_agenda(r))):
                inconsistentes.append(r)
        if inconsistentes:
            st.warning(f"{len(inconsistentes)} serviço(s) ficaram em dia bloqueado. Reagende antes de executar.")
            with st.expander('Reagendar serviços afetados por bloqueios', expanded=True):
                for r in inconsistentes:
                    num=str(r.get('numero','')).zfill(4)
                    st.markdown(f"**#{num} · {r.get('cliente',{}).get('nome','Cliente')}**")
                    if st.button('Escolher nova data e horário',key=f'bloqueado_reag_{num}'):
                        reagendar_por_impedimento(num)
    except Exception as e:
        st.error(f"Não foi possível conferir bloqueios: {e}")
    col1, col2, col3 = st.columns(3)
    col1.metric("A fazer", len(proximos))
    col2.metric("Atrasados", len(atrasados))
    col3.metric("Realizados", len(realizados))

    if sem_data:
        st.warning(f"{len(sem_data)} pedido(s) pendente(s) de agendamento.")
        with st.expander(f"Pendentes de agendamento ({len(sem_data)})"):
            for registro in sem_data:
                num=str(registro.get('numero','')).zfill(4)
                nome=registro.get('cliente',{}).get('nome','Cliente')
                st.markdown(f'**Pedido #{num} · {nome}** · {descricao_agendamento(registro)}')
                if st.button('Escolher horário',key=f'ag_pendente_{num}'):
                    editar_agendamento_pedido(num)

    grupos = [
        ("HOJE", hoje, "#ff9c35"),
        ("AMANHÃ", hoje + timedelta(days=1), "#65b5ff"),
        ("DEPOIS DE AMANHÃ", hoje + timedelta(days=2), "#8ed3aa"),
    ]
    for nome_grupo, dia, cor in grupos:
        st.markdown(f"<div style='font-size:13px;font-weight:900;color:{cor};margin-top:10px'>{nome_grupo} · {dia.strftime('%d/%m')}</div>", unsafe_allow_html=True)
        itens = [(dt, r) for dt, r in proximos if dt.date() == dia]
        if not itens:
            st.caption("Sem serviços agendados.")
        for dt, registro in itens:
            exibir_compromisso(dt, registro)

    futuros = [(dt, r) for dt, r in proximos if dt.date() > hoje + timedelta(days=2)]
    with st.expander(f"Próximos dias ({len(futuros)})", expanded=not compacta and bool(futuros)):
        if not futuros:
            st.caption("Sem outros agendamentos.")
        for dt, registro in futuros:
            exibir_compromisso(dt, registro)

    # Preservar datas antigas: não desaparecer da agenda quando o dia passa.
    with st.expander(f"Pendentes de datas anteriores ({len(atrasados)})", expanded=bool(atrasados)):
        if not atrasados:
            st.caption("Nenhum serviço antigo pendente.")
        for dt, registro in atrasados:
            exibir_compromisso(dt, registro, atrasado=True)

    with st.expander(f"Histórico de serviços realizados ({len(realizados)})", expanded=False):
        if not realizados:
            st.caption("Nenhum serviço realizado registrado.")
        for dt, registro in realizados:
            exibir_compromisso(dt, registro, realizado=True)


@st.dialog("Confirmar serviço realizado")
def confirmar_servico_realizado(numero):
    registros = carregar_orcamentos()
    registro = next((r for r in registros if str(r.get("numero", "")).zfill(4) == str(numero).zfill(4)), None)
    if registro is None or registro.get("status") != "Pedido de venda":
        st.warning("Pedido não disponível para marcar como realizado.")
        return
    st.write(f"Pedido **#{numero}** · **{registro.get('cliente', {}).get('nome', 'Cliente')}**")
    st.write(f"Serviço: **{descricao_agendamento(registro)}**")
    st.info("Marcar como realizado confirma a execução do serviço, mas NÃO fatura a venda. Você poderá concluir a venda depois.")
    a, b = st.columns(2)
    with a:
        if st.button("Cancelar", use_container_width=True, key=f"cancel_exec_{numero}"):
            st.rerun()
    with b:
        if st.button("Sim, serviço realizado", type="primary", use_container_width=True, key=f"ok_exec_{numero}"):
            ag = registro.setdefault("agendamento", {})
            ag["realizado"] = True
            ag["realizado_em"] = datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M")
            registro["atualizado_em"] = ag["realizado_em"]
            try:
                salvar_orcamentos(registros)
                st.rerun()
            except Exception as e:
                st.error(f"Não foi possível salvar a execução: {e}")


@st.dialog("Concluir venda do serviço")
def confirmar_faturamento_agenda(numero):
    registros = carregar_orcamentos()
    registro = next((r for r in registros if str(r.get("numero", "")).zfill(4) == str(numero).zfill(4)), None)
    if registro is None or registro.get("status") != "Pedido de venda":
        st.warning("Pedido não disponível para conclusão.")
        return
    st.write(f"Pedido **#{numero}** · **{registro.get('cliente', {}).get('nome', 'Cliente')}**")
    st.caption("Ao confirmar, o pedido passará para Vendas concluídas e será incluído na Central de Faturamento.")
    pagamento = registro.get("pagamento_pedido") or {}
    forma_inicial = pagamento.get("forma", FORMAS_PAGAMENTO[0])
    if forma_inicial not in FORMAS_PAGAMENTO:
        forma_inicial = FORMAS_PAGAMENTO[0]
    forma = st.selectbox("Forma de pagamento", FORMAS_PAGAMENTO, index=FORMAS_PAGAMENTO.index(forma_inicial), key=f"fat_ag_forma_{numero}")
    parcelas = 1
    if pagamento_exige_parcelas(forma):
        parcelas = st.number_input("Parcelas", min_value=2, max_value=60, value=max(2, min(60, int(pagamento.get('parcelas', 2) or 2))), key=f"fat_ag_parcelas_{numero}")
    obs = st.text_input("Observação do pagamento", value=pagamento.get("observacao", ""), key=f"fat_ag_obs_{numero}")
    a, b = st.columns(2)
    with a:
        if st.button("Cancelar", use_container_width=True, key=f"cancel_fat_ag_{numero}"):
            st.rerun()
    with b:
        if st.button("Confirmar conclusão", type="primary", use_container_width=True, key=f"ok_fat_ag_{numero}"):
            if len(registro.get("opcoes_equipamentos", [])) > 1:
                st.error("Escolha somente uma opção de equipamento antes de concluir a venda na aba Orçamentos.")
                return
            agora_texto = datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M")
            ag = registro.setdefault("agendamento", {})
            ag["realizado"] = True
            ag.setdefault("realizado_em", agora_texto)
            try:
                alterar_status_orcamento(registros, registro, "Faturado / Concluído", carregar_financeiro(), pagamento={"forma": forma, "parcelas": int(parcelas), "observacao": obs.strip()})
                st.rerun()
            except Exception as e:
                st.error(f"Não foi possível concluir a venda: {e}")


def exibir_compromisso(dt, registro, *, atrasado=False, realizado=False, contexto="agenda"):
    from html import escape
    nome = escape(str(registro.get("cliente", {}).get("nome", "Cliente")))
    ag = registro.get("agendamento") or {}
    cidade = registro.get("cliente", {}).get("cidade", "")
    local = escape(str(ag.get("local", "") or cidade or "Local não informado"))
    servico = escape(descricao_agendamento(registro))
    numero = str(registro.get("numero", "")).zfill(4)
    numero_html = escape(numero)
    cor = "#35c584" if realizado else "#ff7770" if atrasado else "#ff821d"
    situacao = "REALIZADO" if realizado else "PENDENTE · DATA PASSADA" if atrasado else "AGENDADO"
    duracao=int(ag.get('duracao_minutos',60) or 60)
    termino=dt+timedelta(minutes=duracao)
    st.markdown(
        f"<div style='margin:6px 0 5px;padding:12px 14px;border:1px solid #25466e;"
        f"border-left:4px solid {cor};border-radius:13px;background:#101a2a'>"
        f"<div style='font-weight:850;color:#fff;font-size:15px'>{dt.strftime('%d/%m/%Y')} · {dt.strftime('%H:%M')} — {nome}</div>"
        f"<div style='color:#75baff;font-weight:700;font-size:13px;margin-top:4px'>{servico} · até {termino.strftime('%H:%M')}</div>"
        f"<div style='color:#c6d5e8;font-size:12px;margin-top:5px'>📍 {local} · Pedido #{numero_html}</div>"
        f"<div style='font-size:11px;font-weight:800;color:{cor};margin-top:6px'>{situacao}</div>"
        f"</div>", unsafe_allow_html=True,
    )
    if registro.get("status") == "Pedido de venda":
        if realizado:
            if st.button("Concluir venda", key=f"{contexto}_faturar_{numero}", use_container_width=True):
                confirmar_faturamento_agenda(numero)
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✓ Serviço realizado", key=f"{contexto}_realizar_{numero}", use_container_width=True):
                    confirmar_servico_realizado(numero)
            with c2:
                if st.button("Concluir venda", key=f"{contexto}_faturar_{numero}", use_container_width=True):
                    confirmar_faturamento_agenda(numero)
            if st.button("⚠ Não será possível realizar · reagendar", key=f"{contexto}_reagendar_{numero}", use_container_width=True):
                reagendar_por_impedimento(numero)
    elif realizado:
        st.caption("Venda concluída · registro mantido no histórico")


@st.dialog("Confirmar alteração do pedido")
def confirmar_status_com_agenda(numero, novo_status, pagamento):
    registros = carregar_orcamentos()
    registro = next((r for r in registros if str(r.get('numero','')).zfill(4)==str(numero).zfill(4)),None)
    if registro is None:
        st.error('Documento não encontrado.')
        return
    st.write(f"Documento **#{numero}** · **{registro.get('cliente',{}).get('nome','Cliente')}**")
    st.write(f'Novo status: **{novo_status}**')
    agenda_nova=None
    if novo_status=='Pedido de venda':
        ag=registro.get('agendamento') or {}
        local=st.text_input('Endereço/local do trabalho',value=ag.get('local',''),
                           key=f'ag_local_{numero}')
        servico=st.text_area('Serviço que será executado',value=ag.get('servico','') or descricao_agendamento(registro),
                             key=f'ag_servico_{numero}',height=75)
        observacoes=st.text_input('Observações',value=ag.get('observacoes',''),key=f'ag_obs_{numero}')
        agendar_agora=st.checkbox('Definir data e horário agora',value=True,key=f'ag_agendar_{numero}')
        if agendar_agora:
            try:
                disponibilidade=carregar_disponibilidade_agenda()
                # A escolha do serviço também determina quais datas são bloqueadas por chuva.
                temporario=copy.deepcopy(registro)
                temporario['agendamento']={'servico':servico, **{k:v for k,v in ag.items() if k!='servico'}}
                horario=seletor_horarios_agenda(numero,temporario,registros,disponibilidade,'confirmar')
                if horario:
                    agenda_nova={**horario,'local':local.strip(),'servico':servico.strip(),
                                 'observacoes':observacoes.strip(),'realizado':False}
            except Exception as e:
                st.error(f'Erro ao buscar horários: {e}')
        else:
            st.info('O pedido ficará na agenda como Pendente de agendamento, até escolher uma data.')
            agenda_nova={'local':local.strip(),'servico':servico.strip(),
                         'observacoes':observacoes.strip(),'realizado':False,
                         'pendente_agendamento':True}
    c1,c2=st.columns(2)
    with c1:
        if st.button('Cancelar',use_container_width=True,key=f'cancel_status_{numero}'):
            st.rerun()
    with c2:
        if st.button('Confirmar',type='primary',use_container_width=True,key=f'ok_status_{numero}'):
            if novo_status=='Pedido de venda':
                if not (agenda_nova and agenda_nova.get('local') and agenda_nova.get('servico')):
                    st.error('Preencha local e serviço e escolha um horário livre, ou marque Pendente de agendamento.')
                    return
                if agenda_nova.get('data'):
                    disp=carregar_disponibilidade_agenda()
                    dia=date.fromisoformat(agenda_nova['data'])
                    temporario=copy.deepcopy(registro)
                    temporario['agendamento']=agenda_nova
                    candidatos=horarios_livres_agenda(dia,agenda_nova['duracao_minutos'],registros,disp,
                                registro_id=numero,instalacao=eh_instalacao_agenda(temporario))
                    if agenda_nova['hora'] not in candidatos:
                        st.error('Este horário deixou de estar disponível. Escolha outro intervalo.')
                        return
                registro['agendamento']=agenda_nova
            try:
                alterar_status_orcamento(registros,registro,novo_status,carregar_financeiro(),pagamento=pagamento)
                st.rerun()
            except Exception as e:
                st.error(f'Não foi possível confirmar: {e}')


@st.dialog("Editar agendamento")
def editar_agendamento_pedido(numero):
    registros=carregar_orcamentos()
    registro=next((r for r in registros if str(r.get('numero','')).zfill(4)==str(numero).zfill(4)),None)
    if registro is None or registro.get('status')!='Pedido de venda':
        st.warning('Pedido não disponível.')
        return
    ag=registro.get('agendamento') or {}
    local=st.text_input('Endereço/local',value=ag.get('local',''),key=f'edi_ag_loc_{numero}')
    servico=st.text_area('Serviço',value=ag.get('servico','') or descricao_agendamento(registro),key=f'edi_ag_serv_{numero}')
    obs=st.text_input('Observações',value=ag.get('observacoes',''),key=f'edi_ag_obs_{numero}')
    try:
        disponibilidade=carregar_disponibilidade_agenda()
        temporario=copy.deepcopy(registro)
        temporario['agendamento']={**ag,'servico':servico}
        novo=seletor_horarios_agenda(numero,temporario,registros,disponibilidade,'edi')
    except Exception as e:
        st.error(f'Erro ao carregar agenda: {e}')
        return
    a,b=st.columns(2)
    with a:
        if st.button('Cancelar',use_container_width=True,key=f'canc_ag_{numero}'):
            st.rerun()
    with b:
        if st.button('Salvar agendamento',type='primary',use_container_width=True,key=f'save_ag_{numero}'):
            if not novo or not local.strip() or not servico.strip():
                st.error('Informe serviço, local e escolha um horário livre.')
                return
            dia=date.fromisoformat(novo['data'])
            temporario['agendamento']={**novo,'servico':servico}
            if novo['hora'] not in horarios_livres_agenda(dia,novo['duracao_minutos'],registros,
                  disponibilidade,registro_id=numero,instalacao=eh_instalacao_agenda(temporario)):
                st.error('Horário ocupado ou indisponível. Selecione outro.')
                return
            registro['agendamento']={**ag,**novo,'local':local.strip(),'servico':servico.strip(),
                                    'observacoes':obs.strip(),'pendente_agendamento':False}
            salvar_orcamentos(registros)
            st.rerun()


@st.dialog('Impedimento · reagendar serviço')
def reagendar_por_impedimento(numero):
    """Nunca deixa o pedido sem horário: grava motivo e novo horário juntos."""
    registros=carregar_orcamentos()
    registro=next((r for r in registros if str(r.get('numero','')).zfill(4)==str(numero).zfill(4)),None)
    if not registro or registro.get('status')!='Pedido de venda':
        st.warning('Pedido indisponível para reagendar.')
        return
    ag=registro.get('agendamento') or {}
    antigo=data_hora_agendamento(registro)
    st.write(f"**{registro.get('cliente',{}).get('nome','Cliente')}** · Pedido #{numero}")
    if antigo:
        st.caption(f"Agendado anteriormente: {antigo.strftime('%d/%m/%Y %H:%M')}")
    motivo=st.selectbox('Por que o serviço não poderá ser feito?',
         ['Chuva / mau tempo','Compromisso no outro trabalho','Indisponibilidade do cliente',
          'Falta de material','Outro motivo'],key=f'imp_motivo_{numero}')
    detalhe=st.text_input('Detalhes (opcional)',key=f'imp_detalhe_{numero}')
    st.info('Escolha outro dia e horário disponível. O agendamento antigo só será substituído depois da confirmação.')
    try:
        disponibilidade=carregar_disponibilidade_agenda()
        novo=seletor_horarios_agenda(numero,registro,registros,disponibilidade,'reagendar')
    except Exception as e:
        st.error(f'Não foi possível consultar os horários: {e}')
        return
    a,b=st.columns(2)
    with a:
        if st.button('Cancelar',use_container_width=True,key=f'cancelar_imp_{numero}'):
            st.rerun()
    with b:
        if st.button('Confirmar novo agendamento',type='primary',use_container_width=True,key=f'ok_imp_{numero}'):
            if not novo:
                st.error('Selecione uma data e um horário livre. O pedido não será deixado pendente.')
                return
            dia=date.fromisoformat(novo['data'])
            if antigo and antigo.date()==dia and antigo.strftime('%H:%M')==novo['hora']:
                st.error('Escolha um horário diferente do compromisso que está sendo remarcado.')
                return
            if novo['hora'] not in horarios_livres_agenda(dia,novo['duracao_minutos'],registros,
                disponibilidade,registro_id=numero,instalacao=eh_instalacao_agenda(registro)):
                st.error('Horário não está mais livre. Escolha outra opção.')
                return
            hist=ag.get('historico_reagendamentos',[])
            hist.append({'data_anterior':ag.get('data'), 'hora_anterior':ag.get('hora'),
                        'nova_data':novo['data'], 'nova_hora':novo['hora'],
                        'motivo':motivo,'detalhes':detalhe.strip(),
                        'registrado_em':datetime.now(FUSO_BRASILIA).strftime('%d/%m/%Y %H:%M')})
            registro['agendamento']={**ag,**novo,'historico_reagendamentos':hist,
                                    'pendente_agendamento':False,'realizado':False}
            registro['atualizado_em']=datetime.now(FUSO_BRASILIA).strftime('%d/%m/%Y %H:%M')
            try:
                salvar_orcamentos(registros)
                st.rerun()
            except Exception as e:
                st.error(f'Não foi possível confirmar o reagendamento: {e}')


# =========================================================
# ADMIN - ORÇAMENTOS
# =========================================================

@st.dialog("Excluir orçamento")
def confirmar_exclusao_orcamento(numero):
    numero = str(numero).zfill(4)
    registros = carregar_orcamentos()
    registro = next((r for r in registros if str(r.get("numero", "")).zfill(4) == numero), None)
    if registro is None:
        st.info("Este orçamento já foi excluído.")
        if st.button("Fechar", key="orc_ausente_fechar"):
            st.rerun()
        return

    cliente = registro.get("cliente", {}).get("nome", "Cliente")
    st.warning(f"Excluir definitivamente o documento **{numero}** de **{cliente}**?")
    st.caption("Esta operação exclui o orçamento inteiro da Gestão Comercial. "
               "Se estiver faturado, também retira sua movimentação da Central. "
               "A numeração de outros documentos não será alterada.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", use_container_width=True, key="cancelar_orc_modal"):
            st.rerun()
    with c2:
        if st.button("Sim, excluir definitivamente", type="primary", use_container_width=True,
                     key="confirmar_orc_modal"):
            restantes = [r for r in registros if str(r.get("numero", "")).zfill(4) != numero]
            try:
                salvar_orcamentos(restantes)
            except Exception as e:
                st.error(f"Não foi possível excluir o orçamento: {e}")
                return
            try:
                financeiro_atual = carregar_financeiro()
                movimentacoes = financeiro_atual.setdefault("movimentacoes", {})
                if numero in movimentacoes:
                    movimentacoes.pop(numero, None)
                    salvar_financeiro(financeiro_atual)
            except Exception as e:
                st.error("O orçamento foi excluído, mas houve falha ao retirar o faturamento "
                         f"da Central: {e}. Use Atualizar dados da Central para conciliar.")
                return
            st.session_state["adm_orc_excluido_msg"] = f"Documento {numero} excluído definitivamente."
            st.rerun()


@st.dialog("Confirmar reinicialização da base")
def confirmar_reset_base_dialog():
    st.error("Esta ação removerá TODOS os registros comerciais ativos e os lançamentos financeiros.")
    st.caption("Um backup privado será criado antes da operação. Os custos dos cadastros serão preservados.")
    confirmacao = st.text_input("Digite RESETAR para confirmar", key="dialog_confirmar_reset")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", key="dialog_reset_cancelar", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Confirmar reset", key="dialog_reset_ok", type="primary", use_container_width=True):
            if confirmacao.strip().upper() != "RESETAR":
                st.error("Digite RESETAR.")
                return
            try:
                caminho = resetar_base_orcamentos()
                st.session_state["msg_reset_base"] = f"Base reiniciada. Backup: {caminho}"
                st.rerun()
            except Exception as exc:
                st.error(f"Não foi possível reiniciar: {exc}")


def aba_orcamentos(status_fixo="Orçamentos"):
    """Uma única interface de edição, filtrada pela aba do estágio comercial."""
    secoes = {
        "Orçamentos": (
            "Orçamentos",
            "Propostas ainda não confirmadas. Edite, confirme o pedido ou exclua.",
        ),
        "Pedidos de venda": (
            "Pedidos de venda",
            "Pedidos confirmados aguardando conclusão ou faturamento.",
        ),
        "Vendas concluídas": (
            "Vendas concluídas",
            "Vendas faturadas. Consulte, edite ou confira as condições registradas.",
        ),
    }
    if status_fixo not in secoes:
        raise ValueError("Categoria comercial inválida.")
    secao(*secoes[status_fixo])

    with tela_carregamento("Carregando gestão comercial..."):
        orcamentos = carregar_orcamentos()
        financeiro = carregar_financeiro()

    aviso_exclusao = st.session_state.pop("adm_orc_excluido_msg", None)
    if aviso_exclusao:
        st.success(aviso_exclusao)

    if status_fixo == "Orçamentos":
        if st.session_state.pop("msg_reset_base", None):
            st.success("Base reiniciada com backup privado.")
        with st.expander("Ferramentas da base"):
            st.caption("Para reiniciar o contador e apagar os registros ativos, é necessária confirmação.")
            if st.button("Reiniciar base (com backup)", key="btn_reset_base_orcamentos"):
                confirmar_reset_base_dialog()

    if not orcamentos:
        st.info("Nenhum registro comercial salvo ainda.")
        return

    # A aba já define o estágio. Não exibir um segundo seletor redundante.
    status_view = status_fixo

    mapa_status = {
        "Orçamentos": "Orçamento",
        "Pedidos de venda": "Pedido de venda",
        "Vendas concluídas": "Faturado / Concluído",
    }
    status_filtro = mapa_status[status_view]

    contagens = {
        "Orçamento": 0,
        "Pedido de venda": 0,
        "Faturado / Concluído": 0,
    }

    for item_status in orcamentos:
        estado = item_status.get("status", "Orçamento")
        if estado not in contagens:
            estado = "Orçamento"
        contagens[estado] += 1

    st.caption(
        f'Orçamentos: {contagens["Orçamento"]} • '
        f'Pedidos: {contagens["Pedido de venda"]} • '
        f'Concluídas: {contagens["Faturado / Concluído"]}'
    )

    busca = st.text_input(
        "Buscar por número, cliente ou telefone",
        key=f"adm_buscar_{status_fixo.lower().replace(' ', '_')}",
    ).strip().lower()

    filtrados = []

    for o in sorted(
        orcamentos,
        key=lambda x: str(x.get("numero", "")),
        reverse=True,
    ):
        estado = o.get("status", "Orçamento")
        if estado not in mapa_status.values():
            estado = "Orçamento"

        if estado != status_filtro:
            continue

        texto = " ".join(
            [
                str(o.get("numero", "")),
                str(o.get("cliente", {}).get("nome", "")),
                str(o.get("cliente", {}).get("telefone", "")),
            ]
        ).lower()

        if not busca or busca in texto:
            filtrados.append(o)

    if not filtrados:
        st.info(f"Nenhum registro em {status_view.lower()} com esse filtro.")
        return

    for o in filtrados:
        numero = str(o.get("numero", "----")).zfill(4)
        nome = o.get("cliente", {}).get("nome", "Cliente")
        opcoes = o.get("opcoes_equipamentos", [])

        if opcoes:
            rotulo_total = f"{len(opcoes)} opção(ões)"
        else:
            rotulo_total = dinheiro(total_orcamento(o))

        tipo_rotulo = {
            "Orçamento": "Orçamento",
            "Pedido de venda": "Pedido",
            "Faturado / Concluído": "Venda",
        }.get(o.get("status", "Orçamento"), "Orçamento")

        with st.container(key=f"fc_linha_registro_{numero}"):
            col_registro, col_lixeira = st.columns([12, 1], gap="small", vertical_alignment="top")
            with col_registro:
                painel_registro = st.expander(
                    f"{tipo_rotulo} {numero} • {nome} • {rotulo_total}"
                )
            with col_lixeira:
                if st.button(
                    "🗑", key=f"excluir_registro_comercial_{numero}",
                    help=f"Excluir {tipo_rotulo.lower()} {numero}",
                    use_container_width=True,
                ):
                    confirmar_exclusao_orcamento(numero)
        with painel_registro:
            st.caption(
                f"{o.get('data','')} • "
                f"{o.get('cliente',{}).get('telefone','')} • "
                f"{o.get('cliente',{}).get('cidade','')}"
            )

            if o.get("status") == "Pedido de venda":
                ag_atual = o.get("agendamento") or {}
                st.caption(
                    f"📅 Serviço: {ag_atual.get('data', 'Pendente de agendamento')} "
                    f"às {ag_atual.get('hora', '--:--')} · "
                    f"{ag_atual.get('local', 'Local não informado')}"
                )
                if st.button("📅 Editar data / horário / local", key=f"editar_ag_pedido_{numero}"):
                    editar_agendamento_pedido(numero)

            status_opcoes = [
                "Orçamento",
                "Pedido de venda",
                "Faturado / Concluído",
            ]
            status_atual = o.get("status", "Orçamento")
            if status_atual not in status_opcoes:
                status_atual = "Orçamento"

            novo_status = st.selectbox(
                "Status",
                status_opcoes,
                index=status_opcoes.index(status_atual),
                key=f"adm_status_{numero}",
            )

            pagamento_status = None

            precisa_pagamento = novo_status in (
                "Pedido de venda",
                "Faturado / Concluído",
            )

            if precisa_pagamento:
                pagamento_salvo = {}

                if novo_status == "Pedido de venda":
                    pagamento_salvo = copy.deepcopy(
                        o.get("pagamento_pedido", {})
                    )
                    st.markdown("#### Condição do pedido")

                else:
                    pagamento_salvo = copy.deepcopy(
                        o.get("pagamento_faturamento")
                        or o.get("pagamento_pedido")
                        or {}
                    )
                    st.markdown("#### Forma de pagamento")

                forma_salva = pagamento_salvo.get(
                    "forma",
                    FORMAS_PAGAMENTO[0],
                )
                if forma_salva not in FORMAS_PAGAMENTO:
                    forma_salva = FORMAS_PAGAMENTO[0]

                forma_pagamento = st.selectbox(
                    "Método de pagamento",
                    FORMAS_PAGAMENTO,
                    index=FORMAS_PAGAMENTO.index(forma_salva),
                    key=f"adm_pagamento_forma_{numero}_{novo_status}",
                )

                parcelas = 1
                if pagamento_exige_parcelas(forma_pagamento):
                    parcelas_salvas = int(
                        pagamento_salvo.get("parcelas", 2) or 2
                    )
                    parcelas_salvas = max(2, min(60, parcelas_salvas))

                    parcelas = st.number_input(
                        "Número de parcelas",
                        min_value=2,
                        max_value=60,
                        value=parcelas_salvas,
                        step=1,
                        key=f"adm_pagamento_parcelas_{numero}_{novo_status}",
                    )

                observacao_pagamento = st.text_input(
                    "Observação do pagamento",
                    value=pagamento_salvo.get("observacao", ""),
                    placeholder="Opcional",
                    key=f"adm_pagamento_obs_{numero}_{novo_status}",
                )

                pagamento_status = {
                    "forma": forma_pagamento,
                    "parcelas": int(parcelas),
                    "observacao": observacao_pagamento.strip(),
                }

                if status_atual == "Pedido de venda" and novo_status == "Pedido de venda":
                    if st.button(
                        "Salvar condição de pagamento do pedido",
                        use_container_width=True,
                        key=f"adm_salvar_pagamento_pedido_{numero}",
                    ):
                        try:
                            o["pagamento_pedido"] = copy.deepcopy(
                                pagamento_status
                            )
                            o["atualizado_em"] = datetime.now(
                                FUSO_BRASILIA
                            ).strftime("%d/%m/%Y %H:%M")
                            salvar_orcamentos(orcamentos)
                            st.success(
                                "Condição de pagamento do pedido salva."
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(
                                f"Erro ao salvar condição de pagamento: {e}"
                            )

            if novo_status != status_atual:
                if novo_status == "Faturado / Concluído":
                    texto_botao = "Faturar / concluir venda"
                elif novo_status == "Pedido de venda":
                    texto_botao = "Confirmar pedido de venda"
                else:
                    texto_botao = f"Aplicar status: {novo_status}"

                if st.button(
                    texto_botao,
                    type="primary",
                    use_container_width=True,
                    key=f"adm_aplicar_status_{numero}",
                ):
                    confirmar_status_com_agenda(numero, novo_status, pagamento_status)

            # ---------------------------------------------
            # DESCONTO GERAL
            # ---------------------------------------------
            desconto_geral = st.number_input(
                "Desconto no orçamento (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(o.get("desconto_percentual", 0) or 0),
                step=1.0,
                key=f"adm_desc_geral_{numero}",
            )
            o["desconto_percentual"] = float(desconto_geral)

            # ---------------------------------------------
            # ITENS COMUNS / ORÇAMENTO SIMPLES
            # ---------------------------------------------
            st.markdown("#### Itens")

            itens_editados = []

            for idx, item in enumerate(o.get("itens", [])):
                iid = item.get("id") or f"item_{idx}"

                with st.expander(
                    item.get("descricao", f"Item {idx + 1}")
                ):
                    descricao_base_adm = item.get("descricao", "")
                    if (
                        item.get("origem") == "equipamento"
                        and o.get("instalacao_inclusa_equipamento")
                    ):
                        descricao_base_adm = descricao_equipamento_com_instalacao(
                            descricao_base_adm
                        )

                    desc = st.text_input(
                        "Descrição",
                        value=descricao_base_adm,
                        key=f"adm_item_desc_{numero}_{iid}",
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        qtd = st.number_input(
                            "Quantidade",
                            min_value=0.0,
                            value=float(item.get("quantidade", 1) or 0),
                            step=0.5 if item.get("unidade") == "metro" else 1.0,
                            key=f"adm_item_qtd_{numero}_{iid}",
                        )

                    with c2:
                        unidade_atual = item.get("unidade", "unidade")
                        if unidade_atual not in UNIDADES_ITEM:
                            unidade_atual = "unidade"

                        unidade = st.selectbox(
                            "Unidade",
                            UNIDADES_ITEM,
                            index=UNIDADES_ITEM.index(unidade_atual),
                            key=f"adm_item_un_{numero}_{iid}",
                        )

                    c3, c4 = st.columns(2)

                    with c3:
                        valor_unitario = st.number_input(
                            "Valor unitário",
                            min_value=0.0,
                            value=float(item.get("valor_unitario", 0) or 0),
                            step=1.0,
                            key=f"adm_item_valor_{numero}_{iid}",
                        )

                    with c4:
                        desconto_item = st.number_input(
                            "Desconto (%)",
                            min_value=0.0,
                            max_value=100.0,
                            value=float(item.get("desconto_percentual", 0) or 0),
                            step=1.0,
                            key=f"adm_item_descpct_{numero}_{iid}",
                        )

                    preview = aplicar_desconto(
                        float(qtd) * float(valor_unitario),
                        desconto_item,
                    )
                    st.caption(f"Total do item: {dinheiro(preview)}")

                    remover = st.checkbox(
                        "Remover item",
                        key=f"adm_item_del_{numero}_{iid}",
                    )

                    if not remover:
                        itens_editados.append(
                            {
                                "id": iid,
                                "descricao": desc,
                                "quantidade": float(qtd),
                                "unidade": unidade,
                                "valor_unitario": float(valor_unitario),
                                "desconto_percentual": float(desconto_item),
                                "origem": item.get("origem", "manual"),
                            }
                        )

            # ---------------------------------------------
            # OPÇÕES COMPARATIVAS
            # ---------------------------------------------
            opcoes_editadas = []

            if opcoes:
                st.markdown("#### Opções de aparelhos")

                for idx, opcao in enumerate(opcoes):
                    oid = str(opcao.get("id", f"opcao_{idx}"))

                    with st.expander(
                        opcao.get("descricao", f"Opção {idx + 1}")
                    ):
                        desc_opcao = st.text_input(
                            "Descrição do aparelho",
                            value=opcao.get("descricao", ""),
                            key=f"adm_op_desc_{numero}_{oid}",
                        )

                        c1, c2 = st.columns(2)
                        with c1:
                            preco_opcao = st.number_input(
                                "Preço do aparelho",
                                min_value=0.0,
                                value=float(opcao.get("preco", 0) or 0),
                                step=10.0,
                                key=f"adm_op_preco_{numero}_{oid}",
                            )

                        with c2:
                            desc_opcao_pct = st.number_input(
                                "Desconto do aparelho (%)",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(opcao.get("desconto_percentual", 0) or 0),
                                step=1.0,
                                key=f"adm_op_descpct_{numero}_{oid}",
                            )

                        servicos_editados = []

                        if opcao.get("servicos"):
                            st.caption("Serviços desta opção")

                        for sidx, servico in enumerate(opcao.get("servicos", [])):
                            sdesc = servico.get("descricao", f"Serviço {sidx + 1}")
                            sc1, sc2 = st.columns(2)

                            with sc1:
                                sval = st.number_input(
                                    sdesc,
                                    min_value=0.0,
                                    value=float(servico.get("valor", 0) or 0),
                                    step=1.0,
                                    key=f"adm_op_serv_val_{numero}_{oid}_{sidx}",
                                )

                            with sc2:
                                sdesconto = st.number_input(
                                    f"Desconto (%) — {sdesc}",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=float(servico.get("desconto_percentual", 0) or 0),
                                    step=1.0,
                                    key=f"adm_op_serv_desc_{numero}_{oid}_{sidx}",
                                )

                            remover_serv = st.checkbox(
                                f"Remover {sdesc}",
                                key=f"adm_op_serv_del_{numero}_{oid}_{sidx}",
                            )

                            if not remover_serv:
                                servicos_editados.append(
                                    {
                                        "descricao": sdesc,
                                        "valor": float(sval),
                                        "desconto_percentual": float(sdesconto),
                                    }
                                )

                        remover_opcao = st.checkbox(
                            "Remover esta opção de aparelho",
                            key=f"adm_op_del_{numero}_{oid}",
                        )

                        if not remover_opcao:
                            nova_opcao = copy.deepcopy(opcao)
                            nova_opcao["descricao"] = desc_opcao
                            nova_opcao["preco"] = float(preco_opcao)
                            nova_opcao["desconto_percentual"] = float(desc_opcao_pct)
                            nova_opcao["servicos"] = servicos_editados
                            nova_opcao["total_servicos"] = sum(
                                aplicar_desconto(
                                    s.get("valor", 0),
                                    s.get("desconto_percentual", 0),
                                )
                                for s in servicos_editados
                            )
                            opcoes_editadas.append(nova_opcao)

                            preview_orc = copy.deepcopy(o)
                            preview_orc["itens"] = itens_editados
                            preview_orc["opcoes_equipamentos"] = [nova_opcao]
                            preview_orc["desconto_percentual"] = float(desconto_geral)

                            st.caption(
                                f"Total desta opção: "
                                f"{dinheiro(total_opcao_orcamento(preview_orc, nova_opcao))}"
                            )

            # ---------------------------------------------
            # ADICIONAR ITEM
            # Cadastrado ou novo, salvando no catálogo correto
            # ---------------------------------------------
            with st.expander("Adicionar item"):
                tipo_novo_item = st.radio(
                    "Tipo de item",
                    ["Material", "Serviço"],
                    horizontal=True,
                    key=f"adm_add_tipo_{numero}",
                )

                origem_novo_item = st.radio(
                    "Origem",
                    ["Cadastrado", "Criar novo"],
                    horizontal=True,
                    key=f"adm_add_origem_{numero}",
                )

                item_para_adicionar = None
                novo_catalogo = None

                # =================================================
                # MATERIAL
                # =================================================
                if tipo_novo_item == "Material":
                    if origem_novo_item == "Cadastrado":
                        materiais_ativos = {
                            nome_mat: dados_mat
                            for nome_mat, dados_mat
                            in config.get("materiais", {}).items()
                            if dados_mat.get("ativo", True)
                        }

                        if not materiais_ativos:
                            st.info("Nenhum material ativo cadastrado.")
                        else:
                            material_nome = st.selectbox(
                                "Material",
                                list(materiais_ativos.keys()),
                                key=f"adm_add_mat_nome_{numero}",
                            )

                            material_dados = materiais_ativos[material_nome]
                            unidade_material = material_dados.get(
                                "unidade",
                                "unidade",
                            )
                            preco_material = float(
                                material_dados.get("preco", 0) or 0
                            )

                            mc1, mc2 = st.columns(2)

                            with mc1:
                                material_qtd = st.number_input(
                                    f"Quantidade ({unidade_material})",
                                    min_value=0.0,
                                    value=1.0,
                                    step=(
                                        0.5
                                        if unidade_material == "metro"
                                        else 1.0
                                    ),
                                    key=f"adm_add_mat_qtd_{numero}",
                                )

                            with mc2:
                                material_desc = st.number_input(
                                    "Desconto (%)",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=0.0,
                                    step=1.0,
                                    key=f"adm_add_mat_desc_{numero}",
                                )

                            st.caption(
                                f"Preço cadastrado: {dinheiro(preco_material)} / "
                                f"{unidade_material}"
                            )

                            if material_qtd > 0:
                                item_para_adicionar = montar_item(
                                    material_nome,
                                    material_qtd,
                                    unidade_material,
                                    preco_material,
                                    origem="material",
                                    desconto_percentual=material_desc,
                                )

                    else:
                        novo_mat_nome = st.text_input(
                            "Nome do novo material",
                            key=f"adm_novo_mat_nome_{numero}",
                        ).strip()

                        nm1, nm2 = st.columns(2)

                        with nm1:
                            novo_mat_un = st.selectbox(
                                "Unidade",
                                UNIDADES_ITEM,
                                key=f"adm_novo_mat_un_{numero}",
                            )

                        with nm2:
                            novo_mat_preco = st.number_input(
                                "Preço cadastrado",
                                min_value=0.0,
                                value=0.0,
                                step=1.0,
                                key=f"adm_novo_mat_preco_{numero}",
                            )

                        nm3, nm4 = st.columns(2)

                        with nm3:
                            novo_mat_qtd = st.number_input(
                                "Quantidade no orçamento",
                                min_value=0.0,
                                value=1.0,
                                step=(
                                    0.5
                                    if novo_mat_un == "metro"
                                    else 1.0
                                ),
                                key=f"adm_novo_mat_qtd_{numero}",
                            )

                        with nm4:
                            novo_mat_desc = st.number_input(
                                "Desconto (%)",
                                min_value=0.0,
                                max_value=100.0,
                                value=0.0,
                                step=1.0,
                                key=f"adm_novo_mat_desc_{numero}",
                            )

                        if novo_mat_nome and novo_mat_qtd > 0:
                            item_para_adicionar = montar_item(
                                novo_mat_nome,
                                novo_mat_qtd,
                                novo_mat_un,
                                novo_mat_preco,
                                origem="material",
                                desconto_percentual=novo_mat_desc,
                            )

                            novo_catalogo = {
                                "tipo": "material",
                                "nome": novo_mat_nome,
                                "dados": {
                                    "unidade": novo_mat_un,
                                    "preco": float(novo_mat_preco),
                                    "ativo": True,
                                },
                            }

                # =================================================
                # SERVIÇO
                # =================================================
                else:
                    if origem_novo_item == "Cadastrado":
                        servicos_ativos = {
                            nome_serv: dados_serv
                            for nome_serv, dados_serv
                            in config.get("servicos", {}).items()
                            if dados_serv.get("ativo", True)
                        }

                        if not servicos_ativos:
                            st.info("Nenhum serviço ativo cadastrado.")
                        else:
                            servico_nome = st.selectbox(
                                "Serviço",
                                list(servicos_ativos.keys()),
                                key=f"adm_add_serv_nome_{numero}",
                            )

                            capacidade_serv = st.selectbox(
                                "Capacidade",
                                CAPACIDADES,
                                key=f"adm_add_serv_cap_{numero}",
                            )

                            preco_servico = float(
                                servicos_ativos[servico_nome]
                                .get("precos", {})
                                .get(capacidade_serv, 0)
                                or 0
                            )

                            sc1, sc2 = st.columns(2)

                            with sc1:
                                servico_qtd = st.number_input(
                                    "Quantidade",
                                    min_value=0.0,
                                    value=1.0,
                                    step=1.0,
                                    key=f"adm_add_serv_qtd_{numero}",
                                )

                            with sc2:
                                servico_desc = st.number_input(
                                    "Desconto (%)",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=0.0,
                                    step=1.0,
                                    key=f"adm_add_serv_desc_{numero}",
                                )

                            st.caption(
                                f"Preço cadastrado para {capacidade_serv}: "
                                f"{dinheiro(preco_servico)}"
                            )

                            if servico_qtd > 0:
                                item_para_adicionar = montar_item(
                                    descricao_servico_orcamento(servico_nome, capacidade_serv, servico_qtd),
                                    servico_qtd,
                                    unidade_servico_orcamento(servico_nome),
                                    preco_servico,
                                    origem="servico",
                                    desconto_percentual=servico_desc,
                                )

                    else:
                        novo_serv_nome = st.text_input(
                            "Nome do novo serviço",
                            key=f"adm_novo_serv_nome_{numero}",
                        ).strip()

                        novo_serv_desc_texto = st.text_input(
                            "Descrição curta",
                            key=f"adm_novo_serv_descricao_{numero}",
                        )

                        st.caption("Defina o preço-base por capacidade.")

                        novos_precos_serv = {}

                        sp1, sp2 = st.columns(2)

                        for cap_idx, cap in enumerate(CAPACIDADES):
                            coluna = sp1 if cap_idx % 2 == 0 else sp2
                            with coluna:
                                novos_precos_serv[cap] = st.number_input(
                                    cap,
                                    min_value=0.0,
                                    value=0.0,
                                    step=10.0,
                                    key=f"adm_novo_serv_preco_{numero}_{cap}",
                                )

                        capacidade_novo_serv = st.selectbox(
                            "Capacidade usada neste orçamento",
                            CAPACIDADES,
                            key=f"adm_novo_serv_cap_{numero}",
                        )

                        ns1, ns2 = st.columns(2)

                        with ns1:
                            novo_serv_qtd = st.number_input(
                                "Quantidade no orçamento",
                                min_value=0.0,
                                value=1.0,
                                step=1.0,
                                key=f"adm_novo_serv_qtd_{numero}",
                            )

                        with ns2:
                            novo_serv_desconto = st.number_input(
                                "Desconto (%)",
                                min_value=0.0,
                                max_value=100.0,
                                value=0.0,
                                step=1.0,
                                key=f"adm_novo_serv_descpct_{numero}",
                            )

                        if novo_serv_nome and novo_serv_qtd > 0:
                            preco_atual_serv = float(
                                novos_precos_serv.get(
                                    capacidade_novo_serv,
                                    0,
                                )
                                or 0
                            )

                            item_para_adicionar = montar_item(
                                f"{novo_serv_nome} • {capacidade_novo_serv}",
                                novo_serv_qtd,
                                "serviço",
                                preco_atual_serv,
                                origem="servico",
                                desconto_percentual=novo_serv_desconto,
                            )

                            novo_catalogo = {
                                "tipo": "servico",
                                "nome": novo_serv_nome,
                                "dados": {
                                    "ativo": True,
                                    "mostrar_cliente": True,
                                    "descricao": novo_serv_desc_texto.strip(),
                                    "precos": {
                                        cap: float(valor)
                                        for cap, valor
                                        in novos_precos_serv.items()
                                    },
                                },
                            }

                adicionar_novo = st.checkbox(
                    (
                        "Adicionar ao orçamento e salvar no catálogo"
                        if origem_novo_item == "Criar novo"
                        else "Adicionar este item ao orçamento"
                    ),
                    key=f"adm_add_confirmar_{numero}",
                )

            preview = copy.deepcopy(o)
            preview["itens"] = itens_editados[:]
            preview["opcoes_equipamentos"] = opcoes_editadas if opcoes else []
            preview["desconto_percentual"] = float(desconto_geral)

            if adicionar_novo and item_para_adicionar:
                preview["itens"].append(item_para_adicionar)

            if preview.get("opcoes_equipamentos"):
                st.markdown("**Totais finais das opções**")
                for opcao in preview["opcoes_equipamentos"]:
                    st.write(
                        f'{opcao.get("descricao","Aparelho")}: '
                        f'**{dinheiro(total_opcao_orcamento(preview, opcao))}**'
                    )
            else:
                subtotal = calcular_total(preview.get("itens", []))
                st.caption(f"Subtotal: {dinheiro(subtotal)}")
                st.metric(
                    "Total final",
                    dinheiro(total_orcamento(preview)),
                )

            # -------------------------------------------------
            # SALVAMENTO AUTOMÁTICO DO ORÇAMENTO
            # -------------------------------------------------
            itens_finais_auto = itens_editados[:]
            if adicionar_novo and item_para_adicionar:
                itens_finais_auto.append(item_para_adicionar)

            estado_auto = {
                "itens": itens_finais_auto,
                "opcoes_equipamentos": (
                    opcoes_editadas if opcoes else []
                ),
                "desconto_percentual": float(desconto_geral),
            }

            sig_auto = assinatura_dados(estado_auto)
            chave_sig_auto = f"_autosave_orc_{numero}"
            sig_anterior = st.session_state.get(chave_sig_auto)

            if sig_anterior is None:
                st.session_state[chave_sig_auto] = sig_auto

            elif sig_anterior != sig_auto:
                try:
                    if adicionar_novo and novo_catalogo:
                        nome_catalogo = novo_catalogo["nome"]
                        tipo_catalogo = novo_catalogo["tipo"]

                        if tipo_catalogo == "material":
                            config.setdefault("materiais", {})[
                                nome_catalogo
                            ] = novo_catalogo["dados"]
                        elif tipo_catalogo == "servico":
                            config.setdefault("servicos", {})[
                                nome_catalogo
                            ] = novo_catalogo["dados"]

                        salvar_config()

                    o["itens"] = itens_finais_auto
                    o["opcoes_equipamentos"] = (
                        opcoes_editadas if opcoes else []
                    )
                    o["desconto_percentual"] = float(desconto_geral)
                    o["atualizado_em"] = datetime.now(
                        FUSO_BRASILIA
                    ).strftime("%d/%m/%Y %H:%M")

                    salvar_orcamentos(orcamentos)

                    # Se já está faturado, refaz a central com os valores novos.
                    if o.get("status") == "Faturado / Concluído":
                        fin_auto = carregar_financeiro()
                        sincronizar_central_faturamento(
                            orcamentos,
                            fin_auto,
                        )

                    st.session_state[chave_sig_auto] = sig_auto
                    st.caption("✓ Alterações deste registro salvas automaticamente.")
                except Exception as e:
                    st.error(f"Erro no salvamento automático: {e}")
            else:
                st.caption("✓ Salvamento automático deste registro ativo.")

            csave, cpdf = st.columns(2)

            with csave:
                st.caption(
                    "Não é necessário salvar manualmente. "
                    "Alterações de itens, preços e descontos são gravadas automaticamente."
                )

            with cpdf:
                pdf_bytes = gerar_pdf(preview)
                compartilhar_pdf(
                    pdf_bytes,
                    f"orcamento_{numero}_F_Climatizacao.pdf",
                    titulo=f"Orçamento {numero} - F Climatização",
                )


# =========================================================
# ADMIN - SERVIÇOS
# =========================================================

def aba_servicos():
    secao(
        "Serviços",
        "Crie, renomeie, remova e edite preços dos serviços.",
    )

    st.caption(
        "Renomear altera o serviço existente; excluir remove do catálogo após salvar. "
        "Orçamentos já salvos mantêm os dados registrados até serem editados."
    )

    reconstruidos = {}

    for idx, (nome, dados) in enumerate(list(config["servicos"].items())):
        with st.expander(nome):
            novo_nome = st.text_input(
                "Nome do serviço",
                value=nome,
                key=f"serv_nome_{idx}_{nome}",
            ).strip()

            dados["ativo"] = st.checkbox(
                "Ativo",
                value=bool(dados.get("ativo", True)),
                key=f"serv_ativo_{idx}_{nome}",
            )

            dados["mostrar_cliente"] = st.checkbox(
                "Disponível para o cliente",
                value=bool(dados.get("mostrar_cliente", True)),
                key=f"serv_cliente_{idx}_{nome}",
            )

            dados["descricao"] = st.text_area(
                "Descrição",
                value=dados.get("descricao", ""),
                key=f"serv_desc_{idx}_{nome}",
            )
            dados["cobranca_por_ponto"] = st.checkbox(
                "Cobrar por ponto (quantidade × valor unitário)",
                value=bool(dados.get("cobranca_por_ponto", "infraestrutura" in nome.lower())),
                key=f"serv_por_ponto_{idx}_{nome}",
                help="Ideal para instalação de infraestrutura. O valor informado para cada capacidade é cobrado por ponto.",
            )
            if dados["cobranca_por_ponto"]:
                st.caption("Os preços abaixo são por ponto. Ex.: 4 pontos × R$ 250 = R$ 1.000.")

            dados.setdefault("precos", {})

            if dados["cobranca_por_ponto"]:
                preco_atual_ponto = float(
                    dados.get("preco_por_ponto", 0)
                    or next((v for v in dados["precos"].values() if float(v or 0) > 0), 0)
                    or 0
                )
                valor_ponto = st.number_input(
                    "Valor de cada ponto (R$)",
                    min_value=0.0,
                    value=preco_atual_ponto,
                    step=10.0,
                    key=f"serv_ponto_preco_{idx}_{nome}",
                )
                dados["preco_por_ponto"] = float(valor_ponto)
                dados["precos"] = {cap: float(valor_ponto) for cap in CAPACIDADES}
            else:
                c1, c2 = st.columns(2)
                for cap_idx, cap in enumerate(CAPACIDADES):
                    coluna = c1 if cap_idx % 2 == 0 else c2
                    with coluna:
                        dados["precos"][cap] = st.number_input(
                            cap,
                            min_value=0.0,
                            value=float(dados["precos"].get(cap, 0) or 0),
                            step=10.0,
                            key=f"serv_preco_{idx}_{nome}_{cap}",
                        )

            if st.button("Excluir serviço", key=f"serv_excluir_{idx}_{nome}"):
                confirmar_exclusao_servico(nome)

            chave_final = novo_nome or nome

            if chave_final in reconstruidos and chave_final != nome:
                st.warning(
                    "Já existe outro serviço com esse nome. "
                    "Use um nome diferente antes de salvar."
                )
                chave_final = nome

            reconstruidos[chave_final] = dados

    config["servicos"] = reconstruidos

    with st.expander("Adicionar novo serviço"):
        novo_serv_nome = st.text_input(
            "Nome do novo serviço",
            key="novo_serv_catalogo_nome",
        ).strip()

        novo_serv_desc = st.text_area(
            "Descrição",
            key="novo_serv_catalogo_desc",
        )

        novo_serv_ativo = st.checkbox(
            "Ativo",
            value=True,
            key="novo_serv_catalogo_ativo",
        )

        novo_serv_cliente = st.checkbox(
            "Disponível para o cliente",
            value=True,
            key="novo_serv_catalogo_cliente",
        )
        novo_serv_pontos = st.checkbox(
            "Cobrar por ponto (infraestrutura)",
            value="infraestrutura" in novo_serv_nome.lower(),
            key="novo_serv_catalogo_por_ponto",
        )
        if novo_serv_pontos:
            st.caption("Cadastre o preço de UM ponto. No orçamento será informada a quantidade de pontos.")

        novos_precos = {}
        preco_novo_ponto = 0.0
        if novo_serv_pontos:
            preco_novo_ponto = st.number_input(
                "Preço por ponto (R$)", min_value=0.0, value=0.0, step=10.0,
                key="novo_serv_catalogo_preco_ponto",
            )
            novos_precos = {cap: float(preco_novo_ponto) for cap in CAPACIDADES}
        else:
            c1, c2 = st.columns(2)
            for cap_idx, cap in enumerate(CAPACIDADES):
                coluna = c1 if cap_idx % 2 == 0 else c2
                with coluna:
                    novos_precos[cap] = st.number_input(
                        cap,
                        min_value=0.0,
                        value=0.0,
                        step=10.0,
                        key=f"novo_serv_catalogo_preco_{cap}",
                    )

        if st.button(
            "Adicionar serviço",
            type="primary",
            use_container_width=True,
            key="btn_novo_serv_catalogo",
        ):
            if not novo_serv_nome:
                st.warning("Informe o nome do serviço.")
            elif novo_serv_nome in config["servicos"]:
                st.warning("Já existe um serviço com esse nome.")
            else:
                config["servicos"][novo_serv_nome] = {
                    "ativo": bool(novo_serv_ativo),
                    "mostrar_cliente": bool(novo_serv_cliente),
                    "descricao": novo_serv_desc.strip(),
                    "cobranca_por_ponto": bool(novo_serv_pontos),
                    "preco_por_ponto": float(preco_novo_ponto),
                    "precos": {
                        cap: float(valor)
                        for cap, valor in novos_precos.items()
                    },
                }

                try:
                    salvar_config()
                    st.success("Serviço criado e salvo.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar serviço: {e}")


@st.dialog("Excluir serviço")
def confirmar_exclusao_servico(nome):
    st.warning(f"Excluir permanentemente **{nome}** do catálogo de serviços?")
    st.caption("Orçamentos emitidos permanecem no histórico.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", key="cancelar_servico_dialog", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Excluir definitivamente", key="excluir_servico_dialog", type="primary", use_container_width=True):
            if nome not in config.get("servicos", {}):
                st.warning("Serviço não encontrado.")
                return
            original = copy.deepcopy(config["servicos"])
            config["servicos"].pop(nome, None)
            try:
                salvar_config()
                st.session_state["_autosave_sig_painel"] = assinatura_dados(config)
                st.rerun()
            except Exception as exc:
                config["servicos"] = original
                st.error(f"Não foi possível excluir: {exc}")


@st.dialog("Excluir aparelho")
def confirmar_exclusao_aparelho(eid):
    aparelho = config.get("equipamentos", {}).get(str(eid))
    if not aparelho:
        st.warning("Aparelho não encontrado.")
        return
    st.warning(f"Excluir permanentemente **{nome_equipamento(aparelho)}**?")
    st.caption("O aparelho deixa de aparecer em novos orçamentos. Documentos anteriores permanecem.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancelar", key="cancel_eq_dialog", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Excluir definitivamente", key="ok_eq_dialog", type="primary", use_container_width=True):
            anterior = copy.deepcopy(config["equipamentos"])
            config["equipamentos"].pop(str(eid), None)
            try:
                salvar_config()
                fin = carregar_financeiro()
                fin.setdefault("custos_equipamentos", {}).pop(str(eid), None)
                salvar_financeiro(fin)
                st.session_state["_autosave_sig_painel"] = assinatura_dados(config)
                st.rerun()
            except Exception as exc:
                config["equipamentos"] = anterior
                st.error(f"Falha na exclusão: {exc}")


# =========================================================
# ADMIN - MATERIAIS
# =========================================================

@st.dialog("Confirmar exclusão de material")
def confirmar_exclusao_material(nome):
    st.warning(f"Você deseja excluir definitivamente o material **{nome}**?")
    st.caption("O cadastro e seu custo privado serão excluídos. Os itens já registrados em orçamentos antigos permanecem no histórico.")
    c_cancelar, c_excluir = st.columns(2)
    with c_cancelar:
        if st.button("Cancelar", use_container_width=True, key="cancelar_exclusao_mat_dialog"):
            st.rerun()
    with c_excluir:
        if st.button("Sim, excluir definitivamente", type="primary", use_container_width=True, key="confirmar_exclusao_mat_dialog"):
            if nome not in config.get("materiais", {}):
                st.info("O material já não existe no catálogo.")
                return
            financeiro_atual = carregar_financeiro()
            catalogo_anterior = copy.deepcopy(config["materiais"])
            novo_catalogo = copy.deepcopy(catalogo_anterior)
            novo_catalogo.pop(nome, None)
            custos_anteriores = copy.deepcopy(financeiro_atual.get("custos_materiais", {}))
            config["materiais"] = novo_catalogo
            try:
                # Primeiro efetiva a exclusão do catálogo; falha remota restaura
                # a cópia local, sem fingir que o material foi excluído.
                salvar_config()
            except Exception as exc:
                config["materiais"] = catalogo_anterior
                st.error(f"Não foi possível excluir: {exc}")
                return
            financeiro_atual.setdefault("custos_materiais", {}).pop(nome, None)
            try:
                salvar_financeiro(financeiro_atual)
            except Exception as exc:
                # O material foi excluído com sucesso; informe explicitamente
                # se apenas a limpeza do custo privado falhou.
                st.error(f"Material excluído, mas não foi possível limpar o custo privado: {exc}")
                return
            st.session_state["_autosave_sig_painel"] = assinatura_dados(config)
            st.session_state["_autosave_fin_sig_materiais"] = assinatura_dados({
                "custos_materiais": financeiro_atual.get("custos_materiais", {}),
                "custos_equipamentos": financeiro_atual.get("custos_equipamentos", {}),
            })
            st.session_state["material_excluido_msg"] = f"Material '{nome}' excluído definitivamente."
            st.rerun()


def aba_materiais():
    secao(
        "Materiais",
        "Edite nome, unidade, preço e disponibilidade do catálogo interno.",
    )

    mensagem = st.session_state.pop("material_excluido_msg", None)
    if mensagem:
        st.success(mensagem)

    st.caption(f"{len(config.get('materiais', {}))} materiais cadastrados.")

    financeiro = carregar_financeiro()
    custos_privados = financeiro.setdefault("custos_materiais", {})
    # Capture persisted state before widgets mutate catalog and costs.
    # This makes even the first edit of a new session persist reliably.
    st.session_state.setdefault(
        "_autosave_sig_painel", assinatura_dados(config)
    )
    st.session_state.setdefault(
        "_autosave_fin_sig_materiais",
        assinatura_dados({
            "custos_materiais": financeiro.get("custos_materiais", {}),
            "custos_equipamentos": financeiro.get("custos_equipamentos", {}),
        }),
    )

    reconstruidos = {}

    for idx, (nome, dados) in enumerate(list(config["materiais"].items())):
        with st.container(key=f"fc_linha_material_{idx}"):
            col_item, col_lixeira = st.columns([12, 1], gap="small", vertical_alignment="top")
            with col_item:
                painel_material = st.expander(nome)
            with col_lixeira:
                if st.button(
                    "🗑", key=f"lixeira_material_lista_{idx}_{nome}",
                    help=f"Excluir material {nome}", use_container_width=True,
                ):
                    confirmar_exclusao_material(nome)
        with painel_material:
            novo_nome = st.text_input(
                "Nome / descrição",
                value=nome,
                key=f"mat_nome_{idx}_{nome}",
            ).strip()

            dados["ativo"] = st.checkbox(
                "Ativo",
                value=bool(dados.get("ativo", True)),
                key=f"mat_ativo_{idx}_{nome}",
            )

            unidade = dados.get("unidade", "metro")
            if unidade not in UNIDADES_ITEM:
                unidade = "metro"

            dados["unidade"] = st.selectbox(
                "Unidade",
                UNIDADES_ITEM,
                index=UNIDADES_ITEM.index(unidade),
                key=f"mat_un_{idx}_{nome}",
            )

            dados["preco"] = st.number_input(
                "Preço de venda",
                min_value=0.0,
                value=float(dados.get("preco", 0) or 0),
                step=1.0,
                key=f"mat_val_{idx}_{nome}",
            )

            custo_atual = float(
                custos_privados.get(nome, {}).get("custo", 0) or 0
            )
            custo_novo = st.number_input(
                "Custo de aquisição (privado)",
                min_value=0.0,
                value=custo_atual,
                step=1.0,
                key=f"mat_custo_{idx}_{nome}",
            )

            margem_sugerida = st.number_input(
                "Calcular venda por acréscimo (%)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key=f"mat_margem_{idx}_{nome}",
            )

            if custo_novo > 0 and margem_sugerida > 0:
                preco_sugerido = custo_novo * (
                    1 + margem_sugerida / 100.0
                )
                st.caption(
                    f"Venda sugerida: {dinheiro(preco_sugerido)}"
                )

            chave_final = novo_nome or nome

            # Não permitir que renomeação sobrescreva outro material.
            if chave_final != nome and (
                chave_final in config["materiais"] or chave_final in reconstruidos
            ):
                st.warning(
                    "Já existe outro material com esse nome. "
                    "Escolha um nome diferente."
                )
                chave_final = nome

            # Mantém o custo privado associado ao nome efetivamente salvo.
            if nome != chave_final:
                custos_privados.pop(nome, None)
            custos_privados[chave_final] = {"custo": float(custo_novo)}
            reconstruidos[chave_final] = dados


    config["materiais"] = reconstruidos

    with st.expander("Adicionar novo material"):
        novo_nome = st.text_input("Nome do material", key="novo_mat_nome")
        c1, c2 = st.columns(2)

        with c1:
            novo_un = st.selectbox(
                "Unidade",
                UNIDADES_ITEM,
                key="novo_mat_un",
            )

        with c2:
            novo_preco = st.number_input(
                "Preço de venda",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key="novo_mat_preco",
            )

        novo_custo = st.number_input(
            "Custo de aquisição (privado)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="novo_mat_custo",
        )

        if st.button("Adicionar ao catálogo", key="add_mat"):
            nome_limpo = novo_nome.strip()

            if not nome_limpo:
                st.warning("Informe o nome do material.")
            elif nome_limpo in config["materiais"]:
                st.warning("Já existe um material com esse nome.")
            else:
                config["materiais"][nome_limpo] = {
                    "unidade": novo_un,
                    "preco": float(novo_preco),
                    "ativo": True,
                }

                try:
                    salvar_config()
                    financeiro.setdefault("custos_materiais", {})[
                        nome_limpo
                    ] = {
                        "custo": float(novo_custo),
                    }
                    salvar_financeiro(financeiro)
                    st.success("Material criado e salvo.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar material: {e}")

    try:
        salvou_fin_mat = autosalvar_financeiro_admin(
            financeiro,
            "materiais",
        )
        if salvou_fin_mat:
            st.caption(
                "✓ Custos dos materiais salvos automaticamente e Central recalculada."
            )
        else:
            st.caption("✓ Custos privados: salvamento automático ativo.")
    except Exception as e:
        st.error(f"Erro no salvamento automático dos custos: {e}")


# =========================================================
# ADMIN - APARELHOS
# =========================================================

def aba_aparelhos():
    secao(
        "Aparelhos",
        "Cadastre marca, capacidade, tipo e preço. A descrição é criada automaticamente.",
    )

    financeiro = carregar_financeiro()
    custos_privados = financeiro.setdefault("custos_equipamentos", {})

    remover = []

    for eid, eq in list(config["equipamentos"].items()):
        titulo = nome_equipamento(eq)

        with st.expander(titulo):
            eq["ativo"] = st.checkbox(
                "Disponível para o cliente",
                value=bool(eq.get("ativo", False)),
                key=f"eq_ativo_{eid}",
            )
            eq["marca"] = st.text_input(
                "Marca",
                value=eq.get("marca", ""),
                key=f"eq_marca_{eid}",
            )

            cap = eq.get("capacidade", "9.000 BTUs")
            if cap not in CAPACIDADES:
                cap = "9.000 BTUs"
            eq["capacidade"] = st.selectbox(
                "Capacidade",
                CAPACIDADES,
                index=CAPACIDADES.index(cap),
                key=f"eq_cap_{eid}",
            )

            tipo = eq.get("tipo", "Inverter")
            if tipo not in TIPOS_AR:
                tipo = "Inverter"
            eq["tipo"] = st.selectbox(
                "Tipo",
                TIPOS_AR,
                index=TIPOS_AR.index(tipo),
                key=f"eq_tipo_{eid}",
            )

            eq["preco"] = st.number_input(
                "Preço estimado do equipamento",
                min_value=0.0,
                value=float(eq.get("preco", 0) or 0),
                step=50.0,
                key=f"eq_preco_{eid}",
            )

            custo_eq = st.number_input(
                "Custo de aquisição (privado)",
                min_value=0.0,
                value=float(
                    custos_privados.get(str(eid), {}).get(
                        "custo",
                        0,
                    )
                    or 0
                ),
                step=50.0,
                key=f"eq_custo_{eid}",
            )

            margem_eq = st.number_input(
                "Calcular venda por acréscimo (%)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key=f"eq_margem_{eid}",
            )

            custos_privados[str(eid)] = {
                "custo": float(custo_eq),
            }

            if custo_eq > 0 and margem_eq > 0:
                st.caption(
                    f"Venda sugerida: "
                    f"{dinheiro(custo_eq * (1 + margem_eq / 100.0))}"
                )

            st.caption(f"Descrição automática: {nome_equipamento(eq)}")

            if st.button("Excluir aparelho", key=f"eq_del_{eid}"):
                confirmar_exclusao_aparelho(eid)

    st.markdown("#### Criar novo aparelho")

    marca = st.text_input("Marca do novo aparelho", key="novo_eq_marca")
    cap = st.selectbox("Capacidade do novo aparelho", CAPACIDADES, key="novo_eq_cap")
    tipo = st.selectbox("Tipo do novo aparelho", TIPOS_AR, key="novo_eq_tipo")
    preco = st.number_input(
        "Preço de venda do novo aparelho",
        min_value=0.0,
        value=0.0,
        step=50.0,
        key="novo_eq_preco",
    )
    custo_novo_eq = st.number_input(
        "Custo de aquisição do novo aparelho (privado)",
        min_value=0.0,
        value=0.0,
        step=50.0,
        key="novo_eq_custo",
    )
    ativo = st.checkbox("Disponível para o cliente", value=True, key="novo_eq_ativo")

    if st.button("Criar aparelho", key="criar_eq"):
        if not marca.strip():
            st.warning("Informe a marca.")
        else:
            eid = uuid.uuid4().hex[:12]
            config["equipamentos"][eid] = {
                "id": eid,
                "marca": marca.strip(),
                "capacidade": cap,
                "tipo": tipo,
                "preco": float(preco),
                "ativo": bool(ativo),
            }
            try:
                salvar_config()
                financeiro.setdefault("custos_equipamentos", {})[
                    eid
                ] = {
                    "custo": float(custo_novo_eq),
                }
                salvar_financeiro(financeiro)
                st.success("Aparelho criado e salvo.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    try:
        salvou_fin_eq = autosalvar_financeiro_admin(
            financeiro,
            "aparelhos",
        )
        if salvou_fin_eq:
            st.caption(
                "✓ Custos dos aparelhos salvos automaticamente e Central recalculada."
            )
        else:
            st.caption("✓ Custos privados: salvamento automático ativo.")
    except Exception as e:
        st.error(f"Erro no salvamento automático dos custos: {e}")


# =========================================================
# ADMIN - REGRAS E EMPRESA
# =========================================================

def aba_regras():
    secao("Regras", "Configure valores e avisos usados nas estimativas.")

    config["regras"]["adicional_apartamento_2_mais"] = st.number_input(
        "Adicional a partir do 2º piso",
        min_value=0.0,
        value=float(config["regras"].get("adicional_apartamento_2_mais", 0) or 0),
        step=10.0,
    )
    config["regras"]["valor_por_km"] = st.number_input(
        "Deslocamento — valor por km rodado (R$)",
        min_value=0.0,
        value=float(config["regras"].get("valor_por_km", 0) or 0),
        step=0.10,
        format="%.2f",
        help="Tarifa para o total de quilômetros rodados (ida + volta). Salva automaticamente.",
        key="regra_valor_por_km",
    )
    st.caption("No orçamento, marque Cobrar km e informe a distância total de ida e volta.")
    config["regras"]["texto_variacao"] = st.text_area(
        "Aviso geral de variação do orçamento",
        value=config["regras"].get("texto_variacao", ""),
    )
    config["regras"]["texto_equipamento"] = st.text_area(
        "Aviso de preço dos aparelhos",
        value=config["regras"].get("texto_equipamento", ""),
    )


def aba_empresa():
    secao("Empresa", "Dados exibidos no aplicativo e nos orçamentos.")

    emp = config["empresa"]
    emp["nome"] = st.text_input("Nome", value=emp.get("nome", "F Climatização"))
    emp["slogan"] = st.text_input("Slogan", value=emp.get("slogan", ""))
    emp["whatsapp"] = st.text_input(
        "WhatsApp",
        value=emp.get("whatsapp", ""),
        help="Código do país + DDD + número. Exemplo: 5554999999999",
    )
    emp["local_atendimento"] = st.text_input(
        "Cidade/UF",
        value=emp.get("local_atendimento", "Não-Me-Toque/RS"),
    )
    emp["texto_atendimento"] = st.text_input(
        "Texto da área de atendimento",
        value=emp.get("texto_atendimento", "Atendimento em Não-Me-Toque e região"),
    )
    emp["endereco"] = st.text_input(
        "Endereço",
        value=emp.get("endereco", ""),
        placeholder="Rua, número, bairro, cidade/UF",
    )
    emp["cnpj"] = st.text_input(
        "CNPJ",
        value=emp.get("cnpj", ""),
        placeholder="00.000.000/0000-00",
    )


# =========================================================
# ADMIN
# =========================================================

def pagina_central_faturamento():
    cabecalho(admin=True)

    if st.button(
        "← Voltar ao painel administrativo",
        use_container_width=True,
        key="voltar_central_faturamento",
    ):
        st.session_state["admin_view"] = "painel"
        st.rerun()

    st.markdown(
        """
        <div class="finance-hero">
          <div class="finance-kicker">Painel comercial e financeiro</div>
          <div class="finance-title">Gestão financeira</div>
          <div class="finance-sub">
            Acompanhe vendas concluídas, custos de aquisição, lucro, formas de pagamento
            e desempenho por período. Custos alterados em Materiais e Aparelhos
            passam a recalcular os resultados da Central.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "ATUALIZAR DADOS DA CENTRAL",
        type="primary",
        use_container_width=True,
        key="atualizar_central_faturamento",
    ):
        try:
            with tela_carregamento(
                "Sincronizando pedidos e vendas com a Gestão Comercial..."
            ):
                orcamentos_sync = carregar_orcamentos()
                financeiro_sync = carregar_financeiro()
                resultado_sync = sincronizar_central_faturamento(
                    orcamentos_sync,
                    financeiro_sync,
                )

            st.success(
                "Central atualizada. "
                f"{resultado_sync['atualizados']} venda(s) faturada(s) sincronizada(s)"
                + (
                    f" e {resultado_sync['removidos']} registro(s) antigo(s) removido(s)."
                    if resultado_sync["removidos"] > 0
                    else "."
                )
            )
            st.rerun()
        except Exception as e:
            st.error(f"Não foi possível atualizar a central: {e}")


    with tela_carregamento("Carregando dados financeiros..."):
        financeiro = carregar_financeiro()
        orcamentos = carregar_orcamentos()

    movimentacoes = list(
        financeiro.get("movimentacoes", {}).values()
    )

    ultima_sync = financeiro.get("ultima_sincronizacao")
    if ultima_sync:
        st.caption(f"Última atualização da central: {ultima_sync}")
    else:
        st.caption(
            "A central ainda não foi sincronizada manualmente. "
            "Use o botão Atualizar dados da central."
        )

    anos_encontrados = {
        ano
        for mov in movimentacoes
        for _, ano in [extrair_mes_ano(mov.get("data_faturamento"))]
        if ano is not None
    }

    for orc in orcamentos:
        if orc.get("status") == "Pedido de venda":
            _, ano = extrair_mes_ano(
                orc.get("data_status") or orc.get("atualizado_em") or orc.get("data")
            )
            if ano is not None:
                anos_encontrados.add(ano)

    anos_disponiveis = sorted(
        anos_encontrados,
        reverse=True,
    )

    ano_atual = datetime.now(FUSO_BRASILIA).year
    if ano_atual not in anos_disponiveis:
        anos_disponiveis.insert(0, ano_atual)

    c1, c2 = st.columns(2)

    with c1:
        ano_filtro = st.selectbox(
            "Ano",
            anos_disponiveis,
            key="finance_ano",
        )

    with c2:
        meses = ["Todos"] + [
            nome_mes(i)
            for i in range(1, 13)
        ]
        mes_nome = st.selectbox(
            "Mês",
            meses,
            key="finance_mes",
        )

    mes_filtro = None
    if mes_nome != "Todos":
        mes_filtro = [
            i
            for i in range(1, 13)
            if nome_mes(i) == mes_nome
        ][0]

    filtradas = []

    for mov in movimentacoes:
        mes, ano = extrair_mes_ano(
            mov.get("data_faturamento")
        )

        if ano != ano_filtro:
            continue

        if mes_filtro is not None and mes != mes_filtro:
            continue

        filtradas.append(mov)

    pedidos_filtrados = []

    for orc in orcamentos:
        if orc.get("status") != "Pedido de venda":
            continue

        mes_pedido, ano_pedido = extrair_mes_ano(
            orc.get("data_status")
            or orc.get("atualizado_em")
            or orc.get("data")
        )

        if ano_pedido != ano_filtro:
            continue

        if mes_filtro is not None and mes_pedido != mes_filtro:
            continue

        pedidos_filtrados.append(orc)

    valor_pedidos = 0.0
    for pedido in pedidos_filtrados:
        opcoes_pedido = pedido.get("opcoes_equipamentos", [])
        if len(opcoes_pedido) == 1:
            valor_pedidos += total_opcao_orcamento(
                pedido,
                opcoes_pedido[0],
            )
        elif not opcoes_pedido:
            valor_pedidos += total_orcamento(pedido)

    receita = sum(
        float(m.get("receita", 0) or 0)
        for m in filtradas
    )
    custo = sum(
        float(m.get("custo", 0) or 0)
        for m in filtradas
    )
    lucro = receita - custo
    qtd = len(filtradas)
    ticket = receita / qtd if qtd else 0.0
    margem = (lucro / receita * 100) if receita > 0 else 0.0

    periodo_texto = (
        f"{mes_nome} de {ano_filtro}"
        if mes_nome != "Todos"
        else f"Ano de {ano_filtro}"
    )

    st.caption(f"Período selecionado: {periodo_texto}")

    st.markdown(
        f"""
        <div class="finance-grid">
          <div class="finance-card">
            <div class="finance-card-label">Pedidos confirmados</div>
            <div class="finance-card-value orange">{dinheiro(valor_pedidos)}</div>
          </div>
          <div class="finance-card">
            <div class="finance-card-label">Pedidos em aberto</div>
            <div class="finance-card-value">{len(pedidos_filtrados)}</div>
          </div>
          <div class="finance-card">
            <div class="finance-card-label">Venda concluída</div>
            <div class="finance-card-value blue">{dinheiro(receita)}</div>
          </div>
          <div class="finance-card">
            <div class="finance-card-label">Lucro</div>
            <div class="finance-card-value positive">{dinheiro(lucro)}</div>
          </div>
          <div class="finance-card">
            <div class="finance-card-label">Custos</div>
            <div class="finance-card-value orange">{dinheiro(custo)}</div>
          </div>
          <div class="finance-card">
            <div class="finance-card-label">Margem</div>
            <div class="finance-card-value">{margem:.1f}%</div>
          </div>
          <div class="finance-card">
            <div class="finance-card-label">Vendas concluídas</div>
            <div class="finance-card-value">{qtd}</div>
          </div>
          <div class="finance-card">
            <div class="finance-card-label">Ticket médio</div>
            <div class="finance-card-value">{dinheiro(ticket)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    secao(
        "Pedidos de venda",
        "Lançamentos futuros: receita, custo e lucro estimados dos pedidos ainda não concluídos.",
    )

    receita_pedidos = 0.0
    custo_pedidos = 0.0
    lucro_pedidos = 0.0

    for pedido in pedidos_filtrados:
        estimativa_pedido = estimar_resultado_pedido(
            pedido,
            financeiro,
        )
        receita_pedidos += estimativa_pedido["receita"]
        custo_pedidos += estimativa_pedido["custo"]
        lucro_pedidos += estimativa_pedido["lucro"]

    if pedidos_filtrados:
        margem_pedidos = (
            lucro_pedidos / receita_pedidos * 100
            if receita_pedidos > 0
            else 0.0
        )

        st.markdown(
            f"""
            <div class="finance-grid">
              <div class="finance-card">
                <div class="finance-card-label">Receita futura</div>
                <div class="finance-card-value blue">{dinheiro(receita_pedidos)}</div>
              </div>
              <div class="finance-card">
                <div class="finance-card-label">Custo previsto</div>
                <div class="finance-card-value orange">{dinheiro(custo_pedidos)}</div>
              </div>
              <div class="finance-card">
                <div class="finance-card-label">Lucro previsto</div>
                <div class="finance-card-value positive">{dinheiro(lucro_pedidos)}</div>
              </div>
              <div class="finance-card">
                <div class="finance-card-label">Margem prevista</div>
                <div class="finance-card-value">{margem_pedidos:.1f}%</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for pedido in sorted(
            pedidos_filtrados,
            key=lambda x: str(x.get("numero", "")),
            reverse=True,
        ):
            opcoes_pedido = pedido.get("opcoes_equipamentos", [])
            if len(opcoes_pedido) == 1:
                valor_pedido = total_opcao_orcamento(
                    pedido,
                    opcoes_pedido[0],
                )
            else:
                valor_pedido = total_orcamento(pedido)

            estimativa_pedido = estimar_resultado_pedido(
                pedido,
                financeiro,
            )

            pagamento_pedido = pedido.get(
                "pagamento_pedido",
                {},
            )
            forma_pedido = pagamento_pedido.get(
                "forma",
                "Pagamento não informado",
            )
            parcelas_pedido = int(
                pagamento_pedido.get("parcelas", 1) or 1
            )
            if parcelas_pedido > 1:
                forma_pedido = (
                    f"{forma_pedido} • {parcelas_pedido}x"
                )

            observacao_pedido = pagamento_pedido.get(
                "observacao",
                "",
            ).strip()
            detalhe_pagamento = (
                f"{forma_pedido}"
                + (
                    f" • {observacao_pedido}"
                    if observacao_pedido
                    else ""
                )
            )

            st.markdown(
                f"""
                <div class="finance-pay">
                  <div class="finance-pay-name">
                    Pedido {str(pedido.get("numero","")).zfill(4)} •
                    {pedido.get("cliente",{}).get("nome","Cliente")}
                  </div>
                  <div class="finance-pay-meta">
                    Receita prevista: {dinheiro(estimativa_pedido["receita"])}
                    • Custo: {dinheiro(estimativa_pedido["custo"])}
                    • Lucro: {dinheiro(estimativa_pedido["lucro"])}
                    • Margem: {estimativa_pedido["margem"]:.1f}%
                    • {detalhe_pagamento}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("Nenhum pedido de venda neste período.")

    # -----------------------------------------------------
    # MÉTODOS DE PAGAMENTO
    # -----------------------------------------------------
    secao(
        "Formas de pagamento",
        "Distribuição das vendas concluídas no período.",
    )

    pagamentos = {}

    for mov in filtradas:
        pagamento = mov.get("pagamento", {})
        forma = pagamento.get("forma") or "Não informado"

        pagamentos.setdefault(
            forma,
            {
                "qtd": 0,
                "valor": 0.0,
            },
        )

        pagamentos[forma]["qtd"] += 1
        pagamentos[forma]["valor"] += float(
            mov.get("receita", 0) or 0
        )

    for forma, dados in sorted(
        pagamentos.items(),
        key=lambda x: x[1]["valor"],
        reverse=True,
    ):
        meta = f'{dados["qtd"]} venda(s) • {dinheiro(dados["valor"])}'

        st.markdown(
            f"""
            <div class="finance-pay">
              <div class="finance-pay-name">{forma}</div>
              <div class="finance-pay-meta">{meta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------
    # EVOLUÇÃO MENSAL
    # -----------------------------------------------------
    if mes_nome == "Todos":
        secao(
            "Evolução mensal",
            "Faturamento por mês no ano selecionado.",
        )

        totais_mes = {
            i: 0.0
            for i in range(1, 13)
        }

        for mov in movimentacoes:
            mes, ano = extrair_mes_ano(
                mov.get("data_faturamento")
            )
            if ano == ano_filtro and mes in totais_mes:
                totais_mes[mes] += float(
                    mov.get("receita", 0) or 0
                )

        maximo = max(totais_mes.values()) if totais_mes else 0.0

        for mes in range(1, 13):
            valor = totais_mes[mes]
            largura = (
                (valor / maximo) * 100
                if maximo > 0
                else 0
            )

            st.markdown(
                f"""
                <div class="finance-bar-row">
                  <div class="finance-bar-head">
                    <span>{nome_mes(mes)}</span>
                    <strong>{dinheiro(valor)}</strong>
                  </div>
                  <div class="finance-bar-track">
                    <div class="finance-bar-fill" style="width:{largura:.1f}%"></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------
    # VENDAS DO PERÍODO
    # -----------------------------------------------------
    secao(
        "Vendas faturadas",
        "Detalhamento das vendas concluídas no período.",
    )

    if not filtradas:
        st.info("Nenhuma venda faturada neste período.")
        return

    for mov in sorted(
        filtradas,
        key=lambda m: str(m.get("data_faturamento", "")),
        reverse=True,
    ):
        numero = mov.get("numero", "----")
        cliente = mov.get("cliente", {}).get(
            "nome",
            "Cliente",
        )
        pagamento = mov.get("pagamento", {})
        forma = pagamento.get("forma", "Não informado")
        parcelas = int(pagamento.get("parcelas", 1) or 1)

        if parcelas > 1:
            forma_exibida = f"{forma} • {parcelas}x"
        else:
            forma_exibida = forma

        with st.expander(
            f"Venda {numero} • {cliente} • {dinheiro(mov.get('receita',0))}"
        ):
            st.write(
                f"**Faturado em:** {mov.get('data_faturamento','')}"
            )
            st.write(
                f"**Pagamento:** {forma_exibida}"
            )

            if pagamento.get("observacao"):
                st.caption(
                    pagamento.get("observacao")
                )

            vc1, vc2, vc3 = st.columns(3)
            with vc1:
                st.metric(
                    "Receita",
                    dinheiro(mov.get("receita", 0)),
                )
            with vc2:
                st.metric(
                    "Custo",
                    dinheiro(mov.get("custo", 0)),
                )
            with vc3:
                st.metric(
                    "Lucro",
                    dinheiro(mov.get("lucro", 0)),
                )

            st.markdown("#### Itens")

            for linha in mov.get("linhas", []):
                origem = linha.get("origem", "")
                custo_linha = float(
                    linha.get("custo_total", 0) or 0
                )
                venda_linha = float(
                    linha.get("valor_venda", 0) or 0
                )
                lucro_linha = venda_linha - custo_linha

                st.write(
                    f'**{linha.get("descricao","Item")}** — '
                    f'venda {dinheiro(venda_linha)} • '
                    f'custo {dinheiro(custo_linha)} • '
                    f'resultado {dinheiro(lucro_linha)}'
                )



def aba_gestao_comercial():
    """Painel comercial enxuto, sem repetir a listagem de orçamentos."""
    secao("Visão comercial", "Resumo dos orçamentos, pedidos e vendas.")
    registros = carregar_orcamentos()
    totais = {"Orçamento": 0, "Pedido de venda": 0, "Faturado / Concluído": 0}
    for registro in registros:
        estado = registro.get("status", "Orçamento")
        if estado in totais:
            totais[estado] += 1
    c1, c2, c3 = st.columns(3)
    c1.metric("Orçamentos", totais["Orçamento"])
    c2.metric("Pedidos", totais["Pedido de venda"])
    c3.metric("Concluídas", totais["Faturado / Concluído"])
    financeiro = carregar_financeiro()
    previstos = [r for r in registros if r.get("status") == "Pedido de venda"]
    previsoes = [estimar_resultado_pedido(r, financeiro) for r in previstos]
    receita_prevista = sum(resultado["receita"] for resultado in previsoes)
    custo_previsto = sum(resultado["custo"] for resultado in previsoes)
    concluidos = [r for r in registros if r.get("status") == "Faturado / Concluído"]
    receita_realizada = sum(total_orcamento(r) for r in concluidos if len(r.get("opcoes_equipamentos", [])) <= 1)
    st.markdown("#### Resumo financeiro")
    st.metric("Receita prevista de pedidos", dinheiro(receita_prevista))
    st.metric("Lucro previsto de pedidos", dinheiro(receita_prevista - custo_previsto))
    st.metric("Valor das vendas concluídas", dinheiro(receita_realizada))
    st.caption("Previsões não são recebimentos. Abaixo estão os detalhes e filtros por período.")


def painel_semana_admin(registros):
    """Agenda desta semana em ordem cronológica, com acesso à agenda completa."""
    from html import escape

    hoje = datetime.now(FUSO_BRASILIA).date()
    # Sete dias a partir de hoje, para sempre mostrar os próximos compromissos.
    dias = [hoje + timedelta(days=indice) for indice in range(7)]
    agenda = {dia: [] for dia in dias}
    atrasados = 0
    sem_data = 0
    for registro in registros:
        if registro.get("status") != "Pedido de venda" or servico_ja_realizado(registro):
            continue
        momento = data_hora_agendamento(registro)
        if momento is None:
            sem_data += 1
        elif momento.date() < hoje:
            atrasados += 1
        elif momento.date() in agenda:
            agenda[momento.date()].append((momento, registro))
    for compromissos in agenda.values():
        compromissos.sort(key=lambda item: (item[0], str(item[1].get("numero", ""))))

    st.markdown("""
    <div class="fc-home-heading">
      <div class="fc-home-eyebrow">PAINEL OPERACIONAL</div>
      <div class="fc-home-title">Minha semana</div>
      <div class="fc-home-sub">Próximos 7 dias • serviços confirmados e ainda não realizados</div>
    </div>
    """, unsafe_allow_html=True)
    dias_semana = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")
    for dia in dias:
        compromissos = agenda[dia]
        titulo_dia = "HOJE" if dia == hoje else "AMANHÃ" if dia == hoje + timedelta(days=1) else dias_semana[dia.weekday()].upper()
        titulo = f"{titulo_dia} · {dia.strftime('%d/%m')}"
        itens_html = []
        for momento, registro in compromissos:
            nome = escape(str((registro.get("cliente") or {}).get("nome") or "Cliente"))
            numero = escape(str(registro.get("numero", "")).zfill(4))
            servico = escape(str(descricao_agendamento(registro)))
            ag = registro.get("agendamento") or {}
            local = escape(str(ag.get("endereco") or (registro.get("cliente") or {}).get("cidade") or "Local a confirmar"))
            itens_html.append(
                '<div class="fc-home-event">'
                f'<div class="fc-home-event-time">{momento.strftime("%H:%M")}</div>'
                '<div class="fc-home-event-info">'
                f'<strong>{nome}</strong><span>{servico}</span>'
                f'<small>{local} · Pedido #{numero}</small>'
                '</div></div>'
            )
        conteudo = "".join(itens_html) if itens_html else '<div class="fc-home-empty">Nenhum serviço agendado</div>'
        quantidade = f"{len(compromissos)} serviço(s)" if compromissos else "Livre"
        st.markdown(
            '<div class="fc-home-day">'
            '<div class="fc-home-day-heading">'
            f'<strong>{titulo}</strong><span>{quantidade}</span>'
            '</div>' + conteudo + '</div>',
            unsafe_allow_html=True,
        )

    if atrasados or sem_data:
        st.warning(
            f"{atrasados} serviço(s) atrasado(s) · {sem_data} pedido(s) sem agendamento. "
            "Consulte a Agenda para resolver."
        )
    if st.button("Abrir agenda completa e histórico", icon=":material/calendar_month:", key="fc_home_abrir_agenda", use_container_width=True, type="primary"):
        st.session_state["admin_view"] = "agenda"
        st.rerun()


def estilo_dashboard_admin():
    st.markdown("""
<style>
.fc-home-heading {margin: 8px 0 12px;}
.fc-home-eyebrow {font-size: 10px;letter-spacing: 1.5px;color: #73b4ff;font-weight: 800;}
.fc-home-title {font-size: 23px;line-height: 1.3;font-weight: 850;color: #f7faff;margin-top: 3px;}
.fc-home-sub {font-size: 12px;color: #aab7cd;margin-top: 4px;}
.fc-home-day {background: linear-gradient(130deg,#141c2b,#101721);border:1px solid #2d3e58;border-radius: 12px;padding: 11px 12px;margin-bottom: 7px;}
.fc-home-day-heading {display:flex;align-items:center;justify-content:space-between;gap:8px;color:#eaf3ff;font-size:12px;}
.fc-home-day-heading strong {color:#6eb5ff;letter-spacing:.5px;}
.fc-home-day-heading span {color:#99abc4;font-size:11px;}
.fc-home-empty {font-size:11px;color:#7f8fa6;margin-top:5px;}
.fc-home-event {display:flex;gap:12px;align-items:flex-start;border-top:1px solid #293549;margin-top:9px;padding-top:9px;}
.fc-home-event-time {font-weight:850;color:#ffad61;font-size:14px;min-width:44px;}
.fc-home-event-info {display:flex;flex-direction:column;gap:3px;min-width:0;}
.fc-home-event-info strong {color:#f4f8ff;font-size:12px;}
.fc-home-event-info span {color:#b6c8df;font-size:11px;}
.fc-home-event-info small {color:#94a6bc;font-size:10px;}
.fc-home-grid-title {font-size:17px;font-weight:850;color:#f1f8ff;margin:20px 0 10px;}
div[class*="st-key-fc_atalho_"] button {min-height:64px !important;background:linear-gradient(140deg,#172339,#121a29) !important;border:1px solid #2b4669 !important;border-radius:14px !important;color:#f0f7ff !important;box-shadow: 0 3px 12px #0003 !important;padding:7px 5px !important;font-size:11px !important;font-weight:750 !important;white-space:normal !important;line-height:1.35 !important;}
div[class*="st-key-fc_atalho_"] button:hover {border-color:#3996ff !important;background:#1c2d45 !important;}

/* Apenas atalhos: impede que o Streamlit empilhe as colunas no celular. */
div[class*="st-key-fc_home_shortcuts"] div[data-testid="stHorizontalBlock"] {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
  gap: 8px !important;
  width: 100% !important;
  align-items: stretch !important;
}
div[class*="st-key-fc_home_shortcuts"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
  min-width: 0 !important;
  width: 100% !important;
  max-width: none !important;
  flex: 1 1 0 !important;
}
div[class*="st-key-fc_atalho_"] button {
  width: 100% !important;
  min-height: 62px !important;
  height: 100% !important;
  justify-content: center !important;
  gap: 5px !important;
}
div[class*="st-key-fc_atalho_"] button span[data-testid="stIconMaterial"] {
  font-size: 19px !important;
  color: #7dbbff !important;
}
@media (max-width: 520px) {
  div[class*="st-key-fc_atalho_"] button {font-size: 11px !important; padding: 7px 4px !important;}
}
</style>
    """, unsafe_allow_html=True)


def atalhos_inicio_admin():
    atalhos = [
        ('novo', 'Novo orçamento', ':material/note_add:'),
        ('agenda', 'Agenda', ':material/calendar_month:'),
        ('orcamentos', 'Orçamentos', ':material/description:'),
        ('pedidos', 'Pedidos de venda', ':material/assignment:'),
        ('vendas', 'Vendas concluídas', ':material/check_circle:'),
        ('realizados', 'Serviços realizados', ':material/handyman:'),
        ('horarios', 'Horários de trabalho', ':material/schedule:'),
        ('financeiro', 'Gestão financeira', ':material/bar_chart:'),
        ('servicos', 'Serviços', ':material/build:'),
        ('materiais', 'Materiais', ':material/inventory_2:'),
        ('aparelhos', 'Aparelhos', ':material/ac_unit:'),
        ('regras', 'Regras', ':material/tune:'),
        ('empresa', 'Empresa', ':material/business:'),
    ]
    st.markdown('<div class="fc-home-grid-title">Acessos rápidos</div>', unsafe_allow_html=True)
    with st.container(key='fc_home_shortcuts'):
        for pos in range(0, len(atalhos), 2):
            colunas = st.columns(2, gap='small')
            for coluna, (destino, rotulo, icone) in zip(colunas, atalhos[pos:pos+2]):
                with coluna:
                    if st.button(rotulo, icon=icone, use_container_width=True,
                                 key=f'fc_atalho_{destino}'):
                        st.session_state['admin_view'] = destino
                        st.rerun()


def historico_servicos_admin(registros):
    """Histórico dedicado, preservando a possibilidade de concluir vendas."""
    realizados = []
    for registro in registros:
        if not servico_ja_realizado(registro):
            continue
        momento = data_hora_agendamento(registro)
        if momento is not None:
            realizados.append((momento, registro))
    realizados.sort(key=lambda item: item[0], reverse=True)
    secao("Serviços realizados", "Histórico de trabalhos executados, do mais recente ao mais antigo.")
    if not realizados:
        st.info("Nenhum serviço realizado registrado.")
        return
    st.caption(f"{len(realizados)} serviço(s) realizado(s)")
    for momento, registro in realizados:
        exibir_compromisso(momento, registro, realizado=True, contexto="historico")


def pagina_admin():
    # Nunca renderizar informações, cadastros ou orçamento antes da autenticação.
    if not ADMIN_KEY:
        st.error("ADMIN_KEY não configurada nos Secrets do Streamlit.")
        return

    if st.session_state.get("admin_logado", False):
        token = st.session_state.get("admin_token")
        if not verificar_token_admin(token):
            encerrar_sessao_admin()
    if not st.session_state.get("admin_logado", False):
        restaurar_sessao_admin()
    if not st.session_state.get("admin_logado", False):
        cabecalho(admin=True)
        secao("Acesso restrito", "O aplicativo é exclusivo da administração.")
        with st.form("login_admin_exclusivo", clear_on_submit=True):
            senha = st.text_input("Senha administrativa", type="password")
            entrar = st.form_submit_button("ENTRAR", type="primary", use_container_width=True)
        if entrar:
            if hmac.compare_digest(str(senha), str(ADMIN_KEY)):
                st.session_state["admin_logado"] = True
                persistir_sessao_admin()
                st.rerun()
            else:
                st.error("Senha incorreta.")
        st.caption("Neste dispositivo, o acesso pode permanecer ativo por até 14 dias. Use Sair para encerrá-lo.")
        return

    pagina = st.session_state.get("admin_view", "painel")
    if pagina in ("faturamento", "gestao"):
        # Rotas anteriores abrem o painel unificado.
        pagina = "financeiro"
    if pagina == "financeiro":
        pagina_central_faturamento()
        return

    cabecalho(admin=True)
    estilo_dashboard_admin()
    st.markdown(ESTILO_LINHAS_ADMIN, unsafe_allow_html=True)

    if pagina == "painel":
        registros_resumo = carregar_orcamentos()
        painel_semana_admin(registros_resumo)
        atalhos_inicio_admin()
    else:
        if st.button("← Voltar ao início", use_container_width=True, key="fc_voltar_inicio"):
            st.session_state["admin_view"] = "painel"
            st.rerun()
        telas = {
            "novo": lambda: pagina_cliente(interno=True),
            "agenda": lambda: agenda_admin(carregar_orcamentos()),
            "horarios": painel_configuracao_agenda,
            "orcamentos": lambda: aba_orcamentos("Orçamentos"),
            "pedidos": lambda: aba_orcamentos("Pedidos de venda"),
            "vendas": lambda: aba_orcamentos("Vendas concluídas"),
            "realizados": lambda: historico_servicos_admin(carregar_orcamentos()),
            "servicos": aba_servicos,
            "materiais": aba_materiais,
            "aparelhos": aba_aparelhos,
            "regras": aba_regras,
            "empresa": aba_empresa,
        }
        tela = telas.get(pagina)
        if tela is None:
            st.session_state["admin_view"] = "painel"
            st.rerun()
        tela()

    st.divider()
    try:
        autosalvar_config_admin("painel")
        st.caption("✓ Configurações com salvamento automático.")
    except Exception as e:
        st.error(f"Erro ao salvar configurações: {e}")
    if st.button("Sair da administração", key="sair_admin_exclusivo", use_container_width=True):
        encerrar_sessao_admin()
        st.session_state["admin_view"] = "painel"
        st.rerun()


def somente_digitos(valor):
    return "".join(c for c in str(valor or "") if c.isdigit())


def atualizar_totais_opcoes(orcamento):
    for opcao in orcamento.get("opcoes_equipamentos", []):
        opcao["total_servicos"] = sum(
            float(servico.get("valor", 0) or 0)
            for servico in opcao.get("servicos", [])
        )


def salvar_orcamento_editado(orcamentos, orcamento):
    orcamento["atualizado_em"] = datetime.now(FUSO_BRASILIA).strftime(
        "%d/%m/%Y %H:%M"
    )
    atualizar_totais_opcoes(orcamento)

    for idx, item in enumerate(orcamentos):
        if str(item.get("numero", "")) == str(orcamento.get("numero", "")):
            orcamentos[idx] = orcamento
            break

    salvar_orcamentos(orcamentos)


def localizar_orcamento_cliente(orcamentos, numero):
    numero_limpo = str(numero or "").strip().lstrip("#").strip()

    if not numero_limpo.isdigit():
        return None

    numero_normalizado = numero_limpo.zfill(4)

    for orcamento in orcamentos:
        if str(orcamento.get("numero", "")).zfill(4) == numero_normalizado:
            return orcamento

    return None


def editor_orcamento_cliente():
    secao(
        "Editar orçamento",
        "Localize um orçamento já criado pelo número de 4 dígitos.",
    )

    st.markdown(
        """
        <div class="info-card">
          <div class="card-title">Edição completa</div>
          <div class="card-text">
            Refaça o orçamento usando os mesmos cadastros e preços do sistema.
            Você pode trocar aparelhos, serviços, materiais, quantidades e dados do local.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    numero_busca = st.text_input(
        "Número do orçamento",
        placeholder="Ex.: 0012",
        max_chars=4,
        key="editar_busca_numero",
    )

    if st.button(
        "LOCALIZAR ORÇAMENTO",
        type="primary",
        use_container_width=True,
        key="btn_localizar_orcamento_cliente",
    ):
        numero_limpo = str(numero_busca or "").strip()

        if not numero_limpo.isdigit() or len(numero_limpo) != 4:
            st.warning("Informe o número do orçamento com 4 dígitos. Ex.: 0012.")
        else:
            orcamentos = carregar_orcamentos()
            encontrado = localizar_orcamento_cliente(
                orcamentos,
                numero_limpo,
            )

            if encontrado:
                st.session_state["orcamento_cliente_em_edicao"] = encontrado.get("numero")
                st.rerun()
            else:
                st.error("Orçamento não localizado.")

    numero_edicao = st.session_state.get("orcamento_cliente_em_edicao")

    if not numero_edicao:
        return

    orcamentos = carregar_orcamentos()
    orcamento = localizar_orcamento_cliente(
        orcamentos,
        numero_edicao,
    )

    if not orcamento:
        st.session_state.pop("orcamento_cliente_em_edicao", None)
        st.warning("Esse orçamento não está mais disponível para edição.")
        return

    numero = str(orcamento.get("numero", "")).zfill(4)
    cliente = orcamento.get("cliente", {})
    itens_atuais = orcamento.get("itens", [])
    opcoes_atuais = orcamento.get("opcoes_equipamentos", [])

    st.divider()
    st.markdown(
        f'<span class="budget-number">#{numero}</span>',
        unsafe_allow_html=True,
    )
    st.caption(
        f'{orcamento.get("data","")} • '
        f'{cliente.get("nome","")} • '
        f'{cliente.get("cidade","")}'
    )

    # -----------------------------------------------------
    # ESTADO ATUAL DO ORÇAMENTO
    # -----------------------------------------------------

    servicos_atuais = []
    precos_servicos_atuais = {}

    if opcoes_atuais:
        for opcao in opcoes_atuais:
            for servico in opcao.get("servicos", []):
                descricao = str(servico.get("descricao", ""))
                nome_base = descricao.split(" • ")[0].strip()
                if nome_base and nome_base not in servicos_atuais:
                    servicos_atuais.append(nome_base)
                if nome_base:
                    quantidade_existente = max(1, float(servico.get("quantidade", 1) or 1))
                    precos_servicos_atuais[nome_base] = float(
                        servico.get("valor_unitario", float(servico.get("valor", 0) or 0) / quantidade_existente) or 0
                    )
    else:
        for item in itens_atuais:
            if item.get("origem") == "servico":
                descricao = str(item.get("descricao", ""))
                nome_base = descricao.split(" • ")[0].strip()
                if nome_base and nome_base not in servicos_atuais:
                    servicos_atuais.append(nome_base)
                if nome_base:
                    precos_servicos_atuais[nome_base] = float(
                        item.get("valor_unitario", 0) or 0
                    )

    materiais_atuais = {}
    for item in itens_atuais:
        if item.get("origem") == "material":
            materiais_atuais[str(item.get("descricao", ""))] = {
                "quantidade": float(item.get("quantidade", 1) or 0),
                "unidade": item.get("unidade", "unidade"),
                "preco": float(item.get("valor_unitario", 0) or 0),
            }

    outros_itens = [
        copy.deepcopy(item)
        for item in itens_atuais
        if item.get("origem") not in ("servico", "material", "equipamento", "regra", "deslocamento")
    ]

    item_equipamento_atual = next(
        (
            item
            for item in itens_atuais
            if item.get("origem") == "equipamento"
        ),
        None,
    )

    # -----------------------------------------------------
    # DADOS DO CLIENTE
    # -----------------------------------------------------

    with st.expander("Dados do cliente"):
        edit_nome = st.text_input(
            "Nome",
            value=cliente.get("nome", ""),
            key=f"edit_nome_{numero}",
        )
        edit_telefone = st.text_input(
            "Telefone / WhatsApp",
            value=cliente.get("telefone", ""),
            key=f"edit_telefone_{numero}",
        )
        edit_cidade = st.text_input(
            "Cidade",
            value=cliente.get("cidade", ""),
            key=f"edit_cidade_{numero}",
        )

    # -----------------------------------------------------
    # APARELHO / EQUIPAMENTOS
    # -----------------------------------------------------

    with st.expander("Aparelho / equipamentos", expanded=True):
        opcoes_possui = [
            "Sim, já tenho o aparelho",
            "Não, quero comprar",
            "Ainda estou avaliando",
        ]

        possui_atual = orcamento.get(
            "possui_aparelho",
            "Sim, já tenho o aparelho",
        )
        if possui_atual not in opcoes_possui:
            possui_atual = "Sim, já tenho o aparelho"

        edit_possui = st.radio(
            "Situação do aparelho do cliente",
            opcoes_possui,
            index=opcoes_possui.index(possui_atual),
            format_func=lambda valor: {
                "Sim, já tenho o aparelho": "O cliente já possui o aparelho",
                "Não, quero comprar": "O cliente quer comprar um aparelho",
                "Já tenho um e também quero comprar outro": "O cliente possui um e quer comprar outro",
                "Ainda estou avaliando": "O cliente está avaliando as opções",
            }.get(valor, valor),
            key=f"edit_possui_{numero}",
        )

        edit_modo_compra = None
        edit_equipamento_unico = None
        edit_opcoes_comparacao = []
        edit_capacidade = orcamento.get("capacidade", "9.000 BTUs")

        # Catálogo ativo + equipamentos antigos deste orçamento
        catalogo_equipamentos = []

        for eid, eq in config.get("equipamentos", {}).items():
            if eq.get("ativo", False):
                catalogo_equipamentos.append(
                    {
                        "id": str(eid),
                        "marca": eq.get("marca", ""),
                        "capacidade": eq.get("capacidade", ""),
                        "tipo": eq.get("tipo", ""),
                        "preco": float(eq.get("preco", 0) or 0),
                        "descricao": nome_equipamento(eq),
                    }
                )

        ids_catalogo = {str(eq["id"]) for eq in catalogo_equipamentos}

        if item_equipamento_atual and orcamento.get("equipamento_id"):
            eid_atual = str(orcamento.get("equipamento_id"))
            if eid_atual not in ids_catalogo:
                catalogo_equipamentos.append(
                    {
                        "id": eid_atual,
                        "marca": "",
                        "capacidade": orcamento.get("capacidade", ""),
                        "tipo": "",
                        "preco": float(
                            item_equipamento_atual.get("valor_unitario", 0) or 0
                        ),
                        "descricao": item_equipamento_atual.get(
                            "descricao",
                            "Ar-condicionado",
                        ),
                    }
                )

        for opcao in opcoes_atuais:
            oid = str(opcao.get("id", ""))
            if oid and oid not in {str(eq["id"]) for eq in catalogo_equipamentos}:
                catalogo_equipamentos.append(
                    {
                        "id": oid,
                        "marca": opcao.get("marca", ""),
                        "capacidade": opcao.get("capacidade", ""),
                        "tipo": opcao.get("tipo", ""),
                        "preco": float(opcao.get("preco", 0) or 0),
                        "descricao": opcao.get("descricao", "Ar-condicionado"),
                    }
                )

        if situacao_tem_compra(edit_possui):
            modos_compra = [
                "Escolher um aparelho",
                "Comparar aparelhos",
            ]

            modo_atual = orcamento.get("modo_compra")
            if modo_atual not in modos_compra:
                modo_atual = (
                    "Comparar aparelhos"
                    if opcoes_atuais
                    else "Escolher um aparelho"
                )

            edit_modo_compra = st.radio(
                "Tipo de seleção de equipamentos",
                modos_compra,
                index=modos_compra.index(modo_atual),
                horizontal=True,
                key=f"edit_modo_compra_{numero}",
            )

            st.info(
                "Os aparelhos fornecidos pela F Climatização já incluem "
                "instalação padrão com até 2 metros de linha."
            )

            if edit_modo_compra == "Escolher um aparelho":
                capacidade_atual = orcamento.get("capacidade")
                if capacidade_atual not in CAPACIDADES:
                    if item_equipamento_atual:
                        capacidade_atual = next(
                            (
                                cap
                                for cap in CAPACIDADES
                                if cap in str(
                                    item_equipamento_atual.get("descricao", "")
                                )
                            ),
                            CAPACIDADES[0],
                        )
                    else:
                        capacidade_atual = CAPACIDADES[0]

                edit_capacidade = st.selectbox(
                    "Capacidade desejada",
                    CAPACIDADES,
                    index=CAPACIDADES.index(capacidade_atual),
                    key=f"edit_cap_unico_{numero}",
                )

                mostrar_referencia_capacidade(edit_capacidade)

                disponiveis = [
                    eq
                    for eq in catalogo_equipamentos
                    if eq.get("capacidade") == edit_capacidade
                ]
                disponiveis.sort(
                    key=lambda item: (
                        float(item.get("preco", 0) or 0),
                        item.get("descricao", "").lower(),
                    )
                )

                if disponiveis:
                    labels = {
                        f'{eq["descricao"]} — {dinheiro(eq["preco"])}': eq
                        for eq in disponiveis
                    }

                    atual_id = str(orcamento.get("equipamento_id") or "")
                    default_label = next(
                        (
                            label
                            for label, eq in labels.items()
                            if str(eq["id"]) == atual_id
                        ),
                        list(labels.keys())[0],
                    )

                    edit_label_unico = st.selectbox(
                        "Aparelho",
                        list(labels.keys()),
                        index=list(labels.keys()).index(default_label),
                        key=f"edit_eq_unico_{numero}",
                    )

                    edit_equipamento_unico = labels[edit_label_unico]
                else:
                    st.info("Nenhum aparelho dessa capacidade está disponível.")

            else:
                filtro_atual = (
                    orcamento.get("capacidade")
                    if orcamento.get("capacidade") in CAPACIDADES
                    else CAPACIDADES[0]
                )

                filtro_cap = st.selectbox(
                    "Capacidade para visualizar",
                    CAPACIDADES,
                    index=CAPACIDADES.index(filtro_atual),
                    key=f"edit_filtro_cap_{numero}",
                )
                mostrar_referencia_capacidade(filtro_cap)

                state_key = f"edit_eq_ids_{numero}"
                if state_key not in st.session_state:
                    st.session_state[state_key] = [
                        str(opcao.get("id", ""))
                        for opcao in opcoes_atuais
                        if opcao.get("id")
                    ]

                ids_selecionados = set(
                    str(x)
                    for x in st.session_state.get(state_key, [])
                )

                visiveis = [
                    eq
                    for eq in catalogo_equipamentos
                    if eq.get("capacidade") == filtro_cap
                ]
                visiveis.sort(
                    key=lambda item: (
                        float(item.get("preco", 0) or 0),
                        item.get("descricao", "").lower(),
                    )
                )

                if visiveis:
                    st.caption(
                        "Marque os modelos desejados. As seleções continuam salvas ao trocar os BTUs."
                    )

                for eq in visiveis:
                    eid = str(eq["id"])
                    wk = f"edit_eq_chk_{numero}_{eid}"

                    if wk not in st.session_state:
                        st.session_state[wk] = eid in ids_selecionados

                    marcado = st.checkbox(
                        f'{eq["descricao"]} — {dinheiro(eq["preco"])}',
                        key=wk,
                    )

                    if marcado:
                        ids_selecionados.add(eid)
                    else:
                        ids_selecionados.discard(eid)

                st.session_state[state_key] = sorted(ids_selecionados)

                edit_opcoes_comparacao = [
                    eq
                    for eq in catalogo_equipamentos
                    if str(eq["id"]) in ids_selecionados
                ]
                edit_opcoes_comparacao.sort(
                    key=lambda item: (
                        BTU_NUM.get(item.get("capacidade"), 999999),
                        float(item.get("preco", 0) or 0),
                    )
                )

                if edit_opcoes_comparacao:
                    st.markdown(
                        f'<div class="capacity-ok">'
                        f'{len(edit_opcoes_comparacao)} modelo(s) selecionado(s).'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    with st.expander("Ver selecionados"):
                        for eq in edit_opcoes_comparacao:
                            st.write(
                                f'**{eq["descricao"]}** — {dinheiro(eq["preco"])} '
                                f'• instalação inclusa até 2 m de linha'
                            )

            if edit_possui == "Já tenho um e também quero comprar outro":
                cap_existente_atual = orcamento.get(
                    "capacidade_aparelho_existente",
                    "Não sei",
                )
                opcoes_cap_existente = CAPACIDADES + ["Não sei"]
                if cap_existente_atual not in opcoes_cap_existente:
                    cap_existente_atual = "Não sei"

                edit_capacidade_existente = st.selectbox(
                    "Capacidade do aparelho que já possui",
                    opcoes_cap_existente,
                    index=opcoes_cap_existente.index(cap_existente_atual),
                    key=f"edit_cap_existente_{numero}",
                )
            else:
                edit_capacidade_existente = None

        else:
            edit_capacidade_existente = None
            cap_atual = orcamento.get("capacidade")
            opcoes_capacidade = CAPACIDADES + ["Não sei"]

            if cap_atual not in opcoes_capacidade:
                cap_atual = "Não sei"

            edit_capacidade = st.selectbox(
                "Capacidade do aparelho",
                opcoes_capacidade,
                index=opcoes_capacidade.index(cap_atual),
                key=f"edit_cap_sem_compra_{numero}",
            )

            mostrar_referencia_capacidade(edit_capacidade)

    # -----------------------------------------------------
    # SERVIÇOS
    # -----------------------------------------------------

    with st.expander("Serviços"):
        servicos_ativos = [
            nome
            for nome, dados in config.get("servicos", {}).items()
            if dados.get("ativo", True)
            and dados.get("mostrar_cliente", True)
        ]

        if situacao_tem_compra(edit_possui):
            servicos_ativos = [
                nome
                for nome in servicos_ativos
                if nome.strip().lower() != "instalação"
            ]

        servicos_opcoes = servicos_ativos[:]
        for nome in servicos_atuais:
            # Não reoferece Instalação separada em compra simples.
            if (
                edit_possui == "Não, quero comprar"
                and nome.strip().lower() == "instalação"
            ):
                continue
            if nome not in servicos_opcoes:
                servicos_opcoes.append(nome)

        if edit_possui == "Já tenho um e também quero comprar outro":
            st.caption(
                "Estes serviços são do aparelho que o cliente já possui. "
                "O aparelho comprado já inclui instalação até 2 m de linha."
            )
        elif edit_possui == "Não, quero comprar":
            st.caption(
                "A instalação do aparelho comprado já está inclusa no preço."
            )

        defaults_servicos = [
            nome
            for nome in servicos_atuais
            if nome in servicos_opcoes
        ]

        edit_servicos = st.multiselect(
            "Serviços do orçamento",
            servicos_opcoes,
            default=defaults_servicos,
            key=f"edit_servicos_{numero}",
        )
        edit_quantidades_pontos = {}
        for nome_servico in edit_servicos:
            if servico_com_quantidade(nome_servico):
                qtd_anterior = next((int(float(i.get("quantidade", 1) or 1)) for i in itens_atuais
                    if i.get("origem") == "servico" and str(i.get("descricao", "")).startswith(nome_servico + " •")), None)
                if qtd_anterior is None:
                    qtd_anterior = next((int(float(sv.get("quantidade", 1) or 1)) for op in opcoes_atuais
                        for sv in op.get("servicos", []) if str(sv.get("descricao", "")).startswith(nome_servico + " •")), 1)
                unidade = unidade_servico_orcamento(nome_servico)
                rotulo = {"ponto": "pontos", "aparelho": "aparelhos", "serviço": "serviços"}.get(unidade, "unidades")
                edit_quantidades_pontos[nome_servico] = st.number_input(
                    f"Quantidade de {rotulo} — {nome_servico}",
                    min_value=1, max_value=10000 if unidade == "ponto" else 1000,
                    value=max(1, qtd_anterior), step=1,
                    key=f"edit_pontos_{numero}_{nome_servico}",
                    help="O valor unitário é multiplicado pela quantidade escolhida.",
                )

    # -----------------------------------------------------
    # MATERIAIS / QUANTIDADES
    # -----------------------------------------------------

    with st.expander("Materiais"):
        materiais_ativos = {
            nome: dados
            for nome, dados in config.get("materiais", {}).items()
            if dados.get("ativo", True)
        }

        nomes_materiais = list(materiais_ativos.keys())
        for nome in materiais_atuais.keys():
            if nome not in nomes_materiais:
                nomes_materiais.append(nome)

        defaults_materiais = [
            nome
            for nome in materiais_atuais.keys()
            if nome in nomes_materiais
        ]

        edit_materiais_nomes = st.multiselect(
            "Materiais do orçamento",
            nomes_materiais,
            default=defaults_materiais,
            key=f"edit_materiais_{numero}",
        )

        edit_materiais = []

        for nome_material in edit_materiais_nomes:
            dados_catalogo = materiais_ativos.get(nome_material, {})
            dados_antigos = materiais_atuais.get(nome_material, {})

            unidade = dados_catalogo.get(
                "unidade",
                dados_antigos.get("unidade", "unidade"),
            )
            preco = float(
                dados_catalogo.get(
                    "preco",
                    dados_antigos.get("preco", 0),
                )
                or 0
            )

            qtd_default = float(
                dados_antigos.get("quantidade", 1) or 1
            )

            quantidade = st.number_input(
                f"{nome_material} • quantidade ({unidade})",
                min_value=0.0,
                value=qtd_default,
                step=0.5 if unidade == "metro" else 1.0,
                key=f"edit_mat_qtd_{numero}_{nome_material}",
            )

            st.caption(
                f"{dinheiro(preco)} / {unidade} • "
                f"Total: {dinheiro(quantidade * preco)}"
            )

            if quantidade > 0:
                edit_materiais.append(
                    {
                        "nome": nome_material,
                        "quantidade": float(quantidade),
                        "unidade": unidade,
                        "preco": preco,
                    }
                )

    # -----------------------------------------------------
    # LOCAL / ANDAR / ÁREA
    # -----------------------------------------------------

    with st.expander("Local do serviço"):
        tipos_imovel = [
            "Casa",
            "Apartamento",
            "Comércio",
            "Outro",
        ]

        tipo_atual = orcamento.get("tipo_imovel", "Casa")
        if tipo_atual not in tipos_imovel:
            tipo_atual = "Outro"

        edit_tipo_imovel = st.selectbox(
            "Tipo de imóvel",
            tipos_imovel,
            index=tipos_imovel.index(tipo_atual),
            key=f"edit_tipo_imovel_{numero}",
        )

        edit_andar = 0
        if edit_tipo_imovel == "Apartamento":
            edit_andar = st.number_input(
                "Andar/piso",
                min_value=0,
                value=int(orcamento.get("andar") or 1),
                step=1,
                key=f"edit_andar_{numero}",
            )

        area_atual = orcamento.get("area_ambiente", "Não sei")
        opcoes_area_edit = OPCOES_AREA[:]

        if area_atual not in opcoes_area_edit:
            opcoes_area_edit.append(area_atual)

        edit_area = st.selectbox(
            "Tamanho aproximado do ambiente",
            opcoes_area_edit,
            index=opcoes_area_edit.index(area_atual),
            key=f"edit_area_{numero}",
        )

        capacidade_para_area = None

        if (
            situacao_tem_compra(edit_possui)
            and edit_modo_compra == "Escolher um aparelho"
            and edit_equipamento_unico
        ):
            capacidade_para_area = edit_equipamento_unico.get("capacidade")
        elif edit_possui != "Não, quero comprar":
            capacidade_para_area = (
                edit_capacidade
                if edit_capacidade in CAPACIDADES
                else None
            )

        mostrar_compatibilidade_area(
            capacidade_para_area,
            edit_area,
        )

    # -----------------------------------------------------
    # ADICIONAL / OBSERVAÇÕES
    # -----------------------------------------------------

    with st.expander("Adicional e observações"):
        adicional_atual = orcamento.get("adicional", {})
        adicional_default = (
            "Sim"
            if adicional_atual.get("solicitado")
            else "Não"
        )

        edit_adicional = st.radio(
            "Precisa de algum serviço ou material adicional?",
            ["Não", "Sim"],
            index=["Não", "Sim"].index(adicional_default),
            horizontal=True,
            key=f"edit_adicional_{numero}",
        )

        edit_adicional_desc = ""

        if edit_adicional == "Sim":
            edit_adicional_desc = st.text_area(
                "Descrição do adicional",
                value=adicional_atual.get("descricao", ""),
                key=f"edit_adicional_desc_{numero}",
            )

        edit_observacoes = st.text_area(
            "Outras observações",
            value=orcamento.get("observacoes", ""),
            key=f"edit_observacoes_{numero}",
        )

    # -----------------------------------------------------
    # DESLOCAMENTO / COBRAR KM
    # -----------------------------------------------------
    km_item_antigo = next(
        (it for it in itens_atuais if it.get("origem") == "deslocamento"),
        None,
    )
    deslocamento_antigo = orcamento.get("deslocamento", {})
    cobrar_km_antigo = bool(km_item_antigo) or bool(
        deslocamento_antigo.get("cobrar_km", False)
    )
    km_antigo = (
        float(km_item_antigo.get("quantidade", 0) or 0)
        if km_item_antigo else float(deslocamento_antigo.get("km_rodados", 0) or 0)
    )
    with st.expander("Deslocamento / Cobrar km", expanded=cobrar_km_antigo):
        edit_cobrar_km, edit_km, edit_tarifa_km = controles_cobranca_km(
            f"edit_deslocamento_{numero}",
            ativo=cobrar_km_antigo,
            distancia=km_antigo,
        )

    # -----------------------------------------------------
    # OUTROS ITENS ANTIGOS / MANUAIS
    # -----------------------------------------------------

    manter_outros = []

    if outros_itens:
        with st.expander("Outros itens existentes"):
            st.caption(
                "Itens manuais de versões anteriores. Desmarque para remover."
            )

            for idx, item in enumerate(outros_itens):
                iid = item.get("id") or f"outro_{idx}"
                qtd = float(item.get("quantidade", 0) or 0)
                vu = float(item.get("valor_unitario", 0) or 0)

                manter = st.checkbox(
                    (
                        f'{item.get("descricao","Item")} — '
                        f'{qtd:g} {item.get("unidade","")} — '
                        f'{dinheiro(qtd * vu)}'
                    ),
                    value=True,
                    key=f"edit_manter_outro_{numero}_{iid}",
                )

                if manter:
                    manter_outros.append(copy.deepcopy(item))

    # -----------------------------------------------------
    # PRÉVIA E SALVAR
    # -----------------------------------------------------

    st.divider()
    st.caption(
        "Os preços unitários continuam vindo dos cadastros do sistema. "
        "Nesta área você altera somente a composição do orçamento."
    )

    if st.button(
        "SALVAR ALTERAÇÕES DO ORÇAMENTO",
        type="primary",
        use_container_width=True,
        key=f"salvar_edicao_completa_{numero}",
    ):
        if not edit_nome.strip():
            st.warning("Informe o nome do cliente.")
            return

        if not edit_telefone.strip():
            st.warning("Informe o telefone/WhatsApp.")
            return

        novos_itens = []
        novas_opcoes = []
        novo_equipamento_id = None
        nova_capacidade = edit_capacidade

        # Mantém itens manuais escolhidos
        novos_itens.extend(manter_outros)

        # Materiais
        for material in edit_materiais:
            novos_itens.append(
                montar_item(
                    material["nome"],
                    material["quantidade"],
                    material["unidade"],
                    material["preco"],
                    origem="material",
                )
            )

        # Regra automática de apartamento
        if edit_tipo_imovel == "Apartamento" and int(edit_andar) >= 2:
            valor_andar = float(
                config.get("regras", {}).get(
                    "adicional_apartamento_2_mais",
                    0,
                )
                or 0
            )

            if valor_andar > 0:
                novos_itens.append(
                    montar_item(
                        f"Adicional de acesso • {int(edit_andar)}º piso",
                        1,
                        "serviço",
                        valor_andar,
                        origem="regra",
                    )
                )

        # Compra de aparelho
        if edit_possui == "Não, quero comprar":
            if edit_modo_compra == "Escolher um aparelho":
                if not edit_equipamento_unico:
                    st.warning("Escolha um aparelho.")
                    return

                novo_equipamento_id = edit_equipamento_unico["id"]
                nova_capacidade = edit_equipamento_unico["capacidade"]

                novos_itens.append(
                    montar_item(
                        descricao_equipamento_com_instalacao(
                            edit_equipamento_unico["descricao"]
                        ),
                        1,
                        "equipamento",
                        edit_equipamento_unico["preco"],
                        origem="equipamento",
                    )
                )

                cap_servico_editor = (
                    edit_capacidade_existente
                    if edit_possui == "Já tenho um e também quero comprar outro"
                    else nova_capacidade
                )
                cap_servico_editor = (
                    cap_servico_editor
                    if cap_servico_editor in CAPACIDADES
                    else None
                )

                for nome_servico in edit_servicos:
                    dados_servico = config.get("servicos", {}).get(
                        nome_servico,
                        {},
                    )
                    valor = float(
                        dados_servico.get("precos", {}).get(
                            cap_servico_editor,
                            precos_servicos_atuais.get(
                                nome_servico,
                                0,
                            ),
                        )
                        or 0
                    ) if cap_servico_editor else 0.0

                    descricao_servico = descricao_servico_orcamento(nome_servico, cap_servico_editor, edit_quantidades_pontos.get(nome_servico, 1))

                    novos_itens.append(
                        montar_item(
                            descricao_servico,
                            edit_quantidades_pontos.get(nome_servico, 1),
                            unidade_servico_orcamento(nome_servico),
                            valor,
                            origem="servico",
                        )
                    )

            else:
                if not edit_opcoes_comparacao:
                    st.warning("Selecione pelo menos um aparelho para comparar.")
                    return

                capacidades_escolhidas = []

                for eq in edit_opcoes_comparacao:
                    cap_eq = eq.get("capacidade")
                    if cap_eq and cap_eq not in capacidades_escolhidas:
                        capacidades_escolhidas.append(cap_eq)

                    servicos_eq = []

                    if edit_possui == "Não, quero comprar":
                        for nome_servico in edit_servicos:
                            dados_servico = config.get("servicos", {}).get(
                                nome_servico,
                                {},
                            )
                            valor = float(
                                dados_servico.get("precos", {}).get(
                                    cap_eq,
                                    precos_servicos_atuais.get(
                                        nome_servico,
                                        0,
                                    ),
                                )
                                or 0
                            )

                            servicos_eq.append(
                                {
                                    "descricao": descricao_servico_orcamento(nome_servico, cap_eq, edit_quantidades_pontos.get(nome_servico, 1)),
                                    "quantidade": edit_quantidades_pontos.get(nome_servico, 1),
                                    "valor_unitario": valor,
                                    "valor": valor * edit_quantidades_pontos.get(nome_servico, 1),
                                }
                            )

                    nova_opcao = copy.deepcopy(eq)
                    nova_opcao["descricao"] = descricao_equipamento_com_instalacao(
                        nova_opcao.get("descricao", "Ar-condicionado")
                    )
                    nova_opcao["servicos"] = servicos_eq
                    nova_opcao["total_servicos"] = sum(
                        float(s.get("valor", 0) or 0)
                        for s in servicos_eq
                    )
                    novas_opcoes.append(nova_opcao)

                nova_capacidade = (
                    capacidades_escolhidas[0]
                    if len(capacidades_escolhidas) == 1
                    else "Várias capacidades"
                )

                if edit_possui == "Já tenho um e também quero comprar outro":
                    cap_existente_editor = (
                        edit_capacidade_existente
                        if edit_capacidade_existente in CAPACIDADES
                        else None
                    )
                    for nome_servico in edit_servicos:
                        dados_servico = config.get("servicos", {}).get(
                            nome_servico,
                            {},
                        )
                        valor = float(
                            dados_servico.get("precos", {}).get(
                                cap_existente_editor,
                                precos_servicos_atuais.get(nome_servico, 0),
                            )
                            or 0
                        ) if cap_existente_editor else 0.0
                        descricao = (
                            descricao_servico_orcamento(nome_servico, cap_existente_editor, edit_quantidades_pontos.get(nome_servico, 1))
                        )
                        novos_itens.append(
                            montar_item(
                                descricao,
                                edit_quantidades_pontos.get(nome_servico, 1),
                                unidade_servico_orcamento(nome_servico),
                                valor,
                                origem="servico",
                            )
                        )

        # Já possui / avaliando
        else:
            cap_servico = (
                edit_capacidade
                if edit_capacidade in CAPACIDADES
                else None
            )

            nova_capacidade = edit_capacidade

            for nome_servico in edit_servicos:
                dados_servico = config.get("servicos", {}).get(
                    nome_servico,
                    {},
                )

                if cap_servico:
                    valor = float(
                        dados_servico.get("precos", {}).get(
                            cap_servico,
                            precos_servicos_atuais.get(
                                nome_servico,
                                0,
                            ),
                        )
                        or 0
                    )
                    descricao = descricao_servico_orcamento(nome_servico, cap_servico, edit_quantidades_pontos.get(nome_servico, 1))
                else:
                    valor = 0.0
                    descricao = descricao_servico_orcamento(nome_servico, None, edit_quantidades_pontos.get(nome_servico, 1))

                novos_itens.append(
                    montar_item(
                        descricao,
                        edit_quantidades_pontos.get(nome_servico, 1),
                        unidade_servico_orcamento(nome_servico),
                        valor,
                        origem="servico",
                    )
                )

        try:
            adicionar_cobranca_km(
                novos_itens, edit_cobrar_km, edit_km, edit_tarifa_km
            )
        except ValueError as erro_km:
            st.warning(str(erro_km))
            return

        orcamento["cliente"] = {
            "nome": edit_nome.strip(),
            "telefone": edit_telefone.strip(),
            "cidade": edit_cidade.strip(),
        }
        orcamento["possui_aparelho"] = edit_possui
        orcamento["modo_compra"] = (
            edit_modo_compra
            if situacao_tem_compra(edit_possui)
            else None
        )
        orcamento["capacidade_aparelho_existente"] = (
            edit_capacidade_existente
            if edit_possui == "Já tenho um e também quero comprar outro"
            else None
        )
        orcamento["instalacao_inclusa_equipamento"] = situacao_tem_compra(
            edit_possui
        )
        orcamento["capacidade"] = nova_capacidade
        orcamento["equipamento_id"] = novo_equipamento_id
        orcamento["opcoes_equipamentos"] = novas_opcoes
        orcamento["itens"] = novos_itens
        orcamento["tipo_imovel"] = edit_tipo_imovel
        orcamento["andar"] = (
            int(edit_andar)
            if edit_tipo_imovel == "Apartamento"
            else None
        )
        orcamento["area_ambiente"] = edit_area
        orcamento["adicional"] = {
            "solicitado": edit_adicional == "Sim",
            "descricao": edit_adicional_desc.strip(),
        }
        orcamento["observacoes"] = edit_observacoes.strip()
        orcamento["deslocamento"] = {
            "cobrar_km": bool(edit_cobrar_km),
            "km_rodados": float(edit_km if edit_cobrar_km else 0),
            "valor_por_km": float(edit_tarifa_km if edit_cobrar_km else 0),
        }

        try:
            salvar_orcamento_editado(
                orcamentos,
                orcamento,
            )
            if orcamento.get("status") == "Faturado / Concluído":
                sincronizar_central_faturamento(
                    orcamentos, carregar_financeiro()
                )
            st.success("Orçamento atualizado com sucesso.")
            st.rerun()
        except Exception as e:
            st.error(f"Não foi possível salvar: {e}")
            return

    # -----------------------------------------------------
    # PDF ATUALIZADO / FECHAR
    # -----------------------------------------------------

    pdf_atualizado = gerar_pdf(orcamento)
    compartilhar_pdf(
        pdf_atualizado,
        f'orcamento_{numero}_F_Climatizacao.pdf',
        titulo=f'Orçamento {numero} - F Climatização',
    )

    if st.button(
        "Fechar edição",
        use_container_width=True,
        key=f"fechar_edicao_cliente_{numero}",
    ):
        st.session_state.pop("orcamento_cliente_em_edicao", None)

        for chave in list(st.session_state.keys()):
            if str(chave).startswith(f"edit_eq_chk_{numero}_"):
                st.session_state.pop(chave, None)

        st.session_state.pop(f"edit_eq_ids_{numero}", None)
        st.rerun()


def pagina_cliente(interno=False):
    restaurar_rascunho_cliente()

    # A mudança de um widget chega a session_state ANTES de a página rodar.
    # Salvar agora evita perder todo o último evento quando a tela demora a
    # renderizar ou uma consulta externa falha antes do final do formulário.
    # Nunca gravar antes de a restauração inicial ser concluída, para não
    # substituir um rascunho ainda armazenado no navegador.
    if st.session_state.get("_rascunho_restaurado", False):
        salvar_rascunho_cliente()

    if st.session_state.pop("_mostrar_aviso_rascunho", False):
        st.info("Rascunho do orçamento restaurado.")

    if not interno:
        cabecalho(admin=False)

    # O uso é exclusivamente administrativo. A edição está na aba Orçamentos.
    st.markdown(
        """
        <div class="info-card">
          <div class="card-title">Criar novo orçamento</div>
          <div class="card-text">
            Cadastre os dados e serviços do cliente para gerar um orçamento.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    secao(
        "Aparelho do cliente",
        "Selecione a situação do equipamento para preparar o orçamento.",
    )

    opcoes_possui = [
        "Sim, já tenho o aparelho",
        "Não, quero comprar",
        "Já tenho um e também quero comprar outro",
        "Ainda estou avaliando",
    ]
    rotulos_possui_adm = {
        "Sim, já tenho o aparelho": "O cliente já possui o aparelho",
        "Não, quero comprar": "O cliente quer comprar um aparelho",
        "Já tenho um e também quero comprar outro": "O cliente possui um e quer comprar outro",
        "Ainda estou avaliando": "O cliente está avaliando as opções",
    }
    garantir_opcao_valida("cliente_possui", opcoes_possui)

    possui = st.radio(
        "Situação do aparelho do cliente",
        opcoes_possui,
        format_func=lambda valor: rotulos_possui_adm.get(valor, valor),
        key="cliente_possui",
    )

    equipamento_id = None
    equipamento = None
    opcoes_equipamentos = []
    modo_compra = None

    if situacao_tem_compra(possui):
        modos_compra = [
            "Escolher um aparelho",
            "Comparar aparelhos",
        ]
        garantir_opcao_valida("cliente_modo_compra", modos_compra)

        modo_compra = st.radio(
            "Como deseja montar o orçamento?",
            modos_compra,
            horizontal=True,
            key="cliente_modo_compra",
        )

        st.markdown(
            """
            <div class="info-card">
              <div class="card-title">Instalação já inclusa</div>
              <div class="card-text">
                Os aparelhos fornecidos pela F Climatização já incluem
                instalação padrão com até 2 metros de linha entre evaporadora
                e condensadora. A instalação não será cobrada novamente.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        todos_ativos = [
            {
                "id": str(eid),
                "marca": eq.get("marca", ""),
                "capacidade": eq.get("capacidade", ""),
                "tipo": eq.get("tipo", ""),
                "preco": float(eq.get("preco", 0) or 0),
                "descricao": nome_equipamento(eq),
            }
            for eid, eq in config["equipamentos"].items()
            if eq.get("ativo", False)
        ]

        if modo_compra == "Escolher um aparelho":
            garantir_opcao_valida(
                "cliente_capacidade_compra_unico",
                CAPACIDADES,
            )

            capacidade = st.selectbox(
                "Capacidade desejada",
                CAPACIDADES,
                key="cliente_capacidade_compra_unico",
            )

            mostrar_referencia_capacidade(capacidade)

            disponiveis = [
                opcao
                for opcao in todos_ativos
                if opcao.get("capacidade") == capacidade
            ]
            disponiveis.sort(
                key=lambda item: (
                    float(item.get("preco", 0) or 0),
                    item.get("marca", "").lower(),
                    item.get("tipo", "").lower(),
                )
            )

            if disponiveis:
                mapa_unico = {
                    f'{opcao["descricao"]} — {dinheiro(opcao["preco"])}': opcao
                    for opcao in disponiveis
                }

                nomes_unicos = list(mapa_unico.keys())
                garantir_opcao_valida(
                    "cliente_equipamento_unico",
                    nomes_unicos,
                )

                escolha_unica = st.selectbox(
                    "Escolha o aparelho",
                    nomes_unicos,
                    key="cliente_equipamento_unico",
                )

                equipamento = mapa_unico[escolha_unica]
                equipamento_id = equipamento["id"]

                st.markdown(
                    (
                        '<div class="equipment-option">'
                        f'<div class="equipment-option-name">{equipamento["descricao"]}</div>'
                        f'<div class="equipment-option-price">{dinheiro(equipamento["preco"])}</div>'
                        '<div class="equipment-option-total">'
                        'Este aparelho será somado aos serviços e demais itens do orçamento.'
                        '</div>'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.info(
                    f"Nenhum aparelho de {capacidade} está ativo no catálogo no momento."
                )

        else:
            garantir_opcao_valida(
                "cliente_capacidade_compra",
                CAPACIDADES,
            )

            if "cliente_equipamentos_selecionados" not in st.session_state:
                st.session_state["cliente_equipamentos_selecionados"] = []

            selecionados_ids = set(
                str(x)
                for x in st.session_state.get(
                    "cliente_equipamentos_selecionados",
                    [],
                )
            )

            capacidade = st.selectbox(
                "Capacidade para visualizar",
                CAPACIDADES,
                key="cliente_capacidade_compra",
            )

            mostrar_referencia_capacidade(capacidade)

            ids_ativos = {
                str(opcao["id"])
                for opcao in todos_ativos
            }

            selecionados_ids = {
                eid
                for eid in selecionados_ids
                if eid in ids_ativos
            }

            opcoes_disponiveis = [
                opcao
                for opcao in todos_ativos
                if opcao.get("capacidade") == capacidade
            ]

            opcoes_disponiveis.sort(
                key=lambda item: (
                    float(item.get("preco", 0) or 0),
                    item.get("marca", "").lower(),
                    item.get("tipo", "").lower(),
                )
            )

            if opcoes_disponiveis:
                st.caption(
                    "Marque os modelos desejados. Você pode trocar os BTUs "
                    "e continuar selecionando sem perder as escolhas anteriores."
                )

                for opcao in opcoes_disponiveis:
                    eid = str(opcao["id"])
                    widget_key = f"cliente_eq_visivel_{eid}"

                    if widget_key not in st.session_state:
                        st.session_state[widget_key] = eid in selecionados_ids

                    marcado = st.checkbox(
                        f'{opcao["descricao"]} — {dinheiro(opcao["preco"])}',
                        key=widget_key,
                    )

                    if marcado:
                        selecionados_ids.add(eid)
                    else:
                        selecionados_ids.discard(eid)

            else:
                st.info(
                    f"Nenhum aparelho de {capacidade} está ativo no catálogo no momento."
                )

            st.session_state["cliente_equipamentos_selecionados"] = sorted(
                selecionados_ids
            )

            opcoes_equipamentos = [
                opcao
                for opcao in todos_ativos
                if str(opcao["id"]) in selecionados_ids
            ]

            opcoes_equipamentos.sort(
                key=lambda item: (
                    BTU_NUM.get(
                        item.get("capacidade"),
                        999999,
                    ),
                    float(item.get("preco", 0) or 0),
                    item.get("marca", "").lower(),
                )
            )

            if opcoes_equipamentos:
                capacidades_selecionadas = []

                for opcao in opcoes_equipamentos:
                    cap = opcao.get("capacidade", "")
                    if cap and cap not in capacidades_selecionadas:
                        capacidades_selecionadas.append(cap)

                st.markdown(
                    f'<div class="capacity-ok">'
                    f'{len(opcoes_equipamentos)} modelo(s) selecionado(s) em '
                    f'{len(capacidades_selecionadas)} capacidade(s).'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                with st.expander("Ver modelos selecionados"):
                    for opcao in opcoes_equipamentos:
                        st.write(
                            f'**{opcao["descricao"]}** — '
                            f'{dinheiro(opcao["preco"])}  '
                            f'• instalação inclusa até 2 m de linha'
                        )
            else:
                st.markdown(
                    '<div class="capacity-note">'
                    'Nenhum modelo selecionado ainda.'
                    '</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
                <div class="orange-card">
                  <div class="card-title">Orçamento comparativo</div>
                  <div class="card-text">
                    As opções escolhidas serão apresentadas separadamente.
                    Todos os aparelhos já incluem instalação padrão até 2 m de linha.
                    Os preços dos aparelhos não serão somados entre si.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if possui == "Já tenho um e também quero comprar outro":
            st.markdown("#### Aparelho que o cliente já possui")
            capacidade_existente = st.selectbox(
                "Capacidade do aparelho que já possui",
                CAPACIDADES + ["Não sei"],
                key="cliente_capacidade_existente",
            )
            mostrar_referencia_capacidade(capacidade_existente)
        else:
            capacidade_existente = None

    else:
        capacidade_existente = None
        opcoes_capacidade = CAPACIDADES + ["Não sei"]
        garantir_opcao_valida(
            "cliente_capacidade",
            opcoes_capacidade,
        )

        capacidade = st.selectbox(
            "Capacidade do aparelho",
            opcoes_capacidade,
            key="cliente_capacidade",
        )

        mostrar_referencia_capacidade(capacidade)

    if possui == "Já tenho um e também quero comprar outro":
        secao(
            "Serviços para o aparelho que o cliente já possui",
            "O aparelho comprado da F Climatização já terá a instalação inclusa.",
        )
    elif possui == "Não, quero comprar":
        secao(
            "Serviços adicionais",
            "A instalação padrão do aparelho comprado já está inclusa no preço.",
        )
    else:
        secao("Serviços", "Selecione um ou mais serviços.")

    servicos_ativos = [
        nome
        for nome, dados in config["servicos"].items()
        if dados.get("ativo", True)
        and dados.get("mostrar_cliente", True)
    ]

    # Na compra de aparelho da F Climatização, Instalação já está embutida.
    # Em cenário misto, a instalação continua disponível para o aparelho que o cliente já possui.
    if possui == "Não, quero comprar":
        servicos_ativos = [
            nome
            for nome in servicos_ativos
            if nome.strip().lower() != "instalação"
        ]

    garantir_opcao_valida("cliente_servicos", servicos_ativos, multiplo=True)

    servicos = st.multiselect(
        (
            "Serviços para o aparelho já existente"
            if possui == "Já tenho um e também quero comprar outro"
            else "Serviços desejados"
        ),
        servicos_ativos,
        key="cliente_servicos",
    )

    quantidades_servicos_pontos = {}
    for nome_servico in servicos:
        if servico_com_quantidade(nome_servico):
            unidade = unidade_servico_orcamento(nome_servico)
            tipo = {"ponto": "pontos", "aparelho": "aparelhos", "serviço": "serviços"}.get(unidade, "unidades")
            quantidade = st.number_input(
                f"Quantidade de {tipo} — {nome_servico}",
                min_value=1, max_value=10000 if unidade == "ponto" else 1000,
                value=1, step=1,
                key=f"cliente_pontos_{nome_servico}",
                help=f"O valor unitário por {unidade} será multiplicado pela quantidade escolhida.",
            )
            quantidades_servicos_pontos[nome_servico] = int(quantidade)
            st.caption(f"{int(quantidade)} {tipo} × valor unitário cadastrado • total automático no orçamento")

    # Descontos concedidos pelo administrador somente neste orçamento.
    # Os preços do catálogo permanecem inalterados.
    descontos_servicos_novo = {}
    descontos_equipamentos_novo = {}
    desconto_geral_novo = 0.0
    with st.expander("Descontos para este orçamento (%)", expanded=False):
        st.caption("Descontos aplicados somente ao orçamento atual. Não alteram os preços cadastrados.")
        if situacao_tem_compra(possui):
            aparelhos_desconto = (
                [equipamento] if modo_compra == "Escolher um aparelho" and equipamento
                else opcoes_equipamentos
            )
            for aparelho_desc in aparelhos_desconto:
                eid_desc = str(aparelho_desc.get("id", ""))
                if not eid_desc:
                    continue
                desconto_eq_pct = st.number_input(
                    f'Desconto no aparelho (%) — {aparelho_desc.get("descricao", "Aparelho")}',
                    min_value=0.0, max_value=100.0, value=0.0,
                    step=1.0, format="%.2f", key=f"cliente_desc_eq_{eid_desc}",
                )
                descontos_equipamentos_novo[eid_desc] = limitar_percentual(desconto_eq_pct)
        for nome_desconto_serv in servicos:
            desconto_serv_pct = st.number_input(
                f"Desconto no serviço (%) — {nome_desconto_serv}",
                min_value=0.0, max_value=100.0, value=0.0,
                step=1.0, format="%.2f", key=f"cliente_desc_serv_{nome_desconto_serv}",
            )
            descontos_servicos_novo[nome_desconto_serv] = limitar_percentual(desconto_serv_pct)
        desconto_geral_novo = st.number_input(
            "Desconto geral adicional (%)",
            min_value=0.0, max_value=100.0, value=0.0,
            step=1.0, format="%.2f", key="cliente_desconto_geral",
            help="Aplicado sobre o subtotal já descontado dos aparelhos e serviços.",
        )
        st.caption("O desconto geral é aplicado depois dos descontos individuais.")

    materiais_selecionados = []

    materiais_ativos_cliente = {
        nome: dados
        for nome, dados in config.get("materiais", {}).items()
        if dados.get("ativo", True)
    }

    if materiais_ativos_cliente:
        with st.expander("Adicionar materiais ao orçamento"):
            nomes_materiais_cliente = list(materiais_ativos_cliente.keys())

            garantir_opcao_valida(
                "cliente_materiais",
                nomes_materiais_cliente,
                multiplo=True,
            )

            escolhidos_materiais = st.multiselect(
                "Materiais",
                nomes_materiais_cliente,
                key="cliente_materiais",
                placeholder="Selecione somente se necessário",
            )

            for nome_material in escolhidos_materiais:
                dados_material = materiais_ativos_cliente[nome_material]
                unidade_material = dados_material.get("unidade", "unidade")
                preco_material = float(
                    dados_material.get("preco", 0) or 0
                )

                quantidade = st.number_input(
                    f"{nome_material} • quantidade ({unidade_material})",
                    min_value=0.0,
                    value=1.0,
                    step=0.5 if unidade_material == "metro" else 1.0,
                    key=f"cliente_mat_qtd_{nome_material}",
                )

                st.caption(
                    f"{dinheiro(preco_material)} / {unidade_material} • "
                    f"Total: {dinheiro(quantidade * preco_material)}"
                )

                if quantidade > 0:
                    materiais_selecionados.append(
                        {
                            "nome": nome_material,
                            "quantidade": float(quantidade),
                            "unidade": unidade_material,
                            "preco": preco_material,
                        }
                    )

    secao("Local do serviço", "Informações que ajudam a calcular a estimativa.")

    tipos_imovel = ["Casa", "Apartamento", "Comércio", "Outro"]
    garantir_opcao_valida("cliente_tipo_imovel", tipos_imovel)

    tipo_imovel = st.selectbox(
        "Tipo de imóvel",
        tipos_imovel,
        key="cliente_tipo_imovel",
    )

    andar = 0
    if tipo_imovel == "Apartamento":
        andar = st.number_input(
            "Andar/piso",
            min_value=0,
            value=1,
            step=1,
            help=(
                "A partir do 2º piso pode haver adicional, "
                "conforme configuração da empresa."
            ),
            key="cliente_andar",
        )

    garantir_opcao_valida("cliente_area", OPCOES_AREA)

    area = st.selectbox(
        "Tamanho aproximado do ambiente",
        OPCOES_AREA,
        key="cliente_area",
    )

    mostrar_compatibilidade_area(
        capacidade if capacidade in CAPACIDADES else None,
        area,
    )

    secao(
        "Serviço ou material adicional",
        "Use somente se existir algo além das opções acima.",
    )

    opcoes_adicional = ["Não", "Sim"]
    garantir_opcao_valida("cliente_adicional_sim", opcoes_adicional)

    adicional_sim = st.radio(
        "Precisa de algum serviço ou material adicional?",
        opcoes_adicional,
        horizontal=True,
        key="cliente_adicional_sim",
    )

    adicional_desc = ""
    if adicional_sim == "Sim":
        adicional_desc = st.text_area(
            "Se quiser, descreva o adicional",
            placeholder="Ex.: material extra, ajuste elétrico, acesso especial...",
            key="cliente_adicional_desc",
        )
    else:
        st.session_state.pop("cliente_adicional_desc", None)

    observacoes = st.text_area(
        "Outras observações",
        placeholder="Informações que possam ajudar no atendimento.",
        key="cliente_observacoes",
    )

    secao("Deslocamento", "Opcional — tarifa por quilômetro definida em ADM → Regras.")
    cobrar_km_novo, km_novo, tarifa_km_novo = controles_cobranca_km(
        "cliente_deslocamento",
    )

    secao("Dados do cliente", "Identifique o cliente para registrar o orçamento.")

    nome_cliente = st.text_input(
        "Nome",
        key="cliente_nome",
    )
    telefone = st.text_input(
        "Telefone / WhatsApp",
        key="cliente_telefone",
    )
    cidade = st.text_input(
        "Cidade",
        key="cliente_cidade",
    )

    # Prévia dos descontos antes de gerar o orçamento, incluindo todos os
    # itens selecionados e o adicional automático de andar quando aplicável.
    subtotal_comum_previa = sum(
        float(mat["quantidade"]) * float(mat["preco"])
        for mat in materiais_selecionados
    )
    if cobrar_km_novo:
        subtotal_comum_previa += km_novo * tarifa_km_novo
    if tipo_imovel == "Apartamento" and int(andar) >= 2:
        subtotal_comum_previa += float(
            config.get("regras", {}).get("adicional_apartamento_2_mais", 0) or 0
        )

    def previa_servicos(capacidade_btu):
        subtotal_servicos = 0.0
        for nome_previa in servicos:
            dados_previa = config.get("servicos", {}).get(nome_previa, {})
            unitario = float(
                dados_previa.get("precos", {}).get(capacidade_btu, 0) or 0
            )
            qtd_previa = float(quantidades_servicos_pontos.get(nome_previa, 1))
            bruto_previa = unitario * qtd_previa
            subtotal_servicos += aplicar_desconto(
                bruto_previa, descontos_servicos_novo.get(nome_previa, 0)
            )
        return subtotal_servicos

    with st.container(border=True):
        st.markdown("**Prévia do orçamento com descontos**")
        if situacao_tem_compra(possui) and modo_compra == "Comparar aparelhos":
            for eq_previa in opcoes_equipamentos:
                cap_previa = eq_previa.get("capacidade")
                total_previa = subtotal_comum_previa + aplicar_desconto(
                    eq_previa.get("preco", 0),
                    descontos_equipamentos_novo.get(str(eq_previa.get("id", "")), 0),
                )
                if possui == "Não, quero comprar":
                    total_previa += previa_servicos(cap_previa)
                else:
                    total_previa += previa_servicos(capacidade_existente)
                total_previa = aplicar_desconto(total_previa, desconto_geral_novo)
                st.write(f'**{eq_previa.get("descricao", "Aparelho")}** — {dinheiro(total_previa)}')
            if not opcoes_equipamentos:
                st.caption("Selecione um aparelho para visualizar os valores.")
            else:
                st.caption("Alternativas independentes: não serão somadas entre si.")
        else:
            subtotal_previa = subtotal_comum_previa
            if situacao_tem_compra(possui) and equipamento is not None:
                subtotal_previa += aplicar_desconto(
                    equipamento.get("preco", 0),
                    descontos_equipamentos_novo.get(str(equipamento_id), 0),
                )
            cap_servicos_previa = (
                capacidade_existente if possui == "Já tenho um e também quero comprar outro"
                else (equipamento.get("capacidade") if equipamento is not None
                      else capacidade)
            )
            subtotal_previa += previa_servicos(cap_servicos_previa)
            st.metric("Total estimado com descontos", dinheiro(
                aplicar_desconto(subtotal_previa, desconto_geral_novo)
            ))
        if desconto_geral_novo:
            st.caption(f"Desconto geral adicional: {desconto_geral_novo:g}%")

    # O rascunho já é salvo ANTES da montagem do formulário, a cada
    # interação concluída. Evita-se uma segunda instância do mesmo componente
    # de armazenamento local no mesmo rerun (DuplicateElementKey).
    if st.button("GERAR ORÇAMENTO", type="primary", use_container_width=True):
        if not nome_cliente.strip():
            st.warning("Informe o nome do cliente.")
            return

        if not telefone.strip():
            st.warning("Informe um telefone/WhatsApp.")
            return

        if situacao_tem_compra(possui):
            if modo_compra == "Escolher um aparelho" and equipamento is None:
                st.warning("Escolha um aparelho para incluir no orçamento.")
                return

            if modo_compra == "Comparar aparelhos" and not opcoes_equipamentos:
                st.warning("Marque pelo menos um aparelho para comparar.")
                return

            if (
                possui == "Já tenho um e também quero comprar outro"
                and not servicos
            ):
                st.warning(
                    "Selecione pelo menos um serviço para o aparelho que você já possui."
                )
                return

        elif not servicos:
            st.warning("Selecione pelo menos um serviço.")
            return

        itens = []

        # -------------------------------------------------
        # VENDA DE UM APARELHO ESPECÍFICO
        # -------------------------------------------------
        if (
            situacao_tem_compra(possui)
            and modo_compra == "Escolher um aparelho"
            and equipamento is not None
        ):
            cap_calculo = equipamento.get("capacidade")

            itens.append(
                montar_item(
                    descricao_equipamento_com_instalacao(
                        equipamento.get("descricao", "Ar-condicionado")
                    ),
                    1,
                    "equipamento",
                    equipamento.get("preco", 0),
                    origem="equipamento",
                    desconto_percentual=descontos_equipamentos_novo.get(str(equipamento_id), 0),
                )
            )

            # Em compra simples, serviços opcionais são adicionais e usam a
            # capacidade do aparelho comprado. No cenário misto, os serviços
            # pertencem ao aparelho que o cliente já possui.
            cap_servicos = (
                capacidade_existente
                if possui == "Já tenho um e também quero comprar outro"
                else cap_calculo
            )
            cap_servicos = (
                cap_servicos
                if cap_servicos in CAPACIDADES
                else None
            )

            for nome_servico in servicos:
                dados = config["servicos"][nome_servico]
                valor = float(
                    dados.get("precos", {}).get(
                        cap_servicos,
                        0,
                    )
                    or 0
                ) if cap_servicos else 0.0

                descricao_servico = (
                    descricao_servico_orcamento(nome_servico, cap_servicos, quantidades_servicos_pontos.get(nome_servico, 1))
                )

                itens.append(
                    montar_item(
                        descricao_servico,
                        quantidades_servicos_pontos.get(nome_servico, 1),
                        unidade_servico_orcamento(nome_servico),
                        valor,
                        origem="servico",
                        desconto_percentual=descontos_servicos_novo.get(nome_servico, 0),
                    )
                )

        # -------------------------------------------------
        # COMPARAÇÃO ENTRE VÁRIOS APARELHOS
        # -------------------------------------------------
        elif (
            situacao_tem_compra(possui)
            and modo_compra == "Comparar aparelhos"
            and opcoes_equipamentos
        ):
            opcoes_com_servicos = []

            for opcao in opcoes_equipamentos:
                opcao_final = copy.deepcopy(opcao)
                opcao_final["desconto_percentual"] = descontos_equipamentos_novo.get(
                    str(opcao_final.get("id", "")), 0,
                )
                cap_opcao = opcao_final.get("capacidade")
                opcao_final["descricao"] = descricao_equipamento_com_instalacao(
                    opcao_final.get("descricao", "Ar-condicionado")
                )
                servicos_opcao = []

                # Na compra simples, serviços extras (exceto instalação) podem
                # acompanhar cada opção. No cenário misto, os serviços são do
                # aparelho já existente e entram como itens comuns.
                if possui == "Não, quero comprar":
                    for nome_servico in servicos:
                        dados_servico = config["servicos"][nome_servico]
                        valor_servico = float(
                            dados_servico.get("precos", {}).get(
                                cap_opcao,
                                0,
                            )
                            or 0
                        )

                        servicos_opcao.append(
                            {
                                "descricao": descricao_servico_orcamento(nome_servico, cap_opcao, quantidades_servicos_pontos.get(nome_servico, 1)),
                                "quantidade": quantidades_servicos_pontos.get(nome_servico, 1),
                                "valor_unitario": valor_servico,
                                "valor": valor_servico * quantidades_servicos_pontos.get(nome_servico, 1),
                                "desconto_percentual": descontos_servicos_novo.get(nome_servico, 0),
                            }
                        )

                opcao_final["servicos"] = servicos_opcao
                opcao_final["total_servicos"] = sum(
                    float(s.get("valor", 0) or 0)
                    for s in servicos_opcao
                )

                opcoes_com_servicos.append(opcao_final)

            opcoes_equipamentos = opcoes_com_servicos

            if possui == "Já tenho um e também quero comprar outro":
                cap_existente = (
                    capacidade_existente
                    if capacidade_existente in CAPACIDADES
                    else None
                )
                for nome_servico in servicos:
                    dados = config["servicos"][nome_servico]
                    valor = float(
                        dados.get("precos", {}).get(
                            cap_existente,
                            0,
                        )
                        or 0
                    ) if cap_existente else 0.0
                    descricao_servico = (
                        descricao_servico_orcamento(nome_servico, cap_existente, quantidades_servicos_pontos.get(nome_servico, 1))
                    )
                    itens.append(
                        montar_item(
                            descricao_servico,
                            quantidades_servicos_pontos.get(nome_servico, 1),
                            unidade_servico_orcamento(nome_servico),
                            valor,
                            origem="servico",
                            desconto_percentual=descontos_servicos_novo.get(nome_servico, 0),
                        )
                    )

        # -------------------------------------------------
        # CLIENTE JÁ POSSUI / ESTÁ AVALIANDO
        # -------------------------------------------------
        else:
            cap_calculo = capacidade if capacidade in CAPACIDADES else None

            if cap_calculo:
                for nome_servico in servicos:
                    dados = config["servicos"][nome_servico]
                    valor = float(
                        dados.get("precos", {}).get(
                            cap_calculo,
                            0,
                        )
                        or 0
                    )

                    itens.append(
                        montar_item(
                            descricao_servico_orcamento(nome_servico, cap_calculo, quantidades_servicos_pontos.get(nome_servico, 1)),
                            quantidades_servicos_pontos.get(nome_servico, 1),
                            unidade_servico_orcamento(nome_servico),
                            valor,
                            origem="servico",
                            desconto_percentual=descontos_servicos_novo.get(nome_servico, 0),
                        )
                    )
            else:
                for nome_servico in servicos:
                    itens.append(
                        montar_item(
                            descricao_servico_orcamento(nome_servico, None, quantidades_servicos_pontos.get(nome_servico, 1)),
                            quantidades_servicos_pontos.get(nome_servico, 1),
                            unidade_servico_orcamento(nome_servico),
                            0,
                            origem="servico",
                            desconto_percentual=descontos_servicos_novo.get(nome_servico, 0),
                        )
                    )

        if tipo_imovel == "Apartamento" and int(andar) >= 2:
            valor_andar = float(
                config["regras"].get(
                    "adicional_apartamento_2_mais",
                    0,
                )
                or 0
            )
            if valor_andar > 0:
                itens.append(
                    montar_item(
                        f"Adicional de acesso • {int(andar)}º piso",
                        1,
                        "serviço",
                        valor_andar,
                        origem="regra",
                    )
                )

        # Materiais escolhidos no acesso normal usam sempre
        # preço e unidade definidos no catálogo do ADM.
        for material in materiais_selecionados:
            itens.append(
                montar_item(
                    material["nome"],
                    material["quantidade"],
                    material["unidade"],
                    material["preco"],
                    origem="material",
                )
            )

        try:
            adicionar_cobranca_km(itens, cobrar_km_novo, km_novo, tarifa_km_novo)
        except ValueError as erro_km:
            st.warning(str(erro_km))
            return

        orcamentos = carregar_orcamentos()
        numero = reservar_proximo_numero(orcamentos)

        novo = {
            "numero": numero,
            "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M"),
            "cliente": {
                "nome": nome_cliente.strip(),
                "telefone": telefone.strip(),
                "cidade": cidade.strip(),
            },
            "possui_aparelho": possui,
            "capacidade": capacidade,
            "capacidade_aparelho_existente": capacidade_existente,
            "instalacao_inclusa_equipamento": situacao_tem_compra(possui),
            "tipo_imovel": tipo_imovel,
            "andar": int(andar) if tipo_imovel == "Apartamento" else None,
            "area_ambiente": area,
            "equipamento_id": equipamento_id,
            "modo_compra": modo_compra,
            "status": "Orçamento",
            "desconto_percentual": limitar_percentual(desconto_geral_novo),
            "opcoes_equipamentos": opcoes_equipamentos,
            "itens": itens,
            "adicional": {
                "solicitado": adicional_sim == "Sim",
                "descricao": adicional_desc.strip(),
            },
            "observacoes": observacoes.strip(),
            "deslocamento": {
                "cobrar_km": bool(cobrar_km_novo),
                "km_rodados": float(km_novo if cobrar_km_novo else 0),
                "valor_por_km": float(tarifa_km_novo if cobrar_km_novo else 0),
            },
        }

        try:
            orcamentos.append(novo)
            salvar_orcamentos(orcamentos)
            st.session_state["ultimo_orcamento"] = novo

            # Orçamento concluído: apaga o rascunho temporário.
            limpar_rascunho_cliente()

            st.success(f"Orçamento {numero} salvo com sucesso.")
        except Exception as e:
            st.error(f"Não foi possível salvar o orçamento: {e}")
            return

    ultimo = st.session_state.get("ultimo_orcamento")

    if ultimo:
        numero = ultimo["numero"]
        total = total_orcamento(ultimo)

        secao(f"Orçamento {numero}", "Estimativa registrada com sucesso.")

        opcoes_pdf = ultimo.get("opcoes_equipamentos", [])

        if opcoes_pdf:
            if calcular_total(ultimo.get("itens", [])) > 0:
                st.metric(
                    "Itens comuns do orçamento",
                    dinheiro(calcular_total(ultimo.get("itens", []))),
                )
            else:
                st.markdown(
                    '<div class="capacity-note">'
                    'Orçamento comparativo de equipamentos.'
                    '</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.metric("Total estimado", dinheiro(total))

        if ultimo.get("desconto_percentual", 0):
            st.caption(
                f'Desconto geral aplicado: {limitar_percentual(ultimo.get("desconto_percentual")):g}%'
            )

        for item in ultimo.get("itens", []):
            qtd = float(item.get("quantidade", 0) or 0)
            vu = float(item.get("valor_unitario", 0) or 0)
            desconto_item = limitar_percentual(
                item.get("desconto_percentual", 0)
            )
            total_liquido = total_item(item)
            texto_desconto = (
                f" • desconto {desconto_item:g}%"
                if desconto_item > 0
                else ""
            )
            st.write(
                f"**{item.get('descricao','')}** — "
                f"{qtd:g} {item.get('unidade','')} × "
                f"{dinheiro(vu)}{texto_desconto} = "
                f"**{dinheiro(total_liquido)}**"
            )

        if opcoes_pdf:
            st.markdown("#### Opções de aparelho")
            st.caption(
                "Os aparelhos abaixo são alternativas. Os valores não são somados entre si."
            )

            for opcao in opcoes_pdf:
                preco_eq = float(opcao.get("preco", 0) or 0)
                desconto_eq = limitar_percentual(
                    opcao.get("desconto_percentual", 0)
                )
                preco_eq_liquido = aplicar_desconto(
                    preco_eq,
                    desconto_eq,
                )
                total_opcao = total_opcao_orcamento(
                    ultimo,
                    opcao,
                )

                detalhes_servicos = ""
                if opcao.get("servicos"):
                    detalhes_servicos = " • ".join(
                        f'{s.get("descricao","")}: {dinheiro(s.get("valor",0))}'
                        for s in opcao.get("servicos", [])
                    )

                st.markdown(
                    (
                        '<div class="equipment-option">'
                        f'<div class="equipment-option-name">{opcao.get("descricao","Aparelho")}</div>'
                        f'<div class="equipment-option-price">{dinheiro(preco_eq_liquido)}</div>'
                        + (
                            f'<div class="equipment-option-total">Desconto aplicado: {desconto_eq:g}%</div>'
                            if desconto_eq > 0
                            else ""
                        )
                        + (
                            f'<div class="equipment-option-total">{detalhes_servicos}</div>'
                            if detalhes_servicos
                            else ""
                        )
                        + f'<div class="equipment-option-total">Total desta opção: '
                        f'<b>{dinheiro(total_opcao)}</b></div>'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )

        if ultimo.get("adicional", {}).get("solicitado"):
            desc = ultimo.get("adicional", {}).get("descricao", "").strip()
            texto = (
                f"Adicional informado pelo cliente: {desc}. "
                "Valor sujeito à avaliação."
                if desc
                else
                "Adicional informado pelo cliente. "
                "O valor poderá ser ajustado após avaliação."
            )
            st.markdown(
                (
                    '<div class="orange-card">'
                    '<div class="card-title">Solicitação adicional</div>'
                    f'<div class="card-text">{texto}</div>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="info-card">
              <div class="card-title">Estimativa inicial</div>
              <div class="card-text">{config["regras"].get("texto_variacao","")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pdf = gerar_pdf(ultimo)
        compartilhar_pdf(
            pdf,
            f"orcamento_{numero}_F_Climatizacao.pdf",
            titulo=f"Orçamento {numero} - F Climatização",
        )

        mensagem = (
            f"Olá! Sou {ultimo['cliente']['nome']}. "
            f"Gerei o orçamento nº {numero} pelo sistema da F Climatização. "
            "Vou enviar o PDF do orçamento para conferência."
        )

        st.link_button(
            "ENVIAR MENSAGEM PARA A F CLIMATIZAÇÃO",
            link_whatsapp(mensagem),
            use_container_width=True,
        )

        st.caption(
            "Para enviar o PDF pelo WhatsApp, toque em Compartilhar PDF "
            "e escolha o WhatsApp na folha de compartilhamento do celular."
        )

    st.markdown(
        """
        <div class="footer-box">
          F CLIMATIZAÇÃO<br/>
          Orçamento inicial sujeito à avaliação técnica e confirmação final.
        </div>
        """,
        unsafe_allow_html=True,
    )



# =========================================================
# ACESSO: EXCLUSIVAMENTE ADMINISTRATIVO
# =========================================================

pagina_admin()
