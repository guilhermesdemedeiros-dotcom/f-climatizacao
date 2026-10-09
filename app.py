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

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
ADMIN_KEY = st.secrets.get("ADMIN_KEY", "")

CAPACIDADES = ["9.000 BTUs", "12.000 BTUs", "18.000 BTUs", "24.000 BTUs"]
TIPOS_AR = ["Inverter", "Convencional"]
UNIDADES_ITEM = ["unidade", "metro", "serviço", "equipamento"]
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


def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return migrar_config(json.load(f))
    except Exception:
        return copy.deepcopy(DEFAULT_CONFIG)


config = carregar_config()


# =========================================================
# RASCUNHO TEMPORÁRIO DO CLIENTE
# =========================================================

DRAFT_STORAGE_KEY = "f_climatizacao_orcamento_rascunho_v1"
DRAFT_TTL_SECONDS = 5 * 60

CLIENT_DRAFT_FIELDS = [
    "cliente_possui",
    "cliente_equipamento",
    "cliente_capacidade_compra",
    "cliente_capacidade_compra_unico",
    "cliente_modo_compra",
    "cliente_equipamento_unico",
    "cliente_capacidade",
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
    Restaura um rascunho salvo no navegador se ele tiver menos de 5 minutos.
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
            or str(campo).startswith("cliente_eq_visivel_")
            or str(campo).startswith("cliente_mat_qtd_")
        ) and campo not in st.session_state:
            st.session_state[campo] = valor
            alterou = True

    st.session_state["_rascunho_restaurado"] = True

    if alterou:
        st.session_state["_mostrar_aviso_rascunho"] = True
        st.rerun()


