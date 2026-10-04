import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import quote
from io import BytesIO
from datetime import datetime
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
    dados = completar_dict(dados, DEFAULT_CONFIG)

    # Serviços removidos do catálogo padrão
    dados.get("servicos", {}).pop("Reinstalação", None)
    dados.get("servicos", {}).pop("Manutenção", None)

    # Adicionais específicos antigos deixam de ser usados
    dados.pop("adicionais", None)

    # Valores-base novos só substituem zero/ausente
    base_precos = DEFAULT_CONFIG["servicos"]
    for servico in ["Instalação", "Carga de gás", "Desinstalação"]:
        if servico not in dados["servicos"]:
            dados["servicos"][servico] = copy.deepcopy(base_precos[servico])
        else:
            dados["servicos"][servico]["ativo"] = dados["servicos"][servico].get("ativo", True)
            dados["servicos"][servico]["mostrar_cliente"] = dados["servicos"][servico].get("mostrar_cliente", True)
            dados["servicos"][servico]["descricao"] = dados["servicos"][servico].get(
                "descricao", base_precos[servico]["descricao"]
            )
            dados["servicos"][servico].setdefault("precos", {})
            for cap, valor in base_precos[servico]["precos"].items():
                atual = dados["servicos"][servico]["precos"].get(cap)
                if atual in (None, 0, 0.0, ""):
                    dados["servicos"][servico]["precos"][cap] = valor

    # Migração de equipamentos antigos para estrutura nova
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

        # tenta aproveitar capacidade do nome antigo
        if "capacidade" not in eq or not eq.get("capacidade"):
            for cap in CAPACIDADES:
                if cap in chave:
                    eq2["capacidade"] = cap
                    break

        novos[str(eq2["id"])] = eq2
    dados["equipamentos"] = novos

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
    "cliente_capacidade",
    "cliente_servicos",
    "cliente_tipo_imovel",
    "cliente_andar",
    "cliente_area",
    "cliente_adicional_sim",
    "cliente_adicional_desc",
    "cliente_observacoes",
    "cliente_nome",
    "cliente_telefone",
    "cliente_cidade",
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
    for campo in CLIENT_DRAFT_FIELDS:
        if campo in dados and campo not in st.session_state:
            st.session_state[campo] = dados[campo]
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
          <div class="brand-sub">Painel de gestão, preços e orçamentos</div>
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
    cab_dados = [
        [
            logo_flow,
            Paragraph(
                f"<b>{empresa.get('nome','F Climatização')}</b><br/>"
                f"<font size='8'>{empresa.get('slogan','')}</font><br/>"
                f"<font size='8'>{empresa.get('texto_atendimento','')}</font>",
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

    story.append(Paragraph("<b>Itens do orçamento</b>", title_style))
    dados = [["Descrição", "Qtd.", "Unidade", "Valor unit.", "Total"]]

    for item in orcamento.get("itens", []):
        qtd = float(item.get("quantidade", 0) or 0)
        vu = float(item.get("valor_unitario", 0) or 0)
        total = qtd * vu
        dados.append(
            [
                Paragraph(str(item.get("descricao", "")), small),
                f"{qtd:g}",
                item.get("unidade", ""),
                dinheiro(vu),
                dinheiro(total),
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
        for i in orcamento.get("itens", [])
    )

    total_tbl = Table(
        [[Paragraph("<b>TOTAL ESTIMADO</b>", normal), Paragraph(f"<b>{dinheiro(total)}</b>", right)]],
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
    secao("Orçamentos", "Histórico permanente de orçamentos gerados pelo cliente.")

    orcamentos = carregar_orcamentos()

    if not orcamentos:
        st.info("Nenhum orçamento salvo ainda.")
        return

    busca = st.text_input("Buscar por número, cliente ou telefone", key="buscar_orcamentos").strip().lower()

    filtrados = []
    for o in sorted(orcamentos, key=lambda x: str(x.get("numero", "")), reverse=True):
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

        with st.expander(f"Orçamento {numero} • {nome} • {dinheiro(total)}"):
            st.markdown(f'<span class="budget-number">#{numero}</span>', unsafe_allow_html=True)
            st.write(f"**Data:** {o.get('data','')}")
            st.write(f"**Cliente:** {nome}")
            st.write(f"**Contato:** {o.get('cliente',{}).get('telefone','')}")
            st.write(f"**Cidade:** {o.get('cliente',{}).get('cidade','')}")

            st.markdown("#### Itens")

            itens_editados = []
            excluir_ids = []

            for idx, item in enumerate(o.get("itens", [])):
                iid = item.get("id") or f"item{idx}"
                with st.expander(item.get("descricao", f"Item {idx+1}")):
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
                            step=1.0 if item.get("unidade") != "metro" else 0.5,
                            key=f"orc_{numero}_{iid}_qtd",
                        )
                    with c2:
                        unidade_atual = item.get("unidade", "unidade")
                        if unidade_atual not in UNIDADES_ITEM:
                            unidade_atual = "unidade"
                        unidade = st.selectbox(
                            "Unidade",
                            UNIDADES_ITEM,
                            index=UNIDADES_ITEM.index(unidade_atual),
                            key=f"orc_{numero}_{iid}_un",
                        )

                    vu = st.number_input(
                        "Valor unitário",
                        min_value=0.0,
                        value=float(item.get("valor_unitario", 0) or 0),
                        step=1.0,
                        key=f"orc_{numero}_{iid}_vu",
                    )
                    st.caption(f"Total do item: {dinheiro(qtd * vu)}")

                    apagar = st.checkbox(
                        "Excluir este item",
                        value=False,
                        key=f"orc_{numero}_{iid}_del",
                    )

                    if apagar:
                        excluir_ids.append(iid)
                    else:
                        itens_editados.append(
                            {
                                "id": iid,
                                "descricao": desc,
                                "quantidade": float(qtd),
                                "unidade": unidade,
                                "valor_unitario": float(vu),
                                "origem": item.get("origem", "manual"),
                            }
                        )

            st.markdown("#### Adicionar item")
            novo_desc = st.text_input("Descrição do novo item", key=f"novo_desc_{numero}")
            c1, c2 = st.columns(2)
            with c1:
                nova_qtd = st.number_input(
                    "Quantidade do novo item",
                    min_value=0.0,
                    value=1.0,
                    step=1.0,
                    key=f"nova_qtd_{numero}",
                )
            with c2:
                nova_un = st.selectbox(
                    "Unidade do novo item",
                    UNIDADES_ITEM,
                    key=f"nova_un_{numero}",
                )
            novo_vu = st.number_input(
                "Valor unitário do novo item",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key=f"novo_vu_{numero}",
            )

            adicionar = st.checkbox("Adicionar este novo item ao salvar", key=f"add_item_{numero}")

            obs_edit = st.text_area(
                "Observações do orçamento",
                value=o.get("observacoes", ""),
                key=f"obs_orc_{numero}",
            )

            total_prev = calcular_total(itens_editados)
            if adicionar and novo_desc.strip():
                total_prev += float(nova_qtd) * float(novo_vu)

            st.metric("Total atualizado", dinheiro(total_prev))

            csave, cpdf = st.columns(2)
            with csave:
                if st.button("Salvar orçamento", type="primary", key=f"salvar_orc_{numero}"):
                    novos_itens = itens_editados[:]
                    if adicionar and novo_desc.strip():
                        novos_itens.append(
                            montar_item(novo_desc.strip(), nova_qtd, nova_un, novo_vu, origem="adm")
                        )

                    for original in orcamentos:
                        if original.get("numero") == numero:
                            original["itens"] = novos_itens
                            original["observacoes"] = obs_edit
                            original["atualizado_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                            break

                    try:
                        salvar_orcamentos(orcamentos)
                        st.success("Orçamento atualizado e salvo.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar orçamento: {e}")

            with cpdf:
                orc_pdf = copy.deepcopy(o)
                orc_pdf["itens"] = itens_editados[:]
                if adicionar and novo_desc.strip():
                    orc_pdf["itens"].append(
                        montar_item(novo_desc.strip(), nova_qtd, nova_un, novo_vu, origem="adm")
                    )
                orc_pdf["observacoes"] = obs_edit
                pdf_bytes = gerar_pdf(orc_pdf)
                compartilhar_pdf(
                    pdf_bytes,
                    f"orcamento_{numero}_F_Climatizacao.pdf",
                    titulo=f"Orçamento {numero} - F Climatização",
                )


# =========================================================
# ADMIN - SERVIÇOS
# =========================================================

def aba_servicos():
    secao("Serviços", "Ative, desative e edite os preços-base.")

    for nome, dados in list(config["servicos"].items()):
        with st.expander(nome):
            dados["ativo"] = st.checkbox(
                "Ativo",
                value=bool(dados.get("ativo", True)),
                key=f"serv_ativo_{nome}",
            )
            dados["mostrar_cliente"] = st.checkbox(
                "Disponível para o cliente",
                value=bool(dados.get("mostrar_cliente", True)),
                key=f"serv_cliente_{nome}",
            )
            dados["descricao"] = st.text_area(
                "Descrição",
                value=dados.get("descricao", ""),
                key=f"serv_desc_{nome}",
            )

            for cap in CAPACIDADES:
                dados.setdefault("precos", {})
                dados["precos"][cap] = st.number_input(
                    cap,
                    min_value=0.0,
                    value=float(dados["precos"].get(cap, 0) or 0),
                    step=10.0,
                    key=f"serv_preco_{nome}_{cap}",
                )


# =========================================================
# ADMIN - MATERIAIS
# =========================================================

def aba_materiais():
    secao(
        "Materiais",
        "Catálogo interno. Estes itens não aparecem automaticamente para o cliente.",
    )

    st.info(
        "Materiais podem ser adicionados manualmente a um orçamento pelo ADM com quantidade, unidade e valor."
    )

    remover = []
    for nome, dados in list(config["materiais"].items()):
        with st.expander(nome):
            dados["ativo"] = st.checkbox(
                "Ativo",
                value=bool(dados.get("ativo", True)),
                key=f"mat_ativo_{nome}",
            )
            unidade = dados.get("unidade", "metro")
            if unidade not in UNIDADES_ITEM:
                unidade = "metro"
            dados["unidade"] = st.selectbox(
                "Unidade",
                UNIDADES_ITEM,
                index=UNIDADES_ITEM.index(unidade),
                key=f"mat_un_{nome}",
            )
            dados["preco"] = st.number_input(
                "Preço de venda",
                min_value=0.0,
                value=float(dados.get("preco", 0) or 0),
                step=1.0,
                key=f"mat_val_{nome}",
            )
            if st.checkbox("Excluir material", key=f"mat_del_{nome}"):
                remover.append(nome)

    for nome in remover:
        config["materiais"].pop(nome, None)

    st.markdown("#### Criar material")
    novo_nome = st.text_input("Nome do material", key="novo_mat_nome")
    c1, c2 = st.columns(2)
    with c1:
        novo_un = st.selectbox("Unidade", UNIDADES_ITEM, key="novo_mat_un")
    with c2:
        novo_preco = st.number_input(
            "Preço",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="novo_mat_preco",
        )
    if st.button("Adicionar material", key="add_mat"):
        if novo_nome.strip():
            config["materiais"][novo_nome.strip()] = {
                "unidade": novo_un,
                "preco": float(novo_preco),
                "ativo": True,
            }
            st.success("Material adicionado. Use Salvar alterações.")
            st.rerun()


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

    tabs = st.tabs(["Orçamentos", "Serviços", "Materiais", "Aparelhos", "Regras", "Empresa"])

    with tabs[0]:
        aba_orcamentos()
    with tabs[1]:
        aba_servicos()
    with tabs[2]:
        aba_materiais()
    with tabs[3]:
        aba_aparelhos()
    with tabs[4]:
        aba_regras()
    with tabs[5]:
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


# =========================================================
# CLIENTE
# =========================================================

def pagina_cliente():
    restaurar_rascunho_cliente()

    if st.session_state.pop("_mostrar_aviso_rascunho", False):
        st.info("Seu orçamento em andamento foi restaurado.")

    cabecalho(admin=False)

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

    if possui == "Não, quero comprar":
        ativos = [
            (eid, eq)
            for eid, eq in config["equipamentos"].items()
            if eq.get("ativo", False)
        ]

        if ativos:
            mapa = {nome_equipamento(eq): eid for eid, eq in ativos}
            nomes_equipamentos = list(mapa.keys())
            garantir_opcao_valida("cliente_equipamento", nomes_equipamentos)

            escolha = st.selectbox(
                "Escolha o aparelho",
                nomes_equipamentos,
                key="cliente_equipamento",
            )
            equipamento_id = mapa[escolha]
            equipamento = config["equipamentos"][equipamento_id]
            capacidade = equipamento.get("capacidade", "9.000 BTUs")

            st.caption(
                f"Preço-base do equipamento: {dinheiro(equipamento.get('preco', 0))}"
            )
            st.markdown(
                f"""
                <div class="orange-card">
                  <div class="card-title">Valor estimado do equipamento</div>
                  <div class="card-text">{config["regras"].get("texto_equipamento","")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            garantir_opcao_valida("cliente_capacidade_compra", CAPACIDADES)
            capacidade = st.selectbox(
                "Capacidade desejada",
                CAPACIDADES,
                key="cliente_capacidade_compra",
            )
            st.info(
                "Nenhum aparelho está disponível no catálogo no momento. "
                "A equipe confirmará as opções pelo WhatsApp."
            )
    else:
        opcoes_capacidade = CAPACIDADES + ["Não sei"]
        garantir_opcao_valida("cliente_capacidade", opcoes_capacidade)
        capacidade = st.selectbox(
            "Capacidade do aparelho",
            opcoes_capacidade,
            key="cliente_capacidade",
        )

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

    opcoes_area = [
        "Não sei",
        "Até 10 m²",
        "11 a 15 m²",
        "16 a 20 m²",
        "21 a 30 m²",
        "Mais de 30 m²",
    ]
    garantir_opcao_valida("cliente_area", opcoes_area)

    area = st.selectbox(
        "Tamanho aproximado do ambiente",
        opcoes_area,
        key="cliente_area",
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

        if not servicos and equipamento is None:
            st.warning("Selecione pelo menos um serviço ou um aparelho.")
            return

        itens = []

        cap_calculo = capacidade if capacidade in CAPACIDADES else None

        if equipamento is not None:
            itens.append(
                montar_item(
                    nome_equipamento(equipamento),
                    1,
                    "equipamento",
                    equipamento.get("preco", 0),
                    origem="equipamento",
                )
            )

        if cap_calculo:
            for nome_servico in servicos:
                dados = config["servicos"][nome_servico]
                valor = float(
                    dados.get("precos", {}).get(cap_calculo, 0) or 0
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

        orcamentos = carregar_orcamentos()
        numero = proximo_numero(orcamentos)

        novo = {
            "numero": numero,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
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

        st.metric("Total estimado", dinheiro(total))

        for item in ultimo.get("itens", []):
            qtd = float(item.get("quantidade", 0) or 0)
            vu = float(item.get("valor_unitario", 0) or 0)
            st.write(
                f"**{item.get('descricao','')}** — "
                f"{qtd:g} {item.get('unidade','')} × "
                f"{dinheiro(vu)} = **{dinheiro(qtd * vu)}**"
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
