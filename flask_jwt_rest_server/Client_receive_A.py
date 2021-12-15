"""
Programmer: Kelyn Kirt
Algorithm for Client_receive_A program
In this program, the client is in the role of the server.  The full node (as a client)
connects to this program (as a server).  You should bind this program to a different port number, e.g. 20000
for A.

In an infinite loop, the program listens to the full node.  Once it receives a confirmed Tx, it checks whether one
of its accounts is a Payer or a Payee in the Tx.  This is used for confirmed transactions, which have been entered
to the blockchain.
a.  If it is a Payer:
    1. It makes sure that the Tx is available in its Unconfirmed_T.txt
    2. It reduces the {Tx_amount + Tx_fee} from the account's Confirmed_balance.
    3. It removes the Tx from its Unconfirmed_T.txt
    4. It appends the Tx to its Confirmed_T.txt
b.  If it is a Payee:
    1. It adds the Tx_amount to the account's Confirmed_balance and Unconfirmed_balance.
    2. It appends the Tx to its Confirmed_T.txt
"""
from socket import *  # import socket package

current_node_accts = ["A0000001", "A0000002"]  # used to reference the accounts for this node
other_node_accts = ["B0000001", "B0000002"]  # used to reference the accounts for the 2nd node
unconfirmed_acct_balances = {
    'A0000001': '000003E8',  # this amounts to 1000 BC
    'A0000002': '000003E8'  # this amounts to 1000 BC
}
# initialize the confirmed balances dictionary
confirmed_acct_balances = {
    'A0000001': '000003E8',  # this amounts to 1000 BC
    'A0000002': '000003E8'  # this amounts to 1000 BC
}

serverPort = 10001
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))  # binds the client program to the port number 10000


# retrieve info for acct balances from the respective files
def get_acct_balances():
    with open('balances_A.txt', 'r') as f:  # opens the txt file storing the balances in read only mode
        # f.readlines() creates a list of all the lines in the file (including \n)
        acct_list = f.readlines()  # reads all lines within the file and store it as a list, each line includes "\n"
        # char
        for line in acct_list:  # for each line that is stored in the list, note lines contain ":" char separating
            # each section so line contains a list separated by ":" characters in the format e.g.,
            # 'Account1:Unconfirmed_balance:Confirmed_balance\n' separate the list into parts e.g., [Account1,
            # Unconfirmed_balance, Confirmed_balance]
            temp_list = line.split(":")
            # traditional for loop in python
            for index, item in enumerate(temp_list):  # only using this to remove any "\n" chars or whitespace in the
                # list
                temp_list[index] = item.strip()
            # updates the current confirmed/unconfirmed account balances in respective dictionaries according to
            # whats in the accts for first line read, temp_list[0] will be for the first payer's acct for the 2nd
            # line read, temp_list[0] will be for the 2nd payer's acct
            unconfirmed_acct_balances[temp_list[0]] = temp_list[1]  # balances are stored in hex format for this file
            # except without the leading 0x
            confirmed_acct_balances[temp_list[0]] = temp_list[2]


# sets the balances in the balances file
def set_balances():
    with open('balances_A.txt', 'w') as f:  # open the balances file, should completely rewrite the txt file
        # will be in format:
        # Account_1:Unconfirmed:Confirmed
        # Account_2:Unconfirmed:Confirmed
        temp = current_node_accts[0] + ":" + unconfirmed_acct_balances[current_node_accts[0]] + ":" + \
            confirmed_acct_balances[current_node_accts[0]] + "\n"
        f.write(temp)
        temp = current_node_accts[1] + ":" + unconfirmed_acct_balances[current_node_accts[1]] + ":" + \
            confirmed_acct_balances[current_node_accts[1]] + "\n"
        f.write(temp)


