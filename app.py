import streamlit as st
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import quote
import os

st.set_page_config(
    page_title="F Climatização",
    page_icon="❄️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# IDENTIDADE VISUAL
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top right, rgba(0,119,255,.10), transparent 32%),
        linear-gradient(180deg, #F7FAFF 0%, #FFFFFF 38%, #F7FAFF 100%);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    max-width: 760px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #062B63 !important;
}

p, label {
    line-height: 1.45;
}

.f-header {
    background: linear-gradient(135deg, #031D46 0%, #063A82 60%, #0878E8 100%);
    border-radius: 24px;
    padding: 22px 20px;
    margin-bottom: 20px;
    box-shadow: 0 12px 30px rgba(3, 29, 70, .18);
    position: relative;
    overflow: hidden;
}

.f-header:after {
    content: "";
    position: absolute;
    width: 190px;
    height: 190px;
    border-radius: 50%;
    border: 22px solid rgba(255,122,0,.18);
    right: -85px;
    top: -90px;
}

.f-brand {
    font-size: 28px;
    font-weight: 900;
    color: white;
    letter-spacing: .4px;
    margin: 0;
}

.f-brand span {
    color: #FF7A00;
}

.f-slogan {
    color: #DDEBFF;
    font-size: 14px;
    margin-top: 3px;
}

.f-badge {
    display: inline-block;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.18);
    color: white;
    border-radius: 999px;
    padding: 6px 11px;
    margin-top: 13px;
    font-size: 12px;
}

.section-title {
    font-size: 19px;
    font-weight: 800;
    color: #062B63;
    margin-top: 22px;
    margin-bottom: 4px;
}

.section-subtitle {
    font-size: 13px;
    color: #64748B;
    margin-bottom: 12px;
}

.info-card {
    background: white;
    border: 1px solid #E3EAF4;
    border-left: 4px solid #0878E8;
    border-radius: 16px;
    padding: 14px 15px;
    margin: 12px 0;
    box-shadow: 0 5px 16px rgba(6,43,99,.05);
}

.warning-card {
    background: #FFF8EF;
    border: 1px solid #FFE0B7;
    border-left: 4px solid #FF7A00;
    border-radius: 16px;
    padding: 14px 15px;
    margin: 14px 0;
    color: #563000;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 12px !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input {
    border-radius: 12px !important;
}

.stButton > button {
    width: 100%;
    border-radius: 14px;
    min-height: 48px;
    font-weight: 800;
    transition: all .15s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #063A82, #0878E8);
    border: 0;
    color: white;
    box-shadow: 0 7px 18px rgba(8,120,232,.20);
}

.stButton > button[kind="primary"]:hover {
    border: 0;
    transform: translateY(-1px);
}

.stLinkButton > a {
    border-radius: 14px !important;
    min-height: 50px;
    font-weight: 800 !important;
    background: #12B76A !important;
    color: white !important;
    border: none !important;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #DDE7F4;
    border-radius: 18px;
    padding: 15px;
    box-shadow: 0 6px 18px rgba(6,43,99,.06);
}

div[data-testid="stExpander"] {
    border: 1px solid #DDE7F4;
    border-radius: 14px;
    overflow: hidden;
    background: white;
}

button[data-baseweb="tab"] {
    font-weight: 700;
}

.f-footer {
    margin-top: 38px;
    padding-top: 18px;
    border-top: 1px solid #E5EAF1;
    text-align: center;
    color: #8A97A8;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)


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
        "slogan": "Conforto em todas as estações",
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
        'Tubo de cobre 1/4"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        'Tubo de cobre 3/8"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        'Tubo de cobre 1/2"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        'Tubo de cobre 5/8"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        'Tubo de cobre 3/4"': {"unidade": "metro", "preco": 0.0, "ativo": True},
        "Canaleta": {"unidade": "metro", "preco": 0.0, "ativo": True},
        "Cabo elétrico": {"unidade": "metro", "preco": 0.0, "ativo": True},
        "Mangueira de dreno": {"unidade": "metro", "preco": 0.0, "ativo": True},
        "Suporte para condensadora": {"unidade": "unidade", "preco": 0.0, "ativo": True}
    },

    "equipamentos": {
        "Split 9.000 BTUs": {"preco": 0.0, "ativo": False},
        "Split 12.000 BTUs": {"preco": 0.0, "ativo": False},
        "Split 18.000 BTUs": {"preco": 0.0, "ativo": False},
        "Split 24.000 BTUs": {"preco": 0.0, "ativo": False}
    }
}


