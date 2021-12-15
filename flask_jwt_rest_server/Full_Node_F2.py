"""
The full node runs one program, which is a server.  It binds its program to a port number,
e.g. 10000 for F1 and 11000 for F2.  Recall that the full nodes take turns to mine blocks.
F1 mines odd blocks and F2 mines even blocks.  For this purpose, define a variable named "turn",
and initialize it to 1 in F1 and 2 in F2.  Each full node has a balance, which is initially 0BC.
When a full node mines a block, it gets rewarded by the Tx fees and mining fee, which will be added
to the full node balance.

General Algorithm:
--------------------------------------------------------------------------------------------------------
In an infinite loop, the program listens to the requests for connections, which could be from its client
or the other full node.
1. If the requester is its client, the received message is a Tx, do the TTT instructions.
2. If the requester is the other full node, the received message is either a Tx or a block
    A. If the message is a Tx, do the TTT instructions
    B. If the message is a block:
        a. Append the block to the blockchain.txt file
        b. Remove the 4 Tx of the block from Temp_T.txt
        c. Check the 4 Tx of the block and send the Tx where its client is a Payer or Payee to the client.
            The purpose is to let the client know these Tx are confirmed.

    TTT INSTRUCTIONS
    ----------------
1. Receive the Tx and append it to the Temp_T.txt
    a. If the requester is the full node's client, send the Tx to the other full node as well.
2. If the number of Tx in Tempt_T.txt has reached 4, increment "turn" by 1
    a. If (turn % 2 == 1), it is the other full node's turn to mine, exit
    b. Otherwise, it should mine the new block.
        I. Remove the 4 Tx of the block from Temp_t.txt and mine a block with them
        II. Add the mining fee (30 BC) and the total Tx_fee (8 BC) to the full node balance.
        III. Append the block to its blockchain.txt   <-- more complicated step
        IV. Check the 4 Tx of the block and send the Tx where its client is a Payer or Payee to the client.
            The purpose is to let the client know these Tx are confirmed.
        V. Send the block to the other full node.
        VI. Print the block on the screen and exit.

The positions of the transactions/payer/payee positions in a block are as follows:
The 1st transaction is located at char position 136 with payee and payer positions at positions 136 and 143 respectively
The 2nd transaction is located at char position 159 with payee and payer positions at positions 159 and 167 respectively
The 3rd transaction is located at char position 183 with payee and payer positions at positions 183 and 191 respectively
The 4th transaction is located at char position 207 with payee and payer positions at positions 207 and 215 respectively
"""

from socket import *
import hashlib

num_temp_tx = 0
turn = 0
balance = 0  # used to store the balance of the Full Node
mining_fee = 30
total_tx_fee = 8
client_accts = ['B0000001', 'B0000002']


def TTT(transaction):
    # receive the tx and append it to the Temp_T.txt
    with open('Temp_T_F2.txt', 'a') as f:  # opens the file containing the unconfirmed transactions
        f.write(transaction[3:] + "\n")  # appends/writes the transaction to the file
        global num_temp_tx  # used to count the number of transactions
        num_temp_tx += 1
    # if the requester is the full node's client, send the Tx to the other full node as well
    # '000' for the first 3 bits means its an unconfirmed transaction from the attached partial node
    if transaction[:3] == '000':
        transaction = '100' + transaction[3:]
        serverSocket.sendto(transaction.encode(), other_full_node_address)

    # if the number of Tx in Tempt_t.txt has reached 4, increment "turn" by 1
    if num_temp_tx % 4 == 0:
        global turn  # used to determine whose turn it is to mine a block
        turn += 1
        if turn % 2 == 0:  # it is this node's turn to mine
            # Remove the 4 Tx of the block from Temp_t.txt and mine a block with them
            tx_list = remove_temp_txs()
            # MINE THE BLOCK using the 4 transactions put into a list from above
            block = block_mining(tx_list)  # function will return the block
            #  Add the mining fee (30 BC) and the total Tx_fee (8 BC) to the full node balance.
            global balance
            # letting balance store the amount in decimal form, adds the mining fee and the total transaction fee to
            # the balance for each mined block
            balance = balance + mining_fee + total_tx_fee
            hex_balance = hex(balance)
            hex_balance = hex_balance[2:]
            with open('balance_F2.txt', 'w') as f:  # opens the file containing the balance
                f.write(hex_balance)  # appends/writes the new balance to the file
            # Append the block to its blockchain_F1.txt
            append_to_blockchain(block)
            # Check the 4 Tx of the block and send the Tx where its client is a Payer or Payee to the client.
            # The purpose is to let the client know these Tx are confirmed.
            send_confirmed_txs_to_client(block)
            # Send the block to the other full node.
            new_block = '101' + block  # allows for the elif branch to catch that it is a mined block
            serverSocket.sendto(new_block.encode(), other_full_node_address)
            # Print the block on the screen and exit.
            display_block(block)

        else:  # otherwise it should send signal to the other full node to mine the new block
            temp = '111'  # let '111' be the signal for the other node to mine the block
            serverSocket.sendto(temp.encode(), other_full_node_address)


