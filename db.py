import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


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
# INSERT
# ----------------------------------------------------------
def insert_car(
    nome_cliente, telefone, marca, modelo, placa,
    tipo_servico, valor, pago,
    entrega, endereco_entrega, horario_retirada,
    observacoes
):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO carros (
        nome_cliente, telefone, marca, modelo, placa,
        tipo_servico, valor, pago,
        entrega, endereco_entrega, horario_retirada,
        status, observacoes
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Aguardando',%s)
    """

    cur.execute(sql, (
        nome_cliente, telefone, marca, modelo, placa,
        tipo_servico, valor, pago,
        entrega, endereco_entrega, horario_retirada,
        observacoes
    ))

    conn.commit()
    cur.close()
    conn.close()


# ----------------------------------------------------------
# SELECT ALL
# ----------------------------------------------------------
def get_all_cars():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM carros ORDER BY id DESC", conn)
    conn.close()
    return df


# ----------------------------------------------------------
# UPDATE STATUS
# ----------------------------------------------------------
def update_status(car_id, novo_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE carros SET status = %s WHERE id = %s", (novo_status, car_id))
    conn.commit()
    cur.close()
    conn.close()


# ----------------------------------------------------------
# UPDATE PAYMENT
# ----------------------------------------------------------
def update_payment(car_id, pago):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE carros SET pago = %s WHERE id = %s", (pago, car_id))
    conn.commit()
    cur.close()
    conn.close()
