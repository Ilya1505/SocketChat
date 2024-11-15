import sys
import socket
import threading

sys.path = ["", ".."] + sys.path[1:]

from settings import SERVER_HOST, SERVER_PORT
from common import get_utcnow_str


def handle_messages(connection: socket.socket):
    """
    Прием сообщений от сервера и отображение их на дисплей
    :param connection:
    :return:
    """

    while True:
        try:
            msg = connection.recv(1024)  # Ожидание сообщения от сервера

            if msg:
                print(f"[INFO]  [{get_utcnow_str()}]   {msg.decode()}")  # Декодирование сообщения
            else:
                connection.close()
                break

        except Exception as e:
            print(f'[ERROR]  [{get_utcnow_str()}]   Error handling message from server: {e}')
            connection.close()
            break


def client() -> None:
    """
    Главный процесс, подключается к серверу,
    ожидает ввод текста юзера
    и запускает новый поток приема сообщений от сервера
    :return:
    """

    socket_instance = socket.socket()  # Создание сокета

    try:
        socket_instance.connect((SERVER_HOST, SERVER_PORT))  # Подключение к серверу

        threading.Thread(target=handle_messages, args=[socket_instance]).start()  # Создание потока на прием сообщений

        print(f'[INFO]  [{get_utcnow_str()}]   Connected to chat!')

        # Read user's input until it quit from chat and close connection
        while True:
            msg = input()

            if msg == 'exit':
                break

            socket_instance.send(msg.encode())  # Кодирование текста в байты перед отправкой

        socket_instance.close()

    except Exception as e:
        print(f'[ERROR]  [{get_utcnow_str()}]   Error connecting to server socket {e}')
        socket_instance.close()


if __name__ == "__main__":
    client()