def salvar_rascunho_cliente():
    """
    Mantém o formulário atual por até 5 minutos no armazenamento local do navegador.
    Só grava novamente quando algum campo do formulário muda.
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
        elif nome_campo.startswith("cliente_mat_qtd_"):
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
        if nome_campo.startswith("cliente_eq_visivel_") or nome_campo.startswith("cliente_mat_qtd_"):
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

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8")
        except Exception:
            pass
        raise RuntimeError(f"GitHub API {e.code}: {detail or e.reason}")


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


def github_put_file(repo, path, text_content, message, sha=None):
    url = f"https://api.github.com/repos/{OWNER}/{repo}/contents/{quote(path)}"
    payload = {
        "message": message,
        "content": base64.b64encode(text_content.encode("utf-8")).decode("utf-8"),
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha
    return github_request(url, method="PUT", data=payload)


def salvar_config():
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
        content, _ = github_get_file(DATA_REPO, BUDGETS_FILE)
        if content is None:
            return []
        dados = json.loads(content)
        return dados if isinstance(dados, list) else []
    except Exception as e:
        st.error(f"Não foi possível carregar os orçamentos: {e}")
        return []


def salvar_orcamentos(lista):
    texto = json.dumps(lista, ensure_ascii=False, indent=2)
    _, sha = github_get_file(DATA_REPO, BUDGETS_FILE)
    github_put_file(
        DATA_REPO,
        BUDGETS_FILE,
        texto,
        "Atualiza histórico de orçamentos",
        sha=sha,
    )


def proximo_numero(lista):
    maior = 0
    for o in lista:
        try:
            maior = max(maior, int(str(o.get("numero", "0")).lstrip("0") or "0"))
        except Exception:
            pass
    return f"{maior + 1:04d}"


# =========================================================
# LOGO / CABEÇALHO
# =========================================================

def logo_path():
    for nome in ["logo_transparente.png", "logo_transparente.PNG", "logo.png", "logo.PNG"]:
        if os.path.exists(nome):
            return nome
    return None


def logo_data_uri():
    path = logo_path()
    if not path:
        return ""
    try:
        mime = "image/png"
        data = base64.b64encode(open(path, "rb").read()).decode("ascii")
        return f"data:{mime};base64,{data}"
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
          <div class="brand-sub">Painel de gestão de cadastros e preços</div>
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
    st.markdown(
        f"""
        <div class="section-wrap">
          <div class="section-title">{titulo}</div>
          <div class="section-sub">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



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
      const shareTitle = {json.dumps(titulo)};

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
              title: shareTitle,
              text: "Orçamento em PDF da F Climatização",
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
    empresa_linhas = [
        f"<b>{empresa.get('nome','F Climatização')}</b>",
    ]

    if empresa.get("slogan"):
        empresa_linhas.append(f"<font size='8'>{empresa.get('slogan','')}</font>")

    if empresa.get("endereco"):
        empresa_linhas.append(f"<font size='8'>{empresa.get('endereco','')}</font>")

    if empresa.get("cnpj"):
        empresa_linhas.append(f"<font size='8'>CNPJ: {empresa.get('cnpj','')}</font>")

    if empresa.get("texto_atendimento"):
        empresa_linhas.append(f"<font size='8'>{empresa.get('texto_atendimento','')}</font>")

    cab_dados = [
        [
            logo_flow,
            Paragraph(
                "<br/>".join(empresa_linhas),
                title_style,
            ),
            Paragraph(
                f"<b>ORÇAMENTO Nº {orcamento['numero']}</b><br/>"
                f"<font size='8'>Data: {orcamento.get('data','')}</font>",
                right,
            ),
        ]
    ]
    cab = Table(cab_dados, colWidths=[28 * mm, 103 * mm, 43 * mm])
    cab.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 0), (-1, -1), 1.2, laranja),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story += [cab, Spacer(1, 7 * mm)]

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
            total_item = qtd * vu
            dados.append(
                [
                    Paragraph(str(item.get("descricao", "")), small),
                    f"{qtd:g}",
                    item.get("unidade", ""),
                    dinheiro(vu),
                    dinheiro(total_item),
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

    total = sum(
        float(i.get("quantidade", 0) or 0) * float(i.get("valor_unitario", 0) or 0)
        for i in itens_orcamento
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
                "Orçamento comparativo. Cada alternativa apresenta seu próprio valor com os serviços correspondentes, sem somar os aparelhos entre si.",
                small,
            )
        )
        story.append(Spacer(1, 2 * mm))

        dados_opcoes = [["Equipamento", "Preço", "Total c/ serviços"]]

        for opcao in opcoes_equipamentos_pdf:
            preco_eq = float(opcao.get("preco", 0) or 0)
            total_servicos_opcao = float(
                opcao.get("total_servicos", 0) or 0
            )
            total_final_opcao = total + preco_eq + total_servicos_opcao

            descricao_opcao = str(
                opcao.get("descricao", "Ar-condicionado")
            )

            if opcao.get("servicos"):
                linhas_servico = "<br/>".join(
                    f'{s.get("descricao","")}: {dinheiro(s.get("valor",0))}'
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
        total_tbl = Table(
            [[
                Paragraph("<b>TOTAL ESTIMADO</b>", normal),
                Paragraph(f"<b>{dinheiro(total)}</b>", right),
            ]],
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

def calcular_total(itens):
    return sum(
        float(i.get("quantidade", 0) or 0) * float(i.get("valor_unitario", 0) or 0)
        for i in itens
    )


def montar_item(descricao, quantidade, unidade, valor_unitario, origem="manual"):
    return {
        "id": uuid.uuid4().hex[:10],
        "descricao": descricao,
        "quantidade": float(quantidade),
        "unidade": unidade,
        "valor_unitario": float(valor_unitario),
        "origem": origem,
    }


# =========================================================
# ADMIN - ORÇAMENTOS
# =========================================================

def aba_orcamentos():
    secao("Orçamentos", "Abra, ajuste itens e compartilhe novamente em PDF.")

    orcamentos = carregar_orcamentos()

    if not orcamentos:
        st.info("Nenhum orçamento salvo ainda.")
        return

    busca = st.text_input(
        "Buscar por número, cliente ou telefone",
        key="buscar_orcamentos",
    ).strip().lower()

    filtrados = []

    for o in sorted(
        orcamentos,
        key=lambda x: str(x.get("numero", "")),
        reverse=True,
    ):
        texto = " ".join(
            [
                str(o.get("numero", "")),
                str(o.get("cliente", {}).get("nome", "")),
                str(o.get("cliente", {}).get("telefone", "")),
            ]
        ).lower()

        if not busca or busca in texto:
            filtrados.append(o)

    for o in filtrados:
        numero = o.get("numero", "----")
        nome = o.get("cliente", {}).get("nome", "Cliente")
        total = calcular_total(o.get("itens", []))
        qtd_opcoes = len(o.get("opcoes_equipamentos", []))

        rotulo_total = (
            f"{qtd_opcoes} opção(ões) de aparelho"
            if qtd_opcoes
            else dinheiro(total)
        )

        with st.expander(
            f"Orçamento {numero} • {nome} • {rotulo_total}"
        ):
            st.markdown(
                f'<span class="budget-number">#{numero}</span>',
                unsafe_allow_html=True,
            )

            st.caption(
                f"{o.get('data','')} • "
                f"{o.get('cliente',{}).get('telefone','')} • "
                f"{o.get('cliente',{}).get('cidade','')}"
            )

            if o.get("opcoes_equipamentos"):
                st.markdown("#### Opções de aparelho")
                st.caption("Alternativas de compra — não são somadas entre si.")
                for opcao in o.get("opcoes_equipamentos", []):
                    preco_eq = float(opcao.get("preco", 0) or 0)
                    total_servicos_opcao = float(
                        opcao.get("total_servicos", 0) or 0
                    )
                    total_opcao = (
                        total
                        + preco_eq
                        + total_servicos_opcao
                    )
                    st.write(
                        f"**{opcao.get('descricao','Aparelho')}** — "
                        f"{dinheiro(preco_eq)} "
                        f"• total desta opção: **{dinheiro(total_opcao)}**"
                    )

            st.markdown("#### Itens atuais")

            itens_editados = []

            for idx, item in enumerate(o.get("itens", [])):
                iid = item.get("id") or f"item{idx}"

                with st.expander(
                    item.get("descricao", f"Item {idx + 1}")
                ):
                    desc = st.text_input(
                        "Descrição",
                        value=item.get("descricao", ""),
                        key=f"orc_{numero}_{iid}_desc",
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        qtd = st.number_input(
                            "Quantidade",
                            min_value=0.0,
                            value=float(item.get("quantidade", 1) or 0),
                            step=(
                                0.5
                                if item.get("unidade") == "metro"
                                else 1.0
                            ),
                            key=f"orc_{numero}_{iid}_qtd",
                        )

                    with c2:
                        unidade_atual = item.get(
                            "unidade",
                            "unidade",
                        )

                        if unidade_atual not in UNIDADES_ITEM:
                            unidade_atual = "unidade"

                        unidade = st.selectbox(
                            "Unidade",
                            UNIDADES_ITEM,
                            index=UNIDADES_ITEM.index(
                                unidade_atual
                            ),
                            key=f"orc_{numero}_{iid}_un",
                        )

                    vu = st.number_input(
                        "Valor unitário",
                        min_value=0.0,
                        value=float(
                            item.get("valor_unitario", 0) or 0
                        ),
                        step=1.0,
                        key=f"orc_{numero}_{iid}_vu",
                    )

                    st.caption(
                        f"Total: {dinheiro(qtd * vu)}"
                    )

                    remover = st.checkbox(
                        "Remover do orçamento",
                        value=False,
                        key=f"orc_{numero}_{iid}_del",
                    )

                    if not remover:
                        itens_editados.append(
                            {
                                "id": iid,
                                "descricao": desc,
                                "quantidade": float(qtd),
                                "unidade": unidade,
                                "valor_unitario": float(vu),
                                "origem": item.get(
                                    "origem",
                                    "manual",
                                ),
                            }
                        )

            # -------------------------------------------------
            # NOVO ITEM
            # -------------------------------------------------

            with st.expander("Adicionar item"):
                tipo_item = st.radio(
                    "Tipo",
                    ["Material", "Serviço"],
                    horizontal=True,
                    key=f"novo_tipo_{numero}",
                )

                adicionar = False
                item_novo = None
                novo_material_catalogo = None

                if tipo_item == "Material":
                    origem_material = st.radio(
                        "Material",
                        ["Cadastrado", "Criar novo"],
                        horizontal=True,
                        key=f"origem_material_{numero}",
                    )

                    if origem_material == "Cadastrado":
                        materiais_ativos = {
                            nome_mat: dados_mat
                            for nome_mat, dados_mat
                            in config["materiais"].items()
                            if dados_mat.get("ativo", True)
                        }

                        if not materiais_ativos:
                            st.info(
                                "Nenhum material ativo no catálogo."
                            )
                        else:
                            nomes = list(
                                materiais_ativos.keys()
                            )

                            escolhido = st.selectbox(
                                "Escolha o material",
                                nomes,
                                key=f"mat_existente_{numero}",
                            )

                            dados_mat = materiais_ativos[
                                escolhido
                            ]

                            unidade_mat = dados_mat.get(
                                "unidade",
                                "unidade",
                            )

                            if unidade_mat not in UNIDADES_ITEM:
                                unidade_mat = "unidade"

                            c1, c2 = st.columns(2)

                            with c1:
                                qtd_mat = st.number_input(
                                    "Quantidade",
                                    min_value=0.0,
                                    value=1.0,
                                    step=(
                                        0.5
                                        if unidade_mat == "metro"
                                        else 1.0
                                    ),
                                    key=(
                                        f"mat_qtd_{numero}_"
                                        f"{escolhido}"
                                    ),
                                )

                            with c2:
                                valor_mat = st.number_input(
                                    "Valor unitário",
                                    min_value=0.0,
                                    value=float(
                                        dados_mat.get(
                                            "preco",
                                            0,
                                        )
                                        or 0
                                    ),
                                    step=1.0,
                                    key=(
                                        f"mat_preco_{numero}_"
                                        f"{escolhido}"
                                    ),
                                )

                            st.caption(
                                f"Unidade: {unidade_mat} • "
                                f"Total: "
                                f"{dinheiro(qtd_mat * valor_mat)}"
                            )

                            adicionar = st.checkbox(
                                "Adicionar este material ao salvar",
                                key=f"add_mat_exist_{numero}",
                            )

                            if adicionar:
                                item_novo = montar_item(
                                    escolhido,
                                    qtd_mat,
                                    unidade_mat,
                                    valor_mat,
                                    origem="material",
                                )

                    else:
                        novo_nome_mat = st.text_input(
                            "Nome do novo material",
                            key=f"novo_mat_orc_nome_{numero}",
                        )

                        c1, c2 = st.columns(2)

                        with c1:
                            nova_un_mat = st.selectbox(
                                "Unidade",
                                UNIDADES_ITEM,
                                key=f"novo_mat_orc_un_{numero}",
                            )

                        with c2:
                            novo_preco_mat = st.number_input(
                                "Preço unitário",
                                min_value=0.0,
                                value=0.0,
                                step=1.0,
                                key=f"novo_mat_orc_preco_{numero}",
                            )

                        nova_qtd_mat = st.number_input(
                            "Quantidade",
                            min_value=0.0,
                            value=1.0,
                            step=(
                                0.5
                                if nova_un_mat == "metro"
                                else 1.0
                            ),
                            key=f"novo_mat_orc_qtd_{numero}",
                        )

                        adicionar = st.checkbox(
                            "Criar material e adicionar ao orçamento",
                            key=f"add_novo_mat_{numero}",
                        )

                        if adicionar and novo_nome_mat.strip():
                            nome_limpo = novo_nome_mat.strip()

                            item_novo = montar_item(
                                nome_limpo,
                                nova_qtd_mat,
                                nova_un_mat,
                                novo_preco_mat,
                                origem="material",
                            )

                            novo_material_catalogo = {
                                "nome": nome_limpo,
                                "dados": {
                                    "unidade": nova_un_mat,
                                    "preco": float(
                                        novo_preco_mat
                                    ),
                                    "ativo": True,
                                },
                            }

                else:
                    desc_serv = st.text_input(
                        "Descrição do serviço",
                        key=f"novo_serv_desc_{numero}",
                    )

                    c1, c2 = st.columns(2)

                    with c1:
                        qtd_serv = st.number_input(
                            "Quantidade",
                            min_value=0.0,
                            value=1.0,
                            step=1.0,
                            key=f"novo_serv_qtd_{numero}",
                        )

                    with c2:
                        preco_serv = st.number_input(
                            "Valor unitário",
                            min_value=0.0,
                            value=0.0,
                            step=1.0,
                            key=f"novo_serv_preco_{numero}",
                        )

                    adicionar = st.checkbox(
                        "Adicionar este serviço ao salvar",
                        key=f"add_serv_{numero}",
                    )

                    if adicionar and desc_serv.strip():
                        item_novo = montar_item(
                            desc_serv.strip(),
                            qtd_serv,
                            "serviço",
                            preco_serv,
                            origem="adm",
                        )

            obs_edit = st.text_area(
                "Observações do orçamento",
                value=o.get("observacoes", ""),
                key=f"obs_orc_{numero}",
            )

            total_prev = calcular_total(itens_editados)

            if item_novo:
                total_prev += (
                    float(item_novo["quantidade"])
                    * float(item_novo["valor_unitario"])
                )

            st.metric(
                "Total atualizado",
                dinheiro(total_prev),
            )

            csave, cpdf = st.columns(2)

            with csave:
                if st.button(
                    "Salvar orçamento",
                    type="primary",
                    key=f"salvar_orc_{numero}",
                ):
                    novos_itens = itens_editados[:]

                    if item_novo:
                        novos_itens.append(item_novo)

                    # Novo material criado dentro do orçamento
                    # também é salvo no catálogo.
                    if novo_material_catalogo:
                        nome_mat = novo_material_catalogo[
                            "nome"
                        ]
                        config["materiais"][
                            nome_mat
                        ] = novo_material_catalogo["dados"]

                    for original in orcamentos:
                        if original.get("numero") == numero:
                            original["itens"] = novos_itens
                            original[
                                "observacoes"
                            ] = obs_edit
                            original[
                                "atualizado_em"
                            ] = datetime.now(
                                FUSO_BRASILIA
                            ).strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            break

                    try:
                        if novo_material_catalogo:
                            salvar_config()

                        salvar_orcamentos(
                            orcamentos
                        )

                        st.success(
                            "Orçamento atualizado e salvo."
                        )
                        st.rerun()

                    except Exception as e:
                        st.error(
                            f"Erro ao salvar orçamento: {e}"
                        )

            with cpdf:
                orc_pdf = copy.deepcopy(o)
                orc_pdf["itens"] = itens_editados[:]

                if item_novo:
                    orc_pdf["itens"].append(
                        item_novo
                    )

                orc_pdf[
                    "observacoes"
                ] = obs_edit

                pdf_bytes = gerar_pdf(
                    orc_pdf
                )

                compartilhar_pdf(
                    pdf_bytes,
                    (
                        f"orcamento_{numero}_"
                        f"F_Climatizacao.pdf"
                    ),
                    titulo=(
                        f"Orçamento {numero} "
                        f"- F Climatização"
                    ),
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

            dados.setdefault("precos", {})

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

            excluir = st.checkbox(
                "Excluir este serviço",
                value=False,
                key=f"serv_excluir_{idx}_{nome}",
            )

            if excluir:
                st.caption(
                    "Ao salvar as alterações do sistema, este serviço será removido do catálogo."
                )
                continue

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

        novos_precos = {}

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


# =========================================================
# ADMIN - MATERIAIS
# =========================================================

def aba_materiais():
    secao(
        "Materiais",
        "Edite nome, unidade, preço e disponibilidade do catálogo interno.",
    )

    st.info(
        "Os materiais já cadastrados são mantidos no catálogo e podem ser renomeados. "
        "Itens inativos deixam de aparecer nas opções de inclusão em novos orçamentos."
    )

    reconstruidos = {}

    for idx, (nome, dados) in enumerate(list(config["materiais"].items())):
        with st.expander(nome):
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

            chave_final = novo_nome or nome

            # Evita sobrescrever silenciosamente outro material com o mesmo nome.
            if chave_final in reconstruidos and chave_final != nome:
                st.warning(
                    "Já existe outro material com esse nome. "
                    "Use um nome diferente antes de salvar."
                )
                chave_final = nome

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
                "Preço",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key="novo_mat_preco",
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
                    st.success("Material criado e salvo.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar material: {e}")


# =========================================================
# ADMIN - APARELHOS
# =========================================================

def aba_aparelhos():
    secao(
        "Aparelhos",
        "Cadastre marca, capacidade, tipo e preço. A descrição é criada automaticamente.",
    )

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

            st.caption(f"Descrição automática: {nome_equipamento(eq)}")

            if st.checkbox("Excluir este aparelho", key=f"eq_del_{eid}"):
                remover.append(eid)

    for eid in remover:
        config["equipamentos"].pop(eid, None)

    st.markdown("#### Criar novo aparelho")

    marca = st.text_input("Marca do novo aparelho", key="novo_eq_marca")
    cap = st.selectbox("Capacidade do novo aparelho", CAPACIDADES, key="novo_eq_cap")
    tipo = st.selectbox("Tipo do novo aparelho", TIPOS_AR, key="novo_eq_tipo")
    preco = st.number_input(
        "Preço estimado do novo aparelho",
        min_value=0.0,
        value=0.0,
        step=50.0,
        key="novo_eq_preco",
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
                st.success("Aparelho criado e salvo.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")


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

def pagina_admin():
    cabecalho(admin=True)

    if st.button("← Voltar para área do cliente", use_container_width=True):
        st.session_state["pagina"] = "cliente"
        st.query_params.clear()
        st.rerun()

    if not ADMIN_KEY:
        st.error("ADMIN_KEY não configurada nos Secrets.")
        return

    if not st.session_state.get("admin_logado", False):
        secao("Acesso administrativo", "Digite a senha para continuar.")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar no painel", type="primary", use_container_width=True):
            if senha == ADMIN_KEY:
                st.session_state["admin_logado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
        return

    tabs = st.tabs(["Serviços", "Materiais", "Aparelhos", "Regras", "Empresa"])

    with tabs[0]:
        aba_servicos()
    with tabs[1]:
        aba_materiais()
    with tabs[2]:
        aba_aparelhos()
    with tabs[3]:
        aba_regras()
    with tabs[4]:
        aba_empresa()

    st.divider()

    if st.button("Salvar alterações do sistema", type="primary", use_container_width=True):
        try:
            salvar_config()
            st.success("Configurações salvas permanentemente.")
        except Exception as e:
            st.error(f"Erro ao salvar configurações: {e}")

    if st.button("Sair do administrador", use_container_width=True):
        st.session_state["admin_logado"] = False
        st.session_state["pagina"] = "cliente"
        st.query_params.clear()
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
                    precos_servicos_atuais[nome_base] = float(
                        servico.get("valor", 0) or 0
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
        if item.get("origem") not in ("servico", "material", "equipamento", "regra")
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
            "Situação do aparelho",
            opcoes_possui,
            index=opcoes_possui.index(possui_atual),
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

        if edit_possui == "Não, quero comprar":
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
                "Como deseja montar o orçamento?",
                modos_compra,
                index=modos_compra.index(modo_atual),
                horizontal=True,
                key=f"edit_modo_compra_{numero}",
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
                                f'**{eq["descricao"]}** — {dinheiro(eq["preco"])}'
                            )

        else:
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

        servicos_opcoes = servicos_ativos[:]
        for nome in servicos_atuais:
            if nome not in servicos_opcoes:
                servicos_opcoes.append(nome)

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
            edit_possui == "Não, quero comprar"
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
                        edit_equipamento_unico["descricao"],
                        1,
                        "equipamento",
                        edit_equipamento_unico["preco"],
                        origem="equipamento",
                    )
                )

                for nome_servico in edit_servicos:
                    dados_servico = config.get("servicos", {}).get(
                        nome_servico,
                        {},
                    )
                    valor = float(
                        dados_servico.get("precos", {}).get(
                            nova_capacidade,
                            precos_servicos_atuais.get(
                                nome_servico,
                                0,
                            ),
                        )
                        or 0
                    )

                    novos_itens.append(
                        montar_item(
                            f"{nome_servico} • {nova_capacidade}",
                            1,
                            "serviço",
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
                                "descricao": f"{nome_servico} • {cap_eq}",
                                "valor": valor,
                            }
                        )

                    nova_opcao = copy.deepcopy(eq)
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
                    descricao = f"{nome_servico} • {cap_servico}"
                else:
                    valor = 0.0
                    descricao = f"{nome_servico} • capacidade a confirmar"

                novos_itens.append(
                    montar_item(
                        descricao,
                        1,
                        "serviço",
                        valor,
                        origem="servico",
                    )
                )

        orcamento["cliente"] = {
            "nome": edit_nome.strip(),
            "telefone": edit_telefone.strip(),
            "cidade": edit_cidade.strip(),
        }
        orcamento["possui_aparelho"] = edit_possui
        orcamento["modo_compra"] = (
            edit_modo_compra
            if edit_possui == "Não, quero comprar"
            else None
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

        try:
            salvar_orcamento_editado(
                orcamentos,
                orcamento,
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


def pagina_cliente():
    restaurar_rascunho_cliente()

    if st.session_state.pop("_mostrar_aviso_rascunho", False):
        st.info("Seu orçamento em andamento foi restaurado.")

    cabecalho(admin=False)

    modo_area_cliente = st.radio(
        "O que deseja fazer?",
        ["Novo orçamento", "Editar orçamento existente"],
        horizontal=True,
        key="modo_area_cliente",
    )

    if modo_area_cliente == "Editar orçamento existente":
        editor_orcamento_cliente()
        return

    st.markdown(
        """
        <div class="info-card">
          <div class="card-title">Orçamento rápido e prático</div>
          <div class="card-text">
            Monte uma estimativa inicial. O valor final será confirmado antes do serviço.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    secao("Seu aparelho", "Informe se já possui o equipamento ou deseja comprar.")

    opcoes_possui = [
        "Sim, já tenho o aparelho",
        "Não, quero comprar",
        "Ainda estou avaliando",
    ]
    garantir_opcao_valida("cliente_possui", opcoes_possui)

    possui = st.radio(
        "Você já possui o aparelho?",
        opcoes_possui,
        key="cliente_possui",
    )

    equipamento_id = None
    equipamento = None
    opcoes_equipamentos = []
    modo_compra = None

    if possui == "Não, quero comprar":
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
                            f'{dinheiro(opcao["preco"])}'
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
                    Os preços dos aparelhos não serão somados entre si.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
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

    secao("Serviços", "Selecione um ou mais serviços.")

    servicos_ativos = [
        nome
        for nome, dados in config["servicos"].items()
        if dados.get("ativo", True)
        and dados.get("mostrar_cliente", True)
    ]
    garantir_opcao_valida("cliente_servicos", servicos_ativos, multiplo=True)

    servicos = st.multiselect(
        "Serviços desejados",
        servicos_ativos,
        key="cliente_servicos",
    )

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

    secao("Seus dados", "Preencha para identificar e registrar o orçamento.")

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

    # Salva automaticamente o andamento no navegador.
    # Se o iPhone suspender/recarregar o Streamlit, os campos podem ser
    # restaurados por até 5 minutos.
    salvar_rascunho_cliente()

    if st.button("GERAR ORÇAMENTO", type="primary", use_container_width=True):
        if not nome_cliente.strip():
            st.warning("Informe o nome do cliente.")
            return

        if not telefone.strip():
            st.warning("Informe um telefone/WhatsApp.")
            return

        if possui == "Não, quero comprar":
            if modo_compra == "Escolher um aparelho" and equipamento is None:
                st.warning("Escolha um aparelho para incluir no orçamento.")
                return

            if modo_compra == "Comparar aparelhos" and not opcoes_equipamentos:
                st.warning("Marque pelo menos um aparelho para comparar.")
                return

        elif not servicos:
            st.warning("Selecione pelo menos um serviço.")
            return

        itens = []

        # -------------------------------------------------
        # VENDA DE UM APARELHO ESPECÍFICO
        # -------------------------------------------------
        if (
            possui == "Não, quero comprar"
            and modo_compra == "Escolher um aparelho"
            and equipamento is not None
        ):
            cap_calculo = equipamento.get("capacidade")

            itens.append(
                montar_item(
                    equipamento.get("descricao", "Ar-condicionado"),
                    1,
                    "equipamento",
                    equipamento.get("preco", 0),
                    origem="equipamento",
                )
            )

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
                        f"{nome_servico} • {cap_calculo}",
                        1,
                        "serviço",
                        valor,
                        origem="servico",
                    )
                )

        # -------------------------------------------------
        # COMPARAÇÃO ENTRE VÁRIOS APARELHOS
        # -------------------------------------------------
        elif (
            possui == "Não, quero comprar"
            and modo_compra == "Comparar aparelhos"
            and opcoes_equipamentos
        ):
            opcoes_com_servicos = []

            for opcao in opcoes_equipamentos:
                opcao_final = copy.deepcopy(opcao)
                cap_opcao = opcao_final.get("capacidade")
                servicos_opcao = []

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
                            "descricao": f"{nome_servico} • {cap_opcao}",
                            "valor": valor_servico,
                        }
                    )

                opcao_final["servicos"] = servicos_opcao
                opcao_final["total_servicos"] = sum(
                    float(s.get("valor", 0) or 0)
                    for s in servicos_opcao
                )

                opcoes_com_servicos.append(opcao_final)

            opcoes_equipamentos = opcoes_com_servicos

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
                            f"{nome_servico} • {cap_calculo}",
                            1,
                            "serviço",
                            valor,
                            origem="servico",
                        )
                    )
            else:
                for nome_servico in servicos:
                    itens.append(
                        montar_item(
                            f"{nome_servico} • capacidade a confirmar",
                            1,
                            "serviço",
                            0,
                            origem="servico",
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

        orcamentos = carregar_orcamentos()
        numero = proximo_numero(orcamentos)

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
            "tipo_imovel": tipo_imovel,
            "andar": int(andar) if tipo_imovel == "Apartamento" else None,
            "area_ambiente": area,
            "equipamento_id": equipamento_id,
            "modo_compra": modo_compra,
            "opcoes_equipamentos": opcoes_equipamentos,
            "itens": itens,
            "adicional": {
                "solicitado": adicional_sim == "Sim",
                "descricao": adicional_desc.strip(),
            },
            "observacoes": observacoes.strip(),
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
        total = calcular_total(ultimo.get("itens", []))

        secao(f"Orçamento {numero}", "Estimativa registrada com sucesso.")

        opcoes_pdf = ultimo.get("opcoes_equipamentos", [])

        if opcoes_pdf:
            if total > 0:
                st.metric(
                    "Itens comuns do orçamento",
                    dinheiro(total),
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

        for item in ultimo.get("itens", []):
            qtd = float(item.get("quantidade", 0) or 0)
            vu = float(item.get("valor_unitario", 0) or 0)
            st.write(
                f"**{item.get('descricao','')}** — "
                f"{qtd:g} {item.get('unidade','')} × "
                f"{dinheiro(vu)} = **{dinheiro(qtd * vu)}**"
            )

        if opcoes_pdf:
            st.markdown("#### Opções de aparelho")
            st.caption(
                "Os aparelhos abaixo são alternativas. Os valores não são somados entre si."
            )

            for opcao in opcoes_pdf:
                preco_eq = float(opcao.get("preco", 0) or 0)
                total_servicos_opcao = float(
                    opcao.get("total_servicos", 0) or 0
                )
                total_opcao = total + preco_eq + total_servicos_opcao

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
                        f'<div class="equipment-option-price">{dinheiro(preco_eq)}</div>'
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

    with st.expander("Área administrativa"):
        st.caption("Acesso exclusivo da administração.")
        if st.button(
            "Acessar painel administrativo",
            use_container_width=True,
        ):
            st.session_state["pagina"] = "admin"
            st.query_params["modo"] = "admin"
            st.rerun()


# =========================================================
# NAVEGAÇÃO
# =========================================================

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "cliente"

if st.query_params.get("modo", "") == "admin":
    st.session_state["pagina"] = "admin"

if st.session_state["pagina"] == "admin":
    pagina_admin()
else:
    pagina_cliente()