def send_confirmed_txs_to_client(block):
    # gets the 4 transactions from the block
    txs_from_block = get_txs_from_block(block)
    # removes the 4 transactions from the the temporary file holding the temporary transactions
    remove_temp_txs()
    # get client transactions from the list where the client is the payer or the payee in the list of transactions
    confirmed_client_txs = get_client_txs_from_list(txs_from_block)
    # sends a list of transactions to the client where the client is either a payer or a payee
    for tx in confirmed_client_txs:
        serverSocket.sendto(tx.encode(), attached_client_addr_for_confirmed_tx)
    serverSocket.sendto('EOF'.encode(), attached_client_addr_for_confirmed_tx)


# block should be a string to represent the block chain
def append_to_blockchain(block):
    with open('Blockchain_F2.txt', 'a+') as f:  # opens the file containing the block chain
        f.write(block + "\n")  # appends/writes the block to the file


def remove_temp_txs():
    with open('Temp_T_F2.txt', 'r') as f_old:  # opens the balances txt file
        # f.readlines() creates a list of the 4 transactions in the file (including \n)
        tx_list = f_old.readlines()
        for index, tx in enumerate(tx_list):  # for each line (string) in the acct_list
            # need to strip the txs of whitespace chars e.g., "\n"
            tx_list[index] = tx.strip()
    with open('Temp_T_F2.txt', 'w'):  # just doing this should clear the file must be after the read functions
        # or it clears immediately as the function is called
        return tx_list  # to keep the compiler happy


# mines the block
def block_mining(tx_list):
    merkle_root = generate_merkle_root(tx_list)
    last_block_hash = get_last_block_hash()
    nonce = generate_nonce(last_block_hash, merkle_root)
    block = nonce + last_block_hash + merkle_root
    for tx in tx_list:
        block += tx
    return block


# generates the merkle root for the block
def generate_merkle_root(tx_list):
    hash_handler = hashlib.sha256()
    # hashes the first four transactions into 4 separate 64 character strings where each string is stored separately
    # in the list
    abcd_hash_list = []  # create an empty list to include the hashes for the first 4 transactions
    for tx in tx_list:  # for each transaction, create its hash and place the hash into the hash list
        hash_handler.update(tx.encode("utf-8"))  # updates the handler to include the transaction string
        abcd_hash_list.append(hash_handler.hexdigest())  # append the hash to the list
    # update the handler to include the concatenation of the first and second hash strings
    hash_handler.update((abcd_hash_list[0] + abcd_hash_list[1]).encode("utf-8"))
    hash_ab = hash_handler.hexdigest()  # hash that string and store
    # update the handler to include the concatenation of the third and fourth hash strings
    hash_handler.update((abcd_hash_list[2] + abcd_hash_list[3]).encode("utf-8"))
    hash_cd = hash_handler.hexdigest()  # hash that string and store
    # update the handler to include the concatenation of hash_cd and hash_ab
    hash_handler.update((hash_ab + hash_cd).encode("utf-8"))
    merkle_root = hash_handler.hexdigest()  # hash that string, this string represents the merkle root
    return merkle_root  # return the merkle root


# gets the last block in the block chain
# presumption here is that each line stored in the blockchain represents a single hash
def get_last_block_hash():
    hash_handler = hashlib.sha256()
    with open('Blockchain_F2.txt', 'r') as f:
        # f.readlines() creates a list of all the lines in the file (including \n)
        block_list = f.read(1)
        if not block_list:
            # returns the first block hash of 64 0's if this is the first block to be added to the list
            return '0000000000000000000000000000000000000000000000000000000000000000'
        else:
            block_list = f.readlines()
            last_block = block_list[-1]
            hash_handler.update((last_block[:136]).encode("utf-8"))
            new_last_block = hash_handler.hexdigest()
            # hash for the last block will be in char positions 8 to 71
            return new_last_block


def generate_nonce(last_block_hash, merkle_root):
    hash_handler = hashlib.sha256()
    nonce = 0
    while True:
        block_header = str(nonce) + last_block_hash + merkle_root
        hash_handler.update(block_header.encode("utf-8"))
        hash_value = hash_handler.hexdigest()
        # print('nonce:{0}, hash:{1}'.format(nonce, hash_value))   # won't need this line
        nonce_found = True
        for i in range(4):
            if hash_value[i] != '0':
                nonce_found = False
        if nonce_found:
            nonce = hex(nonce)
            return nonce[2:].zfill(8)  # returns the nonce string as an 8 char hex number
        else:
            nonce = nonce + 1


