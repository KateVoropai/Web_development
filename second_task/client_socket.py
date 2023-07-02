import socket
import ssl


def user_input(file_content):
    while True:
        try:
            id_cur = int(input("Введите id валюты, которой хотите узнать код: "))
            flag = False
            for text in file_content:
                if text["Cur_ID"] == id_cur:
                    print(f'Код валюты {text["Cur_Name"]} {text["Cur_Code"]}')
                    flag = True
                    break
            if flag == False:
                print("id под таким номером нет в списке валют!")            
        except ValueError:
            print("Ошибка ввода! Введите числовое значение!")
            
        answer = input("Желаете продолжить?(Y/N): ").lower()
        if answer == 'y':
            continue
        else:
            break

def display_currency(date_month_year):
    date_month_year = date_month_year.split(' ')
    print(f"Список валют на {date_month_year[2]} {date_month_year[3]} {date_month_year[4]}")

    with open('data_currency.json', encoding='utf-8') as file:
        file_content = file.read()
        file_content = eval(file_content)
        for text in file_content:
            print(f'ID {text["Cur_ID"]} - Currency {text["Cur_Name"]}')
        
    return user_input(file_content)

def main():
    package = 'GET http://api.nbrb.by/exrates/currencies HTTP/1.1\r\nHost: api.nbrb.by\r\n\r\n'
    hostname = 'api.nbrb.by'
    port = 443

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        context = ssl.create_default_context()
        ssock = context.wrap_socket(sock, server_hostname=hostname)      
        ssock.send(package.encode('utf-8'))
        data = ''
        while True:
            chunk = ssock.recv(4096).decode('utf-8', 'ignore')
            if chunk:
                data += chunk
            else:
                ssock.close()
                break
    except KeyboardInterrupt:
        ssock.close()
        print('Произошла ошибка')
    
    data_lst = data.split('\r\n')
    date_month_year = (data_lst[5])

    with open('data_currency.json', 'w', encoding="utf-8") as file:
        file.write(data_lst[7])

    display_currency(date_month_year)
    
if __name__ == '__main__':
    main()
