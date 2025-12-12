import streamlit as st
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
# CONFIGURAÇÃO
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

    # ------------------------------
    # CLIENTE
    # ------------------------------
    st.subheader("Cliente")

    nome_cliente_raw = st.text_input("Nome do cliente")
    nome_cliente = nome_cliente_raw.upper() if nome_cliente_raw else None
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
        telefone_raw = st.text_input("Telefone (opcional)")
        telefone = telefone_raw.upper() if telefone_raw else None

        if st.button("Criar cliente"):
            cliente_id = inserir_cliente(nome_cliente, telefone)
            st.success("Cliente criado")

    # ------------------------------
    # CARRO
    # ------------------------------
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
                marca_raw = linha["marca"]
                modelo_raw = linha["modelo"]
                placa_raw = linha["placa"]
            else:
                marca_raw = st.text_input("Marca")
                modelo_raw = st.text_input("Modelo")
                placa_raw = st.text_input("Placa")
        else:
            marca_raw = st.text_input("Marca")
            modelo_raw = st.text_input("Modelo")
            placa_raw = st.text_input("Placa")

        marca = marca_raw.upper() if marca_raw else None
        modelo = modelo_raw.upper() if modelo_raw else None
        placa = placa_raw.upper() if placa_raw else None

        if carro_id is None and placa:
            if st.button("Salvar carro"):
                carro_id = inserir_carro(
                    cliente_id,
                    marca,
                    modelo,
                    placa
                )
                st.success("Carro cadastrado")

    # ------------------------------
    # SERVIÇO
    # ------------------------------
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

        entrega_label = st.selectbox(
            "Modalidade",
            ["Cliente vai buscar", "Entrega"]
        )

        horario = st.time_input("Horário combinado")

        observacoes_raw = st.text_area(
            "Observações",
            placeholder="Ex: ENTREGA - AV BRASIL, 123"
        )

        if st.button("Registrar serviço"):
            inserir_servico(
                carro_id=carro_id,
                tipo_servico=tipo_servico.upper(),
                valor=valor,
                pago=pago,
                entrega=entrega_label.upper(),
                horario_retirada=horario,
                observacoes=observacoes_raw.upper() if observacoes_raw else None
            )
            st.success("Serviço registrado com sucesso")
            st.toast("Lavagem registrada 🚗🧼")

# ==================================================
# CARROS DO DIA
# ==================================================
elif menu == "Carros do Dia":

    st.subheader("Serviços do dia")

    data_filtro = st.date_input("Data", value=date.today())

    df = get_servicos_do_dia()

    if df.empty:
        st.info("Nenhum serviço encontrado.")
    else:
        total = df["valor"].sum()
        pago_total = df[df["pago"]]["valor"].sum()
        pendente = total - pago_total

        st.metric("💰 Total", f"R$ {total:.2f}")
        st.metric("✅ Pago", f"R$ {pago_total:.2f}")
        st.metric("⏳ Pendente", f"R$ {pendente:.2f}")

        st.divider()

        status_map = {
            "AGUARDANDO": "Aguardando",
            "EM LAVAGEM": "Em lavagem",
            "PRONTO": "Pronto",
            "ENTREGUE": "Entregue"
        }
        status_reverse = {v: k for k, v in status_map.items()}

        for _, row in df.iterrows():
            with st.expander(f"{row['cliente']} - {row['placa']}"):

                st.markdown(f"""
                **🚗 Veículo**
                - Marca: {row['marca']}
                - Modelo: {row['modelo']}
                - Placa: {row['placa']}

                **🧼 Serviço**
                - Tipo: {row['tipo_servico']}
                - Valor: R$ {row['valor']:.2f}

                **🚚 Modalidade**
                - {row['entrega']}
                """)

                st.markdown(
                    f"⏰ **Horário:** {row['horario_retirada'] if row['horario_retirada'] else '—'}"
                )

                st.markdown(
                    f"📝 **Observações:** {row['observacoes'] if row['observacoes'] else '—'}"
                )

                st.divider()

                status_labels = list(status_map.values())
                status_atual_label = status_map.get(row["status"], "Aguardando")

                novo_status_label = st.selectbox(
                    "Status",
                    status_labels,
                    index=status_labels.index(status_atual_label),
                    key=f"status_{row['id']}"
                )

                pago_chk = st.checkbox(
                    "Pago",
                    value=row["pago"],
                    key=f"pago_{row['id']}"
                )

                if st.button("Atualizar", key=f"btn_{row['id']}"):
                    atualizar_status(
                        row["id"],
                        status_reverse[novo_status_label]
                    )
                    atualizar_pagamento(row["id"], pago_chk)
                    st.toast("Atualizado com sucesso")
