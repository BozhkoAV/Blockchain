import sys
import socket
from blockchain import Blockchain
import json


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

    # список сокетов, подключенных к слушающему сокету этой ноды
    conn_to_our_listening_socket = []
    # список сокетов, используемых этой нодой для подключения к слушающим сокетам других нод
    conn_to_another_nodes_listening_sockets = []

    if node_id == 1:
        # создание слушающего сокета для первой ноды
        node_listening_socket = create_listening_socket(node_index=1)
        # подключение двух сокетов других нод к слушающему сокету первой ноды
        while len(conn_to_our_listening_socket) < 2:
            conn, _ = node_listening_socket.accept()
            conn_to_our_listening_socket.append(conn)

        # подключение к слушающему сокету второй ноды
        node_2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                node_2_socket.connect(('127.0.0.1', 10002))
                conn_to_another_nodes_listening_sockets.append(node_2_socket)
                break
            except ConnectionRefusedError:
                continue

        # подключение к слушающему сокету третьей ноды
        node_3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                node_3_socket.connect(('127.0.0.1', 10003))
                conn_to_another_nodes_listening_sockets.append(node_3_socket)
                break
            except ConnectionRefusedError:
                continue

    if node_id == 2:
        node_1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                node_1_socket.connect(('127.0.0.1', 10001))
                conn_to_another_nodes_listening_sockets.append(node_1_socket)
                break
            except ConnectionRefusedError:
                continue

        node_listening_socket = create_listening_socket(node_index=2)
        while len(conn_to_our_listening_socket) < 2:
            conn, _ = node_listening_socket.accept()
            conn_to_our_listening_socket.append(conn)

        node_3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                node_3_socket.connect(('127.0.0.1', 10003))
                conn_to_another_nodes_listening_sockets.append(node_3_socket)
                break
            except ConnectionRefusedError:
                continue

    if node_id == 3:
        node_1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                node_1_socket.connect(('127.0.0.1', 10001))
                conn_to_another_nodes_listening_sockets.append(node_1_socket)
                break
            except ConnectionRefusedError:
                continue

        node_2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                node_2_socket.connect(('127.0.0.1', 10002))
                conn_to_another_nodes_listening_sockets.append(node_2_socket)
                break
            except ConnectionRefusedError:
                continue

        node_listening_socket = create_listening_socket(node_index=3)
        while len(conn_to_our_listening_socket) < 2:
            conn, _ = node_listening_socket.accept()
            conn_to_our_listening_socket.append(conn)

    # создание цепи для ноды
    bc = Blockchain(node_index=node_id)

    if node_id == 1:
        print("Node 1 generated genesis")
        bc.add_genesis()
        # Нода 1 посылает генезис остальным нодам
        for conn in conn_to_our_listening_socket:
            conn.sendall(bytes(json.dumps(bc.chain[0]), encoding="utf-8"))

    if node_id == 2 or node_id == 3:
        print(f"Node {node_id} received genesis from Node 1")
        # Нода 2 и 3 получают генезис по сокетам подключённым к слушающему порту ноды 1
        node_1_genesis = conn_to_another_nodes_listening_sockets[0].recv(4096)
        genesis_str = "".join(node_1_genesis.decode("utf-8"))
        bc.add_block(json.loads(genesis_str))
        print(bc.chain)
