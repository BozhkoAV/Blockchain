import sys
import socket


def create_listening_socket(node_index):
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listening_socket.bind(('127.0.0.1', 10000 + node_index))
    listening_socket.listen()
    return listening_socket


if __name__ == '__main__':
    if len(sys.argv) > 1:
        node_id = int(sys.argv[1])
    else:
        node_id = int(input("Введите номер ноды: "))
    while node_id > 3 or node_id < 1:
        node_id = int(input("Неправильный ввод. Введите номер ноды (от 1 до 3): "))

    # для каждой ноды на порте 10000+node_id необходимо будет создать слушающий сокет
    # работа не может быть начата, пока не будут созданны три ноды с разными порядковыми номерами
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            is_node_already_created = s.connect_ex(('127.0.0.1', 10000 + node_id)) == 0
        if is_node_already_created:
            node_id = int(input("Нода с таким порядковым номером уже есть. Введите номер ноды (от 1 до 3): "))
        else:
            break

    # создание слушающего сокета
    node_listening_socket = create_listening_socket(node_index=node_id)
