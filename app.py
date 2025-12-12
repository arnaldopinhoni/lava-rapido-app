import streamlit as st
import pandas as pd

from db import (
    buscar_clientes_por_nome,
    inserir_cliente,
    get_carros_por_cliente,
    inserir_carro,
    inserir_servico,
    get_servicos_do_dia
)

st.set_page_config(
    page_title="Lava Rápido",
    layout="centered"
)

st.title("🚗 Lava Rápido")

menu = st.sidebar.radio(
    "Menu",
    ["Novo Serviço", "Carros do Dia"]
)

# ==========================================================
# NOVO SERVIÇO
# ==========================================================
if menu == "Novo Serviço":

    st.subheader("Cliente")

    nome_cliente = st.text_input("Nome do cliente")

    cliente_id = None

    if nome_cliente:
        sugestoes = buscar_clientes_por_nome(nome_cliente)

        if not sugestoes.empty:
            nomes = sugestoes["nome"].tolist()
            escolha = st.selectbox(
                "Clientes encontrados",
                ["Novo cliente"] + nomes
            )

            if escolha != "Novo cliente":
                cliente_id = int(
                    sugestoes[sugestoes["nome"] == escolha]["id"].iloc[0]
                )
        else:
            st.info("Cliente novo")

    telefone = None
    if cliente_id is None and nome_cliente:
        telefone = st.text_input("Telefone (opcional)")

        if st.button("Criar cliente"):
            cliente_id = inserir_cliente(nome_cliente, telefone)
            st.success("Cliente criado com sucesso")

    # ------------------------------------------------------
    # CARROS
    # ------------------------------------------------------
    if cliente_id:
        st.divider()
        st.subheader("Carro")

        carros = get_carros_por_cliente(cliente_id)

        carro_id = None

        if not carros.empty:
            opcoes = [
                f"{row['marca']} {row['modelo']} - {row['placa']}"
                for _, row in carros.iterrows()
            ]

            escolha_carro = st.selectbox(
                "Escolha um carro",
                ["Novo carro"] + opcoes
            )

            if escolha_carro != "Novo carro":
                linha = carros.iloc[
                    opcoes.index(escolha_carro)
                ]
                carro_id = int(linha["id"])
                marca = st.text_input("Marca", linha["marca"])
                modelo = st.text_input("Modelo", linha["modelo"])
                placa = st.text_input("Placa", linha["placa"])
            else:
                marca = st.text_input("Marca")
                modelo = st.text_input("Modelo")
                placa = st.text_input("Placa")
        else:
            st.info("Nenhum carro cadastrado para este cliente.")
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            placa = st.text_input("Placa")

        if carro_id is None and placa:
            if st.button("Salvar carro"):
                carro_id = inserir_carro(
                    cliente_id, marca, modelo, placa
                )
                st.success("Carro cadastrado")

    # ------------------------------------------------------
    # SERVIÇO
    # ------------------------------------------------------
    if cliente_id and carro_id:
        st.divider()
        st.subheader("Serviço")

        tipo_servico = st.selectbox(
            "Tipo de serviço",
            ["Lavagem", "Lavagem + Cera"]
        )

        valor = st.number_input(
            "Valor (R$)",
            min_value=0.0,
            step=5.0
        )

        pago = st.checkbox("Pago")

        entrega = st.selectbox(
            "Entrega",
            ["Cliente vai buscar", "Entrega no endereço"]
        )

        endereco = None
        if entrega == "Entrega no endereço":
            endereco = st.text_input("Endereço de entrega")

        horario = st.time_input("Horário combinado")

        observacoes = st.text_area("Observações")

        if st.button("Registrar serviço"):
            inserir_servico(
                carro_id=carro_id,
                tipo_servico=tipo_servico,
                valor=valor,
                pago=pago,
                entrega=entrega,
                endereco_entrega=endereco,
                horario_retirada=horario,
                observacoes=observacoes
            )
            st.success("Serviço registrado com sucesso")

# ==========================================================
# CARROS DO DIA
# ==========================================================
elif menu == "Carros do Dia":

    st.subheader("Serviços de hoje")

    df = get_servicos_do_dia()

    if df.empty:
        st.info("Nenhum serviço cadastrado hoje.")
    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
