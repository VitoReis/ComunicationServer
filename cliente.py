from socket import *
import re
import socket
import sys
import threading
import os
import time

def thread(clientSocket):
    while True:
        message = clientSocket.recv(1024).decode()
        print(f'{message}\n')



def main():
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    else:
        ip = input('Type the server IP: ')
        port = int(input('Type the server port: '))

    #REGEX FOR CLIENT MESSAGES:
    identifierStartingTag = re.compile('^#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+\s[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+')
    identifierMidleTag = re.compile('^[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+\s#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+\s[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+')
    identifierEndingTag = re.compile('^[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+\s#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+')
    identifierText = re.compile('^[a-zA-Z0-9\s,.?!:;+\-*/=@#$%()[\]{}]+$')
    identifierSub = re.compile('^\+[a-zA-Z0-9]+$')
    identifierUnsub = re.compile('^\-[a-zA-Z0-9]+$')
    identifierDesconnect = re.compile('^#quit$')            # Criei este comando para caso o cliente queira se desconectar do servidor
    identifierKill = re.compile('^##kill$')

    clientSocket = socket.socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ip, port))
    threading.Thread(target=thread, args=(clientSocket,)).start()  # Abre uma thread para o cliente escutar
    while True:
        time.sleep(0.05)                            #Time sleep para receber o cliente
        message = input('Insert your message: ')
        if re.match(identifierSub, message):
            message = message.encode()
            if len(message) > 500:
                print('String too large')
            clientSocket.send(message)
        elif re.match(identifierUnsub, message):
            message = message.encode()
            if len(message) > 500:
                print('String too large')
            clientSocket.send(message)
        elif re.match(identifierStartingTag, message) or re.match(identifierMidleTag, message) or re.match(identifierEndingTag, message):
            message = message.encode()
            if len(message) > 500:
                print('String too large')
            clientSocket.send(message)
        elif re.match(identifierDesconnect, message):
            message = message.encode()
            clientSocket.send(message)
            os._exit(1)
        elif re.match(identifierKill, message):
            message = message.encode()
            clientSocket.send(message)
            os._exit(1)
        elif re.match(identifierText, message):
            message = message.encode()
            if len(message) > 500:
                print('String too large')
            clientSocket.send(message)
        else:
            print('Invalid message')

if __name__ == '__main__':
    main()