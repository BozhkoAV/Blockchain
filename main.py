import sys
import socket
from blockchain import Blockchain
import json
import time


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

    while True:
        new_block = bc.create_block()
        block_generation_time = time.time()

        # значения времени, когда новый блок был сгенерирован нодами 2 и 3, передаются ноде 1
        if node_id == 2 or node_id == 3:
            # ноды 2 и 3 отправляют значения времени на слушающий сокет ноды 1
            conn_to_another_nodes_listening_sockets[0].\
                sendall(bytes(f"{node_id} {block_generation_time}", encoding="utf-8"))

        node_winner_id = 0
        if node_id == 1:
            nodes_time = []
            # нода 1 получает на слушающий сокет значения времени нод 2 и 3
            for conn in conn_to_our_listening_socket:
                node_time = conn.recv(4096)
                node_time_str = "".join(node_time.decode("utf-8"))
                nodes_time.append(node_time_str.replace("\"", ""))

            # нода 1 определяет блок какой ноды был сгенерирован раньше
            node_winner_id = 1
            for node_id_and_time in nodes_time:
                i = int(node_id_and_time.split(" ")[0])
                node_i_time = float(node_id_and_time.split(" ")[1])
                if node_i_time < block_generation_time:
                    block_generation_time = node_i_time
                    node_winner_id = i

            # нода 1 отправляет нодам 2 и 3 номер победившей ноды
            for conn in conn_to_our_listening_socket:
                conn.sendall(bytes(str(node_winner_id), encoding="utf-8"))

        # ноды 2 и 3 получают от ноды 1 номер победившей ноды
        if node_id == 2 or node_id == 3:
            node_winner_id_from_node_1 = conn_to_another_nodes_listening_sockets[0].recv(4096)
            node_winner_id = int("".join(node_winner_id_from_node_1.decode("utf-8")))

        # если нода 1 сгенерировала блок раньше всех
        if node_winner_id == 1:
            if node_id == 1:
                print(f'Node 1 created block {new_block["index"]}:')
                print(json.dumps(new_block, indent=4))
                for conn in conn_to_our_listening_socket:
                    conn.sendall(bytes(json.dumps(new_block), encoding="utf-8"))
            if node_id == 2 or node_id == 3:
                node_1_block = conn_to_another_nodes_listening_sockets[0].recv(4096)
                block_str = "".join(node_1_block.decode("utf-8"))
                new_block = json.loads(block_str)
                print(f'Node {node_id} received block {new_block["index"]} from Node 1')

        # если нода 2 сгенерировала блок раньше всех
        if node_winner_id == 2:
            if node_id == 1:
                node_2_block = conn_to_another_nodes_listening_sockets[0].recv(4096)
                block_str = "".join(node_2_block.decode("utf-8"))
                new_block = json.loads(block_str)
                print(f'Node 1 received block {new_block["index"]} from Node 2')
            if node_id == 2:
                print(f'Node 2 created block {new_block["index"]}:')
                print(json.dumps(new_block, indent=4))
                for conn in conn_to_our_listening_socket:
                    conn.sendall(bytes(json.dumps(new_block), encoding="utf-8"))
            if node_id == 3:
                node_2_block = conn_to_another_nodes_listening_sockets[1].recv(4096)
                block_str = "".join(node_2_block.decode("utf-8"))
                new_block = json.loads(block_str)
                print(f'Node 3 received block {new_block["index"]} from Node 2')

        # если нода 3 сгенерировала блок раньше всех
        if node_winner_id == 3:
            if node_id == 1 or node_id == 2:
                node_3_block = conn_to_another_nodes_listening_sockets[1].recv(4096)
                block_str = "".join(node_3_block.decode("utf-8"))
                new_block = json.loads(block_str)
                print(f'Node {node_id} received block {new_block["index"]} from Node 3')
            if node_id == 3:
                print(f'Node 2 created block {new_block["index"]}:')
                print(json.dumps(new_block, indent=4))
                for conn in conn_to_our_listening_socket:
                    conn.sendall(bytes(json.dumps(new_block), encoding="utf-8"))

        bc.add_block(new_block)
