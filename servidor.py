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
    identifierText = re.compile('^[a-zA-Z0-9\s,.?!:;+\-*/=@#$%()[\]{}]+$')
    identifierSub = re.compile('^\+[a-zA-Z0-9]+$')
    identifierUnsub = re.compile('^\-[a-zA-Z0-9]+$')
    identifierDesconnect = re.compile('^#quit$')
    identifierKill = re.compile('^##kill$')
    while True:
        message = connectionSocket.recv(500).decode()
        if re.match(identifierSub, message):
            tag = message.split('+')[1]
            if tag in tags:
                if addr in tags[tag]:
                    connectionSocket.send(f'Already subscribed +{tag}'.encode())
                else:
                    tags[tag].append(addr)
            else:
                tags[tag] = []
                tags[tag].append(addr)
                connectionSocket.send(f'Subscribed +{tag}'.encode())
        elif re.match(identifierUnsub, message):
            addrList = []
            tag = message.split('-')[1]
            finded = False
            if tag in tags:                             # Verifica se a tag existe
                for addres in tags[tag]:
                    if addres != addr:                  # Adiciona todos os endereços em uma lista exceto o do usuario
                        addrList.append(addr)
                    else:
                        finded = True
                if not finded:                                  # Se não encontrado ele não esta escrito
                    connectionSocket.send(f'Not subscribed -{tag}'.encode())
                else:
                    tags[tag] = addrList
                    connectionSocket.send(f'Unsubscribed -{tag}'.encode())
            else:                                               # Caso contrario a tag n existe
                connectionSocket.send(f'Not subscribed -{tag}'.encode())
        elif re.match(identifierStartingTag, message) or \
             re.match(identifierMiddleTag, message) or \
             re.match(identifierEndingTag, message):
            i = 0
            tagList = []
            addrs = []
            findTag = message.split()
            while i < len(findTag):                         # Encontra as tags da mensagem e salva em uma lista
                if findTag[i].startswith('#'):
                    tagList.append(findTag[i].split('#')[1])
                i += 1
            for t in tags:                                  # Salva os endereços inscritos nas tags da mensagem enviada
                if t in tagList:
                    for a in tags.get(t):
                        if a in addrs or a == addr:
                            continue
                        else:
                            addrs.append(addr)
            for addresses in addrs:                         # Envia a mensagem para os endereços salvos na lista
                connectionSocket.sendto(message.encode(), (addresses, port))
        elif re.match(identifierDesconnect, message):
            list = []
            for t in tags:                      # Encontra as tags que o cliente esta inscrito e o remove da lista
                if addr in tags[t]:
                    for a in tags[t]:
                            if a == addr:
                                continue
                            else:
                                list.append(a)
                    tags[t] = list
            break                               # Sai do loop da thread para finaliza-la
        elif re.match(identifierKill, message):
            tags = {}
            os._exit(1)
        elif re.match(identifierText, message):         # Reconhece um texto sem tags e responde o cliente que recebeu
            connectionSocket.send('Message received'.encode())
        else:                                           # Reconhece um texto invalido e responde ao cliente
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
    serverSocket.listen(1)
    print('The server is ready to receive')
    while True:
        connectionSocket, addr = serverSocket.accept()
        threading.Thread(target=thread, args=(connectionSocket,addr[0],port,)).start()

if __name__ == '__main__':
    main()