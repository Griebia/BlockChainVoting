from blockchain import *

# initiate the node
app = Flask(__name__)
# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')
# initiate the Blockchain
blockchain = BlockChain()


@staticmethod
def validate_signature(public_key: bytes, signature: bytes, transaction_data: bytes):
    public_key_object = RSA.import_key(public_key)
    transaction_hash = SHA256.new(transaction_data)
    pkcs1_15.new(public_key_object).verify(transaction_hash, signature)



# @app.route('/mine', methods=['GET'])
# def mine():
#     block = blockchain.mine()
#
#     response = {
#         'message': "Forged new block.",
#         'index': block['index'],
#         'transactions': block['transactions'],
#         'proof': block['proof'],
#         'previous_hash': block['previous_hash'],
#     }
#     return jsonify(response, 200)


@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']

    if blockchain.started_voting and not blockchain.ended_voting:
        return 'Voting is not allowed now', 400

    if not all(k in values for k in required):
        return 'Missing values.', 400

    # create a new transaction
    index = blockchain.new_transaction(
        sender=values['sender'],
        recipient=values['recipient'],
        amount=values['amount']
    )

    response = {
        'message': f'Transaction will be added to the Block {index}',
    }
    return jsonify(response, 200)


@app.route('/candidate/new', methods=['POST'])
def new_candidate():
    values = request.get_json()
    required = ['name', 'hash']

    if not all(k in values for k in required):
        return 'Missing values.', 400

    if blockchain.started_voting:
        return 'Vote has already started, adding candidates is not allowed', 400

    index = blockchain.new_candidate(
        name=values['name'],
        hash=values['hash']
    )

    response = {
        'message': f'Candidate will be added to the Block {index}',
    }
    return jsonify(response, 200)


@app.route('/voter/new', methods=['GET'])
def new_voter():
    if blockchain.started_voting:
        return 'Vote has already started, adding candidates is not allowed', 400

    private_key, public_key, wallet = blockchain.new_voter()

    response = {
        'private_key': private_key,
        'public_key': public_key,
        'wallet': wallet
    }

    return jsonify(response, 200)


@app.route('/startvote', methods=['GET'])
def start_vote():
    blockchain.start_voting()
    response = {
        'message': f'Started the vote!',
    }
    return jsonify(response, 200)


@app.route('/endvote', methods=['GET'])
def end_vote():
    blockchain.ended_voting()
    response = {
        'message': f'Ended the vote!',
    }
    return jsonify(response, 200)


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    print('values', values)
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    if blockchain.started_voting:
        return "Error: Vote has already started", 400

    # register each newly added node
    for node in nodes: blockchain.register_node(node)

    response = {
        'message': "New nodes have been added",
        'all_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201


@app.route('/miner/nodes/resolve', methods=['GET'])
def consensus():
    # an attempt to resolve conflicts to reach the consensus
    conflicts = blockchain.resolve_conflicts()

    if (conflicts):
        response = {
            'message': 'Our chain was replaced.',
            'new_chain': blockchain.chain,
        }
        return jsonify(response), 200

    response = {
        'message': 'Our chain is authoritative.',
        'chain': blockchain.chain,
    }
    return jsonify(response), 200


if __name__ == '__main__':
    defPort = 5000
    if len(sys.argv) > 1:
        defPort = sys.argv[1]
    app.run(host='0.0.0.0', port=defPort)