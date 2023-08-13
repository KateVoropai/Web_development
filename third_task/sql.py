import sqlite3
from sqlite3 import Error
import requests
import datetime


def data_processing(data_response):
    for row in data_response:
        row.pop('Cur_ID') 
        row.pop('Cur_Abbreviation') 
        row.pop('Cur_Scale') 
        for key, value in row.items():
            if key == "Date":
                row["Date"] = datetime.date.fromisoformat(value[:10])
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
        print("Соединение с базой данных не установлено, {e}")
    return connection, cursor
    
def create_table(connection):
    try:
        connection.execute(""" CREATE TABLE IF NOT EXISTS currency_rate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT NOT NULL,
                    date DATE,
                    rate REAL
                    )""")
    except Error as e:
        print("Ошибка выполнения запроса, {e}")

def insert_data(connection, data):
    try:
        with connection:
            connection.executemany("""INSERT INTO currency_rate (currency, date, rate) VALUES (:Cur_Name, :Date, :Cur_OfficialRate)""", data)
    except Error as e:
        print("Ошибка выполнения запроса, {e}")

def update_table(connection, data):
    try:
        with connection:
            connection.executemany("""UPDATE currency_rate 
                                    SET date = :Date, rate = :Cur_OfficialRate
                                    WHERE currency = :Cur_Name""", data)
    except Error as e:
        print("Ошибка выполнения запроса, {e}")

def checking_table(cursor):
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currency_rate'")
        result = cursor.fetchone()
        if result:
            return True
        return False
    except Error as e:
        print("Ошибка выполнения запроса, {e}")

def checking_date(cursor):
    try:
        cursor.execute("SELECT date FROM currency_rate")
        result = cursor.fetchone()
        if result is None:
            return False
        if result['date'] == datetime.date.today():
            return False
        if result['date'] != datetime.date.today():
            return True
    except Error as e:
        print("Ошибка выполнения запроса, {e}")

def fetch_table(cursor):
    try:
        cursor.execute("SELECT * FROM currency_rate")
        currencies = cursor.fetchall()
        return currencies
    except Error as e:
        print("Ошибка выполнения запроса, {e}")

def print_currency(currencies):
    for result in currencies:
        print(f"Курс {result['currency']} на дату {result['date']} составляет {result['rate']} BYN")

def checking_answer():
    while True:
        answer = input("Создать таблицу? (Y/N): ").lower()
        if answer == 'y':
            return True
        if answer == 'n':
            return False
        else:
            print("Некорректный ввод! Введите (Y/N)")

def main():
    database = 'data_currency.db'
    data = download_data_currensy()
    connection, cursor = create_connection(database)

    if checking_table(cursor):
        if checking_date(cursor):
            update_table(connection, data)
    else:
        create_table(connection)
        insert_data(connection, data)
    
    if checking_answer():
        currencies = fetch_table(cursor)
        print_currency(currencies)
    
    connection.close()

if __name__ == '__main__':
    main()