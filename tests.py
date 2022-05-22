import unittest
import time

from main import *


class TestBlockChain(unittest.TestCase):

    def test_simple(self):
        blockchain = BlockChain()
        self.assertEqual(blockchain.current_transactions, BlockChain().current_transactions)

    def test_start_vote(self):
        blockchain = BlockChain()
        f = open("private.pem", "r");
        private_key = RSA.importKey(f.read())
        signature = TestBlockChain.sign("StartVote".encode('utf-8'), private_key)

        blockchain.start_voting(signature, "StartVote".encode('utf-8'))
        self.assertEqual(blockchain.started_voting, True)

    def test_end_vote_when_not_started(self):
        blockchain = BlockChain()
        f = open("private.pem", "r");
        private_key = RSA.importKey(f.read())
        signature = TestBlockChain.sign("EndVote".encode('utf-8'), private_key)

        blockchain.end_voting(signature, "EndVote".encode('utf-8'))
        self.assertEqual(blockchain.ended_voting, False)

    def test_add_transaction_to_be_voted_simple(self):
        blockchain = BlockChain()
        name = 'First'

        f = open("private.pem", "r");
        private_key = RSA.importKey(f.read())
        signature = TestBlockChain.sign(name.encode('utf-8'), private_key)
        candidate_wallet = blockchain.new_candidate(name.encode('utf-8'), signature)
        blockchain.started_voting = True
        private_key, public_key, wallet_address = blockchain.new_voter()
        transaction = Transaction(wallet_address, candidate_wallet)
        transaction.sign(private_key)

        blockchain.new_transaction(transaction)
        last_transactions = blockchain.chain[-1]['transactions']
        self.assertEqual(len(last_transactions), 1)

    def test_add_transaction_to_be_voted(self):
        blockchain = BlockChain()

        name = 'First'

        f = open("private.pem", "r");
        private_key = RSA.importKey(f.read())
        signature = TestBlockChain.sign(name.encode('utf-8'), private_key)
        candidate_wallet = blockchain.new_candidate(name.encode('utf-8'), signature)

        blockchain.started_voting = True

        private_key, public_key, wallet_address = blockchain.new_voter()
        transaction = Transaction(wallet_address, candidate_wallet)
        transaction.sign(private_key)
        blockchain.new_transaction(transaction)

        private_key, public_key, wallet_address = blockchain.new_voter()
        transaction = Transaction(wallet_address, candidate_wallet)
        transaction.sign(private_key)
        blockchain.new_transaction(transaction)
        print(blockchain.get_all_transactions())
        self.assertEqual(len(blockchain.get_all_transactions()), 2)

    def test_add_transaction_to_be_voted_by_the_same_voter(self):
        blockchain = BlockChain()

        name = 'First'

        f = open("private.pem", "r");
        private_key = RSA.importKey(f.read())
        signature = TestBlockChain.sign(name.encode('utf-8'), private_key)
        candidate_wallet = blockchain.new_candidate(name.encode('utf-8'), signature)

        blockchain.started_voting = True

        private_key, public_key, wallet_address = blockchain.new_voter()
        transaction = Transaction(wallet_address, candidate_wallet)
        transaction.sign(private_key)
        blockchain.new_transaction(transaction)

        blockchain.new_transaction(transaction)

        self.assertEqual(len(blockchain.get_all_transactions()), 1)

    def test_add_transaction_with_wrong_signature(self):
        blockchain = BlockChain()
        name = 'First'

        f = open("private.pem", "r");
        private_key = RSA.importKey(f.read())
        signature = TestBlockChain.sign(name.encode('utf-8'), private_key)
        candidate_wallet = blockchain.new_candidate(name.encode('utf-8'), signature)
        blockchain.started_voting = True
        private_key, public_key, wallet_address = blockchain.new_voter()
        transaction = Transaction(wallet_address, candidate_wallet)
        transaction.sign(private_key)
        transaction.signature = transaction.signature[:-1]

        try:
            blockchain.new_transaction(transaction)
        except ValueError as e:
            self.assertEqual(type(e), ValueError)



    def test_add_transaction_to_be_voted_x_times(self):
        nodes = set()
        for x in range(5001, 5007):
            nodes.add("localhost:" + str(x))
        blockchain = BlockChain(nodes)

        candidate_wallet = "Candidate1"

        transactions = set()
        for x in range(0,100):
            private_key, public_key, wallet_address = blockchain.new_voter()
            transaction = Transaction(wallet_address, candidate_wallet)
            transaction.sign(private_key)

            transactions.add(transaction)

        blockchain.started_voting = True
        times = set()
        for transaction in transactions:
            start = time.time()
            blockchain.new_transaction(transaction)
            end = time.time()
            times.add(end - start)

        with open('TimeResult.txt', 'w') as f:
            for item in times:
                f.write("%s\n" % item)

        print(blockchain.get_all_transactions())
        self.assertEqual(len(blockchain.get_all_transactions()), 10)

    @staticmethod
    def sign(data, private_key):
        hash_object = SHA256.new(data)
        signature = pkcs1_15.new(private_key).sign(hash_object)
        return signature

    @staticmethod
    def create_candidate(name):
        f = open("private.pem", "r");
        private_key = RSA.importKey(f.read())

        signature = TestBlockChain.sign(name.encode('utf-8'), private_key)
        return blockchain.new_candidate(name.encode('utf-8'), signature)


class TestCommunication(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_chain_get(self):
        response = self.client.get("/chain")
        assert response.status_code == 200

    def test_candidate_votes_get_empty(self):
        response = self.client.get("/candidate/results")
        print(response.get_json())
        assert response.status_code == 200

    def test_candidate_votes_get(self):
        response = self.client.get("/candidate/results")
        values = response.get_json()
        candidate_counts = values['candidate_gotten_votes']

        assert len(candidate_counts) == 1
        assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()
