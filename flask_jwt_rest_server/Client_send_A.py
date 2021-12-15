"""
Programmer: Kaleb Newsom & Kelyn Kirt

Algorithm for Client_send_A.py

The client will have three files:
1. Unconfirmed_T_A.txt to store the unconfirmed transactions
2. Confirmed_T_A.txt to store the confirmed transactions
3. balances_A.txt

Each client has two accounts and each client account has two balances:
1. Unconfirmed_balance to store the balance after all unconfirmed transactions
2. Confirmed_balance to store the balance after all confirmed transactions.

All client balances are initialized to 1000 BC (0x000003E8).

1. Unconfirmed_balance
This is used for new transactions that have not been entered to the blockchain yet.
 For entering a new transaction:
 The payer could be one of the client's accounts.  The Payee could be one of the other client's accounts.
 At each step, provide a list of possible accounts to the user and ask them to select the accounts from the list.
 Once the user entered a new Tx, the client takes the following steps.

• When a user enters a new Tx, the client takes the following steps.
1. It checks whether {Tx_amount + Tx_fee} would not exceed the current value of Unconfirmed_balance, then reduces the
    Unconfirmed_balance by {Tx_amount + Tx_fee}.
2. It appends the Tx to a file containing its unconfirmed transactions (Unconfirmed_T. txt).
3. It sends the Tx to the full node.

The client balance file
The client stores the current values of its balances for each of its two accounts in a file named balance.txt.
The values in the files are initialized at the beginning and updated while running the program. I suggest the following
structure for the file. You are free to select another structure.
Account1:Unconfirmed_balance:Confirmed_balance
Account2:Unconfirmed_balance:Confirmed_balance
For example, for Client A, the file will be initialized as following. We store the values in HEX.
A0000001:000003E8:000003E8
A0000002:000003E8:000003E8

The client implementation
The client runs two programs:
1. Client_send.py: To send Tx to the full node.
2. Client_receive.py: To receive Tx from the full node.

-- should connect to it's full node where the node acts as a server
-- need to bind the full node program to a port number e.g., 100000 for F1.

unconfirmed transaction from client to full node will have header '000'
blockchain request from client to full node will have header '001'
"""

from socket import *  # import the socket program


# store the string for the menu in a menu variable
menu = "Please make a choice from the following selection:\n \
        1: Enter a new transaction.\n \
        2: The current balance for each account.\n \
        3: Print the unconfirmed transactions.\n \
        4: Print the confirmed transactions.\n \
        5: Print the blockchain.\n \
        6: Exit.\n"
current_node_accts = ["A0000001", "A0000002"]
other_node_accts = ["B0000001", "B0000002"]

# initialize the unconfirmed balances dictionary
unconfirmed_acct_balances = {
    'A0000001': '000003E8',  # this amounts to 1000 BC
    'A0000002': '000003E8'  # this amounts to 1000 BC
}
# initialize the confirmed balances dictionary
confirmed_acct_balances = {
    'A0000001': '000003E8',  # this amounts to 1000 BC
    'A0000002': '000003E8'  # this amounts to 1000 BC
}

# as a client connection
serverName = 'localhost'  # 'localhost' is the same pc
serverPort = 10000  # hw instructions suggest port 10000
clientSocket = socket(AF_INET, SOCK_DGRAM)  # connects to the full node using UDP



# sends a transaction to the node
def send_tx_to_node(tx):
    tx = '000' + tx  # contains the header bits '000 ' as way to tell the full node that this is from the client
    clientSocket.sendto(tx.encode(), (serverName, serverPort))  # encodes and sends the transaction information to the
    # full node


# requests the blockchain data from the full node
def request_node_blockchain():
    request = '011'  # initializes request variable to request blockchain
    clientSocket.sendto(request.encode(), (serverName, serverPort))  # sends the string for the request to the full node
    blockchain = []
    clientSocket.settimeout(5)

    while True:  # waits for the blockchain to return to the user
        block, address = (clientSocket.recvfrom(1024))
        block = block.decode()
        if block == 'EOF':
            break
        blockchain.append(block)
    return blockchain  # function returns the blockchain as a list of blocks


