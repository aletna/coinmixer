import sys
import click
from . import jobcoin


def start(deposit_address, house_address, deposit_expiry, time_step):
    '''this starts the process for a particular use to initate the mixer'''

    receiving_addresses = getReceivingAddresses()

    click.echo(
        '\nYou may now send Jobcoins to address {deposit_address}. They '
        'will be mixed and sent to your destination address(es).'
         .format(deposit_address=deposit_address))

    choice = click.prompt(
        "\nWould you like to send the jobcoins through this application (1) or manually, e.g. using the api web interface (2)?\n\n(1) Send automatically\n(2) Send manually\n\nChoose one option",
        type=click.Choice(['1', '2']),
        show_default=False,
    )

    if choice == '1':
        # user sends automatically via the cli application
        res, msg = jobcoin.initMixer(
            receiving_addresses, deposit_address, house_address, send_here=True)

    if choice == '2':
        # user sends manually
        res, msg = jobcoin.initMixer(
            receiving_addresses, deposit_address, house_address, deposit_expiry, time_step)

    if not res:
        click.echo(
            "\nERROR: {}\nLet's try this again:\n".format(msg))
        start(deposit_address, house_address, deposit_expiry, time_step)

    return res


def getReceivingAddresses():
    '''This prompts the user to enter all addresses they want to send their balance of jobcoins to'''

    addresses = click.prompt(
        '\nPlease enter a comma-separated list of new, unused Jobcoin '
        'addresses where your mixed Jobcoins will be sent.',
        prompt_suffix='\n[blank to quit (warning: this will close the application)] > ',
        default='',
        show_default=False)

    if addresses.strip() == '':
        sys.exit(0)

    receiving_addresses = jobcoin.splitAddresses(addresses)

    for address in receiving_addresses:
        if not jobcoin.isValidAddress(address):
            print('\nOops, looks like {} is not a valid address. Please re-enter all addresses and make sure you enter a one word string of alphanumeric characters for each address.\n'.format(address))
            getReceivingAddresses()

    return receiving_addresses


def getSendAddress():
    '''This prompts the user to enter the address they will be sending their jobcoins from'''

    sender = click.prompt(
        '\nPlease enter an existing Jobcoin address that you will be transfering the funds from.',
        prompt_suffix='\n[blank to quit (warning: this will close the application)] > ',
        default='',
        show_default=False)

    send_address = sender.strip()

    if send_address == '':
        sys.exit(0)

    if not jobcoin.isValidAddress(send_address):
        print('\nOops, looks like your address is not valid. Please make sure you enter a one word string of alphanumeric characters.\n')
        getSendAddress()

    return send_address


def getAmount():
    '''This prompts the user to enter the amount of jobcoins they want to send'''

    amount = click.prompt(
        '\nPlease enter how many Jobcoins you want to send.',
        prompt_suffix='\n[blank to quit (warning: this will close the application)] > ',
        default='',
        show_default=False)

    if amount.strip() == '':
        sys.exit(0)

    if jobcoin.isValidPositiveNum(amount):
        return amount
    else:
        print('\nOops, looks like {} is not a valid positive number. Please try again.'.format(amount))
        getAmount()

