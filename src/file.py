#coding: utf-8

import sys
import time
import types
import threading

LOCK = threading.RLock()
folder = ''

class io:
    def readfrom(self, name):
        if (name == ''): 
            print('Не указано имя файла для чтения!')
            status = False
        else:
            data = []
            try:
                with open(folder+name, 'r') as rf:
                    for line in rf:
                        data.append(line)
                status = True
            except IOError:
                print("Не найден файл: "+name)
                status = False
            except ValueError:
                print("Неверный формат файла: "+name)
                status = False
        if (status == True):
            return status, data
        else:
            data = []
            return status, data
        
    

    def writeto(self, name, data):
        if not name or not data:
            print('Не указано имя файла или отсутствуют данные для записи в файл')
            return False
        else:
            filename = folder+name
            
            try:
              basestring
            except NameError:
              basestring = str
            
            for i in list(range(5)):
                try:
                    with LOCK:
                        with open(filename, 'a') as out:
                            if isinstance(data, basestring):
                                out.write(data+'\n')
                            else:
                                for i in data:
                                    i = i.replace('\n', '')
                                    out.write(i+'\n')
                    return True
                except:
                    time.sleep(0.5)
            print('5 попыток записи в файл оказались неудачными. Проверьте права на каталог и на файл для записи.')
            return False

    def rewriteto(self, name, data):
        if not name or not data:
            print('Не указано имя файла или отсутствуют данные для записи в файл')
            return False
        else:
            filename = folder+name

            try:
              basestring
            except NameError:
              basestring = str

            for i in list(range(5)):
                try:
                    with LOCK:
                        with open(filename, 'w') as out:
                            if isinstance(data, basestring):
                                out.write(data+'\n')
                            else:
                                for i in data:
                                    i = i.replace('\n', '')
                                    out.write(i+'\n')
                    return True
                except:
                    time.sleep(0.5)
            print('5 попыток записи в файл оказались неудачными. Проверьте права на каталог и на файл для записи.')
            return False
