import streamlit as st
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import quote
import os
import copy

# =========================================================
# PÁGINA
# =========================================================

st.set_page_config(
    page_title="F Climatização",
    page_icon="❄️",
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
    --f-bg: #070A0F;
    --f-card: #0E131C;
    --f-card2: #111A27;
    --f-blue-dark: #062B63;
    --f-blue: #0878E8;
    --f-blue-light: #22A7FF;
    --f-orange: #FF7A00;
    --f-orange-light: #FF9D21;
    --f-white: #FFFFFF;
    --f-muted: #AAB6C8;
    --f-border: #243247;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

html, body {
    background: #070A0F;
}

.stApp {
    background:
        radial-gradient(circle at top right, rgba(8,120,232,.13), transparent 28%),
        radial-gradient(circle at top left, rgba(255,122,0,.06), transparent 20%),
        linear-gradient(180deg, #070A0F 0%, #090D14 55%, #070A0F 100%);
    color: #FFFFFF;
}

/* Esconde itens padrão */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* Área principal */
.block-container {
    max-width: 760px;
    padding-top: 1rem;
    padding-bottom: 4rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* Textos */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}

p,
span,
label {
    color: #FFFFFF;
}

div[data-testid="stMarkdownContainer"] p {
    color: #FFFFFF;
}

/* Cabeçalho */
.brand-box {
    background:
        linear-gradient(135deg, rgba(6,43,99,.96), rgba(8,120,232,.82)),
        #0E131C;
    border: 1px solid rgba(34,167,255,.35);
    border-radius: 22px;
    padding: 18px 18px;
    box-shadow:
        0 14px 35px rgba(0,0,0,.35),
        0 0 35px rgba(8,120,232,.07);
    margin-bottom: 12px;
}

.brand-title {
    font-size: 24px;
    line-height: 1.05;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: .3px;
}

.brand-title-accent {
    color: #FF8A00;
}

.brand-subtitle {
    color: #BFD7F5;
    font-size: 13px;
    margin-top: 7px;
    font-weight: 500;
}

.brand-admin {
    color: #FF9D21;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .8px;
    margin-bottom: 5px;
}

/* Cards */
.f-card {
    background: linear-gradient(180deg, #101722 0%, #0D131C 100%);
    border: 1px solid #243247;
    border-radius: 18px;
    padding: 16px;
    margin: 14px 0;
    box-shadow: 0 10px 25px rgba(0,0,0,.20);
}

.f-card-blue {
    background: linear-gradient(135deg, rgba(6,43,99,.40), rgba(14,19,28,.95));
    border: 1px solid rgba(8,120,232,.42);
    border-left: 4px solid #0878E8;
    border-radius: 18px;
    padding: 16px;
    margin: 14px 0;
}

.f-card-orange {
    background: linear-gradient(135deg, rgba(255,122,0,.13), rgba(14,19,28,.96));
    border: 1px solid rgba(255,122,0,.32);
    border-left: 4px solid #FF7A00;
    border-radius: 18px;
    padding: 16px;
    margin: 14px 0;
}

.f-card-title {
    color: #FFFFFF;
    font-weight: 850;
    font-size: 16px;
    margin-bottom: 4px;
}

.f-card-text {
    color: #AAB6C8;
    font-size: 13px;
    line-height: 1.5;
}

/* Títulos */
.section-wrap {
    margin-top: 27px;
    margin-bottom: 12px;
}

.section-title {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 900;
    line-height: 1.2;
}

.section-title span {
    color: #FF8A00;
}

.section-subtitle {
    color: #8FA1B7;
    font-size: 13px;
    margin-top: 4px;
}

/* Divisor */
hr {
    border-color: #233044 !important;
}

/* Labels de formulário */
div[data-testid="stWidgetLabel"] p {
    color: #FFFFFF !important;
    font-weight: 650 !important;
}

div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label {
    color: #FFFFFF !important;
}

div[data-testid="stRadio"] p,
div[data-testid="stCheckbox"] p {
    color: #FFFFFF !important;
}

/* Radio buttons */
div[data-testid="stRadio"] {
    background: #0D131C;
    border: 1px solid #243247;
    border-radius: 16px;
    padding: 12px 14px;
}

div[data-testid="stRadio"] label > div:first-child {
    border-color: #0878E8 !important;
}

/* Checkbox */
div[data-testid="stCheckbox"] {
    background: #0D131C;
    border: 1px solid #202D3E;
    border-radius: 12px;
    padding: 7px 10px;
    margin-bottom: 5px;
}

/* Inputs */
div[data-baseweb="select"] > div {
    background-color: #111722 !important;
    border-color: #2A3A51 !important;
    border-radius: 13px !important;
    color: white !important;
}

div[data-baseweb="select"] span {
    color: #FFFFFF !important;
}

div[data-baseweb="input"] > div {
    background-color: #111722 !important;
    border-color: #2A3A51 !important;
    border-radius: 13px !important;
}

input {
    color: #FFFFFF !important;
    caret-color: #FF7A00 !important;
}

textarea {
    color: #FFFFFF !important;
    background-color: #111722 !important;
    border-color: #2A3A51 !important;
    border-radius: 13px !important;
}

input::placeholder,
textarea::placeholder {
    color: #74859A !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #111722 !important;
    border-radius: 13px !important;
}

ul[role="listbox"] {
    background: #111722 !important;
}

li[role="option"] {
    color: white !important;
}

/* Multiselect */
div[data-baseweb="tag"] {
    background-color: #0878E8 !important;
}

div[data-baseweb="tag"] span {
    color: #FFFFFF !important;
}

/* Botões */
.stButton > button {
    width: 100%;
    min-height: 49px;
    border-radius: 14px;
    font-weight: 800;
    background: #111722;
    color: #FFFFFF;
    border: 1px solid #2A3A51;
}

.stButton > button:hover {
    border-color: #0878E8;
    color: #FFFFFF;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #0755B2 0%, #0878E8 100%);
    color: #FFFFFF;
    border: 1px solid #188EFC;
    box-shadow: 0 8px 20px rgba(8,120,232,.22);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(90deg, #0878E8 0%, #1496FF 100%);
    color: #FFFFFF;
}

/* WhatsApp */
.stLinkButton > a {
    background: linear-gradient(90deg, #0AAE64, #14C879) !important;
    color: #FFFFFF !important;
    border: 0 !important;
    border-radius: 14px !important;
    min-height: 51px !important;
    font-weight: 850 !important;
}

/* Métrica */
div[data-testid="stMetric"] {
    background:
        linear-gradient(135deg, rgba(8,120,232,.18), rgba(14,19,28,.95));
    border: 1px solid rgba(8,120,232,.45);
    border-radius: 18px;
    padding: 17px;
}

div[data-testid="stMetric"] label {
    color: #AFC9E9 !important;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

div[data-testid="stMetricValue"] > div {
    color: #FFFFFF !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: #0D131C;
    border: 1px solid #243247;
    border-radius: 15px;
    overflow: hidden;
}

div[data-testid="stExpander"] details summary p {
    color: #FFFFFF !important;
    font-weight: 700;
}

/* Tabs */
div[data-baseweb="tab-list"] {
    gap: 6px;
}

button[data-baseweb="tab"] {
    color: #9AAABD !important;
    font-weight: 750;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #FF7A00 !important;
}

/* Alertas */
div[data-testid="stAlert"] {
    border-radius: 14px;
}

/* Caption */
div[data-testid="stCaptionContainer"] p {
    color: #8FA1B7 !important;
}

/* Rodapé */
.f-footer {
    margin-top: 38px;
    border-top: 1px solid #1D2A3C;
    padding: 22px 5px 0 5px;
    text-align: center;
}

.f-footer-name {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 900;
    letter-spacing: .8px;
}

.f-footer-sub {
    color: #74859A;
    font-size: 11px;
    margin-top: 4px;
}

.orange {
    color: #FF7A00 !important;
}

.blue {
    color: #22A7FF !important;
}

/* Mobile */
@media (max-width: 600px) {

    .block-container {
        padding-left: .9rem;
        padding-right: .9rem;
        padding-top: .7rem;
    }

    .brand-title {
        font-size: 20px;
    }

    .brand-subtitle {
        font-size: 12px;
    }

    .section-title {
        font-size: 18px;
    }
}
</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# GITHUB
# =========================================================

GITHUB_OWNER = "guilhermesdemedeiros-dotcom"
GITHUB_REPO = "f-climatizacao"
GITHUB_BRANCH = "main"
CONFIG_FILE = "config.json"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
ADMIN_KEY = st.secrets.get("ADMIN_KEY", "")

# =========================================================
# CONFIGURAÇÃO PADRÃO
# =========================================================

DEFAULT_CONFIG = {
    "empresa": {
        "nome": "F Climatização",
        "slogan": "Seu ambiente na temperatura ideal",
        "whatsapp": "5555999999999"
    },
    "servicos": {
        "Instalação": {
            "icone": "🛠️",
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Instalação padrão de ar-condicionado Split.",
            "precos": {
                "9.000 BTUs": 0.0,
                "12.000 BTUs": 0.0,
                "18.000 BTUs": 0.0,
                "24.000 BTUs": 0.0
            }
        },
        "Higienização": {
            "icone": "✨",
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Limpeza e higienização do aparelho.",
            "precos": {
                "9.000 BTUs": 0.0,
                "12.000 BTUs": 0.0,
                "18.000 BTUs": 0.0,
                "24.000 BTUs": 0.0
            }
        },
        "Manutenção": {
            "icone": "🔧",
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Avaliação e manutenção do equipamento.",
            "precos": {
                "9.000 BTUs": 0.0,
                "12.000 BTUs": 0.0,
                "18.000 BTUs": 0.0,
                "24.000 BTUs": 0.0
            }
        },
        "Desinstalação": {
            "icone": "📦",
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Retirada do aparelho instalado.",
            "precos": {
                "9.000 BTUs": 0.0,
                "12.000 BTUs": 0.0,
                "18.000 BTUs": 0.0,
                "24.000 BTUs": 0.0
            }
        },
        "Reinstalação": {
            "icone": "♻️",
            "ativo": True,
            "mostrar_cliente": True,
            "descricao": "Reinstalação de aparelho já existente.",
            "precos": {
                "9.000 BTUs": 0.0,
                "12.000 BTUs": 0.0,
                "18.000 BTUs": 0.0,
                "24.000 BTUs": 0.0
            }
        }
    },
    "adicionais": {
        "Apartamento": {
            "mostrar_cliente": True,
            "descricao": "Instalação ou serviço em apartamento.",
            "preco": 0.0
        },
        "Instalação em altura": {
            "mostrar_cliente": True,
            "descricao": "Local que pode exigir trabalho em altura.",
            "preco": 0.0
        },
        "Acesso difícil": {
            "mostrar_cliente": True,
            "descricao": "Local com acesso mais complexo.",
            "preco": 0.0
        },
        "Retirada de aparelho antigo": {
            "mostrar_cliente": True,
            "descricao": "Existe aparelho antigo para retirada.",
            "preco": 0.0
        },
        "Pode precisar de material adicional": {
            "mostrar_cliente": True,
            "descricao": "Pode haver necessidade de material adicional.",
            "preco": 0.0
        },
        "Adequação ou reparo": {
            "mostrar_cliente": True,
            "descricao": "Pode ser necessária alguma adequação ou reparo.",
            "preco": 0.0
        }
    },
    "materiais": {
        'Tubo de cobre 1/4"': {
            "unidade": "metro",
            "preco": 0.0,
            "ativo": True
        },
        'Tubo de cobre 3/8"': {
            "unidade": "metro",
            "preco": 0.0,
            "ativo": True
        },
        'Tubo de cobre 1/2"': {
            "unidade": "metro",
            "preco": 0.0,
            "ativo": True
        },
        'Tubo de cobre 5/8"': {
            "unidade": "metro",
            "preco": 0.0,
            "ativo": True
        },
        'Tubo de cobre 3/4"': {
            "unidade": "metro",
            "preco": 0.0,
            "ativo": True
        },
        "Canaleta": {
            "unidade": "metro",
            "preco": 0.0,
            "ativo": True
        },
        "Cabo elétrico": {
            "unidade": "metro",
            "preco": 0.0,
            "ativo": True
        },
        "Mangueira de dreno": {
            "unidade": "metro",
            "preco": 0.0,
            "ativo": True
        },
        "Suporte para condensadora": {
            "unidade": "unidade",
            "preco": 0.0,
            "ativo": True
        }
    },
    "equipamentos": {
        "Split 9.000 BTUs": {
            "preco": 0.0,
            "ativo": False
        },
        "Split 12.000 BTUs": {
            "preco": 0.0,
            "ativo": False
        },
        "Split 18.000 BTUs": {
            "preco": 0.0,
            "ativo": False
        },
        "Split 24.000 BTUs": {
            "preco": 0.0,
            "ativo": False
        }
    }
}

# =========================================================
# FUNÇÕES DE CONFIGURAÇÃO
# =========================================================

def completar_config(base, padrao):
    if not isinstance(base, dict):
        return copy.deepcopy(padrao)

    resultado = copy.deepcopy(base)

    for chave, valor in padrao.items():
        if chave not in resultado:
            resultado[chave] = copy.deepcopy(valor)

        elif isinstance(valor, dict):
            resultado[chave] = completar_config(
                resultado[chave],
                valor
            )

    return resultado


def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return completar_config(dados, DEFAULT_CONFIG)
    except Exception:
        return copy.deepcopy(DEFAULT_CONFIG)


config = carregar_config()

# =========================================================
# GITHUB API
# =========================================================

def github_request(url, method="GET", data=None):

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "F-Climatizacao"
    }

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method
    )

    with urllib.request.urlopen(
        request,
        timeout=20
    ) as response:

        conteudo = response.read().decode("utf-8")

        if not conteudo:
            return {}

        return json.loads(conteudo)


def salvar_config_github(nova_config):

    if not GITHUB_TOKEN:
        raise Exception(
            "GITHUB_TOKEN não encontrado nos Secrets."
        )

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/contents/{CONFIG_FILE}"
    )

    sha = None

    try:
        atual = github_request(
            url + f"?ref={quote(GITHUB_BRANCH)}"
        )
        sha = atual.get("sha")

    except urllib.error.HTTPError as erro:
        if erro.code != 404:
            raise

    conteudo = json.dumps(
        nova_config,
        ensure_ascii=False,
        indent=2
    )

    payload = {
        "message": "Atualiza configurações pelo painel ADM",
        "content": base64.b64encode(
            conteudo.encode("utf-8")
        ).decode("utf-8"),
        "branch": GITHUB_BRANCH
    }

    if sha:
        payload["sha"] = sha

    return github_request(
        url,
        method="PUT",
        data=payload
    )

# =========================================================
# UTILIDADES
# =========================================================

def dinheiro(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def link_whatsapp(texto):

    numero = "".join(
        c
        for c in config["empresa"].get(
            "whatsapp",
            ""
        )
        if c.isdigit()
    )

    return (
        f"https://wa.me/{numero}"
        f"?text={quote(texto)}"
    )


def encontrar_logo():

    possibilidades = [
        "logo.PNG",
        "logo.png",
        "Logo.PNG",
        "Logo.png"
    ]

    for caminho in possibilidades:
        if os.path.exists(caminho):
            return caminho

    return None


def titulo_secao(titulo, subtitulo=""):

    html = (
        '<div class="section-wrap">'
        f'<div class="section-title">{titulo}</div>'
        f'<div class="section-subtitle">{subtitulo}</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def cabecalho(area="cliente"):

    logo = encontrar_logo()

    col_logo, col_texto = st.columns(
        [1, 2.6],
        vertical_alignment="center"
    )

    with col_logo:

        if logo:
            st.image(
                logo,
                use_container_width=True
            )
        else:
            st.markdown(
                '<div style="font-size:54px;text-align:center;">❄️</div>',
                unsafe_allow_html=True
            )

    with col_texto:

        if area == "admin":

            html = (
                '<div class="brand-box">'
                '<div class="brand-admin">ADMINISTRAÇÃO</div>'
                '<div class="brand-title">'
                'F <span class="brand-title-accent">CLIMATIZAÇÃO</span>'
                '</div>'
                '<div class="brand-subtitle">'
                'Painel de gestão e configurações'
                '</div>'
                '</div>'
            )

        else:

            nome = config["empresa"].get(
                "nome",
                "F Climatização"
            )

            slogan = config["empresa"].get(
                "slogan",
                "Seu ambiente na temperatura ideal"
            )

            html = (
                '<div class="brand-box">'
                f'<div class="brand-title">{nome.upper()}</div>'
                f'<div class="brand-subtitle">{slogan}</div>'
                '</div>'
            )

        st.markdown(
            html,
            unsafe_allow_html=True
        )

# =========================================================
# ADMIN
# =========================================================

def pagina_admin():

    cabecalho("admin")

    if st.button(
        "← Voltar para área do cliente",
        use_container_width=True
    ):
        st.session_state["pagina"] = "cliente"
        st.rerun()

    if not ADMIN_KEY:
        st.error(
            "ADMIN_KEY não configurada nos Secrets."
        )
        return

    if not st.session_state.get(
        "admin_logado",
        False
    ):

        titulo_secao(
            "🔐 Acesso administrativo",
            "Digite a senha para abrir o painel."
        )

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Senha do administrador"
        )

        if st.button(
            "ENTRAR NO PAINEL",
            type="primary",
            use_container_width=True
        ):

            if senha == ADMIN_KEY:

                st.session_state[
                    "admin_logado"
                ] = True

                st.rerun()

            else:
                st.error(
                    "Senha incorreta."
                )

        return

    st.success(
        "Administrador conectado"
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Serviços",
            "Adicionais",
            "Materiais",
            "Aparelhos",
            "Empresa"
        ]
    )

    # =====================================================
    # SERVIÇOS
    # =====================================================

    with tab1:

        titulo_secao(
            "Serviços",
            "Defina quais serviços aparecem e os respectivos valores."
        )

        for nome, dados in config[
            "servicos"
        ].items():

            with st.expander(nome):

                dados["ativo"] = st.checkbox(
                    "Serviço ativo",
                    value=dados.get(
                        "ativo",
                        True
                    ),
                    key=f"serv_ativo_{nome}"
                )

                dados[
                    "mostrar_cliente"
                ] = st.checkbox(
                    "Mostrar para o cliente",
                    value=dados.get(
                        "mostrar_cliente",
                        True
                    ),
                    key=f"serv_cliente_{nome}"
                )

                dados[
                    "descricao"
                ] = st.text_area(
                    "Descrição",
                    value=dados.get(
                        "descricao",
                        ""
                    ),
                    key=f"serv_desc_{nome}"
                )

                st.markdown(
                    "**Valores por capacidade**"
                )

                for capacidade in [
                    "9.000 BTUs",
                    "12.000 BTUs",
                    "18.000 BTUs",
                    "24.000 BTUs"
                ]:

                    dados[
                        "precos"
                    ][capacidade] = st.number_input(
                        capacidade,
                        min_value=0.0,
                        value=float(
                            dados[
                                "precos"
                            ].get(
                                capacidade,
                                0
                            )
                        ),
                        step=10.0,
                        key=(
                            f"serv_preco_"
                            f"{nome}_{capacidade}"
                        )
                    )

    # =====================================================
    # ADICIONAIS
    # =====================================================

    with tab2:

        titulo_secao(
            "Situações adicionais",
            "Configure situações que podem alterar o orçamento."
        )

        for nome, dados in config[
            "adicionais"
        ].items():

            with st.expander(nome):

                dados[
                    "mostrar_cliente"
                ] = st.checkbox(
                    "Mostrar para o cliente",
                    value=dados.get(
                        "mostrar_cliente",
                        True
                    ),
                    key=f"adic_mostrar_{nome}"
                )

                dados[
                    "descricao"
                ] = st.text_area(
                    "Descrição",
                    value=dados.get(
                        "descricao",
                        ""
                    ),
                    key=f"adic_desc_{nome}"
                )

                dados[
                    "preco"
                ] = st.number_input(
                    "Valor adicional",
                    min_value=0.0,
                    value=float(
                        dados.get(
                            "preco",
                            0
                        )
                    ),
                    step=10.0,
                    key=f"adic_preco_{nome}"
                )

    # =====================================================
    # MATERIAIS
    # =====================================================

    with tab3:

        titulo_secao(
            "Materiais",
            "Controle técnico e preços de venda."
        )

        st.info(
            "Os materiais ficam no painel administrativo. "
            "O cliente não precisa selecionar componentes técnicos."
        )

        unidades = [
            "metro",
            "unidade",
            "serviço"
        ]

        for nome, dados in config[
            "materiais"
        ].items():

            with st.expander(nome):

                dados["ativo"] = st.checkbox(
                    "Material ativo",
                    value=dados.get(
                        "ativo",
                        True
                    ),
                    key=f"mat_ativo_{nome}"
                )

                unidade_atual = dados.get(
                    "unidade",
                    "metro"
                )

                if unidade_atual not in unidades:
                    unidade_atual = "metro"

                dados[
                    "unidade"
                ] = st.selectbox(
                    "Unidade de cobrança",
                    unidades,
                    index=unidades.index(
                        unidade_atual
                    ),
                    key=f"mat_unidade_{nome}"
                )

                dados[
                    "preco"
                ] = st.number_input(
                    "Preço de venda",
                    min_value=0.0,
                    value=float(
                        dados.get(
                            "preco",
                            0
                        )
                    ),
                    step=1.0,
                    key=f"mat_preco_{nome}"
                )

    # =====================================================
    # APARELHOS
    # =====================================================

    with tab4:

        titulo_secao(
            "Aparelhos",
            "Gerencie equipamentos disponíveis para venda."
        )

        for nome, dados in config[
            "equipamentos"
        ].items():

            with st.expander(nome):

                dados["ativo"] = st.checkbox(
                    "Disponível para venda",
                    value=dados.get(
                        "ativo",
                        False
                    ),
                    key=f"equip_ativo_{nome}"
                )

                dados[
                    "preco"
                ] = st.number_input(
                    "Preço de venda",
                    min_value=0.0,
                    value=float(
                        dados.get(
                            "preco",
                            0
                        )
                    ),
                    step=50.0,
                    key=f"equip_preco_{nome}"
                )

    # =====================================================
    # EMPRESA
    # =====================================================

    with tab5:

        titulo_secao(
            "Empresa",
            "Informações exibidas no aplicativo."
        )

        config[
            "empresa"
        ]["nome"] = st.text_input(
            "Nome da empresa",
            value=config[
                "empresa"
            ].get(
                "nome",
                "F Climatização"
            ),
            key="empresa_nome"
        )

        config[
            "empresa"
        ]["slogan"] = st.text_input(
            "Slogan",
            value=config[
                "empresa"
            ].get(
                "slogan",
                "Seu ambiente na temperatura ideal"
            ),
            key="empresa_slogan"
        )

        config[
            "empresa"
        ]["whatsapp"] = st.text_input(
            "WhatsApp",
            value=config[
                "empresa"
            ].get(
                "whatsapp",
                ""
            ),
            help=(
                "Use código do país + DDD + número. "
                "Exemplo: 5554999999999"
            ),
            key="empresa_whatsapp"
        )

    st.divider()

    if st.button(
        "💾 SALVAR ALTERAÇÕES",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Salvando alterações..."
            ):

                salvar_config_github(
                    config
                )

            st.success(
                "✅ Alterações salvas permanentemente."
            )

        except Exception as erro:

            st.error(
                f"Não foi possível salvar: {erro}"
            )

    if st.button(
        "🔒 SAIR DO ADMINISTRADOR",
        use_container_width=True
    ):

        st.session_state[
            "admin_logado"
        ] = False

        st.session_state[
            "pagina"
        ] = "cliente"

        st.rerun()

# =========================================================
# CLIENTE
# =========================================================

def pagina_cliente():

    cabecalho("cliente")

    st.markdown(
        (
            '<div class="f-card-blue">'
            '<div class="f-card-title">Orçamento rápido e prático</div>'
            '<div class="f-card-text">'
            'Informe os dados abaixo para receber uma estimativa inicial.'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True
    )

    # =====================================================
    # APARELHO
    # =====================================================

    titulo_secao(
        "❄️ Seu aparelho",
        "Conte primeiro qual é a sua necessidade."
    )

    possui = st.radio(
        "Você já possui o aparelho?",
        [
            "Sim, já tenho o aparelho",
            "Não, quero comprar",
            "Ainda estou avaliando"
        ]
    )

    capacidade = st.selectbox(
        "Qual a capacidade?",
        [
            "9.000 BTUs",
            "12.000 BTUs",
            "18.000 BTUs",
            "24.000 BTUs",
            "Não sei"
        ]
    )

    # =====================================================
    # SERVIÇO
    # =====================================================

    titulo_secao(
        "🛠️ Serviço",
        "Selecione o que você precisa."
    )

    servicos_disponiveis = [
        nome
        for nome, dados
        in config["servicos"].items()
        if dados.get(
            "ativo",
            True
        )
        and dados.get(
            "mostrar_cliente",
            True
        )
    ]

    servicos = st.multiselect(
        "Serviço desejado",
        servicos_disponiveis,
        placeholder=(
            "Selecione um ou mais serviços"
        )
    )

    # =====================================================
    # AMBIENTE
    # =====================================================

    titulo_secao(
        "🏠 Ambiente",
        "Essas informações ajudam a entender o serviço."
    )

    tipo_imovel = st.selectbox(
        "Tipo de imóvel",
        [
            "Casa",
            "Apartamento",
            "Comércio",
            "Outro"
        ]
    )

    area = st.selectbox(
        "Tamanho aproximado do ambiente",
        [
            "Não sei",
            "Até 10 m²",
            "11 a 15 m²",
            "16 a 20 m²",
            "21 a 30 m²",
            "Mais de 30 m²"
        ]
    )

    # =====================================================
    # LOCAL
    # =====================================================

    titulo_secao(
        "📋 Sobre o local",
        "Marque somente as situações que se aplicam."
    )

    situacoes = []

    for nome, dados in config[
        "adicionais"
    ].items():

        if dados.get(
            "mostrar_cliente",
            True
        ):

            marcado = st.checkbox(
                nome,
                key=f"cliente_{nome}"
            )

            if marcado:
                situacoes.append(nome)

    observacoes = st.text_area(
        "Alguma observação?",
        placeholder=(
            "Ex.: acesso, local da instalação "
            "ou alguma necessidade específica."
        )
    )

    # =====================================================
    # APARELHOS PARA VENDA
    # =====================================================

    aparelho_escolhido = None

    if possui == "Não, quero comprar":

        titulo_secao(
            "🧊 Aparelhos disponíveis",
            "Confira os equipamentos disponíveis."
        )

        equipamentos_ativos = [
            nome
            for nome, dados
            in config[
                "equipamentos"
            ].items()
            if dados.get(
                "ativo",
                False
            )
        ]

        if equipamentos_ativos:

            aparelho_escolhido = st.selectbox(
                "Aparelho",
                equipamentos_ativos
            )

        else:

            st.info(
                "Consulte a F Climatização "
                "sobre aparelhos disponíveis."
            )

    # =====================================================
    # DADOS DO CLIENTE
    # =====================================================

    titulo_secao(
        "👤 Seus dados",
        "Informações para facilitar o atendimento."
    )

    nome_cliente = st.text_input(
        "Nome",
        placeholder="Seu nome"
    )

    telefone = st.text_input(
        "Telefone / WhatsApp",
        placeholder="Seu telefone"
    )

    cidade = st.text_input(
        "Cidade",
        placeholder="Sua cidade"
    )

    # =====================================================
    # CÁLCULO
    # =====================================================

    total = 0.0
    tem_valor = False

    if capacidade != "Não sei":

        for servico in servicos:

            valor = float(
                config[
                    "servicos"
                ][servico][
                    "precos"
                ].get(
                    capacidade,
                    0
                )
            )

            if valor > 0:
                total += valor
                tem_valor = True

    for adicional in situacoes:

        valor = float(
            config[
                "adicionais"
            ][adicional].get(
                "preco",
                0
            )
        )

        if valor > 0:
            total += valor
            tem_valor = True

    if aparelho_escolhido:

        preco_aparelho = float(
            config[
                "equipamentos"
            ][aparelho_escolhido].get(
                "preco",
                0
            )
        )

        if preco_aparelho > 0:
            total += preco_aparelho
            tem_valor = True

    st.write("")

    # =====================================================
    # BOTÃO ORÇAMENTO
    # =====================================================

    if st.button(
        "CALCULAR ORÇAMENTO",
        type="primary",
        use_container_width=True
    ):

        if not servicos:

            st.warning(
                "Selecione pelo menos um serviço."
            )

        else:

            titulo_secao(
                "💰 Sua estimativa",
                "Resumo inicial do orçamento."
            )

            st.markdown(
                '<div class="f-card">',
                unsafe_allow_html=True
            )

            for servico in servicos:
                st.write(
                    f"✓ {servico}"
                )

            if aparelho_escolhido:
                st.write(
                    f"✓ {aparelho_escolhido}"
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

            if tem_valor:

                st.metric(
                    "Estimativa inicial",
                    dinheiro(total)
                )

            else:

                st.info(
                    "O valor será confirmado pela "
                    "F Climatização após avaliar "
                    "as informações do serviço."
                )

            st.markdown(
                (
                    '<div class="f-card-orange">'
                    '<div class="f-card-title">Importante</div>'
                    '<div class="f-card-text">'
                    'Esta é uma estimativa inicial. Caso sejam necessários '
                    'materiais adicionais, tubulação extra, adequações, '
                    'reparos ou condições especiais de instalação, '
                    'o valor será informado antes da execução. '
                    '<strong style="color:#FFFFFF;">'
                    'Nada será acrescentado sem sua aprovação.'
                    '</strong>'
                    '</div>'
                    '</div>'
                ),
                unsafe_allow_html=True
            )

            mensagem = (
                f"Olá! Gostaria de solicitar um orçamento "
                f"com a {config['empresa']['nome']}.\n\n"
                f"Nome: {nome_cliente}\n"
                f"Telefone: {telefone}\n"
                f"Cidade: {cidade}\n"
                f"Aparelho: {possui}\n"
                f"Capacidade: {capacidade}\n"
                f"Serviços: {', '.join(servicos)}\n"
                f"Imóvel: {tipo_imovel}\n"
                f"Ambiente: {area}\n"
            )

            if situacoes:

                mensagem += (
                    "Situações informadas: "
                    + ", ".join(
                        situacoes
                    )
                    + "\n"
                )

            if aparelho_escolhido:

                mensagem += (
                    "Aparelho escolhido: "
                    f"{aparelho_escolhido}\n"
                )

            if observacoes:

                mensagem += (
                    "Observações: "
                    f"{observacoes}\n"
                )

            if tem_valor:

                mensagem += (
                    "\nEstimativa inicial: "
                    f"{dinheiro(total)}"
                )

            st.link_button(
                "📲 SOLICITAR PELO WHATSAPP",
                link_whatsapp(
                    mensagem
                ),
                use_container_width=True
            )

            st.markdown(
                (
                    '<div class="f-card-blue">'
                    '<div class="f-card-title">'
                    '📷 Agilize seu atendimento'
                    '</div>'
                    '<div class="f-card-text">'
                    'Envie pelo WhatsApp fotos do local onde ficarão '
                    'a unidade interna e a unidade externa. '
                    'Se já possui o aparelho, envie também uma foto '
                    'da etiqueta ou modelo.'
                    '</div>'
                    '</div>'
                ),
                unsafe_allow_html=True
            )

    # =====================================================
    # OBSERVAÇÕES
    # =====================================================

    titulo_secao(
        "ℹ️ Observações importantes",
        ""
    )

    st.markdown(
        (
            '<div class="f-card">'
            '<div class="f-card-text">'
            'Se o serviço, material ou condição necessária não estiver '
            'listada, fale conosco pelo WhatsApp. Qualquer adicional será '
            'informado antes e dependerá da aprovação do cliente.'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True
    )

    # =====================================================
    # RODAPÉ
    # =====================================================

    st.markdown(
        (
            '<div class="f-footer">'
            '<div class="f-footer-name">'
            'F CLIMATIZAÇÃO'
            '</div>'
            '<div class="f-footer-sub">'
            'Atendimento residencial e comercial'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True
    )

    st.write("")

    # =====================================================
    # ACESSO ADMIN
    # =====================================================

    with st.expander(
        "🔐 Área administrativa"
    ):

        st.caption(
            "Acesso exclusivo da administração."
        )

        if st.button(
            "ACESSAR PAINEL ADMINISTRATIVO",
            use_container_width=True
        ):

            st.session_state[
                "pagina"
            ] = "admin"

            st.rerun()

# =========================================================
# NAVEGAÇÃO
# =========================================================

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "cliente"

# Mantém compatibilidade com o link antigo
if st.query_params.get(
    "modo",
    ""
) == "admin":

    st.session_state[
        "pagina"
    ] = "admin"

if st.session_state[
    "pagina"
] == "admin":

    pagina_admin()

else:

    pagina_cliente()