# retrieves the account balances from the balances txt file
def get_acct_balances():
    with open('balances_A.txt', 'r') as f:  # opens the balances txt file
        # f.readlines() creates a list of all the lines in the file (including \n)
        acct_list = f.readlines()
        for line in acct_list:  # for each line (string) in the acct_list
            # line will contain a string with ":" chars in the format:
            # account_num:Unconfirmed_balance:Confirmed_balance so temp_list will store the items on the line in the
            # format: [Account1, Unconfirmed_balance, Confirmed_balance] by using the split() method
            temp_list = line.split(":")
            for index, item in enumerate(
                    temp_list):  # only using this to remove any "\n" chars or whitespace in the list
                temp_list[index] = item.strip()
            # updates the current confirmed/unconfirmed account balances according to what's in the accts
            # for first line read, temp_list[0] will be for the first payer's acct
            # for the 2nd line read, temp_list[0] will be for the 2nd payer's acct
            # updates account balances according to the hex string equivalents without the '0x' chars
            unconfirmed_acct_balances[temp_list[0]] = temp_list[1]
            confirmed_acct_balances[temp_list[0]] = temp_list[2]


# retrieves the unconfirmed transactions from the respective txt file
def get_unconfirmed_txs():
    with open('Unconfirmed_T_A.txt', 'r') as f:  # opens the unconfirmed transactions text file
        # f.readlines() creates a list of all the lines in the file (including \n)
        unconfirmed_tx_list = f.readlines()
        # remove unnecessary whitespace from the list
        for index, line in enumerate(unconfirmed_tx_list):
            unconfirmed_tx_list[index] = line.strip()
        return unconfirmed_tx_list  # returns the unconfirmed transactions as a list


# retrieves the confirmed transactions from the respective txt file
def get_confirmed_txs():  # opens the confirmed transactions text file
    with open('Confirmed_T_A.txt', 'r') as f:
        # f.readlines() creates a list of all the lines in the file (including \n)
        confirmed_tx_list = f.readlines()
        # remove unnecessary whitespace from the list
        for index, line in enumerate(confirmed_tx_list):
            confirmed_tx_list[index] = line.strip()
        return confirmed_tx_list  # returns the confirmed transactions as a list


def display_block_chain(blockchain):
    # use these lines if blockchain was a list e.g, if readlines() is used
    for block_num, block in enumerate(blockchain):
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

        print(f"Block Number {block_num + 1}:\n\
                Nonce (4-byte): {nonce}\n\
                Last Block hash (32-byte): {last_block_hash}\n\
                Merkle root (32-byte): {merkle_root}\n\
                Tx1 (12-byte): {tx1_payer} pays {tx1_payee} the amount of {tx1_amount} BC.\n\
                Tx2 (12-byte): {tx2_payer} pays {tx2_payee} the amount of {tx2_amount} BC.\n\
                Tx3 (12-byte): {tx3_payer} pays {tx3_payee} the amount of {tx3_amount} BC.\n\
                Tx4 (12-byte): {tx4_payer} pays {tx4_payee} the amount of {tx4_amount} BC.\n")


'''
In an infinite loop, the program displays a menu and asks the client to enter a choice:
 1. Enter a new transaction.
 2. The current balance for each account.
 3. Print the unconfirmed transactions.
 4. Print the last X number of confirmed transactions (either as a Payee or a Payer).
 5. Print the blockchain(Get the blockchain from the full node and print it in a structured format
    block by block.  Separate the fields of each block as well.
 6. Exit 
'''
# before doing the while loop, I need to send an initialization to the full node in order for the full node to have
# this address string '00' will be for Client_send program tell full node this client's address.
init = '00'
clientSocket.sendto(init.encode(), (serverName, serverPort))

