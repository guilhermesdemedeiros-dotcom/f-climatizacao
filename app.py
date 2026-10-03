import streamlit as st
from urllib.parse import quote
from datetime import datetime

# =========================================================
# F CLIMATIZAÇÃO - V2
# =========================================================

st.set_page_config(
    page_title="F Climatização",
    page_icon="❄️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CONFIGURAÇÕES DA EMPRESA
# =========================================================

EMPRESA = {
    "nome": "F Climatização",
    "slogan": "Seu ambiente na temperatura ideal",
    "whatsapp": "5555999999999",  # ALTERAR DEPOIS
    "cidade_base": "",
}

# Chave provisória do administrador.
# Depois trocamos pela chave que você quiser.
CHAVE_ADMIN = "fclima2026"


# =========================================================
# BASE INICIAL
# Valores abaixo são SOMENTE PARA TESTE.
# =========================================================

SERVICOS = {
    "Instalação": {
        "icone": "🛠️",
        "descricao": "Instalação de ar-condicionado Split",
        "ativo": True,
        "opcoes": {
            "9.000 BTUs": 500.00,
            "12.000 BTUs": 550.00,
            "18.000 BTUs": 650.00,
            "24.000 BTUs": 750.00,
            "30.000 BTUs": 850.00,
            "36.000 BTUs": 950.00,
        },
    },

    "Limpeza / Higienização": {
        "icone": "🧼",
        "descricao": "Limpeza e higienização completa",
        "ativo": True,
        "opcoes": {
            "9.000 BTUs": 180.00,
            "12.000 BTUs": 180.00,
            "18.000 BTUs": 220.00,
            "24.000 BTUs": 250.00,
            "30.000 BTUs": 280.00,
            "36.000 BTUs": 300.00,
        },
    },

    "Manutenção": {
        "icone": "🔧",
        "descricao": "Avaliação e manutenção do equipamento",
        "ativo": True,
        "opcoes": {
            "Até 12.000 BTUs": 150.00,
            "18.000 a 24.000 BTUs": 180.00,
            "30.000 BTUs ou mais": 220.00,
        },
    },

    "Desinstalação": {
        "icone": "♻️",
        "descricao": "Retirada do equipamento instalado",
        "ativo": True,
        "opcoes": {
            "Até 12.000 BTUs": 250.00,
            "18.000 a 24.000 BTUs": 300.00,
            "30.000 BTUs ou mais": 350.00,
        },
    },

    "Reinstalação": {
        "icone": "🔄",
        "descricao": "Retirada e instalação em outro local",
        "ativo": True,
        "opcoes": {
            "Até 12.000 BTUs": 700.00,
            "18.000 a 24.000 BTUs": 850.00,
            "30.000 BTUs ou mais": 1000.00,
        },
    },
}


MATERIAIS = {
    "Tubo de cobre adicional": {
        "unidade": "metro",
        "preco": 100.00,
        "ativo": True,
    },
    "Suporte condensadora": {
        "unidade": "unidade",
        "preco": 120.00,
        "ativo": True,
    },
    "Canaleta": {
        "unidade": "metro",
        "preco": 35.00,
        "ativo": True,
    },
    "Cabo elétrico": {
        "unidade": "metro",
        "preco": 12.00,
        "ativo": True,
    },
    "Mangueira de dreno": {
        "unidade": "metro",
        "preco": 10.00,
        "ativo": True,
    },
}


EQUIPAMENTOS = {
    "Split 9.000 BTUs": {
        "preco": 0.00,
        "ativo": False,
    },
    "Split 12.000 BTUs": {
        "preco": 0.00,
        "ativo": False,
    },
    "Split 18.000 BTUs": {
        "preco": 0.00,
        "ativo": False,
    },
    "Split 24.000 BTUs": {
        "preco": 0.00,
        "ativo": False,
    },
}


# =========================================================
# FUNÇÕES
# =========================================================

def moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def gerar_numero_orcamento():
    return datetime.now().strftime("%d%m%y%H%M")


def reset_orcamento():
    chaves = [
        "servico_escolhido",
        "orcamento_finalizado",
        "numero_orcamento",
    ]

    for chave in chaves:
        if chave in st.session_state:
            del st.session_state[chave]


# =========================================================
# CSS / VISUAL MOBILE
# =========================================================

st.markdown("""
<style>

header {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.block-container {
    max-width: 650px;
    padding-top: 1.1rem;
    padding-bottom: 5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

.f-logo {
    text-align: center;
    font-size: 2rem;
    font-weight: 850;
    margin-top: 0.2rem;
}

.f-slogan {
    text-align: center;
    opacity: 0.65;
    margin-top: -5px;
    margin-bottom: 25px;
    font-size: 0.95rem;
}

.f-titulo {
    font-size: 1.75rem;
    font-weight: 800;
    margin-top: 12px;
    margin-bottom: 5px;
}

.f-texto {
    opacity: 0.75;
    font-size: 1rem;
    margin-bottom: 20px;
}

.card {
    border: 1px solid rgba(128,128,128,.25);
    padding: 18px;
    border-radius: 16px;
    margin-top: 10px;
    margin-bottom: 10px;
}

.orcamento {
    border: 1px solid rgba(128,128,128,.30);
    padding: 20px;
    border-radius: 18px;
    margin-top: 15px;
}

.total-label {
    text-align: center;
    opacity: .65;
    margin-top: 20px;
}

.total {
    text-align: center;
    font-size: 2rem;
    font-weight: 850;
    margin-bottom: 15px;
}

.aviso {
    font-size: .82rem;
    opacity: .65;
    text-align: center;
    line-height: 1.4;
}

.admin-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    border: 1px solid rgba(128,128,128,.3);
    font-size: .8rem;
    margin-bottom: 15px;
}

div.stButton > button {
    min-height: 3.2rem;
    border-radius: 14px;
    font-weight: 700;
}

div.stLinkButton > a {
    min-height: 3.2rem;
    border-radius: 14px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# NAVEGAÇÃO
# =========================================================

query = st.query_params

modo = query.get("modo", "cliente")

if isinstance(modo, list):
    modo = modo[0]


# =========================================================
# ADMINISTRADOR
# =========================================================

if modo == "admin":

    st.markdown(
        '<div class="f-logo">❄️ F Climatização</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="f-slogan">Painel administrativo</div>',
        unsafe_allow_html=True
    )

    if "admin_logado" not in st.session_state:
        st.session_state.admin_logado = False

    if not st.session_state.admin_logado:

        st.markdown(
            '<div class="f-titulo">🔐 Acesso administrativo</div>',
            unsafe_allow_html=True
        )

        st.write(
            "Digite a chave de acesso para abrir o painel."
        )

        chave = st.text_input(
            "Chave de acesso",
            type="password",
            placeholder="Digite sua chave"
        )

        if st.button(
            "Entrar no painel",
            use_container_width=True,
            type="primary"
        ):
            if chave == CHAVE_ADMIN:
                st.session_state.admin_logado = True
                st.rerun()
            else:
                st.error("Chave de acesso incorreta.")

        st.stop()


    # -----------------------------------------------------
    # ADM LOGADO
    # -----------------------------------------------------

    st.markdown(
        '<span class="admin-badge">ADMINISTRADOR</span>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="f-titulo">Painel de controle</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Nesta fase, alterações permanentes ainda são "
        "feitas pelo app.py."
    )

    aba1, aba2, aba3, aba4 = st.tabs([
        "Serviços",
        "Materiais",
        "Equipamentos",
        "Empresa"
    ])


    # -----------------------------------------------------
    # SERVIÇOS
    # -----------------------------------------------------

    with aba1:

        st.subheader("🛠️ Serviços")

        for nome_servico, dados in SERVICOS.items():

            with st.expander(
                f"{dados['icone']} {nome_servico}",
                expanded=False
            ):

                st.write(dados["descricao"])

                st.checkbox(
                    "Ativo para clientes",
                    value=dados["ativo"],
                    key=f"servico_{nome_servico}"
                )

                for nome_opcao, preco in dados["opcoes"].items():

                    st.number_input(
                        nome_opcao,
                        min_value=0.0,
                        value=float(preco),
                        step=10.0,
                        format="%.2f",
                        key=f"{nome_servico}_{nome_opcao}"
                    )

        st.info(
            "Por enquanto estes campos servem para organizar "
            "e testar a estrutura. Depois decidiremos como "
            "salvar alterações permanentemente."
        )


    # -----------------------------------------------------
    # MATERIAIS
    # -----------------------------------------------------

    with aba2:

        st.subheader("📦 Materiais")

        for nome_material, dados in MATERIAIS.items():

            with st.expander(nome_material):

                st.write(
                    f"Unidade de cobrança: **{dados['unidade']}**"
                )

                st.number_input(
                    "Preço",
                    min_value=0.0,
                    value=float(dados["preco"]),
                    step=5.0,
                    format="%.2f",
                    key=f"material_{nome_material}"
                )

                st.checkbox(
                    "Ativo",
                    value=dados["ativo"],
                    key=f"material_ativo_{nome_material}"
                )


    # -----------------------------------------------------
    # EQUIPAMENTOS
    # -----------------------------------------------------

    with aba3:

        st.subheader("❄️ Equipamentos")

        st.write(
            "Aqui ficará o catálogo de aparelhos que "
            "a F Climatização desejar oferecer."
        )

        for equipamento, dados in EQUIPAMENTOS.items():

            with st.expander(equipamento):

                st.number_input(
                    "Preço de venda",
                    min_value=0.0,
                    value=float(dados["preco"]),
                    step=50.0,
                    format="%.2f",
                    key=f"equipamento_{equipamento}"
                )

                st.checkbox(
                    "Disponível para venda",
                    value=dados["ativo"],
                    key=f"equipamento_ativo_{equipamento}"
                )


    # -----------------------------------------------------
    # EMPRESA
    # -----------------------------------------------------

    with aba4:

        st.subheader("🏢 Empresa")

        st.text_input(
            "Nome da empresa",
            value=EMPRESA["nome"]
        )

        st.text_input(
            "Slogan",
            value=EMPRESA["slogan"]
        )

        st.text_input(
            "WhatsApp da empresa",
            value=EMPRESA["whatsapp"]
        )

        st.warning(
            "Esses dados ainda não são salvos permanentemente "
            "ao fechar/reiniciar o aplicativo."
        )


    st.divider()

    if st.button(
        "Sair do administrador",
        use_container_width=True
    ):
        st.session_state.admin_logado = False
        st.rerun()

    st.stop()


# =========================================================
# ÁREA DO CLIENTE
# =========================================================

st.markdown(
    '<div class="f-logo">❄️ F Climatização</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="f-slogan">{EMPRESA["slogan"]}</div>',
    unsafe_allow_html=True
)


# =========================================================
# ETAPA 1 - ESCOLHA
# =========================================================

if "servico_escolhido" not in st.session_state:

    st.markdown(
        '<div class="f-titulo">Como podemos ajudar?</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="f-texto">'
        'Escolha abaixo o que você precisa.'
        '</div>',
        unsafe_allow_html=True
    )

    for nome_servico, dados in SERVICOS.items():

        if dados["ativo"]:

            if st.button(
                f"{dados['icone']}  {nome_servico}",
                key=f"btn_{nome_servico}",
                use_container_width=True
            ):
                st.session_state.servico_escolhido = nome_servico
                st.rerun()


    st.divider()

    st.markdown("#### 🛒 Precisa comprar um ar-condicionado?")

    st.write(
        "Em breve você também poderá consultar equipamentos "
        "disponíveis diretamente por aqui."
    )

    st.button(
        "❄️ Ver aparelhos",
        disabled=True,
        use_container_width=True
    )

    st.divider()

    with st.expander("🔐 Acesso administrativo"):
        st.write(
            "Área exclusiva da F Climatização."
        )

        st.markdown(
            "[Abrir painel administrativo](?modo=admin)"
        )

    st.stop()


# =========================================================
# ETAPA 2 - DADOS DO SERVIÇO
# =========================================================

servico = st.session_state.servico_escolhido
dados_servico = SERVICOS[servico]

if st.button("← Voltar"):
    reset_orcamento()
    st.rerun()


st.markdown(
    f'<div class="f-titulo">'
    f'{dados_servico["icone"]} {servico}'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="f-texto">'
    f'{dados_servico["descricao"]}'
    f'</div>',
    unsafe_allow_html=True
)


opcao = st.selectbox(
    "Capacidade do aparelho",
    list(dados_servico["opcoes"].keys())
)

quantidade = st.number_input(
    "Quantidade de aparelhos",
    min_value=1,
    max_value=20,
    value=1,
    step=1
)


st.markdown("### 📍 Local do atendimento")

cidade = st.text_input(
    "Cidade",
    placeholder="Digite sua cidade"
)

bairro = st.text_input(
    "Bairro",
    placeholder="Digite seu bairro"
)


st.markdown("### 👤 Seus dados")

nome = st.text_input(
    "Nome",
    placeholder="Digite seu nome"
)

telefone = st.text_input(
    "WhatsApp",
    placeholder="(00) 00000-0000"
)

observacoes = st.text_area(
    "Quer nos contar mais alguma coisa?",
    placeholder=(
        "Ex.: aparelho já está instalado, "
        "local de difícil acesso, segundo andar..."
    )
)


# =========================================================
# VALORES
# =========================================================

valor_unitario = dados_servico["opcoes"][opcao]
total = valor_unitario * quantidade


# =========================================================
# FINALIZAÇÃO
# =========================================================

if st.button(
    "Calcular meu orçamento",
    use_container_width=True,
    type="primary"
):

    if not nome.strip():
        st.error("Informe seu nome.")

    elif not telefone.strip():
        st.error("Informe seu WhatsApp.")

    elif not cidade.strip():
        st.error("Informe sua cidade.")

    else:
        st.session_state.orcamento_finalizado = True

        if "numero_orcamento" not in st.session_state:
            st.session_state.numero_orcamento = (
                gerar_numero_orcamento()
            )


# =========================================================
# ORÇAMENTO
# =========================================================

if st.session_state.get("orcamento_finalizado"):

    numero = st.session_state.numero_orcamento

    st.divider()

    st.markdown(
        '<div class="f-titulo">Seu orçamento</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"Orçamento #{numero}"
    )

    st.markdown(
        f"""
        <div class="orcamento">

        <b>F Climatização</b><br>
        {EMPRESA["slogan"]}

        <hr>

        <b>Cliente</b><br>
        {nome}<br>
        {telefone}

        <br><br>

        <b>Local</b><br>
        {bairro + " - " if bairro else ""}{cidade}

        <br><br>

        <b>Serviço</b><br>
        {servico}

        <br><br>

        <b>Capacidade</b><br>
        {opcao}

        <br><br>

        <b>Quantidade</b><br>
        {quantidade}

        <br><br>

        <b>Valor unitário</b><br>
        {moeda(valor_unitario)}

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="total-label">VALOR ESTIMADO</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="total">{moeda(total)}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="aviso">
        Este orçamento é uma estimativa inicial.
        O valor final poderá sofrer alterações conforme
        materiais necessários e condições encontradas no local.
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # WHATSAPP
    # =====================================================

    mensagem = f"""
Olá! Meu nome é {nome}.

Fiz o orçamento #{numero} pelo site da F Climatização e quero prosseguir com o atendimento.

Serviço: {servico}
Capacidade: {opcao}
Quantidade: {quantidade}
Cidade: {cidade}
Bairro: {bairro if bairro else "Não informado"}
Valor estimado: {moeda(total)}

Observações:
{observacoes if observacoes else "Nenhuma observação."}
"""

    link_whatsapp = (
        f"https://wa.me/{EMPRESA['whatsapp']}"
        f"?text={quote(mensagem)}"
    )

    st.link_button(
        "📲 Quero prosseguir pelo WhatsApp",
        link_whatsapp,
        use_container_width=True
    )

    if st.button(
        "Fazer outro orçamento",
        use_container_width=True
    ):
        reset_orcamento()
        st.rerun()


st.divider()

st.caption(
    "F Climatização • Instalação e manutenção de ar-condicionado"
)