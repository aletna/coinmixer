import time

from . import config
from . import prompts


class House:
    '''
        House class that will keep track of a given house account and the transactions it will need to do at any given moment.
        To make it harder to track which transaction came from which address I ensure that all payouts from the house are split evenly, alongside whatever amount is remaining.
            example: 
            - A sends 10 coins to the House, alongside 2 recipient addresses [C,D]
            - B sends 10 coins to the house, alongside 3 recipient addresses [E,F,G]

            then the house will proceed to:
            - send 3 coins to C
            - send 2 coins to C
            - send 3 coins to D
            - send 2 coins to D
            - send 3 coins to E
            - send 3 coins to F
            - send 3 coins to G

        address (str): this is the wallet address of the house account
        waitlist (list): this list keeps track of the balance and a list of receiving addresses that need to receive that balance
        lowest_split (float): this determines the maximum amount that the house will send to any address at once when it unloads (3 in the example above)
    '''

    def __init__(self, address):
        self.address = address
        self.waitlist = []
        self.lowest_split = None

    def getWaitlist(self):
        '''
            prints the current transactions that the house still needs to perform to unload its balance
        '''
        print('QUEUE:', self.waitlist)

    def addToWaitlist(self, txn_details):
        '''
            This adds another job for the house to perform at the point of unloading its balance.

            txn_details (dict): dictionary storing the balance that the house received and the recipient addresses stored in a list
        '''

        even_split = float(txn_details['amount']) / \
            len(txn_details['receiving_addresses'])

        # update the lowest_split value if necessary
        if len(self.waitlist) == 0:
            self.lowest_split = even_split
        else:
            self.lowest_split = min(self.lowest_split, even_split)

        self.waitlist.append(txn_details)
        print('ADDED', txn_details, 'to waitlist.\n\nlowest split:',
              self.lowest_split, '\n\n')

    def splitNumber(self, num, threshold):
        '''
            helper function to divide any balance into splits of equal size, plus its remainder

            num (float): the value that gets split
            threshold (flaot): the split value
        '''
        splits = int(num//threshold)
        remainder = num % threshold
        res = [threshold for i in range(splits)]
        if remainder > 0:
            res.append(remainder)
        return res

    def unloadHouse(self):
        '''
            This unloads the current balance of the house account by performing all the transactions from the house to the receiving addresses.
        '''

        print("\n\nUNLOADING HOUSE:\n\n")
        for job in self.waitlist:
            n = len(job['receiving_addresses'])
            even_split = float(job['amount'])/n

            # check if amounts need to be split further than just its even split to keep values amongs all transactions similar
            if even_split > self.lowest_split:
                for recipient in job['receiving_addresses']:
                    amountPieces = self.splitNumber(
                        even_split, self.lowest_split)
                    for piece in amountPieces:
                        print('\n\ntransferring {} coins to {}:'.format(
                            piece, recipient))
                        code, msg = transferCoins(
                            self.address, recipient, piece)
                        if code != 200:
                            print('\nERROR: {}\nLooks like we could not send {} jobcoins from {} to {}.\n'.format(
                                msg, piece, self.address, recipient))
            else:
                amnt = str(even_split)
                for recipient in job['receiving_addresses']:
                    print('\n\ntransferring {} coins to {}:'.format(
                        amnt, recipient))

                    code, msg = transferCoins(self.address, recipient, amnt)

                    if code != 200:
                        print('\nERROR: {}\nLooks like we could not send {} jobcoins from {} to {}.\n'.format(
                            msg, piece, self.address, recipient))


def initMixer(receiving_addresses, deposit_address, house_address, deposit_expiry=None, time_step=None, send_here=False):
    '''
        this initializes the jobcoin mixer

        receiving_addresses (list): list of strings of all the addresses that the coins should be sent to
        deposit_address (str): the deposit address
        house_address (str): the house address
        time_step (int): time in seconds between every check if a transaction to the deposit addres has been made
        deposit_expiry (int): Number of checks
        send_here (bool): indicator if the user makes the deposit themselves (False) or chooses to use the cli for it (True)

        returns a response object if all went well (else False), and a corresponding message
    '''

    if send_here:
        # if user chooses to automatically deposit the funds via the cli interface

        send_address = prompts.getSendAddress()
        amount = prompts.getAmount()

        balance, msg = depositCoins(send_address, deposit_address, amount)

        if balance:
            res, msg = sendToHouse(deposit_address, house_address,
                                   balance, receiving_addresses)
            return res, msg
        else:
            return False, msg

    else:
        # if user chooses to make the deposit on their own terms (e.g. via the web api interface)
        balance = trackDepositAddress(
            deposit_address, deposit_expiry, time_step)

        if balance:
            res, msg = sendToHouse(deposit_address, house_address,
                                   str(balance), receiving_addresses)
            return res, msg
        else:
            msg = "Your deposit address expired because we did not detect any incoming deposits."
            return False, msg


def isValidAddress(address):
    '''
        Address should be single word (i.e. no whitespaces in between characters) 
        Address should only contain alphanumeric characters

        returns Boolean corresponding to the address being valid (True) or invalid (False)
    '''

    # No empty string allowed
    if address == '':
        return False

    # only allow single word alphanumeric strings as valid addresses
    if any(not character.isalnum() for character in address.strip()):
        return False

    return True


def isValidPositiveNum(amount):
    '''
        returns True if amount is a valid number, else False
    '''
    return amount.replace('.', '', 1).isdigit()


def splitAddresses(addresses):
    '''takes in a string of comma separated addresses, splits them and returns them as a list.'''
    addressList = []
    for address in addresses.split(','):
        addressList.append(address.strip())

    return addressList


def trackDepositAddress(deposit_address, deposit_expiry, time_step):
    '''
        This tracks the deposit address for any incoming transfers. 
        As soon as it finds one, it returns the amount that was deposited.

        deposit_address (str): the deposit address
        time_step (int): time in seconds between every check if a transaction to the deposit addres has been made
        deposit_expiry (int): Number of checks
    '''
    counter = 0

    while counter < deposit_expiry:
        response = config.getAddress(deposit_address)

        print('You have {} seconds until your deposit address expires. Deposit Address: {}.'.format(
            (deposit_expiry-counter)*time_step, deposit_address))

        if response['transactions']:
            print('\nGreat, we successfully detected your deposit. It will be transferred to our House Account shortly. After mixing it with other balances, your balance will be sent to the desired addresses.\n')
            balance = response['balance']
            return balance

        time.sleep(time_step)
        counter += 1

    return False


def transferCoins(sender, recipient, amount):
    '''transfer n amount of coins from one address to another'''

    code, msg = config.postTransaction(sender, recipient, str(amount))

    if code == 200:
        return code, msg['status']

    if code == 422:
        return code, msg['error']


def depositCoins(send_address, deposit_address, amount):
    '''transfer n amount of coins from the user's address to the despoit address'''
    code, msg = transferCoins(send_address, deposit_address, amount)

    if code == 200:
        return amount, msg

    else:
        return False, msg


def sendToHouse(deposit_address, house_address, amount, receiving_addresses):
    '''
        sends the balance from a given deposit address to the house account and passes along the corresponding receiving addresses

        deposit_address (str): the deposit address
        house_address (str): the house address
        amount (str): the amount to be transferred to the house
        receiving_addresses (list): list of strings of all the addresses that the coins should be sent to
    '''
    code, msg = transferCoins(deposit_address, house_address, amount)

    if code == 200:
        return ({'amount': amount, 'receiving_addresses': receiving_addresses}), msg

    else:
        return False, msg
