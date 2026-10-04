import streamlit as st
import json
import base64
import urllib.request
import urllib.error
from urllib.parse import quote

st.set_page_config(
    page_title="F Climatização",
    page_icon="❄️",
    layout="centered"
)

# =========================================================
# CONFIGURAÇÃO DO GITHUB
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
            "icone": "🧼",
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
            "descricao": "Tubulação, cabo, canaleta ou outros materiais adicionais.",
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
# ARQUIVO LOCAL
# =========================================================

def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except Exception:
        return DEFAULT_CONFIG.copy()


config = carregar_config()


# =========================================================
# SALVAR NO GITHUB
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
# FUNÇÕES
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
        c for c in config["empresa"]["whatsapp"]
        if c.isdigit()
    )

    return (
        f"https://wa.me/{numero}"
        f"?text={quote(texto)}"
    )


# =========================================================
# ADMIN
# =========================================================

def pagina_admin():

    st.title("⚙️ Painel Administrativo")
    st.caption("F Climatização")

    if not ADMIN_KEY:
        st.error("ADMIN_KEY não configurada nos Secrets.")
        return

    if not st.session_state.get("admin_logado"):

        senha = st.text_input(
            "Senha do administrador",
            type="password"
        )

        if st.button(
            "Entrar",
            type="primary",
            use_container_width=True
        ):
            if senha == ADMIN_KEY:
                st.session_state.admin_logado = True
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

    # -----------------------------------------------------
    # SERVIÇOS
    # -----------------------------------------------------

    with tab1:

        st.subheader("Serviços")

        for nome, dados in config["servicos"].items():

            with st.expander(nome):

                dados["ativo"] = st.checkbox(
                    "Ativo",
                    value=dados.get("ativo", True),
                    key=f"serv_ativo_{nome}"
                )

                dados["mostrar_cliente"] = st.checkbox(
                    "Mostrar ao cliente",
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

                st.markdown("**Preços**")

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

    # -----------------------------------------------------
    # ADICIONAIS
    # -----------------------------------------------------

    with tab2:

        st.subheader("Situações adicionais")

        for nome, dados in config["adicionais"].items():

            with st.expander(nome):

                dados["mostrar_cliente"] = st.checkbox(
                    "Mostrar ao cliente",
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
                        dados.get("preco", 0)
                    ),
                    step=10.0,
                    key=f"adic_preco_{nome}"
                )

    # -----------------------------------------------------
    # MATERIAIS
    # -----------------------------------------------------

    with tab3:

        st.subheader("Materiais")

        st.info(
            "Estes itens são controlados pelo ADM. "
            "O cliente não precisa escolher bitolas "
            "ou materiais técnicos."
        )

        for nome, dados in config["materiais"].items():

            with st.expander(nome):

                dados["ativo"] = st.checkbox(
                    "Ativo",
                    value=dados.get(
                        "ativo",
                        True
                    ),
                    key=f"mat_ativo_{nome}"
                )

                dados["unidade"] = st.selectbox(
                    "Cobrança",
                    [
                        "metro",
                        "unidade",
                        "serviço"
                    ],
                    index=(
                        [
                            "metro",
                            "unidade",
                            "serviço"
                        ].index(
                            dados.get(
                                "unidade",
                                "metro"
                            )
                        )
                        if dados.get(
                            "unidade",
                            "metro"
                        ) in [
                            "metro",
                            "unidade",
                            "serviço"
                        ]
                        else 0
                    ),
                    key=f"mat_unidade_{nome}"
                )

                dados["preco"] = st.number_input(
                    "Preço de venda",
                    min_value=0.0,
                    value=float(
                        dados.get("preco", 0)
                    ),
                    step=1.0,
                    key=f"mat_preco_{nome}"
                )

    # -----------------------------------------------------
    # APARELHOS
    # -----------------------------------------------------

    with tab4:

        st.subheader("Aparelhos para venda")

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
                    "Preço do aparelho",
                    min_value=0.0,
                    value=float(
                        dados.get("preco", 0)
                    ),
                    step=50.0,
                    key=f"equip_preco_{nome}"
                )

    # -----------------------------------------------------
    # EMPRESA
    # -----------------------------------------------------

    with tab5:

        st.subheader("Empresa")

        config["empresa"]["nome"] = st.text_input(
            "Nome",
            value=config["empresa"].get(
                "nome",
                "F Climatização"
            )
        )

        config["empresa"]["slogan"] = st.text_input(
            "Slogan",
            value=config["empresa"].get(
                "slogan",
                ""
            )
        )

        config["empresa"]["whatsapp"] = st.text_input(
            "WhatsApp",
            value=config["empresa"].get(
                "whatsapp",
                ""
            ),
            help=(
                "Use código do país + DDD + número. "
                "Exemplo: 5554999999999"
            )
        )

    st.divider()

    if st.button(
        "💾 Salvar alterações",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner("Salvando..."):

                salvar_config_github(config)

            st.success(
                "✅ Alterações salvas permanentemente!"
            )

            st.info(
                "O Streamlit pode reiniciar o aplicativo "
                "automaticamente para carregar a nova configuração."
            )

        except Exception as erro:

            st.error(
                f"Não foi possível salvar: {erro}"
            )

    if st.button(
        "Sair do ADM",
        use_container_width=True
    ):
        st.session_state.admin_logado = False
        st.rerun()


# =========================================================
# CLIENTE
# =========================================================

def pagina_cliente():

    empresa = config["empresa"]

    st.title(f"❄️ {empresa['nome']}")
    st.caption(empresa["slogan"])

    st.markdown(
        "### Solicite seu orçamento"
    )

    possui = st.radio(
        "Você já possui o aparelho?",
        [
            "Sim, já tenho o aparelho",
            "Não, quero comprar",
            "Ainda estou avaliando"
        ]
    )

    capacidades = [
        "9.000 BTUs",
        "12.000 BTUs",
        "18.000 BTUs",
        "24.000 BTUs",
        "Não sei"
    ]

    capacidade = st.selectbox(
        "Qual a capacidade do aparelho?",
        capacidades
    )

    servicos_disponiveis = []

    for nome, dados in config["servicos"].items():

        if (
            dados.get("ativo", True)
            and dados.get(
                "mostrar_cliente",
                True
            )
        ):
            servicos_disponiveis.append(nome)

    servicos = st.multiselect(
        "Qual serviço você precisa?",
        servicos_disponiveis
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

    st.markdown("### Sobre o local")

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
        "Observações",
        placeholder=(
            "Conte aqui qualquer detalhe "
            "que possa ajudar no orçamento."
        )
    )

    st.markdown("### Seus dados")

    nome_cliente = st.text_input(
        "Nome"
    )

    telefone = st.text_input(
        "Telefone / WhatsApp"
    )

    cidade = st.text_input(
        "Cidade"
    )

    total = 0.0
    tem_valor = False

    if capacidade != "Não sei":

        for servico in servicos:

            valor = float(
                config["servicos"][servico][
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

    aparelho_escolhido = None

    if possui == "Não, quero comprar":

        st.markdown("### Aparelhos disponíveis")

        equipamentos_ativos = [
            nome
            for nome, dados
            in config["equipamentos"].items()
            if dados.get("ativo", False)
        ]

        if equipamentos_ativos:

            aparelho_escolhido = st.selectbox(
                "Escolha o aparelho",
                equipamentos_ativos
            )

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

        else:
            st.info(
                "Consulte a F Climatização "
                "sobre aparelhos disponíveis."
            )

    st.divider()

    if st.button(
        "Calcular orçamento",
        type="primary",
        use_container_width=True
    ):

        if not servicos:
            st.warning(
                "Selecione pelo menos um serviço."
            )

        else:

            st.subheader("Resumo do orçamento")

            for servico in servicos:

                st.write(
                    f"• {servico}"
                )

            if aparelho_escolhido:
                st.write(
                    f"• {aparelho_escolhido}"
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

            st.warning(
                "A estimativa considera as condições "
                "informadas. Caso sejam necessários "
                "materiais adicionais, tubulação extra, "
                "adequações elétricas, reparos ou trabalho "
                "especial, o valor será informado antes. "
                "Nada será acrescentado sem sua aprovação."
            )

            mensagem = (
                f"Olá! Gostaria de solicitar um orçamento "
                f"com a {empresa['nome']}.\n\n"
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
                    f"Observações: {observacoes}\n"
                )

            if tem_valor:
                mensagem += (
                    f"\nEstimativa inicial: "
                    f"{dinheiro(total)}"
                )

            st.link_button(
                "📲 Enviar pelo WhatsApp",
                link_whatsapp(mensagem),
                use_container_width=True
            )

            st.info(
                "📷 Para agilizar o orçamento, envie pelo "
                "WhatsApp fotos do local da evaporadora e "
                "da condensadora e, se possível, uma foto "
                "da etiqueta/modelo do aparelho."
            )

    st.markdown("### Observações importantes")

    st.caption(
        "Serviços, materiais ou condições que não estejam "
        "listados podem ser adicionados ao orçamento após "
        "avaliação e aprovação do cliente."
    )


# =========================================================
# ROTEAMENTO
# =========================================================

modo = st.query_params.get("modo", "")

if modo == "admin":
    pagina_admin()
else:
    pagina_cliente()
