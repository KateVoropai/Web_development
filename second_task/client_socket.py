import socket
import ssl
import json 
import os.path


def data_processing(response):
    response = response.split('\r\n')
    response = json.loads(response[8])

    data_dict = {}
    for text in response:
        dict1 = {"Cur_Name":text["Cur_Name"]}
        dict2 = {"Cur_Code":text["Cur_Code"]}
        data_dict[text.get("Cur_ID")] = {**dict1, **dict2}
    return data_dict

def download_data_currensy():
    package = 'GET https://www.nbrb.by/api/exrates/currencies HTTP/1.1\r\nHost: www.nbrb.by\r\n\r\n'

    hostname = 'www.nbrb.by'
    port = 443

    context = ssl.create_default_context()

    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.send(package.encode())
            response = b''
            while True:
                data = ssock.recv(4096)
                response += data
                if ( len(data) < 1 ) :
                    break
    response = response.decode('utf-8', 'ignore')
    return data_processing(response)

def checking_file(path):
    if not os.path.exists(path):
        data_dict = download_data_currensy()
        with open(path, 'w') as file:
            json.dump(data_dict, file, indent=3)

    with open(path, 'r') as file:
        file_content = json.load(file)
    return file_content

def print_data_currency(content):
    for key, value in content.items():
        print(f'ID {key} - Currency {value["Cur_Name"]}')  
    return

def checking_answer(file_content):
    while True:
        id_cur = input("Введите id валюты, которой хотите узнать код: ")
        if  not file_content.get(id_cur):
            print("id под таким номером нет в списке валют!")
        else:
            print(f"Код валюты {file_content[id_cur]['Cur_Name']} {file_content[id_cur]['Cur_Code']}")
        
        lst_ans = ['y', 'n']
        while True:    
            answer = input("Желаете продолжить?(Y/N): ").lower()
            if answer in lst_ans:
                if answer == 'y':
                    break
                else:
                    return None
            else:
                print("Некорректный ввод! Введите (Y/N)")

def main():
    file_content = checking_file('data_currency.json')
    print_data_currency(file_content)

    checking_answer(file_content)

if __name__ == '__main__':
    main()