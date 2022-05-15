import unittest


from main import *

class TestBlockChain(unittest.TestCase):

    def test_simple(self):
        blockchain = BlockChain()
        self.assertEqual(blockchain.current_transactions, BlockChain().current_transactions)

    def test_start_vote(self):
        blockchain = BlockChain()
        blockchain.start_voting()
        self.assertEqual(blockchain.started_voting, True)

    def test_end_vote_when_not_started(self):
        blockchain = BlockChain()
        blockchain.end_voting()
        self.assertEqual(blockchain.ended_voting, False)

    def test_add_transaction_to_be_voted_simple(self):
        blockchain = BlockChain()
        blockchain.new_candidate("First", "wallet")
        blockchain.started_voting = True
        private_key, public_key, wallet_address = blockchain.new_voter()
        transaction = Transaction(wallet_address, "wallet")
        transaction.sign(private_key)

        blockchain.new_transaction(transaction)
        last_transactions = blockchain.chain[-1]['transactions']
        self.assertEqual(len(last_transactions), 1)

    @staticmethod
    def sign(data, private_key):
        hash_object = SHA256.new(data)
        signature = pkcs1_15.new(private_key).sign(hash_object)
        return signature

    def test_add_transaction_to_be_voted(self):
        blockchain = BlockChain()

        f = open("private.pem", "r");
        private_key = RSA.importKey(f.read())

        signature = self.sign("First".encode('utf_8'), private_key)
        candidate_wallet = blockchain.new_candidate("First".encode('utf_8'), signature)

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

    def test_add_transaction_with_wrong_signature(self):
        blockchain = BlockChain()
        blockchain.new_candidate("First", "wallet")
        blockchain.started_voting = True
        private_key, public_key, wallet_address = blockchain.new_voter()
        transaction = Transaction(wallet_address, "wallet")
        transaction.sign(private_key)
        transaction.signature = transaction.signature[:-1]

        try:
            blockchain.new_transaction(transaction)
        except ValueError as e:
            self.assertEqual(type(e), ValueError)


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

