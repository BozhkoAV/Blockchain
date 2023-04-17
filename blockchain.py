import random
import string
import hashlib
import json
import math


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

    def create_block(self):
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
                new_block["nonce"] = self.change_nonce(new_block["nonce"])

            return new_block

    def change_nonce(self, nonce):
        if self.node_index % 3 == 1:
            return random.randint(0, 1000000)

        if self.node_index % 3 == 2:
            if nonce < 2:
                return nonce + 1
            else:
                prev_fib = round(nonce / ((1 + math.sqrt(5)) / 2.0))
                new_fib = prev_fib + nonce
                if new_fib < 1000000:
                    return new_fib
                else:
                    return random.randint(0, 1000000)

        return nonce + 1

    def add_block(self, block):
        if len(self.chain) >= 0:
            self.chain.append(block)


def get_hash(block):
    block_string = f'{block["index"]}{block["prev_hash"]}{block["data"]}{block["nonce"]}'.encode()
    new_hash = hashlib.sha256(block_string).hexdigest()
    if new_hash[-4:] == "0000":
        block["hash"] = new_hash
        return True
    else:
        return False
