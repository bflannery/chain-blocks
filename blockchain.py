from time import time, sleep
import json
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import *
from datetime import datetime


class Blockchain:
    def __init__(self):
        self.chain = [self.add_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 3
        self.block_size = 10
        self.miner_reward = 50

    @staticmethod
    def add_genesis_block():
        transactions = []
        transaction = Transaction("me", "you", 10)
        transactions.append(transaction)

        now = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        genesis_block = Block(transactions, now, 0)

        genesis_block.prev = "None"
        return genesis_block

    @staticmethod
    def generate_keys():
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)

        print(public_key.decode('ASCII'))
        return key.publickey().export_key().decode('ASCII')

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, block):
        if len(self.chain) > 0:
            block.prev = self.get_last_block().hash
        else:
            block.prev = "none"
        self.chain.append(block)

    def mine_pending_transactions(self, miner):
        pending_transactions_count = len(self.pending_transactions)

        if pending_transactions_count <= 1:
            print("Not enough transactions to mine! (Must be > 1)")
            return False
        else:
            for i in range(0, pending_transactions_count, self.block_size):
                end = i + self.block_size

                if i >= pending_transactions_count:
                    end = pending_transactions_count

                transaction_slice = self.pending_transactions[i:end]

                new_block = Block(transaction_slice, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), len(self.chain))
                # print(type(self.getLastBlock()))

                hash_value = self.get_last_block().hash
                new_block.prev = hash_value
                new_block.mine_block(self.difficulty)
                self.chain.append(new_block)

            print("Mining Transactions Success!")

            pay_miner = Transaction("Miner Rewards", miner, self.miner_reward)
            self.pending_transactions = [pay_miner]
        return True

    def add_transaction(self, sender, receiver, amount, key_string, sender_key):
        key_byte = key_string.encode("ASCII")
        sender_key_byte = sender_key.encode("ASCII")

        # print(type(key_byte), key_byte)

        key = RSA.import_key(key_byte)
        sender_key = RSA.import_key(sender_key_byte)

        if not sender or not receiver or not amount:
            print("Transaction Error: Invalid data.")
            return False

        transaction = Transaction(sender, receiver, amount)

        transaction.sign_transaction(key, sender_key)

        if not transaction.is_valid_transaction():
            print("Transaction Error: Invalid data.")
            return False

        self.pending_transactions.append(transaction)

        return len(self.chain) + 1

    def chain_json_encode(self):
        blocks_json = []
        for block in self.chain:
            block_json = {
                'hash': block.hash,
                'index': block.index,
                'prev': block.prev,
                'time': block.time,
                'nonce': block.nonce,
                # 'gym': block.gym
            }

            transactions_json = []
            transaction_json = {}
            for transaction in block.transactions:
                transaction_json['time'] = transaction.time
                transaction_json['sender'] = transaction.sender
                transaction_json['receiver'] = transaction.receiver
                transaction_json['amount'] = transaction.amount
                transaction_json['hash'] = transaction.hash
                transactions_json.append(transaction_json)

            block_json['transactions'] = transactions_json
            blocks_json.append(block_json)

        return blocks_json

    @staticmethod
    def chain_json_decode(chain_json):
        chain = []
        for block_json in chain_json:

            transactions = []
            for transaction_json in block_json['transactions']:
                transaction = Transaction(
                    transaction_json['sender'], transaction_json['receiver'], transaction_json['amount']
                )
                transaction.time = transaction_json['time']
                transaction.hash = transaction_json['hash']
                transactions.append(transaction)

            block = Block(transactions, block_json['time'], block_json['index'])
            block.hash = block_json['hash']
            block.prev = block_json['prev']
            block.nonce = block_json['nonce']
            # block.gym = block_json['gym']

            chain.append(block)
        return chain


class Block:
    def __init__(self, transactions, created_at, index):
        self.index = index
        self.transactions = transactions
        self.time = created_at
        self.prev = ''
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        hash_transactions = ""
        for transaction in self.transactions:
            hash_transactions += transaction.hash

        hash_string = str(self.time) + hash_transactions + self.prev + str(self.nonce)
        hash_encoded = json.dumps(hash_string, sort_keys=True).encode()
        return hashlib.sha256(hash_encoded).hexdigest()

    def mine_block(self, difficulty):
        arr = []
        for i in range(0, difficulty):
            arr.append(i)

        arr_str = map(str, arr)
        hash_puzzle = ''.join(arr_str)

        while self.hash[0:difficulty] != hash_puzzle:
            self.nonce += 1
            self.hash = self.calculate_hash()

            print("Nonce: ", self.nonce)
            print("Hash Attempt: ", self.hash)
            print("Hash We Want: ", hash_puzzle, "...")
            print("")
            sleep(0.8)

        print("Block Mined! Nonce to Solve Proof of Work:", self.nonce)

        return True


class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = time()
        self.hash = self.calculate_hash()
        self.signature = ""

    def calculate_hash(self):
        hash_string = self.sender + self.receiver + str(self.amount) + str(self.time)
        hash_encoded = json.dumps(hash_string, sort_keys=True).encode()
        return hashlib.sha256(hash_encoded).hexdigest()

    def is_valid_transaction(self):
        if self.hash != self.calculate_hash():
            return False
        if self.sender == self.receiver:
            return False
        if self.sender == "Miner Rewards":
            # security : unfinished
            return True
        if not self.signature or len(self.signature) == 0:
            print("No Signature!")
            return False
        return True
    # needs work!

    def sign_transaction(self, key, sender_key):
        if self.hash != self.calculate_hash():
            print("transaction tampered error")
            return False

        if str(key.publickey().export_key()) != str(sender_key.publickey().export_key()):
            print("Transaction attempt to be signed from another wallet")
            return False

        # h = MD5.new(self.hash).digest()

        pkcs1_15.new(key)

        self.signature = "made"

        # print(key.sign(self.hash, ""))

        print("made signature!")
        return True
