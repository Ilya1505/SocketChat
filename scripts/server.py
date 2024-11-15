import sys
import socket
import threading

sys.path = ["", ".."] + sys.path[1:]

from settings import SERVER_PORT, MAX_COUNT_CLIENT
from common import get_utcnow_str

# Пул всех соединений с сервером
connections = []


def handle_user_connection(connection: socket.socket, address: str) -> None:
    """
    Ожидаем сообщение от пользователя
    и отправляем сообщения другим клиентам
    :param connection:
    :param address:
    :return:
    """
    while True:
        try:
            msg = connection.recv(1024)  # Ожидаем сообщение от клиента

            if msg:
                # Вывод полученного сообщения от клиента
                print(f'[INFO]   [{get_utcnow_str()}]  {address[0]}:{address[1]} - {msg.decode()}')

                # Формирование сообщения для всех клиентов, кроме отправителя
                msg_to_send = f'From {address[0]}:{address[1]} - {msg.decode()}'
                broadcast(msg_to_send, connection)

            # Закрытие соединения в случае отсутствие msg
            else:
                remove_connection(connection)
                break

        except Exception as e:
            print(f'[ERROR]   [{get_utcnow_str()}]  Error to handle user connection: {e}')
            remove_connection(connection)
            break


def broadcast(message: str, connection: socket.socket) -> None:
    """
    Широковещательная рассылка сообщений всем клиентам
    за исключением отправителя
    :param message:
    :param connection:
    :return:
    """

    for client_conn in connections:
        if client_conn != connection:
            try:
                client_conn.send(message.encode())  # Отправка сообщения

            # В случае ошибки отправки, вывод уведомления и закрытие соединения
            except Exception as e:
                print(f'[ERROR]   [{get_utcnow_str()}]  Error broadcasting message: {e}')
                remove_connection(client_conn)


def remove_connection(conn: socket.socket) -> None:
    """
    Удаление необходимого соединения
    :param conn:
    :return:
    """

    if conn in connections:
        conn.close()
        connections.remove(conn)


def server() -> None:
    """
    Главный процесс системы
    Принимает клиентские соединения
    и запускает в новом потоке обработчик событий
    :return:
    """

    socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создание сокета

    try:
        socket_instance.bind(('', SERVER_PORT))  # Поднятие сервера
        socket_instance.listen(MAX_COUNT_CLIENT)  # Установка максимального кол-ва соединений в очереди

        print(f'[INFO]  [{get_utcnow_str()}]   Server running!')

        while True:
            socket_connection, address = socket_instance.accept()  # Ожидание клиента
            print(f"[INFO]  [{get_utcnow_str()}]   New connection from {address}")
            connections.append(socket_connection)
            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()  # Запуск нового потока для обработки подключений

    except Exception as e:
        print(f'[ERROR]  [{get_utcnow_str()}]   An error has occurred when instancing socket: {e}')
    finally:
        # Если возникает исключение, чистим все соединения и закрываем коннект к серверу
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)

        socket_instance.close()


if __name__ == "__main__":
    server()