# =========================================================
# CARREGAMENTO
# =========================================================

def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

            if "slogan" not in dados.get("empresa", {}):
                dados["empresa"]["slogan"] = "Conforto em todas as estações"

            return dados

    except Exception:
        return DEFAULT_CONFIG.copy()


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

    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def salvar_config_github(nova_config):

    if not GITHUB_TOKEN:
        raise Exception("GITHUB_TOKEN não encontrado nos Secrets.")

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
        c for c in config["empresa"].get("whatsapp", "")
        if c.isdigit()
    )

    return f"https://wa.me/{numero}?text={quote(texto)}"


def cabecalho(area="cliente"):

    col_logo, col_texto = st.columns(
        [1, 2.8],
        vertical_alignment="center"
    )

    with col_logo:

        if os.path.exists("logo.PNG"):
            st.image(
                "logo.PNG",
                use_container_width=True
            )
        else:
            st.markdown(
                "<div style='font-size:55px;text-align:center'>❄️</div>",
                unsafe_allow_html=True
            )

    with col_texto:

        if area == "admin":
            titulo = "PAINEL ADMINISTRATIVO"
            subtitulo = "Gestão • F Climatização"
        else:
            titulo = "F CLIMATIZAÇÃO"
            subtitulo = config["empresa"].get(
                "slogan",
                "Conforto em todas as estações"
            )

        st.markdown(
            f"""
            <div style="
                background:linear-gradient(135deg,#031D46,#0759B5);
                padding:18px;
                border-radius:18px;
                box-shadow:0 8px 22px rgba(3,29,70,.15);
            ">
                <div style="
                    color:white;
                    font-weight:900;
                    font-size:21px;
                    line-height:1.15;
                ">
                    {titulo}
                </div>

                <div style="
                    color:#FF8A00;
                    font-weight:700;
                    margin-top:5px;
                    font-size:13px;
                ">
                    {subtitulo}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def titulo_secao(titulo, subtitulo=""):
    st.markdown(
        f"""
        <div class="section-title">{titulo}</div>
        <div class="section-subtitle">{subtitulo}</div>
        """,
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
            "Digite sua senha para continuar."
        )

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Senha do administrador"
        )

        if st.button(
            "Entrar no painel",
            type="primary",
            use_container_width=True
        ):
            if senha == ADMIN_KEY:
                st.session_state["admin_logado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")

        return

    st.success("Administrador conectado")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Serviços",
        "Adicionais",
        "Materiais",
        "Aparelhos",
        "Empresa"
    ])

    with tab1:

        titulo_secao(
            "Serviços",
            "Defina disponibilidade e valores."
        )

        for nome, dados in config["servicos"].items():

            with st.expander(nome):

                dados["ativo"] = st.checkbox(
                    "Serviço ativo",
                    value=dados.get(
                        "ativo",
                        True
                    ),
                    key=f"serv_ativo_{nome}"
                )

                dados["mostrar_cliente"] = st.checkbox(
                    "Mostrar para o cliente",
                    value=dados.get(
                        "mostrar_cliente",
                        True
                    ),
                    key=f"serv_mostrar_{nome}"
                )

                dados["descricao"] = st.text_area(
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

                    dados["precos"][capacidade] = (
                        st.number_input(
                            capacidade,
                            min_value=0.0,
                            value=float(
                                dados["precos"].get(
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
                    )

    with tab2:

        titulo_secao(
            "Situações adicionais",
            "Configure situações que podem alterar o orçamento."
        )

        for nome, dados in config["adicionais"].items():

            with st.expander(nome):

                dados["mostrar_cliente"] = st.checkbox(
                    "Mostrar para o cliente",
                    value=dados.get(
                        "mostrar_cliente",
                        True
                    ),
                    key=f"adic_mostrar_{nome}"
                )

                dados["descricao"] = st.text_area(
                    "Descrição",
                    value=dados.get(
                        "descricao",
                        ""
                    ),
                    key=f"adic_desc_{nome}"
                )

                dados["preco"] = st.number_input(
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

    with tab3:

        titulo_secao(
            "Materiais",
            "Controle técnico e preços de venda."
        )

        st.info(
            "Os materiais técnicos ficam no ADM. "
            "O cliente não precisa escolher bitolas "
            "ou componentes."
        )

        unidades = [
            "metro",
            "unidade",
            "serviço"
        ]

        for nome, dados in config["materiais"].items():

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

                dados["unidade"] = st.selectbox(
                    "Unidade de cobrança",
                    unidades,
                    index=unidades.index(
                        unidade_atual
                    ),
                    key=f"mat_unidade_{nome}"
                )

                dados["preco"] = st.number_input(
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

    with tab4:

        titulo_secao(
            "Aparelhos",
            "Equipamentos disponíveis para venda."
        )

        for nome, dados in config["equipamentos"].items():

            with st.expander(nome):

                dados["ativo"] = st.checkbox(
                    "Disponível para venda",
                    value=dados.get(
                        "ativo",
                        False
                    ),
                    key=f"equip_ativo_{nome}"
                )

                dados["preco"] = st.number_input(
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

    with tab5:

        titulo_secao(
            "Empresa",
            "Informações utilizadas no orçamento."
        )

        config["empresa"]["nome"] = st.text_input(
            "Nome da empresa",
            value=config["empresa"].get(
                "nome",
                "F Climatização"
            ),
            key="empresa_nome"
        )

        config["empresa"]["slogan"] = st.text_input(
            "Slogan",
            value=config["empresa"].get(
                "slogan",
                "Conforto em todas as estações"
            ),
            key="empresa_slogan"
        )

        config["empresa"]["whatsapp"] = st.text_input(
            "WhatsApp",
            value=config["empresa"].get(
                "whatsapp",
                ""
            ),
            help="Código do país + DDD + número.",
            key="empresa_whatsapp"
        )

    st.divider()

    if st.button(
        "💾 Salvar alterações",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Salvando alterações..."
            ):
                salvar_config_github(config)

            st.success(
                "✅ Alterações salvas permanentemente."
            )

        except Exception as erro:

            st.error(
                f"Não foi possível salvar: {erro}"
            )

    if st.button(
        "🔒 Sair do administrador",
        use_container_width=True
    ):
        st.session_state["admin_logado"] = False
        st.session_state["pagina"] = "cliente"
        st.rerun()


# =========================================================
# CLIENTE
# =========================================================

def pagina_cliente():

    cabecalho("cliente")

    st.markdown(
        """
        <div class="info-card">
            <strong>Orçamento rápido e prático</strong><br>
            <span style="color:#64748B;font-size:13px;">
            Informe os dados abaixo para receber uma estimativa inicial.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

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
        placeholder="Selecione um ou mais serviços"
    )

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

    titulo_secao(
        "📋 Sobre o local",
        "Marque somente o que se aplicar."
    )

    situacoes = []

    for nome, dados in config["adicionais"].items():

        if dados.get(
            "mostrar_cliente",
            True
        ):

            if st.checkbox(
                nome,
                key=f"cliente_{nome}"
            ):
                situacoes.append(nome)

    observacoes = st.text_area(
        "Alguma observação?",
        placeholder=(
            "Ex.: acesso, local da instalação "
            "ou alguma necessidade específica."
        )
    )

    aparelho_escolhido = None

    if possui == "Não, quero comprar":

        titulo_secao(
            "🧊 Aparelhos disponíveis",
            "Confira os equipamentos disponíveis."
        )

        equipamentos_ativos = [
            nome
            for nome, dados
            in config["equipamentos"].items()
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
                "Consulte a F Climatização sobre "
                "os aparelhos disponíveis."
            )

    titulo_secao(
        "👤 Seus dados",
        "Usaremos essas informações somente para o atendimento."
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

    total = 0.0
    tem_valor = False

    if capacidade != "Não sei":

        for servico in servicos:

            valor = float(
                config["servicos"][
                    servico
                ]["precos"].get(
                    capacidade,
                    0
                )
            )

            if valor > 0:
                total += valor
                tem_valor = True

    for adicional in situacoes:

        valor = float(
            config["adicionais"][
                adicional
            ].get(
                "preco",
                0
            )
        )

        if valor > 0:
            total += valor
            tem_valor = True

    if aparelho_escolhido:

        preco_aparelho = float(
            config["equipamentos"][
                aparelho_escolhido
            ].get(
                "preco",
                0
            )
        )

        if preco_aparelho > 0:
            total += preco_aparelho
            tem_valor = True

    st.write("")

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
                "Resumo das informações selecionadas."
            )

            for servico in servicos:
                st.write(
                    f"✓ {servico}"
                )

            if aparelho_escolhido:
                st.write(
                    f"✓ {aparelho_escolhido}"
                )

            if tem_valor:

                st.metric(
                    "Estimativa inicial",
                    dinheiro(total)
                )

            else:

                st.info(
                    "O valor será confirmado após avaliarmos "
                    "as informações do serviço."
                )

            st.markdown(
                """
                <div class="warning-card">
                    <strong>Importante</strong><br>
                    Esta é uma estimativa inicial. Caso sejam necessários
                    materiais adicionais, tubulação extra, adequações,
                    reparos ou condições especiais de instalação,
                    informaremos o valor antes da execução.
                    <strong>Nada será acrescentado sem sua aprovação.</strong>
                </div>
                """,
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
                    "Situações: "
                    + ", ".join(situacoes)
                    + "\n"
                )

            if aparelho_escolhido:
                mensagem += (
                    f"Aparelho escolhido: "
                    f"{aparelho_escolhido}\n"
                )

            if observacoes:
                mensagem += (
                    f"Observações: "
                    f"{observacoes}\n"
                )

            if tem_valor:
                mensagem += (
                    f"\nEstimativa inicial: "
                    f"{dinheiro(total)}"
                )

            st.link_button(
                "📲 SOLICITAR PELO WHATSAPP",
                link_whatsapp(mensagem),
                use_container_width=True
            )

            st.markdown(
                """
                <div class="info-card">
                    <strong>📷 Agilize seu atendimento</strong><br>
                    <span style="color:#64748B;font-size:13px;">
                    Envie pelo WhatsApp fotos do local onde ficarão
                    as unidades interna e externa. Se já possui o
                    aparelho, envie também uma foto da etiqueta/modelo.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    titulo_secao(
        "ℹ️ Observações importantes"
    )

    st.caption(
        "Se o serviço, material ou condição necessária não estiver "
        "listada, fale conosco pelo WhatsApp. Qualquer adicional será "
        "informado antes e dependerá da aprovação do cliente."
    )

    st.markdown(
        """
        <div class="f-footer">
            <strong>F CLIMATIZAÇÃO</strong><br>
            Conforto em todas as estações
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    with st.expander(
        "🔐 Área administrativa"
    ):

        st.caption(
            "Acesso exclusivo para administração."
        )

        if st.button(
            "Acessar painel administrativo",
            use_container_width=True
        ):
            st.session_state["pagina"] = "admin"
            st.rerun()


# =========================================================
# NAVEGAÇÃO
# =========================================================

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "cliente"

if st.query_params.get(
    "modo",
    ""
) == "admin":
    st.session_state["pagina"] = "admin"

if st.session_state["pagina"] == "admin":
    pagina_admin()
else:
    pagina_cliente()
