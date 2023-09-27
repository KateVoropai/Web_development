import sqlite3
from sqlite3 import Error
import requests
import datetime
from contextlib import contextmanager


def create_connection(database):
    connection = None
    try:
        connection = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
    except Error as e:
        print(f"Соединение с базой данных не установлено, {e}")
    return connection, cursor

connection, cursor = create_connection('data_currency.db')

def download_data_currensy():
    response = requests.get('https://api.nbrb.by/exrates/rates?periodicity=0')
    data_response = response.json()
    for row in data_response:
        del row['Cur_ID'] 
        del row['Cur_Abbreviation']
        del row['Cur_Scale']
        row["Date"] = datetime.date.fromisoformat(row.get("Date")[:10])
    return data_response

@contextmanager
def context_manager():
    try:
        yield cursor
    except Error as e:
        connection.rollback()
        print(f"Ошибка выполнения запроса, {e}")
    else:
        connection.commit()

def create_table():
    with context_manager() as cur:
        cur.execute(""" CREATE TABLE IF NOT EXISTS currency_rate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT NOT NULL,
                    date DATE,
                    rate REAL
                    )""")
    return None

def insert_table(data):
    insert_data = """INSERT INTO currency_rate (currency, date, rate) VALUES (:Cur_Name, :Date, :Cur_OfficialRate)"""
    with context_manager() as cur:
        cur.executemany(insert_data, data)
    return None

def update_table(data):
    update_table = """UPDATE currency_rate 
                    SET date = :Date, rate = :Cur_OfficialRate
                    WHERE currency = :Cur_Name"""
    with context_manager() as cur:
        cur.executemany(update_table, data)
    return None

def checking_table():
    with context_manager() as cur:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currency_rate'")   
    result = cursor.fetchone()
    if result:
        return checking_date()
    return False

def checking_date():
    with context_manager() as cur:
        cursor.execute("SELECT date FROM currency_rate")    
    result = cursor.fetchone()
    if result is None:
        return False
    if result['date'] == datetime.date.today():
        return True
    return False
    

def fetch_table():
    with context_manager() as cur:
        cur.execute("SELECT * FROM currency_rate")
        currencies = cursor.fetchall()
        return currencies
    

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

def processing_in_data_base(data):
    if checking_answer():
        create_table()
        insert_table(data)
    else:
        if checking_table() is False: 
            update_table(data)
    return None


def main():
    data = download_data_currensy()
    
    processing_in_data_base(data)
    currencies = fetch_table()
    print_currency(currencies)

if __name__ == '__main__':
    
    main()
    connection.close()