# instead of just setting the balances, this function adds the specified amount to the specified receiving account
def add_to_balances(amount, payee):
    with open('balances_A.txt', 'w') as f:  # open the balances file, should completely rewrite the txt file
        # will be in format:
        # Account_1:Unconfirmed:Confirmed
        # Account_2:Unconfirmed:Confirmed
        if current_node_accts[0] == payee:  # if it is account 1
            # add amount to both unconfirmed and confirmed balances
            unconfirmed_bal = int(unconfirmed_acct_balances[current_node_accts[0]],
                                  16)  # converts the hex string to an int
            confirmed_bal = int(confirmed_acct_balances[current_node_accts[0]], 16)
            unconfirmed_bal += amount  # adds the amount in decimal form to the unconfirmed balance (in decimal)
            confirmed_bal += amount  # adds the amount in decimal form to the confirmed balance (in decimal)
            unconfirmed_bal = hex(unconfirmed_bal) # converts the unconfirmed balance from decimal back to
            # a hex string format
            confirmed_bal = hex(confirmed_bal)  # converts the confirmed balance from decimal back to a hex
            # string format
            # need to store the hex numbers without the 0x lead
            temp = current_node_accts[0] + ":" + unconfirmed_bal[2:].zfill(8) + ":" + confirmed_bal[2:].zfill(8) + "\n"
        else:  # if it is not account 1, then just set temp to the same info that was stored previously in the account
            temp = current_node_accts[0] + ":" + unconfirmed_acct_balances[current_node_accts[0]] + ":" + \
                   confirmed_acct_balances[current_node_accts[0]] + "\n"

        f.write(temp)  # writes the first line in the balances txt file

        if current_node_accts[1] == payee:  # if it is account 2
            # add amount to both unconfirmed and confirmed balances
            unconfirmed_bal = int(unconfirmed_acct_balances[current_node_accts[1]],
                                  16)  # converts the hex string to an int, no need for the leading 0x for this to work
            confirmed_bal = int(confirmed_acct_balances[current_node_accts[1]], 16)
            unconfirmed_bal += amount  # adds the amount in decimal form to the unconfirmed balance (in decimal)
            confirmed_bal += amount  # adds the amount in decimal form to the confirmed balance (in decimal)
            unconfirmed_bal = hex(unconfirmed_bal)  # converts the unconfirmed balance from decimal back to
            # a hex string format
            confirmed_bal = hex(confirmed_bal)  # converts the confirmed balance from decimal back to a hex
            # string format
            # need to store the hex numbers without the 0x lead
            temp = current_node_accts[1] + ":" + unconfirmed_bal[2:].zfill(8) + ":" + confirmed_bal[2:].zfill(8) + "\n"
        else:  # if it is not account 1, then just set temp to the same info that was stored previously in the account
            temp = current_node_accts[1] + ":" + unconfirmed_acct_balances[current_node_accts[0]] + ":" + \
                   confirmed_acct_balances[current_node_accts[1]] + "\n"

        f.write(temp)  # writes the second line in the balances txt file


# gets the payer account represented as a hex number w/o the leading 0x from the transaction received from the
# attached full node
def get_payer(transaction):
    payer = ''  # initializes the payer variable to empty string
    for index in range(0, 8):  # iterates through index numbers 0 to 7   so excludes 8
        payer += transaction[index]  # add current char being examined to the payer string
    return payer  # return the payer as a hex string


# gets the payee account represented as a hex number w/o the leading 0x from the transaction received from the
# attached full node
def get_payee(transaction):
    payee = ''  # initializes the payer variable to empty string
    for index in range(8, 16):  # iterates through index numbers 8 to 15    so excludes 16
        payee += transaction[index]  # add current char being examined to the payer string
    return payee  # returns the payee as a hex string


def get_amount(transaction):
    amount = ''  # initializes the mount variable to empty string
    for index in range(16, 24):  # iterates through the index numbers 16 to 23   so excludes 24
        amount += transaction[index]  # add current char being examined to the amount string
    return amount  # returns the amount as a hex string


# get the unconfirmed transactions from the unconfirmed transaction txt file
def get_unconfirmed_txs():
    with open('Unconfirmed_T_A.txt', 'r') as f:  # open the unconfirmed transaction txt file
        # f.readlines() creates a list of all the lines in the file (including \n)
        unconfirmed_tx_list = f.readlines()
        # remove unnecessary whitespace, including "\n" from the list
        for index, line in enumerate(unconfirmed_tx_list):
            unconfirmed_tx_list[index] = line.strip()

        return unconfirmed_tx_list  # return the unconfirmed transactions as a list of transactions


