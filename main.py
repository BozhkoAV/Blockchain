import sys
from blockchain import Blockchain

if __name__ == '__main__':
    if len(sys.argv) > 1:
        node_id = int(sys.argv[1])
    else:
        node_id = int(input("Введите номер ноды: "))
    while node_id > 3 or node_id < 1:
        node_id = int(input("Неправильный ввод. Введите номер ноды (от 1 до 3): "))

    bc = Blockchain(node_index=node_id)
    bc.add_genesis()
