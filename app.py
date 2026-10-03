import streamlit as st
from urllib.parse import quote

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="F Climatização | Orçamento",
    page_icon="❄️",
    layout="centered"
)

# ==========================================
# DADOS INICIAIS
# Depois vamos deixar tudo editável pelo ADM
# ==========================================

SERVICOS = {
    "Instalação de ar-condicionado": {
        "icone": "🛠️",
        "descricao": "Instalação de aparelho split.",
        "precos": {
            "9.000 BTUs": 500.00,
            "12.000 BTUs": 550.00,
            "18.000 BTUs": 650.00,
            "24.000 BTUs": 750.00,
            "30.000 BTUs": 850.00,
            "36.000 BTUs": 950.00,
        }
    },

    "Limpeza / Higienização": {
        "icone": "🧼",
        "descricao": "Limpeza e higienização do equipamento.",
        "precos": {
            "9.000 BTUs": 180.00,
            "12.000 BTUs": 180.00,
            "18.000 BTUs": 220.00,
            "24.000 BTUs": 250.00,
            "30.000 BTUs": 280.00,
            "36.000 BTUs": 300.00,
        }
    },

    "Manutenção": {
        "icone": "🔧",
        "descricao": "Avaliação e manutenção do equipamento.",
        "precos": {
            "Até 12.000 BTUs": 150.00,
            "18.000 a 24.000 BTUs": 180.00,
            "30.000 BTUs ou mais": 220.00,
        }
    },

    "Desinstalação": {
        "icone": "♻️",
        "descricao": "Retirada do equipamento existente.",
        "precos": {
            "Até 12.000 BTUs": 250.00,
            "18.000 a 24.000 BTUs": 300.00,
            "30.000 BTUs ou mais": 350.00,
        }
    }
}


# ==========================================
# FUNÇÕES
# ==========================================

def moeda(valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ==========================================
# VISUAL
# ==========================================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 700px;
}

.titulo {
    text-align: center;
    font-size: 34px;
    font-weight: 800;
}

.subtitulo {
    text-align: center;
    color: #777;
    margin-bottom: 25px;
}

.caixa {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-top: 15px;
    margin-bottom: 15px;
}

.total {
    font-size: 30px;
    font-weight: 800;
    text-align: center;
}

.aviso {
    font-size: 13px;
    color: #888;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# CABEÇALHO
# ==========================================

st.markdown(
    '<div class="titulo">❄️ F Climatização</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">Seu ambiente na temperatura ideal</div>',
    unsafe_allow_html=True
)

st.title("Faça seu orçamento")

st.write(
    "Responda algumas perguntas simples para receber "
    "uma estimativa do serviço."
)

st.divider()


# ==========================================
# DADOS DO CLIENTE
# ==========================================

st.subheader("👤 Seus dados")

nome = st.text_input(
    "Seu nome",
    placeholder="Digite seu nome"
)

telefone = st.text_input(
    "WhatsApp",
    placeholder="(00) 00000-0000"
)

cidade = st.text_input(
    "Cidade",
    placeholder="Informe sua cidade"
)


# ==========================================
# SERVIÇO
# ==========================================

st.subheader("❄️ O que você precisa?")

servico = st.selectbox(
    "Escolha o serviço",
    list(SERVICOS.keys())
)

dados_servico = SERVICOS[servico]

st.info(
    f"{dados_servico['icone']} "
    f"{dados_servico['descricao']}"
)

opcao = st.selectbox(
    "Capacidade do aparelho",
    list(dados_servico["precos"].keys())
)

quantidade = st.number_input(
    "Quantidade de aparelhos",
    min_value=1,
    max_value=20,
    value=1,
    step=1
)

observacoes = st.text_area(
    "Observações",
    placeholder=(
        "Ex.: aparelho no segundo andar, "
        "já possui instalação antiga, etc."
    )
)


# ==========================================
# CÁLCULO
# ==========================================

valor_unitario = dados_servico["precos"][opcao]
total = valor_unitario * quantidade


st.divider()

st.subheader("📋 Resumo do orçamento")

st.markdown(
    f"""
    <div class="caixa">

    <b>Cliente:</b> {nome if nome else "Não informado"}<br><br>

    <b>Cidade:</b> {cidade if cidade else "Não informada"}<br><br>

    <b>Serviço:</b> {servico}<br><br>

    <b>Capacidade:</b> {opcao}<br><br>

    <b>Quantidade:</b> {quantidade}<br><br>

    <b>Valor unitário:</b> {moeda(valor_unitario)}

    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    f'<div class="total">{moeda(total)}</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="aviso">
    Valor estimado. O preço final poderá sofrer alterações
    conforme as condições encontradas no local da instalação
    ou manutenção.
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# WHATSAPP
# ==========================================

st.divider()

st.subheader("📲 Quero prosseguir")

# IMPORTANTE:
# Depois vamos colocar aqui o WhatsApp oficial da empresa.
# Formato: 55 + DDD + número, somente números.

WHATSAPP_EMPRESA = "5555999999999"

mensagem = f"""
Olá! Meu nome é {nome}.

Fiz um orçamento pelo sistema da F Climatização e gostaria de prosseguir com o atendimento.

SERVIÇO: {servico}
CAPACIDADE: {opcao}
QUANTIDADE: {quantidade}
VALOR ESTIMADO: {moeda(total)}
CIDADE: {cidade}

OBSERVAÇÕES:
{observacoes if observacoes else "Nenhuma observação."}
"""

link_whatsapp = (
    f"https://wa.me/{WHATSAPP_EMPRESA}"
    f"?text={quote(mensagem)}"
)

if nome and telefone and cidade:

    st.link_button(
        "📲 Continuar atendimento pelo WhatsApp",
        link_whatsapp,
        use_container_width=True
    )

else:

    st.warning(
        "Preencha seu nome, WhatsApp e cidade "
        "para continuar o atendimento."
    )


st.divider()

st.caption(
    "F Climatização • Instalação e manutenção de ar-condicionado"
)