import streamlit as st
from urllib.parse import quote
from datetime import datetime

# =========================================================
# F CLIMATIZAÇÃO - V3
# =========================================================

st.set_page_config(
    page_title="F Climatização",
    page_icon="❄️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CONFIGURAÇÕES
# =========================================================

EMPRESA = {
    "nome": "F Climatização",
    "slogan": "Seu ambiente na temperatura ideal",
    "whatsapp": "5555999999999",  # ALTERAR DEPOIS
}

CHAVE_ADMIN = "fclima2026"

CAPACIDADES = [
    "9.000 BTUs",
    "12.000 BTUs",
    "18.000 BTUs",
    "24.000 BTUs",
]

# =========================================================
# SERVIÇOS
# =========================================================

SERVICOS = {
    "Instalação": {
        "icone": "🛠️",
        "ativo": True,
        "mostrar_cliente": True,
        "descricao": "Instalação padrão de ar-condicionado Split.",
        "precos": {
            "9.000 BTUs": 500.00,
            "12.000 BTUs": 550.00,
            "18.000 BTUs": 650.00,
            "24.000 BTUs": 750.00,
        },
    },

    "Higienização": {
        "icone": "✨",
        "ativo": True,
        "mostrar_cliente": True,
        "descricao": "Limpeza e higienização do equipamento.",
        "precos": {
            "9.000 BTUs": 180.00,
            "12.000 BTUs": 180.00,
            "18.000 BTUs": 220.00,
            "24.000 BTUs": 250.00,
        },
    },

    "Manutenção": {
        "icone": "🔧",
        "ativo": True,
        "mostrar_cliente": True,
        "descricao": "Avaliação de problema ou funcionamento do aparelho.",
        "precos": {
            "9.000 BTUs": 150.00,
            "12.000 BTUs": 150.00,
            "18.000 BTUs": 180.00,
            "24.000 BTUs": 180.00,
        },
    },

    "Desinstalação": {
        "icone": "♻️",
        "ativo": True,
        "mostrar_cliente": True,
        "descricao": "Retirada do aparelho instalado.",
        "precos": {
            "9.000 BTUs": 250.00,
            "12.000 BTUs": 250.00,
            "18.000 BTUs": 300.00,
            "24.000 BTUs": 300.00,
        },
    },

    "Reinstalação": {
        "icone": "🔄",
        "ativo": True,
        "mostrar_cliente": True,
        "descricao": "Retirada e instalação do aparelho em outro local.",
        "precos": {
            "9.000 BTUs": 700.00,
            "12.000 BTUs": 750.00,
            "18.000 BTUs": 850.00,
            "24.000 BTUs": 900.00,
        },
    },
}

# =========================================================
# SITUAÇÕES / ADICIONAIS
# O cliente só informa.
# Não somamos automaticamente nesta versão.
# =========================================================

ADICIONAIS = {
    "Apartamento": {
        "mostrar_cliente": True,
        "descricao": "O serviço será realizado em apartamento.",
        "preco": 0.00,
    },

    "Instalação em altura": {
        "mostrar_cliente": True,
        "descricao": "Aparelho ou condensadora em local elevado.",
        "preco": 0.00,
    },

    "Acesso difícil": {
        "mostrar_cliente": True,
        "descricao": "O local pode apresentar dificuldade de acesso.",
        "preco": 0.00,
    },

    "Retirada de aparelho antigo": {
        "mostrar_cliente": True,
        "descricao": "Existe outro aparelho que precisa ser retirado.",
        "preco": 0.00,
    },

    "Pode precisar de material adicional": {
        "mostrar_cliente": True,
        "descricao": "Pode ser necessário material além da instalação padrão.",
        "preco": 0.00,
    },

    "Adequação ou reparo": {
        "mostrar_cliente": True,
        "descricao": "Existe alguma instalação antiga ou ponto que pode precisar de ajuste.",
        "preco": 0.00,
    },
}

# =========================================================
# MATERIAIS - CONTROLE INTERNO
# =========================================================

MATERIAIS = {
    'Tubo de cobre 1/4"': {
        "unidade": "metro",
        "preco": 0.00,
        "ativo": True,
    },

    'Tubo de cobre 3/8"': {
        "unidade": "metro",
        "preco": 0.00,
        "ativo": True,
    },

    'Tubo de cobre 1/2"': {
        "unidade": "metro",
        "preco": 0.00,
        "ativo": True,
    },

    'Tubo de cobre 5/8"': {
        "unidade": "metro",
        "preco": 0.00,
        "ativo": True,
    },

    'Tubo de cobre 3/4"': {
        "unidade": "metro",
        "preco": 0.00,
        "ativo": True,
    },

    "Canaleta": {
        "unidade": "metro",
        "preco": 0.00,
        "ativo": True,
    },

    "Cabo elétrico": {
        "unidade": "metro",
        "preco": 0.00,
        "ativo": True,
    },

    "Mangueira de dreno": {
        "unidade": "metro",
        "preco": 0.00,
        "ativo": True,
    },

    "Suporte para condensadora": {
        "unidade": "unidade",
        "preco": 0.00,
        "ativo": True,
    },
}

# =========================================================
# EQUIPAMENTOS
# =========================================================

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


def numero_orcamento():
    return datetime.now().strftime("%d%m%y%H%M")


def limpar_orcamento():
    manter = {"admin_logado"}

    for chave in list(st.session_state.keys()):
        if chave not in manter:
            del st.session_state[chave]


# =========================================================
# VISUAL
# =========================================================

st.markdown(
    """
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
    max-width: 680px;
    padding-top: 1rem;
    padding-bottom: 5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

.logo {
    text-align: center;
    font-size: 1.9rem;
    font-weight: 850;
    margin-top: 5px;
}

.slogan {
    text-align: center;
    opacity: .65;
    font-size: .92rem;
    margin-bottom: 25px;
}

.titulo {
    font-size: 1.55rem;
    font-weight: 800;
    margin-bottom: 6px;
}

.texto {
    opacity: .72;
    margin-bottom: 18px;
    line-height: 1.45;
}

.card {
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 16px;
    padding: 18px;
    margin-top: 12px;
    margin-bottom: 12px;
}

.resumo {
    border: 1px solid rgba(128,128,128,.28);
    border-radius: 17px;
    padding: 18px;
    margin-top: 15px;
}

.total-label {
    text-align: center;
    opacity: .60;
    font-size: .85rem;
    margin-top: 20px;
}

.total {
    text-align: center;
    font-size: 2rem;
    font-weight: 850;
    margin-bottom: 15px;
}

.aviso {
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 15px;
    padding: 15px;
    margin-top: 15px;
    font-size: .9rem;
    line-height: 1.5;
}

.admin-tag {
    display: inline-block;
    border: 1px solid rgba(128,128,128,.3);
    border-radius: 20px;
    padding: 5px 10px;
    font-size: .75rem;
    margin-bottom: 10px;
}

div.stButton > button {
    min-height: 3.1rem;
    border-radius: 13px;
    font-weight: 700;
}

div.stLinkButton > a {
    min-height: 3.1rem;
    border-radius: 13px;
    font-weight: 700;
}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# CABEÇALHO
# =========================================================

st.markdown(
    '<div class="logo">❄️ F Climatização</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="slogan">{EMPRESA["slogan"]}</div>',
    unsafe_allow_html=True,
)

# =========================================================
# VERIFICA MODO
# =========================================================

query = st.query_params
modo = query.get("modo", "cliente")

if isinstance(modo, list):
    modo = modo[0]

# =========================================================
# ADMIN
# =========================================================

if modo == "admin":

    if "admin_logado" not in st.session_state:
        st.session_state.admin_logado = False

    if not st.session_state.admin_logado:

        st.markdown(
            '<div class="titulo">🔐 Administrador</div>',
            unsafe_allow_html=True,
        )

        st.write("Digite sua chave de acesso.")

        chave = st.text_input(
            "Chave",
            type="password",
        )

        if st.button(
            "Entrar",
            type="primary",
            use_container_width=True,
        ):
            if chave == CHAVE_ADMIN:
                st.session_state.admin_logado = True
                st.rerun()
            else:
                st.error("Chave incorreta.")

        st.stop()

    # =====================================================
    # ADMIN LOGADO
    # =====================================================

    st.markdown(
        '<span class="admin-tag">ADMINISTRADOR</span>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="titulo">Painel F Climatização</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Controle de serviços, adicionais, materiais e equipamentos."
    )

    st.warning(
        "Nesta versão os campos do painel servem para configurar "
        "e testar. Alterações permanentes ainda precisam ser "
        "colocadas no app.py e salvas por commit."
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Serviços",
            "Adicionais",
            "Materiais",
            "Aparelhos",
            "Empresa",
        ]
    )

    # =====================================================
    # ADMIN - SERVIÇOS
    # =====================================================

    with tab1:

        st.subheader("Serviços")

        for servico, dados in SERVICOS.items():

            with st.expander(
                f"{dados['icone']} {servico}"
            ):

                st.checkbox(
                    "Serviço ativo",
                    value=dados["ativo"],
                    key=f"adm_ativo_{servico}",
                )

                st.checkbox(
                    "Mostrar para o cliente",
                    value=dados["mostrar_cliente"],
                    key=f"adm_cliente_{servico}",
                )

                st.text_input(
                    "Descrição",
                    value=dados["descricao"],
                    key=f"adm_desc_{servico}",
                )

                st.markdown("**Preços**")

                for capacidade, preco in dados["precos"].items():

                    st.number_input(
                        capacidade,
                        min_value=0.0,
                        value=float(preco),
                        step=10.0,
                        format="%.2f",
                        key=f"adm_preco_{servico}_{capacidade}",
                    )

    # =====================================================
    # ADMIN - ADICIONAIS
    # =====================================================

    with tab2:

        st.subheader("Adicionais e situações especiais")

        st.caption(
            "Itens que podem ser informados pelo cliente "
            "quando houver alguma condição diferente."
        )

        for adicional, dados in ADICIONAIS.items():

            with st.expander(adicional):

                st.checkbox(
                    "Mostrar para o cliente",
                    value=dados["mostrar_cliente"],
                    key=f"adm_adicional_{adicional}",
                )

                st.text_input(
                    "Descrição",
                    value=dados["descricao"],
                    key=f"adm_adicional_desc_{adicional}",
                )

                st.number_input(
                    "Preço adicional",
                    min_value=0.0,
                    value=float(dados["preco"]),
                    step=10.0,
                    format="%.2f",
                    key=f"adm_adicional_preco_{adicional}",
                )

                st.caption(
                    "Preço zero = avaliar e combinar com o cliente."
                )

    # =====================================================
    # ADMIN - MATERIAIS
    # =====================================================

    with tab3:

        st.subheader("Materiais")

        st.caption(
            "Controle interno. O cliente não precisa conhecer "
            "bitolas ou detalhes técnicos."
        )

        for material, dados in MATERIAIS.items():

            with st.expander(material):

                st.checkbox(
                    "Ativo",
                    value=dados["ativo"],
                    key=f"adm_material_ativo_{material}",
                )

                st.text_input(
                    "Unidade de cobrança",
                    value=dados["unidade"],
                    key=f"adm_material_unidade_{material}",
                )

                st.number_input(
                    "Preço de venda",
                    min_value=0.0,
                    value=float(dados["preco"]),
                    step=1.0,
                    format="%.2f",
                    key=f"adm_material_preco_{material}",
                )

                st.caption(
                    f"Cobrança atual: por {dados['unidade']}."
                )

    # =====================================================
    # ADMIN - APARELHOS
    # =====================================================

    with tab4:

        st.subheader("Aparelhos para venda")

        st.caption(
            "Ative somente os aparelhos que quiser oferecer."
        )

        for aparelho, dados in EQUIPAMENTOS.items():

            with st.expander(aparelho):

                st.checkbox(
                    "Disponível para venda",
                    value=dados["ativo"],
                    key=f"adm_aparelho_ativo_{aparelho}",
                )

                st.number_input(
                    "Preço de venda",
                    min_value=0.0,
                    value=float(dados["preco"]),
                    step=50.0,
                    format="%.2f",
                    key=f"adm_aparelho_preco_{aparelho}",
                )

    # =====================================================
    # ADMIN - EMPRESA
    # =====================================================

    with tab5:

        st.subheader("Empresa")

        st.text_input(
            "Nome",
            value=EMPRESA["nome"],
        )

        st.text_input(
            "Slogan",
            value=EMPRESA["slogan"],
        )

        st.text_input(
            "WhatsApp",
            value=EMPRESA["whatsapp"],
        )

    st.divider()

    if st.button(
        "Sair do administrador",
        use_container_width=True,
    ):
        st.session_state.admin_logado = False
        st.rerun()

    st.stop()

# =========================================================
# CLIENTE - INÍCIO
# =========================================================

st.markdown(
    '<div class="titulo">Vamos fazer seu orçamento?</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="texto">
É rápido. Você não precisa entender de instalação:
responda apenas o que souber.
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 1 - APARELHO
# =========================================================

st.markdown("### 1. Você já possui o ar-condicionado?")

possui_ar = st.radio(
    "Selecione uma opção",
    [
        "Sim, já tenho o aparelho",
        "Não, quero comprar",
        "Ainda estou avaliando",
    ],
    label_visibility="collapsed",
)

capacidade = "Não sei"

if possui_ar == "Sim, já tenho o aparelho":

    capacidade = st.selectbox(
        "Qual a capacidade do aparelho?",
        CAPACIDADES + ["Não sei"],
    )

elif possui_ar == "Não, quero comprar":

    capacidade = st.selectbox(
        "Qual capacidade você procura?",
        CAPACIDADES + ["Não sei qual preciso"],
    )

    st.info(
        "Se você não souber a capacidade ideal, sem problema. "
        "A F Climatização pode orientar você."
    )

# =========================================================
# 2 - NECESSIDADE
# =========================================================

st.markdown("### 2. O que você precisa?")

opcoes_servicos = []

for nome, dados in SERVICOS.items():
    if dados["ativo"] and dados["mostrar_cliente"]:
        opcoes_servicos.append(nome)

servicos_escolhidos = st.multiselect(
    "Você pode selecionar mais de uma opção",
    opcoes_servicos,
)

if possui_ar == "Não, quero comprar":
    quer_instalacao_compra = st.checkbox(
        "Quero orçamento do aparelho + instalação"
    )
else:
    quer_instalacao_compra = False

# =========================================================
# 3 - LOCAL
# =========================================================

st.markdown("### 3. Como é o local?")

tipo_local = st.selectbox(
    "Tipo de imóvel",
    [
        "Casa",
        "Apartamento",
        "Comércio",
        "Outro",
    ],
)

tamanho_ambiente = st.text_input(
    "Tamanho aproximado do ambiente (opcional)",
    placeholder="Ex.: 20 m² ou não sei",
)

st.caption(
    "Essa informação pode nos ajudar a verificar se a "
    "capacidade do aparelho é adequada para o ambiente."
)

# =========================================================
# 4 - SITUAÇÕES DIFERENTES
# =========================================================

st.markdown("### 4. Existe alguma situação diferente?")

st.caption(
    "Marque somente o que você souber. "
    "Se não souber, pode deixar em branco."
)

adicionais_escolhidos = []

for adicional, dados in ADICIONAIS.items():

    if not dados["mostrar_cliente"]:
        continue

    # Apartamento já foi informado acima.
    if adicional == "Apartamento":
        continue

    marcado = st.checkbox(
        adicional,
        help=dados["descricao"],
    )

    if marcado:
        adicionais_escolhidos.append(adicional)

# =========================================================
# 5 - OBSERVAÇÕES
# =========================================================

st.markdown("### 5. Quer nos contar mais alguma coisa?")

observacoes = st.text_area(
    "Observações",
    placeholder=(
        "Ex.: local alto, instalação antiga, "
        "não sei onde ficará a parte externa..."
    ),
    label_visibility="collapsed",
)

# =========================================================
# DADOS CLIENTE
# =========================================================

st.markdown("### Seus dados")

nome = st.text_input(
    "Nome",
    placeholder="Seu nome",
)

telefone = st.text_input(
    "WhatsApp",
    placeholder="(00) 00000-0000",
)

cidade = st.text_input(
    "Cidade",
    placeholder="Sua cidade",
)

bairro = st.text_input(
    "Bairro",
    placeholder="Seu bairro (opcional)",
)

# =========================================================
# CALCULAR PREÇO BASE
# =========================================================

total_base = 0.0
itens_calculados = []
itens_avaliar = []

for servico in servicos_escolhidos:

    dados = SERVICOS[servico]

    if capacidade in dados["precos"]:

        valor = dados["precos"][capacidade]
        total_base += valor

        itens_calculados.append(
            f"{servico} - {capacidade}: {moeda(valor)}"
        )

    else:

        itens_avaliar.append(
            f"{servico}: valor a confirmar"
        )

# =========================================================
# BOTÃO ORÇAMENTO
# =========================================================

st.divider()

if st.button(
    "Ver meu orçamento",
    type="primary",
    use_container_width=True,
):

    if not nome.strip():
        st.error("Informe seu nome.")

    elif not telefone.strip():
        st.error("Informe seu WhatsApp.")

    elif not cidade.strip():
        st.error("Informe sua cidade.")

    elif (
        not servicos_escolhidos
        and possui_ar != "Não, quero comprar"
    ):
        st.error("Selecione pelo menos um serviço.")

    else:

        st.session_state.mostrar_orcamento = True

        if "numero_orcamento" not in st.session_state:
            st.session_state.numero_orcamento = numero_orcamento()

# =========================================================
# RESULTADO
# =========================================================

if st.session_state.get("mostrar_orcamento"):

    numero = st.session_state.numero_orcamento

    st.markdown(
        '<div class="titulo">Seu orçamento</div>',
        unsafe_allow_html=True,
    )

    st.caption(f"Orçamento #{numero}")

    st.markdown(
        '<div class="resumo">',
        unsafe_allow_html=True,
    )

    st.markdown(f"**Cliente:** {nome}")

    st.markdown(
        f"**Aparelho:** {capacidade}"
    )

    st.markdown(
        f"**Local:** {tipo_local}"
    )

    if tamanho_ambiente:
        st.markdown(
            f"**Ambiente:** {tamanho_ambiente}"
        )

    st.markdown("**Serviços:**")

    if itens_calculados:
        for item in itens_calculados:
            st.write(f"• {item}")

    if itens_avaliar:
        for item in itens_avaliar:
            st.write(f"• {item}")

    if possui_ar == "Não, quero comprar":

        st.write("• Aparelho: preço a confirmar")

        if quer_instalacao_compra:
            st.write("• Instalação solicitada")

    if adicionais_escolhidos:

        st.markdown("**Informações adicionais:**")

        for item in adicionais_escolhidos:
            st.write(f"• {item}")

    st.markdown("</div>", unsafe_allow_html=True)

    if total_base > 0:

        st.markdown(
            '<div class="total-label">VALOR BASE ESTIMADO</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="total">{moeda(total_base)}</div>',
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "O valor será confirmado pela F Climatização "
            "após analisar as informações."
        )

    # =====================================================
    # AVISO IMPORTANTE
    # =====================================================

    st.markdown(
        """
<div class="aviso">

<b>Sobre a instalação</b><br><br>

O valor apresentado considera uma instalação em
condições normais.<br><br>

Caso o local necessite de material adicional,
tubulação extra, adequação, reparo ou algum serviço
não previsto, a F Climatização informará você antes
e combinará o valor adicional.<br><br>

<b>Nenhum adicional será realizado sem combinar antes.</b>

</div>
""",
        unsafe_allow_html=True,
    )

    st.info(
        "📸 Para confirmar o orçamento, envie pelo WhatsApp "
        "fotos do local onde ficará a parte interna e a parte "
        "externa do ar-condicionado. Se possível, envie também "
        "uma foto da etiqueta/modelo do aparelho."
    )

    # =====================================================
    # WHATSAPP
    # =====================================================

    lista_servicos = (
        ", ".join(servicos_escolhidos)
        if servicos_escolhidos
        else "A confirmar"
    )

    lista_adicionais = (
        ", ".join(adicionais_escolhidos)
        if adicionais_escolhidos
        else "Nenhuma informada"
    )

    mensagem = f"""
Olá! Meu nome é {nome}.

Fiz o orçamento #{numero} pelo site da F Climatização.

APARELHO
Situação: {possui_ar}
Capacidade: {capacidade}

SERVIÇOS
{lista_servicos}

LOCAL
Tipo: {tipo_local}
Cidade: {cidade}
Bairro: {bairro if bairro else "Não informado"}
Tamanho aproximado: {tamanho_ambiente if tamanho_ambiente else "Não informado"}

SITUAÇÕES INFORMADAS
{lista_adicionais}

OBSERVAÇÕES
{observacoes if observacoes else "Nenhuma observação."}

VALOR BASE ESTIMADO
{moeda(total_base) if total_base > 0 else "A confirmar"}

Gostaria de confirmar o orçamento e enviar as fotos do local.
"""

    link_whatsapp = (
        f"https://wa.me/{EMPRESA['whatsapp']}"
        f"?text={quote(mensagem)}"
    )

    st.link_button(
        "📲 Enviar orçamento e fotos pelo WhatsApp",
        link_whatsapp,
        use_container_width=True,
    )

    if st.button(
        "Começar outro orçamento",
        use_container_width=True,
    ):
        limpar_orcamento()
        st.rerun()

# =========================================================
# RODAPÉ / ADMIN
# =========================================================

st.divider()

with st.expander("Área da F Climatização"):
    st.markdown(
        "[🔐 Abrir administrador](?modo=admin)"
    )

st.caption(
    "F Climatização • Orçamento rápido e sem compromisso"
)