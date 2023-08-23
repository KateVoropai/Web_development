import sqlite3
from sqlite3 import Error
import requests
import datetime
from contextlib import contextmanager


def data_processing(data_response):
    for row in data_response:
        del row['Cur_ID'] 
        del row['Cur_Abbreviation']
        del row['Cur_Scale']
        row["Date"] = datetime.date.fromisoformat(row.get("Date")[:10])
    return data_response

def download_data_currensy():
    response = requests.get('https://api.nbrb.by/exrates/rates?periodicity=0')
    data_response = response.json()
    return data_processing(data_response)

def create_connection(database):
    connection = None
    try:
        connection = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
    except Error as e:
        print(f"Соединение с базой данных не установлено, {e}")
    return connection, cursor
    
def create_table(cursor):
    try:
        cursor.execute(""" CREATE TABLE IF NOT EXISTS currency_rate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT NOT NULL,
                    date DATE,
                    rate REAL
                    )""")
    except Error as e:
        print(f"Ошибка выполнения запроса, {e}")
    return None

@contextmanager
def context_manager(connection, cursor):
    try:
        yield cursor
        connection.commit()
    except Error as e:
        connection.rollback()
        print(f"Ошибка выполнения запроса, {e}")

def checking_table(cursor):
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currency_rate'")
    except Error as e:
        print(f"Ошибка выполнения запроса, {e}")
        return False    
    result = cursor.fetchone()
    if result:
        return checking_date(cursor)
    return False

def checking_date(cursor):
    try:
        cursor.execute("SELECT date FROM currency_rate")
    except Error as e:
        print(f"Ошибка выполнения запроса, {e}")
        return False    
    result = cursor.fetchone()
    if result is None:
        return False
    if result['date'] == datetime.date.today():
        return False
    if result['date'] != datetime.date.today():
        return True
    

def fetch_table(cursor):
    try:
        cursor.execute("SELECT * FROM currency_rate")
        currencies = cursor.fetchall()
        return currencies
    except Error as e:
        print(f"Ошибка выполнения запроса, {e}")
        return None

def print_currency(currencies):
    for result in currencies:
        print(f"Курс {result['currency']} на дату {result['date']} составляет {result['rate']} BYN")
    return None

def checking_answer():
    while True:
        answer = input("Создать таблицу? (Y/N): ").lower()
        if answer == 'y':
            return True
        if answer == 'n':
            return False
        else:
            print("Некорректный ввод! Введите (Y/N)")

def changes_in_table(connection, cursor, data):
    insert_data = """INSERT INTO currency_rate (currency, date, rate) VALUES (:Cur_Name, :Date, :Cur_OfficialRate)"""
    update_table = """UPDATE currency_rate 
                                SET date = :Date, rate = :Cur_OfficialRate
                                WHERE currency = :Cur_Name"""
    
    if checking_table(cursor):
        with context_manager(connection, cursor) as cur:
            cur.executemany(update_table, data)
        return None
    
    create_table(cursor)
    with context_manager(connection, cursor) as cur:
        cur.executemany(insert_data, data)
    return None

def main():
    database = 'data_currency.db'
    data = download_data_currensy()
    connection, cursor = create_connection(database)
    
    changes_in_table(connection, cursor, data)
    
    if checking_answer():
        currencies = fetch_table(cursor)
        print_currency(currencies)
    
    connection.close()

if __name__ == '__main__':
    main()