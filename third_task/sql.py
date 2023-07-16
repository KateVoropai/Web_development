import sqlite3
from sqlite3 import Error
import requests
import datetime


def data_processing(json_response):
    data_list = []
    for row in json_response:
        for key, value in row.items():
            if key == "Cur_Name":
                cur_name = value
            if key == "Date":
                date = datetime.date.fromisoformat(value[:10])
            if key == "Cur_OfficialRate":
                rate = value
        data = cur_name, date, rate
        data_list.append(data)
    return data_list

def download_data_currensy():
    response = requests.get('https://api.nbrb.by/exrates/rates?periodicity=0')
    json_response = response.json()
    return data_processing(json_response)

def create_connection(database):
    connection = None
    try:
        connection = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        connection.row_factory = sqlite3.Row
    except Error:
        print("Соединение с БД не установлено!")
    return connection

def create_table(connection):
    cur = connection.cursor()
    cur.execute(""" CREATE TABLE IF NOT EXISTS currency_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency TEXT NOT NULL,
            date DATE,
            rate REAL
            )""")
    connection.commit()

def insert_data(connection, data):
    cur = connection.cursor()
    cur.executemany("""INSERT INTO currency_rate (currency, date, rate) VALUES (?, ?, ?)""", data)
    connection.commit()

def update_table(connection, data):
    cur = connection.cursor()
    cur.executemany("""UPDATE currency_rate SET (date, rate) = (?, ?) WHERE currency = ?""", data)
    connection.commit()

def checking_table(connection):
    cur = connection.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currency_rate'")
    result = cur.fetchone()
    if result == None:
        return False
    else:
        return True
    
def checking_date(connection):
    cur = connection.cursor()
    cur.execute("SELECT date FROM currency_rate")
    res = cur.fetchone()
    if res['date'] != datetime.date.today():
        return False
    else:
        return True
    
def fetch_table(connection):
    cur = connection.cursor()
    cur.execute("SELECT currency, date, rate FROM currency_rate")
    currencies = cur.fetchall()
    return currencies

def print_currency(currencies):
    for result in currencies:
        print(f"Курс {result['currency']} на дату {result['date']} составляет {result['rate']} BYN")

def main():
    database = 'data_currency.db'
    data = download_data_currensy()
    connection = create_connection(database)

    if checking_table(connection):
        if checking_date(connection) == False:
            print(f"Курс валют нe актуальный!")
            lst_ans = ['y', 'n']
            while True:    
                answer = input("Обновить курс валют на текущую дату? (Y/N): ").lower()
                if answer in lst_ans:
                    if answer == 'y':
                        update_table(connection, data)
                        break
                    else:
                        break
                else:
                    print("Некорректный ввод! Введите (Y/N)")
    else:
        create_table(connection)
        insert_data(connection, data)
    
    currencies = fetch_table(connection)
    print_currency(currencies)
    
    connection.close()

if __name__ == '__main__':
    main()