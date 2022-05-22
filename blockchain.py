from transaction import *


class BlockChain(object):
    """ Main BlockChain class """

    def __init__(self, nodes=set()):
        self.chain = []
        self.current_transactions = []
        self.candidates = []
        self.voters = []
        self.nodes = nodes
        self.started_voting = False
        self.ended_voting = False

        self.resolve_conflicts()
        self.candidates.append({
            "name": "Candidate1",
            "wallet_address": "Candidate1"
        })
        # create the genesis block
        if len(self.chain) == 0:
            private_key = RSA.generate(2048)
            f = open('private.pem', 'wb')
            f.write(private_key.export_key('PEM'))
            f.close()

            public_key = private_key.publickey().export_key()
            self.admin = public_key
            self.new_block(previous_hash=1)
        else:
            self.admin = self.chain[0]["admin"].encode()

    @staticmethod
    def hash(block):
        # hashes a block
        # also make sure that the transactions are ordered otherwise we will have insonsistent hashes!
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def new_block(self, previous_hash=None):
        # creates a new block in the blockchain
        block = {
            'admin': self.admin.decode("utf-8"),
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'voters': self.voters,
            'candidates': self.candidates,
            'transactions': self.current_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'started_voting': self.started_voting,
            'ended_voting': self.ended_voting,
        }

        # reset the current list of transactions
        self.voters = []
        self.candidates = []
        self.current_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        # returns last block in the chain
        return self.chain[-1]

    @staticmethod
    def validate_signature(public_key: bytes, signature: bytes, data: bytes):
        public_key_object = RSA.import_key(public_key)
        data_hash = SHA256.new(data)
        pkcs1_15.new(public_key_object).verify(data_hash, signature)

    def new_transaction(self, transaction: Transaction):
        # adds a new transaction into the list of transactions
        # these transactions go into the next mined block
        if not self.started_voting and self.ended_voting:
            return False, "The vote is not started or ended"

        current_voter = None

        for voter in self.get_all_voters():
            if voter['wallet_address'] == transaction.sender_address:
                current_voter = voter
                break

        if current_voter is None:
            return False, "This kind of voter is not present"

        if current_voter['voted']:
            return False, "This voter has already voted"

        current_candidate = None
        for candidate in self.get_all_candidates():
            if candidate['wallet_address'] == transaction.receiver_address:
                current_candidate = candidate
                break

        if current_candidate is None:
            return False, "Candidate is not present in the given vote"

        try:
            signature_byte = binascii.unhexlify(transaction.signature)
        except:
            signature_byte = transaction.signature

        self.validate_signature(voter['public_key'], signature_byte, transaction.generate_data())

        self.current_transactions.append({
            "sender": transaction.sender_address,
            "receiver": transaction.receiver_address
        })

        self.mine()

        return True, None

    def new_candidate(self, name, signature):
        if self.started_voting:
            return -1;

        signature_byte = binascii.unhexlify(signature)
        self.validate_signature(self.admin.decode('utf-8'), signature_byte, name.encode('utf-8'))

        private_key = RSA.generate(2048)
        public_key = private_key.publickey().export_key()
        hash_1 = self.calculate_hash(public_key, hash_function="sha256")
        hash_2 = self.calculate_hash(hash_1, hash_function="ripemd160")
        wallet_address = base58.b58encode(hash_2)

        self.candidates.append({
            "name": name,
            "wallet_address": wallet_address.decode('utf-8')
        })

        self.mine()

        return wallet_address.decode('utf-8')

    @staticmethod
    def calculate_hash(data, hash_function: str = "sha256"):
        if type(data) == str:
            data = bytearray(data, "utf-8")
        if hash_function == "sha256":
            h = SHA256.new()
            h.update(data)
            return h.hexdigest()
        if hash_function == "ripemd160":
            h = RIPEMD160.new()
            h.update(data)
            return h.hexdigest()

    def new_voter(self):
        if self.started_voting:
            return -1

        private_key = RSA.generate(2048)
        public_key = private_key.publickey().export_key()
        hash_1 = self.calculate_hash(public_key, hash_function="sha256")
        hash_2 = self.calculate_hash(hash_1, hash_function="ripemd160")
        wallet_address = base58.b58encode(hash_2)

        self.voters.append({
            "public_key": public_key.decode("utf-8"),
            "wallet_address": wallet_address.decode("utf-8"),
        })

        self.mine()

        return private_key, public_key.decode("utf-8"), wallet_address.decode('utf-8')

    def mine(self):
        # first we need to run the proof of work algorithm to calculate the new proof..
        last_block = self.last_block

        # forge the new block by adding it to the chain
        previous_hash = self.hash(last_block)
        block = self.new_block(previous_hash)
        self.inform_of_change()
        return block

    def start_voting(self, signature: str, data: str):
        signature_byte = binascii.unhexlify(signature)
        self.validate_signature(self.admin, signature_byte, data.encode('utf-8'))
        self.started_voting = True
        self.mine()

        return True

    def end_voting(self, signature: str, data: str):
        if self.started_voting:
            signature_byte = binascii.unhexlify(signature)
            self.validate_signature(self.admin, signature_byte, data.encode('utf-8'))
            self.ended_voting = True
            self.mine()
        else:
            return False
        return True

    def proof_of_work(self, last_proof):
        # simple proof of work algorithm
        # find a number p' such as hash(pp') containing leading 4 zeros where p is the previous p'
        # p is the previous proof and p' is the new proof
        proof = 0
        while self.validate_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def validate_proof(last_proof, proof):
        # validates the proof: does hash(last_proof, proof) contain 4 leading zeroes?
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        # add a new node to the list of nodes
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def full_chain(self):
        # xxx returns the full chain and a number of blocks
        pass

    def valid_chain(self, chain):

        # determine if a given blockchain is valid
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            # check that the proof of work is correct

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        # this is our Consensus Algorithm, it resolves conflicts by replacing
        # our chain with the longest one in the network.

        neighbours = self.nodes
        new_chain = None

        # we are only looking for the chains longer than ours
        max_length = len(self.chain)

        # grab and verify chains from all the nodes in our network
        for node in neighbours:
            try:
                # we utilize our own api to construct the list of chains :)
                response = requests.get(f'http://{node}/chain')

                if response.status_code == 200:

                    length = response.json()['length']
                    chain = response.json()['chain']

                    # check if the chain is longer and whether the chain is valid
                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except:
                print(node)

        # replace our chain if we discover a new longer valid chain
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def inform_of_change(self):
        neighbours = self.nodes

        # grab and verify chains from all the nodes in our network
        for node in neighbours:
            # we utilize our own api to construct the list of chains :)
            try:
                response = requests.get(f'http://{node}/miner/nodes/resolve',timeout=0.05)
            except requests.exceptions.ReadTimeout:
                pass


        return False

    def candidate_votes(self):
        return Counter(self.candidates)

    def get_all_transactions(self):
        transactions = []
        for block in self.chain:
            for transaction in block['transactions']:
                transactions.append(transaction)

        return transactions

    def get_all_voters(self):
        votersAll = []
        transactions = self.get_all_transactions()
        for block in self.chain:
            for voter in block['voters']:
                curVoter = voter.copy()
                if any(elem['sender'] == voter['wallet_address'] for elem in transactions):
                    curVoter["voted"] = True
                else:
                    curVoter["voted"] = False
                votersAll.append(curVoter)

        return votersAll

    def get_all_candidates(self):
        candidates = []
        for block in self.chain:
            for candidate in block['candidates']:
                candidates.append(candidate)

        return candidates
