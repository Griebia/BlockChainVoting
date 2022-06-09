from blockchain import *

# initiate the node
app = Flask(__name__)
# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')


@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['signature', 'sender', 'receiver']

    if not all(k in values for k in required):
        return 'Missing values.', 400

    if not blockchain.started_voting or blockchain.ended_voting:
        return 'Voting is not allowed now', 400

    # create a new transaction
    result, message = blockchain.new_transaction(
        Transaction(values['sender'], values['receiver'], values['signature'])
    )

    if result:
        response = {
            'message': f'Transaction has been added to the blockchain',
        }
        return jsonify(response, 200)

    response = {
        'error_message': f'{message}',
    }
    return jsonify(response, 500)

@app.route('/transaction/all', methods=['GET'])
def get_all_transactions():
    return jsonify(blockchain.get_all_transactions())


@app.route('/candidate/new', methods=['POST'])
def new_candidate():
    values = request.get_json()
    required = ['name', 'signature']

    if not all(k in values for k in required):
        return 'Missing values.', 400

    if blockchain.started_voting:
        return 'Vote has already started, adding candidates is not allowed', 400

    wallet = blockchain.new_candidate(
        values['name'],
        values['signature']
    )

    response = {
        'wallet': wallet
    }

    return jsonify(response)


@app.route('/voter/new', methods=['GET'])
def new_voter():
    if blockchain.started_voting:
        return 'Vote has already started, adding candidates is not allowed', 400

    private_key, public_key, wallet = blockchain.new_voter()

    response = {
        'private_key': private_key.export_key('PEM').decode('utf-8'),
        'public_key': public_key,
        'wallet': wallet
    }

    return jsonify(response)


@app.route('/startvote', methods=['POST'])
def start_vote():
    values = request.get_json()
    required = ['signature', 'data']

    if not all(k in values for k in required):
        return 'Missing values.', 400


    result = blockchain.start_voting(values['signature'], values['data'])
    if not result:
        response = {
            'message': f'Could not start the vote',
        }
        return jsonify(response, 400)

    response = {
        'message': f'Started the vote!',
    }
    return jsonify(response, 200)


@app.route('/endvote', methods=['POST'])
def end_vote():
    values = request.get_json()
    required = ['signature', 'data']

    if not all(k in values for k in required):
        return 'Missing values.', 400

    result = blockchain.end_voting(values['signature'], values['data'])
    if not result:
        response = {
            'message': f'Could no end the vote',
        }
        return jsonify(response, 400)

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

@app.route('/candidate/results', methods=['GET'])
def candidate_result():
    print(blockchain.candidate_votes())
    return jsonify(blockchain.candidate_votes())

@app.route('/test', methods=['GET'])
def test():
    import time

    candidate_wallet = "Candidate1"

    transactions = set()
    times = set()
    for x in range(0, 1000):
        start = time.time()
        private_key, public_key, wallet_address = blockchain.new_voter()
        end = time.time()
        times.add(end - start)
        transaction = Transaction(wallet_address, candidate_wallet)
        transaction.sign(private_key)

        transactions.add(transaction)

    with open('TimeResult.txt', 'w') as f:
        for item in times:
            f.write("%s\n" % item)

    blockchain.started_voting = True
    times = set()
    for transaction in transactions:
        start = time.time()
        blockchain.new_transaction(transaction)
        end = time.time()
        print(end - start)
        times.add(end - start)

    with open('TimeResult.txt', 'w') as f:
        for item in times:
            f.write("%s\n" % item)

    print(blockchain.get_all_transactions())
    response = {
        'message': 'Results are returned',
        'candidate_gotten_votes': blockchain.candidate_votes(),
    }
    return jsonify(response), 200



if __name__ == '__main__':
    defPort = str(5000)
    mainNodePassword = "Node"

    if len(sys.argv) > 1:
        defPort = sys.argv[1]

    nodes = set()
    for x in range(5000,5003):
        if defPort == str(x):
            continue
        nodes.add("localhost:" + str(x))
    print(nodes)

    blockchain = BlockChain(nodes)

    app.run(host='0.0.0.0', port=defPort)