'''
Displays the newly mined block on the screen
The presumption here is that the block will be in the format of a single string
In terms of chars, the nonce, block hash, Merkle root, and the 4 transactions will be in the
bits 0 to 7, 8 to 71, 72 to 135, 136 to 159, 160 to 183, 184 to 207, 208 to 231 respectively.
Each transaction will be a concatenation of three 8-character strings with the first 8 char set as the
payer, the second 8 char set as the payee and the 3rd 8 char string as the amount (in hex dollars) 
'''


def display_block(block):
    nonce = block[:8]
    last_block_hash = block[8:72]
    merkle_root = block[72:136]

    tx1 = block[136:160]
    tx1_payer = tx1[0:8]
    tx1_payee = tx1[8:16]
    tx1_amount = int(tx1[16:24], 16)

    tx2 = block[160:184]
    tx2_payer = tx2[0:8]
    tx2_payee = tx2[8:16]
    tx2_amount = int(tx2[16:24], 16)

    tx3 = block[184:208]
    tx3_payer = tx3[0:8]
    tx3_payee = tx3[8:16]
    tx3_amount = int(tx3[16:24], 16)

    tx4 = block[208:232]
    tx4_payer = tx4[0:8]
    tx4_payee = tx4[8:16]
    tx4_amount = int(tx4[16:24], 16)

    print(f"Newly Mined Block:\n\
            Nonce (4-byte): {nonce}\n\
            Last Block Hash: {last_block_hash}\n\
            Merkle root (32-byte): {merkle_root}\n\
            Tx1 (12-byte): {tx1_payer} pays {tx1_payee} the amount of {tx1_amount} BC.\n\
            Tx2 (12-byte): {tx2_payer} pays {tx2_payee} the amount of {tx2_amount} BC.\n\
            Tx3 (12-byte): {tx3_payer} pays {tx3_payee} the amount of {tx3_amount} BC.\n\
            Tx4 (12-byte): {tx4_payer} pays {tx4_payee} the amount of {tx4_amount} BC.\n")


# returns a list of the transactions that the client is either the payer or payee on the transaction
# since in this project, the payer or payee must be one of the two different nodes but not both, this
# function is more of a formality
def get_client_txs_from_list(txs_from_block):
    client_txs_list = []
    # recall from above client_accts = ['B0000001', 'B0000002']
    # parse the transactions from the block and check to see if either the payer or the payee is one of the
    # attached client accounts
    for tx in txs_from_block:
        # check it against the accounts
        for acct in client_accts:
            # if the payer (from chars 0 to 7) or the payee (from chars 8 to 15) are the same for the transaction
            # as one of the accounts, append the transaction to the client transaction list
            if acct == tx[:8] or acct == tx[8:16]:
                client_txs_list.append(tx)
    return client_txs_list  # return the client transaction list


# sends the current blockchain to the client as a list
def send_block_chain_to_client():
    with open('Blockchain_F2.txt', 'r') as f:
        # f.readlines() creates a list of all the lines in the file (including \n)
        block_chain = f.readlines()
    # sends the blockchain to the client where the client is either a payer or a payee
    for block in block_chain:
        serverSocket.sendto(block.encode(), attached_client_addr)
    # send EOF
    serverSocket.sendto('EOF'.encode(), attached_client_addr)


'''
This method parses the block and returns the transactions from the block
the transactions inside the block will be located at positions:
The 1st transaction is located at char position 136
The 2nd transaction is located at char position 159
The 3rd transaction is located at char position 183
The 4th transaction is located at char position 207
The block ends at position 231
'''


def get_txs_from_block(block):
    block_txs = [block[136:160], block[160:184], block[184:208], block[208:232]]
    # block_txs.append(block[136:159])  # may not need these 4 lines, erase if everything works
    # block_txs.append(block[159:183])
    # block_txs.append(block[183:207])
    # block_txs.append(block[207:232])
    return block_txs


serverPort = 11000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
global attached_client_addr
attached_client_addr_for_confirmed_tx = ('localhost', 11001)

# the port for the other full node will be 12001 whereas the port number being used for this node is 12000
other_full_node_address = ('localhost', 10000)
# essentially acts as the main function
while True:
    while True:
        communication, address = serverSocket.recvfrom(2048)
        communication = communication.decode()

        # initializes the attached_client_addr
        if communication == '00':
            attached_client_addr = address

        # '000' for the first 3 bits means its an unconfirmed transaction from the attached partial node
        if communication[:3] == '000':
            TTT(communication)
        # if the first 3 bits are '011', it means that the attached client is requesting the block chain
        elif communication[:3] == '011' and len(communication) == 3:
            send_block_chain_to_client()
        # '101' for the first 3 bits means its and unconfirmed transaction from the other full node
        # '100' for the first 3 bits means its a mined block from the other full node
        elif communication[:3] == '100' or communication[:3] == '101':
            if communication[:3] == '100':  # if the message is an unconfirmed transaction from the other node do
                # TTT() method
                TTT(communication)
            elif communication[:3] == '101':  # if the message is a mined block from the other node
                append_to_blockchain(communication[3:])
                send_confirmed_txs_to_client(communication[3:])

    serverSocket.close()
