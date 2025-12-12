import os
import psycopg2
import pandas as pd


# ----------------------------------------------------------
# CONEXÃO COM O BANCO (SUPABASE POOLER + SSL)
# ----------------------------------------------------------
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dbname=os.getenv("DB_NAME"),
        sslmode="require"
    )


# ----------------------------------------------------------
# CLIENTES
# ----------------------------------------------------------
def buscar_clientes_por_nome(nome):
    """
    Retorna até 10 clientes cujo nome contenha o texto informado
    (case insensitive).
    """
    conn = get_connection()
    query = """
        SELECT id, nome
        FROM clientes
        WHERE nome ILIKE %s
        ORDER BY nome
        LIMIT 10
    """
    df = pd.read_sql(query, conn, params=[f"%{nome}%"])
    conn.close()
    return df


def inserir_cliente(nome, telefone=None):
    """
    Insere um novo cliente e retorna o ID criado.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clientes (nome, telefone)
        VALUES (%s, %s)
        RETURNING id
        """,
        (nome, telefone)
    )
    cliente_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return cliente_id


# ----------------------------------------------------------
# CARROS
# ----------------------------------------------------------
def get_carros_por_cliente(cliente_id):
    """
    Retorna todos os carros cadastrados para um cliente.
    """
    conn = get_connection()
    query = """
        SELECT id, marca, modelo, placa
        FROM carros
        WHERE cliente_id = %s
        ORDER BY created_at DESC
    """
    df = pd.read_sql(query, conn, params=[cliente_id])
    conn.close()
    return df


def inserir_carro(cliente_id, marca, modelo, placa):
    """
    Insere um novo carro para o cliente e retorna o ID criado.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO carros (cliente_id, marca, modelo, placa)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (cliente_id, marca, modelo, placa)
    )
    carro_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return carro_id


# ----------------------------------------------------------
# SERVIÇOS (LAVAGENS)
# ----------------------------------------------------------
def inserir_servico(
    carro_id,
    tipo_servico,
    valor,
    pago,
    entrega,
    endereco_entrega,
    horario_retirada,
    observacoes
):
    """
    Registra um serviço (lavagem) para um carro.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO servicos (
            carro_id,
            tipo_servico,
            valor,
            pago,
            entrega,
            endereco_entrega,
            horario_retirada,
            observacoes
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            carro_id,
            tipo_servico,
            valor,
            pago,
            entrega,
            endereco_entrega,
            horario_retirada,
            observacoes
        )
    )
    conn.commit()
    cur.close()
    conn.close()


# ----------------------------------------------------------
# CONSULTA: SERVIÇOS DO DIA (para tela "Carros do Dia")
# ----------------------------------------------------------
def get_servicos_do_dia():
    conn = get_connection()

    query = """
        SELECT
            s.id,
            cl.nome AS cliente,

            ca.marca,
            ca.modelo,
            ca.placa,

            s.tipo_servico,
            s.valor,
            s.status,
            s.pago,

            s.entrega,
            s.endereco_entrega,
            s.horario_retirada,
            s.observacoes
        FROM servicos s
        JOIN carros ca ON ca.id = s.carro_id
        JOIN clientes cl ON cl.id = ca.cliente_id
        WHERE DATE(s.created_at) = CURRENT_DATE
        ORDER BY s.id DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df
# ----------------------------------------------------------
# ATUALIZAÇÕES RÁPIDAS (STATUS / PAGAMENTO)
# ----------------------------------------------------------
def atualizar_status(servico_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE servicos SET status = %s WHERE id = %s",
        (status, servico_id)
    )
    conn.commit()
    cur.close()
    conn.close()


def atualizar_pagamento(servico_id, pago):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE servicos SET pago = %s WHERE id = %s",
        (pago, servico_id)
    )
    conn.commit()
    cur.close()
    conn.close()
