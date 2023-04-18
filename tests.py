import unittest
import json
from blockchain import Blockchain


def valid_block(block):
    return block["hash"][-4:] == "0000"


def valid_chain(chain):
    is_valid = True
    for block in chain:
        is_valid = valid_block(block)
        if not is_valid:
            break
    return is_valid


class TestBlockchain(unittest.TestCase):
    def test_genesis_generation(self):
        for i in range(9):
            bc = Blockchain(node_index=i % 3 + 1)
            bc.add_genesis()
            self.assertTrue(valid_chain(bc.chain))

    def test_block_generation(self):
        for i in range(9):
            bc = Blockchain(node_index=i % 3 + 1)
            bc.add_genesis()
            for j in range(3):
                new_block = bc.create_block()
                print('New block created:')
                print(json.dumps(new_block, indent=4))
                print()
                self.assertTrue(valid_block(new_block))

    def test_chain_generation(self):
        for i in range(9):
            bc = Blockchain(node_index=i % 3 + 1)
            bc.add_genesis()
            for j in range(10):
                new_block = bc.create_block()
                bc.add_block(new_block)
                print('New block created:')
                print(json.dumps(new_block, indent=4))
                print()
            self.assertTrue(valid_chain(bc.chain))


if __name__ == "__main__":
    unittest.main()
