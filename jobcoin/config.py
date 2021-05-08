import sys
import requests

API_BASE_URL = 'https://jobcoin.gemini.com/irrigate-ultimatum/api'
API_ADDRESS_URL = '{}/addresses'.format(API_BASE_URL)
API_TRANSACTIONS_URL = '{}/transactions'.format(API_BASE_URL)


def getAddress(address):
    '''
        This takes in a jobcoin string address as a parameter 
        and returns its jobcoin balance and transaction history
    '''
    response = requests.get("{}/{}".format(API_ADDRESS_URL, address))
    return response.json()


def postTransaction(sender, recipient, amount):
    print('\nPOST TRANSACTION: \n\nFrom: {}\nTo: {}\nAmount: {}'.format(
        sender, recipient, amount))
    data = {
        "fromAddress": sender,
        "toAddress": recipient,
        "amount": amount
    }
    response = requests.post(API_TRANSACTIONS_URL, data=data)

    # can return response.status_code of 200 or 422
    # in both cases, we will pass on the status code and message
    return response.status_code, response.json()

    return
