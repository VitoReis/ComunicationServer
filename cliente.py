from socket import *
import re
import socket
import sys
import threading

def thread(clientSocketRecv):
    while True:
        message = clientSocketRecv.recv(1024).decode()
        # connection, addr = clientSocket.accept()
        # message = connection.recv(1024)
        print(message)
        clientSocketRecv.close()



def main():
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    else:
        # ip = input('Type the server IP: ')
        # port = int(input('Type the server port: '))
        ip = 'localhost'
        port = 5000

    #REGEX FOR CLIENT MESSAGES:
    identifierStartingTag = re.compile('^#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+\s[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+')
    identifierMidleTag = re.compile('^[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+\s#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+\s[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+')
    identifierEndingTag = re.compile('^[a-zA-Z0-9,.?!:;+\-*/=@#$%()[\]{}\s]+\s#[a-zA-Z0-9,.?!:;+\-*/=@$%()[\]{}]+')
    identifierSub = re.compile('^\+[a-zA-Z0-9]+$')
    identifierUnsub = re.compile('^\-[a-zA-Z0-9]+$')
    identifierDesconnect = re.compile('^##kill$')

    clientSocket = socket.socket(AF_INET, SOCK_STREAM)

    # clientSocket.bind(('localhost', port))
    # clientSocket.listen(1)

    clientSocket.connect((ip, port))

    # clientSocketRecv, addr = clientSocket.accept()

    threading.Thread(target=thread, args=(clientSocket,)).start()       # Abre uma thread para o cliente
    while True:
        message = input('Insert your message: ')
        if re.match(identifierSub, message):
            message = message.encode()
            clientSocket.send(message)
        elif re.match(identifierUnsub, message):
            message = message.encode()
            clientSocket.send(message)
        elif re.match(identifierStartingTag, message) or re.match(identifierMidleTag, message) or re.match(identifierEndingTag, message):
            message = message.encode()
            clientSocket.send(message)
        elif re.match(identifierDesconnect, message):
            message = message.encode()
            clientSocket.send(message)
            break #ou quit()
        else:
            print('Mensagem invalida')
    clientSocket.close()

if __name__ == '__main__':
    main()