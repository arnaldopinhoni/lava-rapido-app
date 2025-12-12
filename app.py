import streamlit as st
import pandas as pd
from datetime import date

from db import (
    buscar_clientes_por_nome,
    inserir_cliente,
    get_carros_por_cliente,
    inserir_carro,
    inserir_servico,
    get_servicos_do_dia,
    atualizar_status,
    atualizar_pagamento
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Lava Rápido",
    layout="centered"
)

st.title("🚗 Lava Rápido")

menu = st.sidebar.radio(
    "Menu",
    ["Novo Serviço", "Carros do Dia"]
)

# ==================================================
# NOVO SERVIÇO
# ==================================================
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

    if cliente_id is None and nome_cliente:
        telefone = st.text_input("Telefone (opcional)")
        if st.button("Criar cliente"):
            cliente_id = inserir_cliente(nome_cliente, telefone)
            st.success("Cliente criado")

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
                linha = carros.iloc[opcoes.index(escolha_carro)]
                carro_id = int(linha["id"])
                marca = linha["marca"]
                modelo = linha["modelo"]
                placa = linha["placa"]
            else:
                marca = st.text_input("Marca")
                modelo = st.text_input("Modelo")
                placa = st.text_input("Placa")
        else:
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            placa = st.text_input("Placa")

        if carro_id is None and placa:
            if st.button("Salvar carro"):
                carro_id = inserir_carro(cliente_id, marca, modelo, placa)
                st.success("Carro cadastrado")

    if cliente_id and carro_id:
        st.divider()
        st.subheader("Serviço")

        with st.form("form_servico"):
            tipo_servico = st.selectbox(
                "Tipo de serviço",
                ["Lavagem", "Lavagem + Cera"]
            )
            valor = st.number_input("Valor (R$)", min_value=0.0, step=5.0)
            pago = st.checkbox("Pago")
            entrega = st.selectbox(
                "Entrega",
                ["Cliente vai buscar", "Entrega no endereço"]
            )
            endereco = st.text_input("Endereço") if entrega == "Entrega no endereço" else None
            horario = st.time_input("Horário combinado")
            observacoes = st.text_area("Observações")
            submit = st.form_submit_button("Registrar serviço")

        if submit:
            inserir_servico(
                carro_id,
                tipo_servico,
                valor,
                pago,
                entrega,
                endereco,
                horario,
                observacoes
            )
            st.success("Serviço registrado")
            st.toast("Lavagem registrada 🚗🧼")

# ==================================================
# CARROS DO DIA
# ==================================================
elif menu == "Carros do Dia":

    data = st.date_input("Data", value=date.today())

    df = get_servicos_do_dia()
    df = df[df["horario_retirada"].notna()]

    if df.empty:
        st.info("Nenhum serviço encontrado.")
    else:
        total = df["valor"].sum()
        pago = df[df["pago"]]["valor"].sum()
        pendente = total - pago

        st.metric("💰 Total do dia", f"R$ {total:.2f}")
        st.metric("✅ Pago", f"R$ {pago:.2f}")
        st.metric("⏳ Pendente", f"R$ {pendente:.2f}")

        st.divider()

        for _, row in df.iterrows():
            with st.expander(f"{row['cliente']} - {row['placa']}"):
                st.write(f"**Serviço:** {row['tipo_servico']}")
                st.write(f"**Valor:** R$ {row['valor']:.2f}")

                novo_status = st.selectbox(
                    "Status",
                    ["Aguardando", "Em lavagem", "Pronto", "Entregue"],
                    index=["Aguardando", "Em lavagem", "Pronto", "Entregue"].index(row["status"]),
                    key=f"status_{row['id']}"
                )

                pago_chk = st.checkbox(
                    "Pago",
                    value=row["pago"],
                    key=f"pago_{row['id']}"
                )

                if st.button("Atualizar", key=f"btn_{row['id']}"):
                    atualizar_status(row["id"], novo_status)
                    atualizar_pagamento(row["id"], pago_chk)
                    st.toast("Atualizado com sucesso")
