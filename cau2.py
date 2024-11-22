import hashlib
import json
import time
import requests

class Block:
    def __init__(self, index, timestamp, transactions, proof, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Tính toán hash của block dựa trên các giá trị index, timestamp, transactions, proof và previous_hash
        """
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'proof': self.proof,
            'previous_hash': self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        # Tạo khối genesis (khối đầu tiên)
        self.new_block(proof=100, previous_hash='1')

    def new_block(self, proof, previous_hash=None):
        """
        Tạo một khối mới và thêm vào chuỗi
        """
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash or self.hash(self.chain[-1])  # Hash của khối trước
        )
        self.current_transactions = []  # Reset danh sách giao dịch
        self.chain.append(block)
        return block

    def new_transaction(self):
        """
        Tạo một giao dịch mới, trong trường hợp này không yêu cầu người dùng nhập thông tin
        """
        # Giao dịch rỗng, không cần yêu cầu người dùng nhập
        self.current_transactions.append({
            'sender': 'sender',
            'recipient': 'recipient',
            'amount': 0
        })
        return self.last_block.index + 1

    @property
    def last_block(self):
        """
        Lấy khối cuối cùng trong chuỗi blockchain
        """
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Tạo SHA-256 hash cho một block
        """
        block_string = json.dumps({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': block.transactions,
            'proof': block.proof,
            'previous_hash': block.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Thuật toán Proof of Work: Tìm một số để hash của nó có 4 chữ số 0 đầu tiên
        """
        last_proof = last_block.proof
        last_hash = self.hash(last_block)
        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Xác minh tính hợp lệ của Proof of Work
        """
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def valid_chain(self, chain):
        """
        Xác thực chuỗi blockchain
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Kiểm tra hash của block trước đó
            if block.previous_hash != self.hash(last_block):
                return False
            # Kiểm tra proof of work
            if not self.valid_proof(last_block.proof, block.proof, self.hash(last_block)):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        Thuật toán đồng thuận: Thay thế chuỗi bằng chuỗi dài nhất trong mạng
        """
        neighbors = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

# Khởi tạo blockchain
blockchain = Blockchain()

def create_blockchain():
    print("Khối Genesis đã được tạo:")
    print_block(blockchain.last_block)  # In ra thông tin khối genesis
    while True:
        user_input = input("Nhập 'y' để tạo block mới, hoặc bất kỳ ký tự nào khác để dừng: ")
        if user_input.lower() == 'y':
            mine_block()
        else:
            print("Dừng tạo block.")
            break

def mine_block():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)
    blockchain.new_transaction()  # Tự động thêm một giao dịch rỗng
    new_block = blockchain.new_block(proof)
    print("Block mới đã được tạo thành công!")
    print_block(new_block)  # In ra thông tin của block vừa tạo

def print_block(block):
    """
    In thông tin của một block
    """
    print(json.dumps({
        'index': block.index,
        'timestamp': block.timestamp,
        'transactions': block.transactions,
        'proof': block.proof,
        'previous_hash': block.previous_hash,
        'hash': block.hash
    }, indent=4))

if __name__ == "__main__":
    # Cho phép tạo block
    create_blockchain()
