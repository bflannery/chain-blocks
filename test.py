from blockchain import *
from time import time
import pprint

pp = pprint.PrettyPrinter(indent=4)


def test_blockchain_adds_blocks():
    blockchain = Blockchain()
    transactions = []

    block1 = Block(transactions, time(), 0)
    blockchain.add_block(block1)

    block2 = Block(transactions, time(), 1)
    blockchain.add_block(block2)

    block3 = Block(transactions, time(), 2)
    blockchain.add_block(block3)

    assert len(blockchain.chain) == 4
    last_block = blockchain.get_last_block()
    assert last_block.hash == block3.hash


# def test_blockchain_test_generate_keys():
#     blockchain = Blockchain()
#
#     key = blockchain.generate_keys()
#
#     # blockchain.add_transaction("Brian", "Sophie Lammers", 10, key, key)
#
#     pp.pprint(blockchain.chain_json_encode())
#     print("Length: ", len(blockchain.chain))
#
#
# def test_blockchain_block_mining():
#     blockchain = Blockchain()
#     transaction = Transaction("Brian Flannery", "Sophie Lammers", 10)
#
#     blockchain.pending_transactions.append(transaction)
#
#     blockchain.mine_pending_transactions("Piper")
#
#     pp.pprint(blockchain.chain_json_encode())
#     print("Length: ", len(blockchain.chain))


