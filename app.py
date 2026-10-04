import streamlit as st
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import quote
from datetime import datetime
from io import BytesIO
import os
import copy

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, KeepTogether
)

# =========================================================
# PÁGINA
# =========================================================

st.set_page_config(
    page_title="F Climatização",
    page_icon="logo_transparente.png" if os.path.exists("logo_transparente.png") else "logo.PNG" if os.path.exists("logo.PNG") else None,
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# IDENTIDADE VISUAL
# =========================================================

st.markdown(
    """
<style>
:root {
    --f-bg: #06080C;
    --f-bg-2: #0A0E15;
    --f-card: #0E141E;
    --f-card-2: #121B29;
    --f-blue-dark: #062B63;
    --f-blue: #0878E8;
    --f-blue-light: #20A4FF;
    --f-orange: #FF7A00;
    --f-orange-light: #FFA025;
    --f-white: #FFFFFF;
    --f-muted: #9EACBE;
    --f-border: #243349;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top right, rgba(8,120,232,.16), transparent 28%),
        radial-gradient(circle at top left, rgba(255,122,0,.07), transparent 22%),
        linear-gradient(180deg, #06080C 0%, #090D14 52%, #06080C 100%);
    color: white;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 780px;
    padding-top: .75rem;
    padding-bottom: 4rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

h1, h2, h3, h4, h5, h6, p, label,
[data-testid="stMarkdownContainer"] {
    color: #FFFFFF;
}

/* CABEÇALHO */
.brand-shell {
    background: linear-gradient(135deg, rgba(5,17,35,.98), rgba(6,43,99,.96) 58%, rgba(8,120,232,.92));
    border: 1px solid rgba(32,164,255,.34);
    border-radius: 22px;
    padding: 13px 15px;
    box-shadow: 0 15px 36px rgba(0,0,0,.30);
    overflow: hidden;
}
.brand-row {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
}
.brand-logo {
    width: 52px;
    height: 52px;
    object-fit: contain;
    flex: 0 0 52px;
}
.brand-copy { min-width: 0; }
.brand-title {
    color: #FFFFFF;
    font-weight: 950;
    font-size: 21px;
    line-height: 1.05;
    letter-spacing: .15px;
}
.brand-title .accent { color: #FF8A00; }
.brand-subtitle {
    color: #D4E7FF;
    font-size: 12px;
    margin-top: 5px;
    font-weight: 600;
}
.brand-kicker {
    color: #FF9B1A;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: .8px;
    margin-bottom: 4px;
}
.quick-strip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
    padding: 8px 2px 2px;
}
.service-area {
    color: #94A8C0;
    font-size: 11.5px;
    font-weight: 650;
}
.quick-whatsapp {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    text-decoration: none !important;
    color: #D9FFE9 !important;
    background: rgba(13,174,101,.10);
    border: 1px solid rgba(21,201,122,.30);
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 11.5px;
    font-weight: 800;
}
.quick-whatsapp:hover {
    background: rgba(13,174,101,.17);
    color: #FFFFFF !important;
}

/* SEÇÕES */
.section-wrap { margin-top: 26px; margin-bottom: 11px; }
.section-title {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 900;
    line-height: 1.2;
}
.section-title .accent { color: #FF7A00; }
.section-subtitle {
    color: #8FA1B7;
    font-size: 13px;
    margin-top: 4px;
    line-height: 1.45;
}

/* CARDS */
.f-card,
.f-card-blue,
.f-card-orange {
    border-radius: 18px;
    padding: 15px 16px;
    margin: 13px 0;
}
.f-card {
    background: linear-gradient(180deg, #101722, #0D131C);
    border: 1px solid #243247;
}
.f-card-blue {
    background: linear-gradient(135deg, rgba(8,120,232,.15), rgba(14,19,28,.97));
    border: 1px solid rgba(8,120,232,.42);
    border-left: 4px solid #0878E8;
}
.f-card-orange {
    background: linear-gradient(135deg, rgba(255,122,0,.12), rgba(14,19,28,.97));
    border: 1px solid rgba(255,122,0,.34);
    border-left: 4px solid #FF7A00;
}
.f-card-title { color: white; font-weight: 900; font-size: 16px; }
.f-card-text { color: #AAB6C8; font-size: 13px; line-height: 1.5; margin-top: 4px; }

/* INPUTS */
div[data-testid="stWidgetLabel"] p { color: #FFFFFF !important; font-weight: 650 !important; }
div[data-testid="stRadio"],
div[data-testid="stCheckbox"] {
    background: #0D131C;
    border: 1px solid #202D3E;
    border-radius: 13px;
    padding: 9px 11px;
}
div[data-testid="stCheckbox"] { margin-bottom: 5px; }

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
textarea {
    background: #111722 !important;
    border-color: #2A3A51 !important;
    border-radius: 13px !important;
    color: #FFFFFF !important;
}
input, textarea { color: #FFFFFF !important; caret-color: #FF7A00 !important; }
input::placeholder, textarea::placeholder { color: #718198 !important; }
div[data-baseweb="select"] span { color: #FFFFFF !important; }
ul[role="listbox"] { background: #111722 !important; }
li[role="option"] { color: white !important; }
div[data-baseweb="tag"] { background: #0878E8 !important; }

/* BOTÕES */
.stButton > button {
    width: 100%;
    min-height: 49px;
    border-radius: 14px;
    font-weight: 850;
    background: #111722;
    color: #FFFFFF;
    border: 1px solid #2A3A51;
}
.stButton > button:hover { border-color: #0878E8; color: #FFFFFF; }
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #0754AE, #0878E8);
    border: 1px solid #188EFC;
    color: white;
    box-shadow: 0 8px 20px rgba(8,120,232,.22);
}
.stLinkButton > a {
    background: linear-gradient(90deg, #0DAE65, #15C97A) !important;
    color: white !important;
    border: 0 !important;
    border-radius: 14px !important;
    min-height: 50px !important;
    font-weight: 850 !important;
}

/* TABS / EXPANDERS / MÉTRICAS */
div[data-testid="stExpander"] {
    background: #0D131C;
    border: 1px solid #243247;
    border-radius: 15px;
    overflow: hidden;
}
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(8,120,232,.18), rgba(14,19,28,.96));
    border: 1px solid rgba(8,120,232,.45);
    border-radius: 18px;
    padding: 16px;
}
button[data-baseweb="tab"] { color: #9AAABD !important; font-weight: 750; }
button[data-baseweb="tab"][aria-selected="true"] { color: #FFFFFF !important; }
div[data-baseweb="tab-highlight"] { background-color: #FF7A00 !important; }

/* RODAPÉ */
.f-footer {
    margin-top: 34px;
    border-top: 1px solid #1D2A3C;
    padding: 20px 5px 0;
    text-align: center;
}
.f-footer-name { color: white; font-size: 14px; font-weight: 900; letter-spacing: .8px; }
.f-footer-sub { color: #74859A; font-size: 11px; margin-top: 4px; }

@media (max-width: 600px) {
    .block-container { padding-left: .85rem; padding-right: .85rem; }
    .brand-title { font-size: 18px; }
    .brand-subtitle { font-size: 11.5px; }
    .brand-logo { width: 46px; height: 46px; flex-basis: 46px; }
    .quick-strip { padding-top: 7px; }
    .section-title { font-size: 18px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# GITHUB / SECRETS
# =========================================================

GITHUB_OWNER = "guilhermesdemedeiros-dotcom"
GITHUB_REPO = "f-climatizacao"
GITHUB_BRANCH = "main"
CONFIG_FILE = "config.json"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
ADMIN_KEY = st.secrets.get("ADMIN_KEY", "")

# Histórico privado de orçamentos.
# Para persistência real, crie um repositório PRIVADO e adicione nos Secrets:
# DATA_GITHUB_REPO = "f-climatizacao-dados"
# O GITHUB_TOKEN também precisa ter Contents Read/Write nesse repositório privado.
DATA_GITHUB_REPO = st.secrets.get("DATA_GITHUB_REPO", "")
DATA_FILE = "orcamentos.json"

# =========================================================
# CONFIGURAÇÃO PADRÃO
# =========================================================

DEFAULT_CONFIG = {
    "empresa": {
        "nome": "F Climatização",
        "slogan": "Conforto em todas as estações",
        "whatsapp": "5555999999999",
        "cidade_base": "Não-Me-Toque/RS",
        "regiao_texto": "Atendimento em Não-Me-Toque e região",
    },
    "regras": {
        "adicional_apartamento_2_piso_ou_mais": 0.0,
        "texto_preco_equipamento": (
            "O valor do equipamento é uma estimativa aproximada e pode variar conforme "
            "a disponibilidade e a cotação do fornecedor no dia. O valor final será "
            "confirmado pela F Climatização antes do fechamento do orçamento."
        ),
        "texto_estimativa": (
            "Este orçamento é uma estimativa inicial. O valor final pode variar conforme "
            "as condições reais do local, acesso, altura, materiais adicionais e necessidades "
            "identificadas na avaliação. Qualquer alteração será informada antes da execução."
        ),
    },
    "servicos": {
        "Instalação": {
            "ativo": True,
            "descricao": "Instalação padrão de ar-condicionado Split.",
            "precos": {"9.000 BTUs": 0.0, "12.000 BTUs": 0.0, "18.000 BTUs": 0.0, "24.000 BTUs": 0.0},
        },
        "Higienização": {
            "ativo": True,
            "descricao": "Limpeza e higienização do aparelho.",
            "precos": {"9.000 BTUs": 0.0, "12.000 BTUs": 0.0, "18.000 BTUs": 0.0, "24.000 BTUs": 0.0},
        },
        "Manutenção": {
            "ativo": True,
            "descricao": "Avaliação e manutenção do equipamento.",
            "precos": {"9.000 BTUs": 0.0, "12.000 BTUs": 0.0, "18.000 BTUs": 0.0, "24.000 BTUs": 0.0},
        },
        "Desinstalação": {
            "ativo": True,
            "descricao": "Retirada do aparelho instalado.",
            "precos": {"9.000 BTUs": 0.0, "12.000 BTUs": 0.0, "18.000 BTUs": 0.0, "24.000 BTUs": 0.0},
        },
        "Reinstalação": {
            "ativo": True,
            "descricao": "Reinstalação de aparelho já existente.",
            "precos": {"9.000 BTUs": 0.0, "12.000 BTUs": 0.0, "18.000 BTUs": 0.0, "24.000 BTUs": 0.0},
        },
    },
    "materiais": {
        'Tubo de cobre 1/4"': {"ativo": True, "mostrar_cliente": False, "unidade": "metro", "preco": 0.0},
        'Tubo de cobre 3/8"': {"ativo": True, "mostrar_cliente": False, "unidade": "metro", "preco": 0.0},
        'Tubo de cobre 1/2"': {"ativo": True, "mostrar_cliente": False, "unidade": "metro", "preco": 0.0},
        'Tubo de cobre 5/8"': {"ativo": True, "mostrar_cliente": False, "unidade": "metro", "preco": 0.0},
        'Tubo de cobre 3/4"': {"ativo": True, "mostrar_cliente": False, "unidade": "metro", "preco": 0.0},
        "Canaleta": {"ativo": True, "mostrar_cliente": True, "unidade": "metro", "preco": 0.0},
        "Cabo elétrico": {"ativo": True, "mostrar_cliente": False, "unidade": "metro", "preco": 0.0},
        "Mangueira de dreno": {"ativo": True, "mostrar_cliente": False, "unidade": "metro", "preco": 0.0},
        "Suporte para condensadora": {"ativo": True, "mostrar_cliente": True, "unidade": "unidade", "preco": 0.0},
    },
    "equipamentos": {},
}

# =========================================================
# CONFIG / MERGE
# =========================================================

def completar_config(base, padrao):
    if not isinstance(base, dict):
        return copy.deepcopy(padrao)
    resultado = copy.deepcopy(base)
    for chave, valor in padrao.items():
        if chave not in resultado:
            resultado[chave] = copy.deepcopy(valor)
        elif isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
            resultado[chave] = completar_config(resultado[chave], valor)
    return resultado


def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
            return completar_config(json.load(arquivo), DEFAULT_CONFIG)
    except Exception:
        return copy.deepcopy(DEFAULT_CONFIG)


config = carregar_config()

# =========================================================
# GITHUB API
# =========================================================

def github_request(repo, caminho, method="GET", data=None):
    if not GITHUB_TOKEN:
        raise Exception("GITHUB_TOKEN não encontrado nos Secrets.")

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{repo}/contents/{caminho}"
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

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=25) as response:
        content = response.read().decode("utf-8")
        return json.loads(content) if content else {}


def github_ler_json(repo, caminho, default):
    try:
        resposta = github_request(repo, caminho)
        conteudo = base64.b64decode(resposta["content"]).decode("utf-8")
        return json.loads(conteudo)
    except urllib.error.HTTPError as erro:
        if erro.code == 404:
            return copy.deepcopy(default)
        raise


def github_salvar_json(repo, caminho, dados, mensagem):
    sha = None
    try:
        atual = github_request(repo, caminho)
        sha = atual.get("sha")
    except urllib.error.HTTPError as erro:
        if erro.code != 404:
            raise

    conteudo = json.dumps(dados, ensure_ascii=False, indent=2)
    payload = {
        "message": mensagem,
        "content": base64.b64encode(conteudo.encode("utf-8")).decode("utf-8"),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha
    return github_request(repo, caminho, method="PUT", data=payload)


def salvar_config_github(nova_config):
    return github_salvar_json(
        GITHUB_REPO,
        CONFIG_FILE,
        nova_config,
        "Atualiza configurações pelo painel ADM",
    )

# =========================================================
# HISTÓRICO PRIVADO
# =========================================================

def armazenamento_privado_ok():
    return bool(DATA_GITHUB_REPO and GITHUB_TOKEN)


def carregar_orcamentos():
    if not armazenamento_privado_ok():
        return st.session_state.setdefault("orcamentos_temporarios", [])
    try:
        return github_ler_json(DATA_GITHUB_REPO, DATA_FILE, [])
    except Exception as erro:
        st.warning(f"Não foi possível acessar o histórico privado: {erro}")
        return st.session_state.setdefault("orcamentos_temporarios", [])


def salvar_orcamentos(lista):
    if not armazenamento_privado_ok():
        st.session_state["orcamentos_temporarios"] = lista
        return False
    github_salvar_json(
        DATA_GITHUB_REPO,
        DATA_FILE,
        lista,
        "Atualiza histórico de orçamentos",
    )
    return True


def proximo_numero_orcamento(lista):
    maior = 0
    for item in lista:
        try:
            maior = max(maior, int(str(item.get("numero", "0"))))
        except Exception:
            pass
    return f"{maior + 1:04d}"

# =========================================================
# UTILIDADES
# =========================================================

def dinheiro(valor):
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def encontrar_logo():
    for caminho in ["logo_transparente.png", "logo.PNG", "logo.png", "Logo.PNG", "Logo.png"]:
        if os.path.exists(caminho):
            return caminho
    return None


def logo_data_uri():
    caminho = encontrar_logo()
    if not caminho:
        return ""
    try:
        with open(caminho, "rb") as arquivo:
            conteudo = base64.b64encode(arquivo.read()).decode("ascii")
        ext = os.path.splitext(caminho)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        return f"data:{mime};base64,{conteudo}"
    except Exception:
        return ""


def nome_equipamento(dados):
    marca = str(dados.get("marca", "")).strip()
    capacidade = str(dados.get("capacidade", "")).strip() or "Capacidade não informada"
    tipo = str(dados.get("tipo", "")).strip() or "Tipo não informado"
    partes = ["Ar-condicionado"]
    if marca:
        partes.append(marca)
    partes.extend([capacidade, tipo])
    return " • ".join(partes)


def link_whatsapp(texto):
    numero = "".join(c for c in config["empresa"].get("whatsapp", "") if c.isdigit())
    return f"https://wa.me/{numero}?text={quote(texto)}"


def titulo_secao(titulo, subtitulo=""):
    st.markdown(
        f'<div class="section-wrap"><div class="section-title">{titulo}</div>'
        f'<div class="section-subtitle">{subtitulo}</div></div>',
        unsafe_allow_html=True,
    )


def cabecalho(area="cliente"):
    logo_uri = logo_data_uri()
    img = f'<img class="brand-logo" src="{logo_uri}" alt="Logo F Climatização">' if logo_uri else ""

    if area == "admin":
        html = (
            '<div class="brand-shell">'
            '<div class="brand-row">'
            f'{img}'
            '<div class="brand-copy">'
            '<div class="brand-kicker">ADMINISTRAÇÃO</div>'
            '<div class="brand-title">F <span class="accent">CLIMATIZAÇÃO</span></div>'
            '<div class="brand-subtitle">Painel de gestão, preços e orçamentos</div>'
            '</div></div></div>'
        )
    else:
        nome = config["empresa"].get("nome", "F Climatização").upper()
        slogan = config["empresa"].get("slogan", "Conforto em todas as estações")
        html = (
            '<div class="brand-shell">'
            '<div class="brand-row">'
            f'{img}'
            '<div class="brand-copy">'
            f'<div class="brand-title">{nome}</div>'
            f'<div class="brand-subtitle">{slogan}</div>'
            '</div></div></div>'
        )

    st.markdown(html, unsafe_allow_html=True)


def faixa_atendimento_whatsapp():
    cidade = config["empresa"].get("cidade_base", "Não-Me-Toque/RS")
    regiao = config["empresa"].get("regiao_texto", "Atendimento em Não-Me-Toque e região")
    mensagem = quote("Olá! Gostaria de falar com a F Climatização para solicitar um orçamento.")
    numero = "".join(c for c in config["empresa"].get("whatsapp", "") if c.isdigit())
    href = f"https://wa.me/{numero}?text={mensagem}" if numero else "#"
    st.markdown(
        f'<div class="quick-strip">'
        f'<div class="service-area">📍 {regiao or cidade}</div>'
        f'<a class="quick-whatsapp" href="{href}" target="_blank" rel="noopener noreferrer">WhatsApp</a>'
        f'</div>',
        unsafe_allow_html=True,
    )

# =========================================================
# PDF PROFISSIONAL
# =========================================================

def gerar_pdf_orcamento(orcamento):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=13 * mm,
        bottomMargin=14 * mm,
    )

    styles = getSampleStyleSheet()
    azul = colors.HexColor("#062B63")
    azul_vivo = colors.HexColor("#0878E8")
    laranja = colors.HexColor("#FF7A00")
    grafite = colors.HexColor("#10141C")
    cinza = colors.HexColor("#667085")

    normal = ParagraphStyle(
        "NormalF",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13,
        textColor=grafite,
    )
    small = ParagraphStyle(
        "SmallF",
        parent=normal,
        fontSize=8,
        leading=11,
        textColor=cinza,
    )
    title = ParagraphStyle(
        "TitleF",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=21,
        textColor=azul,
        spaceAfter=2,
    )
    right = ParagraphStyle("RightF", parent=normal, alignment=TA_RIGHT)
    center_small = ParagraphStyle("CenterSmall", parent=small, alignment=TA_CENTER)

    story = []
    logo = encontrar_logo()
    logo_flow = ""
    if logo:
        try:
            logo_flow = RLImage(logo, width=32 * mm, height=32 * mm)
        except Exception:
            logo_flow = ""

    empresa_nome = config["empresa"].get("nome", "F Climatização")
    header_text = [
        Paragraph(empresa_nome.upper(), title),
        Paragraph(config["empresa"].get("slogan", "Conforto em todas as estações"), small),
    ]
    header_data = [[logo_flow, header_text, Paragraph(f"<b>ORÇAMENTO Nº {orcamento['numero']}</b><br/>{orcamento['data']}", right)]]
    header = Table(header_data, colWidths=[36 * mm, 95 * mm, 45 * mm])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, laranja),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(header)
    story.append(Spacer(1, 6 * mm))

    cliente = orcamento.get("cliente", {})
    dados_cliente = [
        [Paragraph("<b>CLIENTE</b>", normal), ""],
        [Paragraph(f"<b>Nome:</b> {cliente.get('nome','-')}", normal), Paragraph(f"<b>Contato:</b> {cliente.get('telefone','-')}", normal)],
        [Paragraph(f"<b>Cidade:</b> {cliente.get('cidade','-')}", normal), Paragraph(f"<b>Imóvel:</b> {orcamento.get('tipo_imovel','-')}", normal)],
    ]
    t_cliente = Table(dados_cliente, colWidths=[88 * mm, 88 * mm])
    t_cliente.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFF6FF")),
        ("SPAN", (0, 0), (1, 0)),
        ("BOX", (0, 0), (-1, -1), .6, colors.HexColor("#D7E2F0")),
        ("INNERGRID", (0, 1), (-1, -1), .35, colors.HexColor("#E4EAF2")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(t_cliente)
    story.append(Spacer(1, 5 * mm))

    cabecalho_itens = ["Descrição", "Qtd.", "Unid.", "Valor unit.", "Total"]
    linhas = [cabecalho_itens]
    for item in orcamento.get("itens", []):
        linhas.append([
            Paragraph(str(item.get("descricao", "")), normal),
            f"{float(item.get('quantidade',1)):g}",
            item.get("unidade", "serviço"),
            dinheiro(item.get("valor_unitario", 0)),
            dinheiro(item.get("total", 0)),
        ])

    tabela = Table(linhas, colWidths=[76 * mm, 18 * mm, 24 * mm, 30 * mm, 30 * mm], repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), azul),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#D8E1EC")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 5 * mm))

    total_table = Table([
        [Paragraph("<b>TOTAL ESTIMADO</b>", normal), Paragraph(f"<b>{dinheiro(orcamento.get('total',0))}</b>", right)]
    ], colWidths=[118 * mm, 60 * mm])
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF4E8")),
        ("BOX", (0, 0), (-1, -1), 1, laranja),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 5 * mm))

    obs = orcamento.get("observacoes", "")
    adicional = orcamento.get("adicional_descricao", "")
    blocos = []
    if adicional:
        blocos.append(Paragraph(f"<b>Adicional informado:</b> {adicional}", normal))
    if obs:
        blocos.append(Paragraph(f"<b>Observações do cliente:</b> {obs}", normal))
    if orcamento.get("tem_equipamento"):
        blocos.append(Paragraph(config["regras"].get("texto_preco_equipamento", ""), small))
    blocos.append(Paragraph(config["regras"].get("texto_estimativa", ""), small))

    if blocos:
        bloco = Table([[blocos]], colWidths=[178 * mm])
        bloco.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F8FB")),
            ("BOX", (0, 0), (-1, -1), .6, colors.HexColor("#D8E1EC")),
            ("PADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(bloco)

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("F Climatização - orçamento sujeito à confirmação final antes da execução.", center_small))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# =========================================================
# CÁLCULO DO ORÇAMENTO
# =========================================================

def calcular_itens_orcamento(servicos, capacidade, equipamento_key, metros_tubulacao, materiais_cliente, tipo_imovel, piso, adicional_sim, adicional_desc):
    itens = []
    tem_equipamento = False

    for servico in servicos:
        valor = float(config["servicos"].get(servico, {}).get("precos", {}).get(capacidade, 0) or 0)
        itens.append({
            "descricao": servico,
            "quantidade": 1.0,
            "unidade": "serviço",
            "valor_unitario": valor,
            "total": valor,
        })

    if equipamento_key:
        eq = config["equipamentos"].get(equipamento_key, {})
        valor_eq = float(eq.get("preco", 0) or 0)
        descricao = nome_equipamento(eq)
        itens.append({
            "descricao": descricao,
            "quantidade": 1.0,
            "unidade": "equipamento",
            "valor_unitario": valor_eq,
            "total": valor_eq,
        })
        tem_equipamento = True

        material_metro = eq.get("material_metro", "")
        if material_metro and metros_tubulacao > 0:
            mat = config["materiais"].get(material_metro, {})
            if mat.get("ativo", False):
                valor_m = float(mat.get("preco", 0) or 0)
                itens.append({
                    "descricao": material_metro,
                    "quantidade": float(metros_tubulacao),
                    "unidade": "metro",
                    "valor_unitario": valor_m,
                    "total": float(metros_tubulacao) * valor_m,
                })

    for nome, quantidade in materiais_cliente.items():
        mat = config["materiais"].get(nome, {})
        if not mat.get("ativo", False) or quantidade <= 0:
            continue
        valor = float(mat.get("preco", 0) or 0)
        itens.append({
            "descricao": nome,
            "quantidade": float(quantidade),
            "unidade": mat.get("unidade", "unidade"),
            "valor_unitario": valor,
            "total": float(quantidade) * valor,
        })

    if tipo_imovel == "Apartamento" and int(piso or 1) >= 2:
        valor_ap = float(config["regras"].get("adicional_apartamento_2_piso_ou_mais", 0) or 0)
        if valor_ap > 0:
            itens.append({
                "descricao": f"Adicional de acesso - apartamento a partir do 2º piso (piso informado: {int(piso)})",
                "quantidade": 1.0,
                "unidade": "serviço",
                "valor_unitario": valor_ap,
                "total": valor_ap,
            })

    if adicional_sim:
        descricao = adicional_desc.strip() or "Adicional solicitado - sujeito a avaliação e possível alteração de valor"
        itens.append({
            "descricao": descricao,
            "quantidade": 1.0,
            "unidade": "avaliação",
            "valor_unitario": 0.0,
            "total": 0.0,
        })

    return itens, tem_equipamento

# =========================================================
# ADMIN - ORÇAMENTOS
# =========================================================

def admin_orcamentos():
    titulo_secao("Orçamentos", "Histórico numerado, edição de itens e geração de PDF.")

    if not armazenamento_privado_ok():
        st.warning(
            "O histórico está temporário nesta sessão porque o armazenamento privado ainda não foi configurado. "
            "Não é seguro salvar dados pessoais no repositório público do aplicativo."
        )

    lista = carregar_orcamentos()
    if not lista:
        st.info("Nenhum orçamento registrado ainda.")
        return

    opcoes = [f"{o.get('numero','----')} - {o.get('cliente',{}).get('nome','Cliente')} - {o.get('data','')}" for o in reversed(lista)]
    escolha = st.selectbox("Abrir orçamento", opcoes)
    indice_reverso = opcoes.index(escolha)
    indice = len(lista) - 1 - indice_reverso
    orc = copy.deepcopy(lista[indice])

    st.markdown(f"### Orçamento #{orc.get('numero','----')}")
    c1, c2 = st.columns(2)
    with c1:
        orc["cliente"]["nome"] = st.text_input("Cliente", value=orc.get("cliente", {}).get("nome", ""), key=f"orcnome_{indice}")
        orc["cliente"]["telefone"] = st.text_input("Contato", value=orc.get("cliente", {}).get("telefone", ""), key=f"orctel_{indice}")
    with c2:
        orc["cliente"]["cidade"] = st.text_input("Cidade", value=orc.get("cliente", {}).get("cidade", ""), key=f"orccidade_{indice}")
        st.text_input("Data", value=orc.get("data", ""), disabled=True, key=f"orcdata_{indice}")

    st.markdown("#### Itens")
    novos_itens = []
    for i, item in enumerate(orc.get("itens", [])):
        with st.expander(f"{i+1}. {item.get('descricao','Item')}"):
            item["descricao"] = st.text_input("Descrição", value=item.get("descricao", ""), key=f"oi_desc_{indice}_{i}")
            col1, col2 = st.columns(2)
            with col1:
                item["quantidade"] = st.number_input("Quantidade", min_value=0.0, value=float(item.get("quantidade", 1)), step=1.0, key=f"oi_qtd_{indice}_{i}")
                item["unidade"] = st.selectbox(
                    "Unidade",
                    ["metro", "unidade", "serviço", "equipamento", "avaliação"],
                    index=["metro", "unidade", "serviço", "equipamento", "avaliação"].index(item.get("unidade", "serviço")) if item.get("unidade", "serviço") in ["metro", "unidade", "serviço", "equipamento", "avaliação"] else 2,
                    key=f"oi_un_{indice}_{i}",
                )
            with col2:
                item["valor_unitario"] = st.number_input("Valor unitário", min_value=0.0, value=float(item.get("valor_unitario", 0)), step=1.0, key=f"oi_vu_{indice}_{i}")
                st.metric("Total do item", dinheiro(item["quantidade"] * item["valor_unitario"]))
            item["total"] = item["quantidade"] * item["valor_unitario"]
            remover = st.checkbox("Remover este item", key=f"oi_del_{indice}_{i}")
            if not remover:
                novos_itens.append(item)

    orc["itens"] = novos_itens

    with st.expander("+ Adicionar novo item"):
        nova_desc = st.text_input("Descrição do novo item", key=f"novo_desc_{indice}")
        c1, c2 = st.columns(2)
        with c1:
            nova_qtd = st.number_input("Quantidade do novo item", min_value=0.0, value=1.0, step=1.0, key=f"novo_qtd_{indice}")
            nova_un = st.selectbox("Unidade do novo item", ["metro", "unidade", "serviço", "equipamento", "avaliação"], key=f"novo_un_{indice}")
        with c2:
            novo_vu = st.number_input("Valor unitário do novo item", min_value=0.0, value=0.0, step=1.0, key=f"novo_vu_{indice}")
        if st.button("Adicionar item ao orçamento", key=f"add_item_{indice}"):
            if nova_desc.strip():
                orc["itens"].append({
                    "descricao": nova_desc.strip(),
                    "quantidade": float(nova_qtd),
                    "unidade": nova_un,
                    "valor_unitario": float(novo_vu),
                    "total": float(nova_qtd) * float(novo_vu),
                })
                lista[indice] = orc
                salvar_orcamentos(lista)
                st.success("Item adicionado.")
                st.rerun()
            else:
                st.warning("Informe uma descrição para o item.")

    orc["observacoes"] = st.text_area("Observações", value=orc.get("observacoes", ""), key=f"orcobs_{indice}")
    orc["total"] = sum(float(i.get("total", 0)) for i in orc.get("itens", []))
    st.metric("Total atualizado", dinheiro(orc["total"]))

    if st.button("💾 Salvar orçamento atualizado", type="primary", key=f"salvar_orc_{indice}"):
        lista[indice] = orc
        persistiu = salvar_orcamentos(lista)
        if persistiu:
            st.success("Orçamento atualizado e salvo no histórico privado.")
        else:
            st.warning("Orçamento atualizado apenas nesta sessão. Configure o repositório privado para persistência.")

    pdf = gerar_pdf_orcamento(orc)
    st.download_button(
        "📄 Baixar PDF profissional",
        data=pdf,
        file_name=f"orcamento_F_Climatizacao_{orc.get('numero','----')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# =========================================================
# ADMIN
# =========================================================

def pagina_admin():
    cabecalho("admin")

    if st.button("← Voltar para área do cliente", use_container_width=True):
        st.session_state["pagina"] = "cliente"
        st.rerun()

    if not ADMIN_KEY:
        st.error("ADMIN_KEY não configurada nos Secrets.")
        return

    if not st.session_state.get("admin_logado", False):
        titulo_secao("Acesso administrativo", "Digite a senha para continuar.")
        senha = st.text_input("Senha", type="password", placeholder="Senha do administrador")
        if st.button("ENTRAR NO PAINEL", type="primary", use_container_width=True):
            if senha == ADMIN_KEY:
                st.session_state["admin_logado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
        return

    tabs = st.tabs(["Orçamentos", "Serviços", "Materiais", "Aparelhos", "Regras", "Empresa"])

    with tabs[0]:
        admin_orcamentos()

    with tabs[1]:
        titulo_secao("Serviços", "Ative/desative e defina os preços por capacidade.")
        for nome, dados in config["servicos"].items():
            with st.expander(nome):
                dados["ativo"] = st.checkbox("Ativo", value=dados.get("ativo", True), key=f"serv_ativo_{nome}")
                dados["descricao"] = st.text_area("Descrição", value=dados.get("descricao", ""), key=f"serv_desc_{nome}")
                for capacidade in ["9.000 BTUs", "12.000 BTUs", "18.000 BTUs", "24.000 BTUs"]:
                    dados["precos"][capacidade] = st.number_input(
                        capacidade,
                        min_value=0.0,
                        value=float(dados.get("precos", {}).get(capacidade, 0)),
                        step=10.0,
                        key=f"serv_preco_{nome}_{capacidade}",
                    )

    with tabs[2]:
        titulo_secao("Materiais", "Preço por metro/unidade e visibilidade para o cliente.")
        for nome, dados in config["materiais"].items():
            with st.expander(nome):
                dados["ativo"] = st.checkbox("Ativo", value=dados.get("ativo", True), key=f"mat_ativo_{nome}")
                dados["mostrar_cliente"] = st.checkbox("Permitir que o cliente adicione", value=dados.get("mostrar_cliente", False), key=f"mat_cliente_{nome}")
                unidades = ["metro", "unidade", "serviço"]
                unidade = dados.get("unidade", "metro")
                dados["unidade"] = st.selectbox("Unidade", unidades, index=unidades.index(unidade) if unidade in unidades else 0, key=f"mat_un_{nome}")
                dados["preco"] = st.number_input("Preço de venda", min_value=0.0, value=float(dados.get("preco", 0)), step=1.0, key=f"mat_preco_{nome}")

    with tabs[3]:
        titulo_secao(
            "Aparelhos",
            "Cadastre a marca, selecione capacidade e tipo, defina o preço e controle se aparece para o cliente.",
        )

        for chave, dados in list(config["equipamentos"].items()):
            # Compatibilidade com cadastros antigos
            if not dados.get("capacidade"):
                for cap_legacy in ["9.000 BTUs", "12.000 BTUs", "18.000 BTUs", "24.000 BTUs"]:
                    if cap_legacy in str(chave):
                        dados["capacidade"] = cap_legacy
                        break
            dados.setdefault("capacidade", "9.000 BTUs")
            dados.setdefault("tipo", "Inverter")
            dados.setdefault("marca", "")
            dados.setdefault("ativo", False)
            dados.setdefault("preco", 0.0)
            dados.setdefault("material_metro", "")
            dados.setdefault("permitir_metragem_cliente", True)

            with st.expander(nome_equipamento(dados)):
                dados["ativo"] = st.checkbox(
                    "Ativo — mostrar este aparelho para o cliente",
                    value=dados.get("ativo", False),
                    key=f"eq_ativo_{chave}",
                )
                dados["marca"] = st.text_input(
                    "Marca",
                    value=dados.get("marca", ""),
                    placeholder="Ex.: LG, Samsung, Midea, Luxor...",
                    key=f"eq_marca_{chave}",
                )

                c1, c2 = st.columns(2)
                with c1:
                    caps = ["9.000 BTUs", "12.000 BTUs", "18.000 BTUs", "24.000 BTUs"]
                    cap = dados.get("capacidade", "9.000 BTUs")
                    dados["capacidade"] = st.selectbox(
                        "Capacidade",
                        caps,
                        index=caps.index(cap) if cap in caps else 0,
                        key=f"eq_cap_{chave}",
                    )
                with c2:
                    tipos = ["Inverter", "Convencional"]
                    tipo = dados.get("tipo", "Inverter")
                    dados["tipo"] = st.selectbox(
                        "Tipo",
                        tipos,
                        index=tipos.index(tipo) if tipo in tipos else 0,
                        key=f"eq_tipo_{chave}",
                    )

                dados["preco"] = st.number_input(
                    "Preço estimado do equipamento (sem instalação)",
                    min_value=0.0,
                    value=float(dados.get("preco", 0)),
                    step=50.0,
                    key=f"eq_preco_{chave}",
                )

                materiais_metro = [""] + [
                    n for n, m in config["materiais"].items()
                    if m.get("ativo") and m.get("unidade") == "metro"
                ]
                atual = dados.get("material_metro", "")
                dados["material_metro"] = st.selectbox(
                    "Tubulação/material por metro associado",
                    materiais_metro,
                    index=materiais_metro.index(atual) if atual in materiais_metro else 0,
                    key=f"eq_mat_{chave}",
                    help="O cliente informa apenas a metragem; o sistema usa este material automaticamente.",
                )
                dados["permitir_metragem_cliente"] = st.checkbox(
                    "Permitir que o cliente informe a metragem",
                    value=dados.get("permitir_metragem_cliente", True),
                    key=f"eq_metros_{chave}",
                )

                if st.button("EXCLUIR APARELHO", key=f"eq_del_btn_{chave}", use_container_width=True):
                    try:
                        del config["equipamentos"][chave]
                        salvar_config_github(config)
                        st.success("Aparelho excluído.")
                        st.rerun()
                    except Exception as erro:
                        st.error(f"Não foi possível excluir: {erro}")

        st.markdown("#### Criar novo aparelho")
        nova_marca = st.text_input(
            "Marca",
            key="nova_marca",
            placeholder="Ex.: LG, Samsung, Midea, Luxor...",
        )

        c1, c2 = st.columns(2)
        with c1:
            nova_cap = st.selectbox(
                "Capacidade",
                ["9.000 BTUs", "12.000 BTUs", "18.000 BTUs", "24.000 BTUs"],
                key="nova_cap",
            )
        with c2:
            novo_tipo = st.selectbox(
                "Tipo",
                ["Inverter", "Convencional"],
                key="novo_tipo",
            )

        novo_preco = st.number_input(
            "Preço estimado do aparelho (sem instalação)",
            min_value=0.0,
            value=0.0,
            step=50.0,
            key="novo_preco",
        )
        novo_ativo = st.checkbox(
            "Criar já ativo para aparecer ao cliente",
            value=True,
            key="novo_ativo",
        )

        materiais_novo = [""] + [
            n for n, m in config["materiais"].items()
            if m.get("ativo") and m.get("unidade") == "metro"
        ]
        novo_material = st.selectbox(
            "Tubulação/material por metro associado",
            materiais_novo,
            key="novo_material",
            help="Opcional. Pode ser definido ou alterado depois.",
        )

        if st.button("+ CRIAR NOVO APARELHO", type="primary", use_container_width=True):
            if not nova_marca.strip():
                st.warning("Informe a marca do aparelho.")
            else:
                chave = f"eq_{int(datetime.now().timestamp())}"
                config["equipamentos"][chave] = {
                    "ativo": bool(novo_ativo),
                    "marca": nova_marca.strip(),
                    "capacidade": nova_cap,
                    "tipo": novo_tipo,
                    "preco": float(novo_preco),
                    "material_metro": novo_material,
                    "permitir_metragem_cliente": True,
                }
                try:
                    salvar_config_github(config)
                    st.success("Aparelho criado e salvo.")
                    st.rerun()
                except Exception as erro:
                    del config["equipamentos"][chave]
                    st.error(f"Não foi possível criar o aparelho: {erro}")

    with tabs[4]:
        titulo_secao("Regras automáticas", "Defina adicionais e textos exibidos no orçamento.")
        config["regras"]["adicional_apartamento_2_piso_ou_mais"] = st.number_input(
            "Adicional para apartamento a partir do 2º piso",
            min_value=0.0,
            value=float(config["regras"].get("adicional_apartamento_2_piso_ou_mais", 0)),
            step=10.0,
        )
        config["regras"]["texto_preco_equipamento"] = st.text_area(
            "Observação sobre preço de equipamentos",
            value=config["regras"].get("texto_preco_equipamento", ""),
        )
        config["regras"]["texto_estimativa"] = st.text_area(
            "Observação geral da estimativa",
            value=config["regras"].get("texto_estimativa", ""),
        )

    with tabs[5]:
        titulo_secao("Empresa", "Informações usadas no aplicativo e nos orçamentos.")
        config["empresa"]["nome"] = st.text_input("Nome", value=config["empresa"].get("nome", "F Climatização"))
        config["empresa"]["slogan"] = st.text_input("Slogan", value=config["empresa"].get("slogan", "Conforto em todas as estações"))
        config["empresa"]["whatsapp"] = st.text_input("WhatsApp", value=config["empresa"].get("whatsapp", ""), help="Código do país + DDD + número.")
        config["empresa"]["cidade_base"] = st.text_input(
            "Cidade base",
            value=config["empresa"].get("cidade_base", "Não-Me-Toque/RS"),
        )
        config["empresa"]["regiao_texto"] = st.text_input(
            "Texto da área de atendimento",
            value=config["empresa"].get("regiao_texto", "Atendimento em Não-Me-Toque e região"),
        )

    st.divider()
    if st.button("💾 SALVAR ALTERAÇÕES DO SISTEMA", type="primary", use_container_width=True):
        try:
            salvar_config_github(config)
            st.success("Alterações salvas permanentemente.")
        except Exception as erro:
            st.error(f"Não foi possível salvar: {erro}")

    if st.button("SAIR DO ADMINISTRADOR", use_container_width=True):
        st.session_state["admin_logado"] = False
        st.session_state["pagina"] = "cliente"
        st.rerun()

# =========================================================
# CLIENTE
# =========================================================

def pagina_cliente():
    cabecalho("cliente")
    faixa_atendimento_whatsapp()

    st.markdown(
        '<div class="f-card-blue"><div class="f-card-title">Orçamento rápido e prático</div>'
        '<div class="f-card-text">Monte uma estimativa inicial. O valor final será confirmado antes do serviço.</div></div>',
        unsafe_allow_html=True,
    )

    titulo_secao("Seu aparelho", "Informe se já possui equipamento ou deseja comprar.")
    possui = st.radio("Você já possui o aparelho?", ["Sim, já tenho o aparelho", "Não, quero comprar", "Ainda estou avaliando"])

    equipamento_key = None
    capacidade = "Não sei"
    metros_tubulacao = 0.0

    if possui == "Não, quero comprar":
        equipamentos_ativos = [(k, v) for k, v in config["equipamentos"].items() if v.get("ativo", False)]
        if equipamentos_ativos:
            labels = []
            mapa = {}
            for k, e in equipamentos_ativos:
                label = nome_equipamento(e)
                labels.append(label)
                mapa[label] = k
            escolha = st.selectbox("Escolha o aparelho", labels)
            equipamento_key = mapa[escolha]
            eq = config["equipamentos"][equipamento_key]
            capacidade = eq.get("capacidade", "Não sei")
            st.markdown(
                f'<div class="f-card-orange"><div class="f-card-title">Valor estimado do equipamento: {dinheiro(eq.get("preco",0))}</div>'
                f'<div class="f-card-text">{config["regras"].get("texto_preco_equipamento","")}</div></div>',
                unsafe_allow_html=True,
            )
            if eq.get("material_metro") and eq.get("permitir_metragem_cliente", True):
                mat_nome = eq.get("material_metro")
                mat = config["materiais"].get(mat_nome, {})
                if mat.get("ativo", False):
                    st.caption(f"{mat_nome}: {dinheiro(mat.get('preco',0))} por metro")
                    metros_tubulacao = st.number_input("Quantos metros desse material deseja incluir?", min_value=0.0, value=0.0, step=0.5)
                    if metros_tubulacao > 0:
                        st.info(f"Total do material: {dinheiro(metros_tubulacao * float(mat.get('preco',0)))}")
        else:
            st.info("Nenhum aparelho está ativo para venda no momento. Entre em contato pelo WhatsApp para consultar opções.")
    else:
        capacidade = st.selectbox("Qual a capacidade do aparelho?", ["9.000 BTUs", "12.000 BTUs", "18.000 BTUs", "24.000 BTUs", "Não sei"])

    titulo_secao("Serviço", "Selecione o que precisa.")
    servicos_disponiveis = [nome for nome, dados in config["servicos"].items() if dados.get("ativo", True)]
    servicos = st.multiselect("Serviços desejados", servicos_disponiveis, placeholder="Selecione um ou mais serviços")

    titulo_secao("Local", "Essas informações ajudam a calcular a estimativa.")
    tipo_imovel = st.selectbox("Tipo de imóvel", ["Casa", "Apartamento", "Comércio", "Outro"])
    piso = 1
    if tipo_imovel == "Apartamento":
        piso = st.number_input("Em qual piso/andar será o serviço?", min_value=1, value=1, step=1)
        if piso >= 2 and float(config["regras"].get("adicional_apartamento_2_piso_ou_mais", 0) or 0) > 0:
            st.caption(f"Adicional estimado a partir do 2º piso: {dinheiro(config['regras']['adicional_apartamento_2_piso_ou_mais'])}")

    area = st.selectbox("Tamanho aproximado do ambiente", ["Não sei", "Até 10 m²", "11 a 15 m²", "16 a 20 m²", "21 a 30 m²", "Mais de 30 m²"])

    titulo_secao("Materiais opcionais", "Somente itens que a empresa deixou disponíveis aparecem aqui.")
    materiais_cliente = {}
    materiais_visiveis = [(n, m) for n, m in config["materiais"].items() if m.get("ativo") and m.get("mostrar_cliente")]
    if materiais_visiveis:
        for nome, mat in materiais_visiveis:
            unidade = mat.get("unidade", "unidade")
            st.caption(f"{nome}: {dinheiro(mat.get('preco',0))} por {unidade}")
            qtd = st.number_input(f"Quantidade - {nome}", min_value=0.0, value=0.0, step=0.5 if unidade == "metro" else 1.0, key=f"cli_mat_{nome}")
            materiais_cliente[nome] = qtd
            if qtd > 0:
                st.caption(f"Total: {dinheiro(qtd * float(mat.get('preco',0)))}")
    else:
        st.caption("Nenhum material opcional disponível para seleção.")

    titulo_secao("Serviço ou material adicional", "Use somente se existir algo que não apareceu nas opções acima.")
    adicional_sim = st.radio("Precisa de algum serviço ou material adicional?", ["Não", "Sim"], horizontal=True) == "Sim"
    adicional_desc = ""
    if adicional_sim:
        adicional_desc = st.text_area("Descreva o adicional, se souber", placeholder="Ex.: adaptação específica, material ou serviço adicional")
        if not adicional_desc.strip():
            st.caption("Se não descrever, o orçamento registrará que existe um adicional sujeito à avaliação e possível mudança de preço.")

    observacoes = st.text_area("Outras observações", placeholder="Informações que possam ajudar no atendimento")

    titulo_secao("Seus dados", "Preencha para identificar e registrar o orçamento.")
    nome_cliente = st.text_input("Nome")
    telefone = st.text_input("Telefone / WhatsApp")
    cidade = st.text_input("Cidade")

    if st.button("GERAR ORÇAMENTO", type="primary", use_container_width=True):
        if not nome_cliente.strip() or not telefone.strip():
            st.warning("Informe pelo menos nome e telefone/WhatsApp.")
            return
        if not servicos and not equipamento_key:
            st.warning("Selecione pelo menos um serviço ou um aparelho.")
            return

        itens, tem_equipamento = calcular_itens_orcamento(
            servicos,
            capacidade,
            equipamento_key,
            metros_tubulacao,
            materiais_cliente,
            tipo_imovel,
            piso,
            adicional_sim,
            adicional_desc,
        )
        total = sum(float(i.get("total", 0)) for i in itens)
        historico = carregar_orcamentos()
        numero = proximo_numero_orcamento(historico)
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")

        orcamento = {
            "numero": numero,
            "data": agora,
            "cliente": {"nome": nome_cliente.strip(), "telefone": telefone.strip(), "cidade": cidade.strip()},
            "tipo_imovel": tipo_imovel,
            "piso": int(piso) if tipo_imovel == "Apartamento" else None,
            "area": area,
            "capacidade": capacidade,
            "observacoes": observacoes.strip(),
            "adicional_solicitado": adicional_sim,
            "adicional_descricao": adicional_desc.strip() if adicional_desc.strip() else ("Adicional solicitado - sujeito a avaliação e possível alteração de valor" if adicional_sim else ""),
            "itens": itens,
            "total": total,
            "tem_equipamento": tem_equipamento,
        }

        historico.append(orcamento)
        persistiu = salvar_orcamentos(historico)
        st.session_state["ultimo_orcamento"] = orcamento
        st.session_state["ultimo_orcamento_persistiu"] = persistiu

    if st.session_state.get("ultimo_orcamento"):
        orcamento = st.session_state["ultimo_orcamento"]
        titulo_secao(f"Orçamento #{orcamento['numero']}", "Estimativa calculada com base nas informações fornecidas.")

        for item in orcamento["itens"]:
            if float(item.get("total", 0)) > 0:
                st.write(f"**{item['descricao']}** — {item['quantidade']:g} {item['unidade']} × {dinheiro(item['valor_unitario'])} = **{dinheiro(item['total'])}**")
            else:
                st.write(f"**{item['descricao']}**")

        st.metric("TOTAL ESTIMADO", dinheiro(orcamento["total"]))
        st.markdown(
            f'<div class="f-card-orange"><div class="f-card-title">Importante</div><div class="f-card-text">{config["regras"].get("texto_estimativa","")}</div></div>',
            unsafe_allow_html=True,
        )

        if orcamento.get("tem_equipamento"):
            st.caption(config["regras"].get("texto_preco_equipamento", ""))

        if not st.session_state.get("ultimo_orcamento_persistiu", False):
            st.warning("Este orçamento foi gerado, mas o histórico permanente ainda depende da configuração do repositório privado de dados.")

        pdf = gerar_pdf_orcamento(orcamento)
        st.download_button(
            "📄 BAIXAR ORÇAMENTO EM PDF",
            data=pdf,
            file_name=f"orcamento_F_Climatizacao_{orcamento['numero']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        mensagem = (
            f"Olá! Segue minha solicitação de orçamento #{orcamento['numero']} da {config['empresa']['nome']}.\n\n"
            f"Cliente: {orcamento['cliente']['nome']}\n"
            f"Contato: {orcamento['cliente']['telefone']}\n"
            f"Cidade: {orcamento['cliente']['cidade']}\n"
            f"Total estimado: {dinheiro(orcamento['total'])}\n\n"
            "Gostaria de confirmar os detalhes e as condições finais do orçamento."
        )
        st.link_button("SOLICITAR / CONFIRMAR PELO WHATSAPP", link_whatsapp(mensagem), use_container_width=True)

    st.markdown(
        '<div class="f-footer"><div class="f-footer-name">F CLIMATIZAÇÃO</div>'
        f'<div class="f-footer-sub">{config["empresa"].get("regiao_texto", "Atendimento em Não-Me-Toque e região")}</div></div>',
        unsafe_allow_html=True,
    )

    with st.expander("Área administrativa"):
        st.caption("Acesso exclusivo da administração.")
        if st.button("ACESSAR PAINEL ADMINISTRATIVO", use_container_width=True):
            st.session_state["pagina"] = "admin"
            st.rerun()

# =========================================================
# NAVEGAÇÃO
# =========================================================

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "cliente"

if st.session_state["pagina"] == "admin":
    pagina_admin()
else:
    pagina_cliente()
