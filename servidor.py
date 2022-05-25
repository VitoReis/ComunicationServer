from socket import *
import threading
import socket
import sys
import re

tags = {}


def thread(connectionSocket,addr,port):
    # Regex para aceitar ou não as menssagens
    identifierStartingTag = re.compile('^#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+\s[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+')
    identifierMiddleTag = re.compile('^[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+\s#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+\s[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+')
    identifierEndingTag = re.compile('^[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+\s#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+')
    identifierSub = re.compile('^\+[a-zA-Z0-9]+$')
    identifierUnsub = re.compile('^\-[a-zA-Z0-9]+$')
    identifierDesconnect = re.compile('^##kill$')
    while True:
        message = connectionSocket.recv(1024).decode()
        global tags
        if re.match(identifierSub, message):
            tag = message.split('+')[1]
            if tag in tags:
                if addr in tags[tag]:
                    print(f'Already subscribed +{tag}')
                else:
                    tags[tag].append(addr)
            else:
                tags[tag] = []
                tags[tag].append(addr)
            print(tags)
            connectionSocket.send(f'Subscribed +{tag}'.encode())
        elif re.match(identifierUnsub, message):
            tag = message.split('+')[1]
            if tag in tags:
                if addr in tags[tag]:
                    tags[tag].pop(addr)
                    connectionSocket.send(f'Unsubscribed -{tag}'.encode())
                    print(tags)
                else:
                    connectionSocket.send(f'Not subscribed -{tag}'.encode())
            else:
                connectionSocket.send('Tag does not exist'.encode())
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
            connectionSocket.send('Closing server'.encode())
            break
        else:
            connectionSocket.send('Invalid message'.encode())
        sys.exit()

def main():
    serverSocket = socket.socket(AF_INET, SOCK_STREAM)
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = int(input('Insert the port: '))
    serverSocket.bind(('', port))
    serverSocket.listen(1)
    print('The server is ready to receive')
    while True:
        connectionSocket, addr = serverSocket.accept()                      # Aceita a conexão
        threading.Thread(target=thread, args=(connectionSocket,addr[0],port,)).start()   # Abre uma thread para o cliente

if __name__ == '__main__':
    main()