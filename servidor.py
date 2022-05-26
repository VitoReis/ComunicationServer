from socket import *
import threading
import socket
import sys
import re
import os

tags = {}


def thread(connectionSocket,addr,port):
    global tags
    # Regex para aceitar ou não as menssagens
    identifierStartingTag = re.compile('^#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+\s[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+')
    identifierMiddleTag = re.compile('^[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+\s#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+\s[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+')
    identifierEndingTag = re.compile('^[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+\s#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+')
    identifierSub = re.compile('^\+[a-zA-Z0-9]+$')
    identifierUnsub = re.compile('^\-[a-zA-Z0-9]+$')
    identifierDesconnect = re.compile('^##kill$')
    while True:
        message = connectionSocket.recv(1024).decode()
        if re.match(identifierSub, message):
            tag = message.split('+')[1]
            if tag in tags:
                if addr in tags[tag]:
                    connectionSocket.send(f'Already subscribed +{tag}')
                else:
                    tags[tag].append(addr)
            else:
                tags[tag] = []
                tags[tag].append(addr)
            connectionSocket.send(f'Subscribed +{tag}'.encode())
        elif re.match(identifierUnsub, message):
            tag = message.split('-')[1]
            finded = False
            if tag in tags:                                     # Procura o endereço do usuario na tag
                for addr in tags[tag]:
                    if addr in tags[tag]:                       # Se encontrado ele é removido
                        tags.pop(tag[addr])
                        connectionSocket.send(f'Unsubscribed -{tag}'.encode())
                        finded = True
                        print(tags)
                        break
                if not finded:                                  # Se não encontrado ele não esta escrito
                    connectionSocket.send(f'Not subscribed -{tag}'.encode())
            else:                                               # Caso contrario a tag n existe
                connectionSocket.send(f'Not subscribed -{tag}'.encode())
        elif re.match(identifierStartingTag, message) or re.match(identifierMiddleTag, message) or re.match(identifierEndingTag, message):
            i = 0
            findTag = message.split()
            while i < len(findTag):                 # Encontra a tag
                if findTag[i].startswith('#'):
                    break
                i += 1
            tag = findTag[i].split('#')[1]          # Salva a tag
            if tag in tags:                         # Envia a mensagem para cada endereço na tag da frase
                for addr in tags.get(tag):
                    connectionSocket.sendto(message.encode(), (addr,port))
        elif re.match(identifierDesconnect, message):
            tags = {}
            os._exit(1)
        else:
            connectionSocket.send('Invalid message'.encode())

def main():
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = int(input('Insert the port: '))

    if socket.has_dualstack_ipv6():
        serverSocket = socket.create_server(('', port), family=socket.AF_INET6, dualstack_ipv6=True)
    else:
        serverSocket = socket.create_server(('', port))
    # serverSocket.bind(('', port))
    serverSocket.listen(1)
    print('The server is ready to receive')
    while True:
        connectionSocket, addr = serverSocket.accept()                      # Aceita a conexão
        threading.Thread(target=thread, args=(connectionSocket,addr[0],port,)).start()   # Abre uma thread para o cliente

if __name__ == '__main__':
    main()

# Falta as strings de 500 bytes, reconhecer mais de 1 tag na frase e remover inscrição