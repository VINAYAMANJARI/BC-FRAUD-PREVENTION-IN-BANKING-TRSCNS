# # blockchain.py
# # import hashlib
# # import time
# # import json
# # import os

# # class Block:
# #     def __init__(self, index, timestamp, data, previous_hash=''):
# #         self.index = index
# #         self.timestamp = timestamp
# #         self.data = data
# #         self.previous_hash = previous_hash
# #         self.hash = self.calculate_hash()

# #     def calculate_hash(self):
# #         sha = hashlib.sha256()
# #         sha.update(
# #             str(self.index).encode('utf-8') +
# #             str(self.timestamp).encode('utf-8') +
# #             str(self.data).encode('utf-8') +
# #             str(self.previous_hash).encode('utf-8')
# #         )
# #         return sha.hexdigest()

# #     def to_dict(self):
# #         return {
# #             'index': self.index,
# #             'timestamp': self.timestamp,
# #             'data': self.data,
# #             'hash': self.hash,
# #             'previous_hash': self.previous_hash
# #         }

# #     @staticmethod
# #     def from_dict(block_data):
# #         block = Block(
# #             block_data['index'],
# #             block_data['timestamp'],
# #             block_data['data'],
# #             block_data['previous_hash']
# #         )
# #         block.hash = block_data['hash']
# #         return block

# # class Blockchain:
# #     def __init__(self, filepath='blockchain.json'):
# #         self.filepath = filepath
# #         self.chain = []
# #         self.transactions = set()
# #         self.load_chain()

# #     def create_genesis_block(self):
# #         return Block(0, time.time(), "Genesis Block", "0")

# #     def get_latest_block(self):
# #         return self.chain[-1]

# #     def add_block(self, data):
# #         if data in self.transactions:
# #             return False  # Duplicate transaction
# #         new_block = Block(len(self.chain), time.time(), data, self.get_latest_block().hash)
# #         self.chain.append(new_block)
# #         self.transactions.add(data)
# #         self.save_chain()
# #         return True

# #     def is_chain_valid(self):
# #         for i in range(1, len(self.chain)):
# #             current = self.chain[i]
# #             prev = self.chain[i - 1]
# #             if current.hash != current.calculate_hash():
# #                 return False
# #             if current.previous_hash != prev.hash:
# #                 return False
# #         return True

# #     def save_chain(self):
# #         with open(self.filepath, 'w') as f:
# #             json.dump([block.to_dict() for block in self.chain], f, indent=4)

# #     def load_chain(self):
# #         if not os.path.exists(self.filepath):
# #             self.chain.append(self.create_genesis_block())
# #             self.save_chain()
# #         else:
# #             with open(self.filepath, 'r') as f:
# #                 blocks = json.load(f)
# #                 self.chain = [Block.from_dict(block) for block in blocks]
# #                 self.transactions = set(block.data for block in self.chain if block.index != 0)


# import time
# import hashlib
# import time

# class Block:
#     def __init__(self, index, timestamp, data, user_id, previous_hash=''):
#         self.index = index
#         self.timestamp = timestamp
#         self.data = data
#         self.user_id = user_id
#         self.previous_hash = previous_hash
#         self.hash = self.calculate_hash()

#     def calculate_hash(self):
#         sha = hashlib.sha256()
#         sha.update(
#             str(self.index).encode('utf-8') +
#             str(self.timestamp).encode('utf-8') +
#             str(self.data).encode('utf-8') +
#             str(self.previous_hash).encode('utf-8') +
#             str(self.user_id).encode('utf-8')  # Include user_id in hash calculation
#         )
#         return sha.hexdigest()

#     def to_dict(self):
#         return {
#             'index': self.index,
#             'timestamp': self.timestamp,
#             'data': self.data,
#             'user_id': self.user_id,  # Include user_id in dict representation
#             'hash': self.hash,
#             'previous_hash': self.previous_hash
#         }

#     @staticmethod
#     def from_dict(block_data):
#         return Block(
#             block_data['index'],
#             block_data['timestamp'],
#             block_data['data'],
#             block_data['user_id'],  # Retrieve user_id from block_data
#             block_data['previous_hash']
#         )

# class Blockchain:
#     def __init__(self):
#         self.chain = []
#         self.transactions = set()
#         self.create_genesis_block()  # Create the genesis block during initialization

#     def create_genesis_block(self):
#         # Create the first block in the chain (the genesis block)
#         genesis_block = Block(0, time.time(), "Genesis Block", 0, "0")
#         self.chain.append(genesis_block)

#     def get_latest_block(self):
#         return self.chain[-1]

#     def add_block(self, data, user_id):
#         if data in self.transactions:
#             return False  # Duplicate transaction
#         new_block = Block(len(self.chain), time.time(), data, user_id, self.get_latest_block().hash)
#         self.chain.append(new_block)
#         self.transactions.add(data)
#         return True

#     def is_chain_valid(self):
#         for i in range(1, len(self.chain)):
#             current = self.chain[i]
#             prev = self.chain[i - 1]
#             if current.hash != current.calculate_hash():
#                 return False
#             if current.previous_hash != prev.hash:
#                 return False
#         return True

# blockchain.py
import time
import hashlib

class Block:
    def __init__(self, index, timestamp, data, user_id, previous_hash=''):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.user_id = user_id  # Associate block with a user
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update(
            str(self.index).encode('utf-8') +
            str(self.timestamp).encode('utf-8') +
            str(self.data).encode('utf-8') +
            str(self.user_id).encode('utf-8') +  # Include user_id in hash calculation
            str(self.previous_hash).encode('utf-8')
        )
        return sha.hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'user_id': self.user_id,  # Include user_id in dictionary representation
            'hash': self.hash,
            'previous_hash': self.previous_hash
        }

    @staticmethod
    def from_dict(block_data):
        user_id = block_data.get('user_id', 0)  # Default to 0 if not found
        return Block(
            block_data['index'],
            block_data['timestamp'],
            block_data['data'],
            user_id,  # Use the retrieved or default user_id
            block_data['previous_hash']
        )

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = set()
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), "Genesis Block", 0, "0")  # Genesis block with user_id=0
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data, user_id):
        if data in self.transactions:
            return False  # Duplicate transaction
        new_block = Block(len(self.chain), time.time(), data, user_id, self.get_latest_block().hash)
        self.chain.append(new_block)
        self.transactions.add(data)
        return True

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != prev.hash:
                return False
        return True
