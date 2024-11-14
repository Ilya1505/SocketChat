import sys
import socket
import threading

sys.path = ["", ".."] + sys.path[1:]

from settings import SERVER_PORT
from common import get_utcnow_str

# Global variable that mantain client's connections
connections = []


def handle_user_connection(connection: socket.socket, address: str) -> None:
    """
    Получаем клиентское соединение, ожидаем сообщение от пользователя
    и отправляем сообщения другим клиентам
    :param connection:
    :param address:
    :return:
    """
    while True:
        try:
            # Get client message
            msg = connection.recv(1024)  # Ожидаем сообщение от клиента

            # If no message is received, there is a chance that connection has ended
            # so in this case, we need to close connection and remove it from connections list.
            if msg:
                # Log message sent by user
                print(f'{address[0]}:{address[1]} - {msg.decode()}')

                # Build message format and broadcast to users connected on server
                msg_to_send = f'From {address[0]}:{address[1]} - {msg.decode()}'
                broadcast(msg_to_send, connection)

            # Close connection if no message was sent
            else:
                remove_connection(connection)
                break

        except Exception as e:
            print(f'Error to handle user connection: {e}')
            remove_connection(connection)
            break


def broadcast(message: str, connection: socket.socket) -> None:
    '''
        Broadcast message to all users connected to the server
    '''

    # Iterate on connections in order to send message to all client's connected
    for client_conn in connections:
        # Check if isn't the connection of who's send
        if client_conn != connection:
            try:
                # Sending message to client connection
                client_conn.send(message.encode())

            # if it fails, there is a chance of socket has died
            except Exception as e:
                print('Error broadcasting message: {e}')
                remove_connection(client_conn)


def remove_connection(conn: socket.socket) -> None:
    '''
        Remove specified connection from connections list
    '''

    # Check if connection exists on connections list
    if conn in connections:
        # Close socket connection and remove connection from connections list
        conn.close()
        connections.remove(conn)


def server() -> None:
    '''
        Main process that receive client's connections and start a new thread
        to handle their messages
    '''

    socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создание сокета

    try:
        socket_instance.bind(('', SERVER_PORT))  # Поднятие сервера
        socket_instance.listen(4)  # Установка максимального кол-ва соединений в очереди

        print(f'[INFO]  [{get_utcnow_str()}]   Server running!')

        while True:
            socket_connection, address = socket_instance.accept()  # Ожидание клиента
            print(f"[INFO]  [{get_utcnow_str()}]   New connection from {address}")
            connections.append(socket_connection)
            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()  # Запуск нового потока для обработки подключений

    except Exception as e:
        print(f'[ERROR]  [{get_utcnow_str()}]  An error has occurred when instancing socket: {e}')
    finally:
        # Если возникает исключение, чистим все соединения и закрываем коннект к серверу
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)

        socket_instance.close()


if __name__ == "__main__":
    server()
