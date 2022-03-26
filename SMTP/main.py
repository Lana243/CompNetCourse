import base64
import sys
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from socket import *
import ssl

SMTP_HOST = "smtp.mail.ru"
SMTP_PORT = 465


def send(socket, msg):
    socket.send(msg)
    print(msg)
    print(socket.recv(1024))
    print("____________________________")



def authorize(socket):
    send(socket, 'AUTH LOGIN\r\n'.encode("utf-8"))
    with open("credentials.txt") as f:
        login = f.readline().rstrip("\n")
        pswd = f.readline().rstrip("\n")

    socket.send(base64.b64encode(login.encode('utf-8')))
    send(socket, "\r\n".encode("utf-8"))

    socket.send(base64.b64encode(pswd.encode('utf-8')))
    send(socket, "\r\n".encode('utf-8'))

    return login, pswd


def build_message(login, recipient, file):
    message = MIMEMultipart()
    message["Subject"] = "Lab message"
    message["From"] = login
    message["To"] = recipient

    path = Path(file)

    if path.suffix == ".txt":
        with open(path, "r") as f:
            msg = MIMEText(f.read(), "plain")

    if path.suffix == ".html":
        with open(path, "r") as f:
            msg = MIMEText(f.read(), "html")

    if path.suffix == ".png":
        with open(path, "rb") as f:
            msg = MIMEImage(f.read())

    message.attach(msg)
    return message.as_bytes()


def send_message(recipient, file):
    context = ssl.create_default_context()
    clientSocket = context.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname=SMTP_HOST)
    clientSocket.connect((SMTP_HOST, SMTP_PORT))
    clientSocket.recv(1024)

    send(clientSocket, 'HELO lab05\r\n'.encode("utf-8"))

    login, pswd = authorize(clientSocket)

    send(clientSocket, f'MAIL FROM: <{login}>\r\n'.encode('utf-8'))

    send(clientSocket, f'RCPT TO: <{recipient}>\r\n'.encode('utf-8'))

    send(clientSocket, 'DATA\r\n'.encode('utf-8'))

    clientSocket.send(build_message(login, recipient, file))

    send(clientSocket, '\r\n.\r\n'.encode("utf-8"))

    send(clientSocket, 'QUIT\r\n'.encode("utf-8"))

    clientSocket.close()


if __name__ == '__main__':
    recipient = sys.argv[1]
    file = sys.argv[2]
    send_message(recipient, file)

