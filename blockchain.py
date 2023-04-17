import random
import string
import hashlib
import json


class Blockchain:
    def __init__(self, node_index):
        self.chain = []
        self.node_index = node_index

    def add_genesis(self):
        block = {
            "index": 0,
            "prev_hash": "0000",
            "hash": "",
            "data": ''.join((random.choice(string.ascii_letters + string.digits)) for _ in range(256)),
            "nonce": 0
        }

        while not (get_hash(block)):
            block["nonce"] += 1

        self.chain.append(block)
        print("Genesis created:")
        print(json.dumps(block, indent=4))
        print()

    def add_block(self):
        if len(self.chain) > 0:
            prev_block = self.chain[-1]

            new_block = {
                "index": prev_block["index"] + 1,
                "prev_hash": prev_block["hash"],
                "hash": "",
                "data": ''.join((random.choice(string.ascii_letters + string.digits)) for _ in range(256)),
                "nonce": 0
            }

            while not (get_hash(new_block)):
                new_block["nonce"] += 1

            print(f'Node {self.node_index} created block {new_block["index"]}:')
            print(json.dumps(new_block, indent=4))
            print()
            self.chain.append(new_block)


def get_hash(block):
    block_string = f'{block["index"]}{block["prev_hash"]}{block["data"]}{block["nonce"]}'.encode()
    new_hash = hashlib.sha256(block_string).hexdigest()
    if new_hash[-4:] == "0000":
        block["hash"] = new_hash
        return True
    else:
        return False
