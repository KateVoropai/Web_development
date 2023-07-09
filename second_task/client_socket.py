import socket
import ssl
import json 
import os.path


def addrress():
    package = 'GET http://api.nbrb.by/exrates/currencies HTTP/1.1\r\nHost: api.nbrb.by\r\n\r\n'
    hostname = 'api.nbrb.by'
    port = 443
    return package, hostname, port

def data_processing(data):
    data = data.split('\r\n')
    data = json.loads(data[7])
    data_dict = {}
    for text in data:
        for key, value in text.items():
            if key == "Cur_Name":
                dict1 = {key:value}
            if key == "Cur_Code":
                dict2 = {key:value}
        data_dict[text.get("Cur_ID")] = {**dict1, **dict2}
    return data_dict

def download_data_currensy():
    package, hostname, port = addrress()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((hostname, port))
    except TimeoutError:
        print("Соединение не установлено,")
    context = ssl.create_default_context()
    ssock = context.wrap_socket(sock, server_hostname=hostname)      
    ssock.send(package.encode('utf-8'))
    data = ''
    print("working...")
    while True:
        chunk = ssock.recv(4096).decode('utf-8', 'ignore')
        if chunk:
            data += chunk
        else:
            ssock.close()
            break
    return data_processing(data)

def checking_file(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as file:
            file_content = file.read()
            file_content = json.loads(file_content)
    else:
        data_dict = download_data_currensy()
        with open(path, 'w+', encoding="utf-8") as file:
            file.write(json.dumps(data_dict, ensure_ascii=False))
            file.seek(0)
            file_content = file.read()
            file_content = json.loads(file_content)
    return file_content

def print_data_currency(content):
    for key, value in content.items():
        print(f'ID {key} - Currency {value["Cur_Name"]}')  
    return

def main():
    file_content = checking_file('data_currency.json')
    print_data_currency(file_content)
    while True:
        id_cur = input("Введите id валюты, которой хотите узнать код: ")
        if file_content.get(id_cur) == None:
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

if __name__ == '__main__':
    main()