# writes the unconfirmed transactions to the unconfirmed transaction file
# parameter is a list
def set_unconfirmed_txt(unconfirmed_txs):
    with open('Unconfirmed_T_A.txt', 'w') as f:  # open the unconfirmed transaction file
        for tx in unconfirmed_txs:  # for each of the transaction in unconfirmed transaction list
            f.write(tx + "\n")  # write it to the file


# appends a transaction to the confirmed transactions txt file
def append_to_confirmed_tx_file(transaction):
    with open('Confirmed_T_A.txt', 'a') as f:  # opens the file containing the confirmed transactions
        f.write(transaction + "\n")  # appends/writes the transaction to the file


'''In this program, the client is in the role of the server.  The full node (as a client)
connects to this program (as a server).  

In an infinite loop, the program listens to the full node.  Once it receives a confirmed Tx, it checks 
whether one of its accounts is a Payer or a Payee in the Tx.

'''
while True:
    # accept a connection, store info re: connection into variables.  2048 bytes of info max per connection
    transaction, clientAddress = serverSocket.recvfrom(2048)
    # decode the message and store it into the transaction variable
    # !!!! MAY NEED TO PUT THIS INTO A WHILE LOOP UNTIL 'EOF' IS ENCOUNTERED !!!
    transaction = transaction.decode()
    # the first 3 bits will be the confirmed transaction from the full node so ignore the first 3 bits
    # for this assignment, the job of making sure that the full node is sending the right communication
    # to the right client will be the responsibility of the full node
    # transaction = transaction[3:]  # line not needed
    get_acct_balances()  # acct balances are listed in the dictionaries with global scope
    # message will be in the format of a transaction where a transaction is a 12 byte-hex for example:
    # A0000001B00000010000000E with payer payee amount joined as one string
    if not transaction == 'EOF':
        payer = get_payer(transaction)
        payee = get_payee(transaction)
        amount = int(get_amount(transaction), 16)  # convert the hex amount into an integer
        # If it is a payer from one of the accounts
        if any(payer in acct for acct in current_node_accts):
            # Make sure that the Tx is available in its Unconfirmed_T.txt
            # get list of Unconfirmed_T_A.txt
            unconfirmed_txs = get_unconfirmed_txs()  # returns a list of the unconfirmed transactions
            # if the transaction is in the list of unconfirmed transactions
            if any(transaction in tx for tx in unconfirmed_txs):
                # Reduce the {Tx_amount + Tx_fee} from the account's Confirmed_balance.
                confirmed_bal = int(confirmed_acct_balances[payer], 16)
                confirmed_bal -= (amount + 2)  # subtract total from confirmed balance
                confirmed_bal = hex(confirmed_bal)  # convert confirmed balance back into a hex string
                confirmed_bal = confirmed_bal[2:]  # remove the '0x' chars from the hex string
                # store the hex string back into the respective confirmed balances dictionary
                confirmed_acct_balances[payer] = confirmed_bal.zfill(8)
                # Repost in the file for balances
                set_balances()
                # Remove the Tx from its Unconfirmed_T.txt
                unconfirmed_txs.remove(transaction)
                # Rewrite to the Unconfirmed_T.txt file
                set_unconfirmed_txt(unconfirmed_txs)
                # Append the Tx to its Confirmed_T.txt
                append_to_confirmed_tx_file(transaction)
        # if it is a payee (receiving payment) from one of the accounts
        if any(payee in acct for acct in current_node_accts):
            # Add the Tx_amount to the account's Confirmed_balance and Unconfirmed_balance.
            add_to_balances(amount, payee)
            get_acct_balances()  # used to keep the acct balances in the file up to date, may not be necessary
            # Append the Tx to its Confirmed_T.txt
            append_to_confirmed_tx_file(transaction)
