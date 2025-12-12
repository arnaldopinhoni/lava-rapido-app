import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# CONEXÃO
# --------------------------------------------------
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        dbname=os.getenv("DB_NAME"),
        sslmode="require"
    )

# --------------------------------------------------
# CLIENTES
# --------------------------------------------------
def buscar_clientes_por_nome(nome):
    conn = get_connection()
    query = """
        SELECT id, nome
        FROM clientes
        WHERE nome ILIKE %s
        ORDER BY nome
    """
    df = pd.read_sql(query, conn, params=(f"%{nome}%",))
    conn.close()
    return df


def inserir_cliente(nome, telefone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO clientes (nome, telefone) VALUES (%s, %s) RETURNING id",
        (nome, telefone)
    )
    cliente_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()
    return cliente_id

# --------------------------------------------------
# CARROS
# --------------------------------------------------
def get_carros_por_cliente(cliente_id):
    conn = get_connection()
    query = """
        SELECT id, marca, modelo, placa
        FROM carros
        WHERE cliente_id = %s
        ORDER BY id DESC
    """
    df = pd.read_sql(query, conn, params=(cliente_id,))
    conn.close()
    return df


def inserir_carro(cliente_id, marca, modelo, placa):
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

# --------------------------------------------------
# SERVIÇOS
# --------------------------------------------------
def inserir_servico(
    carro_id,
    tipo_servico,
    valor,
    pago,
    entrega,
    horario_retirada,
    observacoes
):
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
            horario_retirada,
            observacoes,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'AGUARDANDO')
        """,
        (
            carro_id,
            tipo_servico,
            valor,
            pago,
            entrega,
            horario_retirada,
            observacoes
        )
    )

    conn.commit()
    cur.close()
    conn.close()


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
            s.horario_retirada,
            s.observacoes
        FROM servicos s
        JOIN carros ca ON ca.id = s.carro_id
        JOIN clientes cl ON cl.id = ca.cliente_id
        ORDER BY s.id DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


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