while True:
    print(menu)  # displays the menu for the user
    choice = int(input('Choice: '))  # asks user to choose and gets input from user

    if choice == 1:  # user wishes to enter a new transaction
        # prompt user to select one of their accounts
        print(f"Select the Payer:\n1: {current_node_accts[0]}\n2: {current_node_accts[1]}")
        # tx_payee becomes the string representing the hex number for the account
        tx_payer_acct = current_node_accts[int(input('Choice: ')) - 1]
        # prompt user to select an account to receive user payment this lab instructions only allow us to send
        # instructions over to the other node in the network as opposed to between accounts on the same node
        print(f"Select the Payee:\n1. {other_node_accts[0]}\n2. {other_node_accts[1]}\n")
        # tx_payee becomes the string representing the hex number for the account
        tx_payee_acct = other_node_accts[int(input('Choice: ')) - 1]
        print("Enter the amount of payment in decimal.\n")
        tx_amount = int(input())
        tx_total = tx_amount + 2
        # updates dictionary containing acct balances according to what's in the file in case there are any changes
        get_acct_balances()

        # checks whether {Tx_amount + Tx_fee} would not exceed the current value of Unconfirmed_balance, then reduces
        # the Unconfirmed_balance by {Tx_amount + Tx_fee}.
        unconfirmed_bal = int(unconfirmed_acct_balances[tx_payer_acct], 16)
        if tx_total <= unconfirmed_bal:  # accessing the value in the dictionary using the key
            print(f"Tx: {tx_payer_acct} pays {tx_payee_acct} the amount of {tx_amount} BC.")
            unconfirmed_bal -= tx_total  # reduces the amount in the unconfirmed_balance for the acct
            unconfirmed_bal = hex(unconfirmed_bal)  # changes it to hexadecimal string with leading 0x
            unconfirmed_bal = unconfirmed_bal[2:]  # removes the 0x from the hex string
            unconfirmed_acct_balances[
                tx_payer_acct] = unconfirmed_bal.zfill(
                8)  # stores that amount back into the unconfirmed balance dictionary
            # tx is the string representing the entire transaction, tx_total will be an int so it needs to be
            # converted to a hex value and then a string
            tx_amount = hex(tx_amount)  # converts the transaction total to a hexadecimal string that includes 0x
            tx_amount = tx_amount[2:]  # removes the chars '0x' from the transaction total string
            tx = tx_payer_acct + tx_payee_acct + tx_amount.zfill(
                8)  # creates the 12 byte string that represents the transaction
            with open('Unconfirmed_T_A.txt', 'a') as f:  # opens the unconfirmed transaction file
                f.write(tx + "\n")  # appends the unconfirmed transaction to the file
            with open('balances_A.txt', 'w') as f:
                temp = current_node_accts[0] + ":" + unconfirmed_acct_balances[current_node_accts[0]] + ":" + \
                       confirmed_acct_balances[current_node_accts[0]] + "\n"
                f.write(temp)
                temp = current_node_accts[1] + ":" + unconfirmed_acct_balances[current_node_accts[1]] + ":" + \
                       confirmed_acct_balances[current_node_accts[1]] + "\n"
                f.write(temp)
            send_tx_to_node(tx)  # sends the unconfirmed transaction to the full node
        else:  # else the transaction total exceeds the remaining funds in the account
            print("Insufficient funds.")  # display to the console that their is insufficient funds in the acct for the
            # transaction
    elif choice == 2:  # display the current balance for each account
        # retrieve current confirmed balances and store in the confirmed_acct_balances dictionary above
        get_acct_balances()  # reads the latest acct balances from the file
        print('The current balance of the accounts are:\n')
        for key in confirmed_acct_balances:
            value = int(confirmed_acct_balances[key], 16)  # converts the value from a hex into an int
            print(f'\n{key} : {value} BC\n')  # displays the account and account balances in the format
            # account_num:balance
    elif choice == 3:  # print the unconfirmed transactions
        unconfirmed_tx_list = get_unconfirmed_txs()
        print('The unconfirmed transactions are:\n')
        for tx in unconfirmed_tx_list:  # for each transaction in the unconfirmed transaction list
            print(tx + '\n')  # display the transactions
    elif choice == 4:  # print the confirmed transactions
        confirmed_tx_list = get_confirmed_txs()
        print('The confirmed transactions are:')
        for tx in confirmed_tx_list:
            print(tx + '\n')
    elif choice == 5:  # print the blockchain
        # blockchain here should be a list
        blockchain = request_node_blockchain()  # blockchain will be the blockchain in the form of a single string
        display_block_chain(blockchain)
    elif choice == 6:  # exit
        break

clientSocket.close()  # closes the socket/port to the full node
