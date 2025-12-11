import streamlit as st
from db import insert_car, get_all_cars, update_status, update_payment
from datetime import time

st.set_page_config(
    page_title="Lava-Rápido",
    layout="centered",  # Melhor para iPhone
)

st.markdown("""
<style>
    /* Aumenta espaço e tamanho dos botões no iPhone */
    button[kind="primary"] {
        padding: 14px 20px !important;
        font-size: 18px !important;
        width: 100%;
    }
    input, select, textarea {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚗 Controle do Lava-Rápido")

menu = st.selectbox(
    "Menu",
    ["Cadastrar Carro", "Carros do Dia"],
)


# -------------------------------------------------------------
# CADASTRO DE CARRO
# -------------------------------------------------------------
if menu == "Cadastrar Carro":

    st.subheader("Novo carro")

    nome = st.text_input("Nome do cliente")
    telefone = st.text_input("Telefone")
    marca = st.text_input("Marca")
    modelo = st.text_input("Modelo")
    placa = st.text_input("Placa")

    tipo_servico = st.selectbox("Serviço", ["Lavagem", "Lavagem + Cera"])
    valor = st.number_input("Valor", min_value=0.0, step=5.0)
    pago = st.checkbox("Pagamento realizado?")

    entrega = st.selectbox("Entrega", ["Cliente busca", "Lava-rápido entrega"])
    endereco = ""
    if entrega == "Lava-rápido entrega":
        endereco = st.text_area("Endereço de entrega")

    horario = st.time_input("Horário de retirada", value=time(9, 0))
    observacoes = st.text_area("Observações")

    if st.button("Salvar"):
        if not nome or not placa:
            st.error("Nome e placa são obrigatórios.")
        else:
            insert_car(
                nome, telefone, marca, modelo, placa,
                tipo_servico, valor, pago,
                entrega, endereco, horario,
                observacoes
            )
            st.success("Carro cadastrado com sucesso!")


# -------------------------------------------------------------
# LISTA DE CARROS
# -------------------------------------------------------------
elif menu == "Carros do Dia":
    
    st.subheader("Carros cadastrados")
    df = get_all_cars()

    if df.empty:
        st.info("Nenhum carro cadastrado hoje.")
    else:
        for _, row in df.iterrows():
            with st.container():
                st.markdown(
                    f"""
                    ### {row['marca']} {row['modelo']} — **{row['placa']}**
                    **Cliente:** {row['nome_cliente']}  
                    **Serviço:** {row['tipo_servico']} — R$ {row['valor']}  
                    **Status:** {row['status']}  
                    **Pagamento:** {"Pago" if row['pago'] else "Não pago"}  
                    """
                )
                
                novo_status = st.selectbox(
                    "Atualizar status",
                    ["Aguardando", "Lavando", "Pronto", "Entregue"],
                    index=["Aguardando", "Lavando", "Pronto", "Entregue"].index(row["status"]),
                    key=f"status_{row['id']}"
                )

                pago_novo = st.checkbox(
                    "Marcar como pago", 
                    value=row["pago"], 
                    key=f"pago_{row['id']}"
                )

                if st.button("Salvar alterações", key=f"save_{row['id']}"):
                    update_status(row["id"], novo_status)
                    update_payment(row["id"], pago_novo)
                    st.success("Atualizado!")
                    st.experimental_rerun()