#!/usr/bin/env python
import uuid
import sys

import click

from jobcoin import jobcoin
from jobcoin import prompts

@click.command()
@click.argument('wait_period', default=2)
@click.argument('time_step', default=5)
@click.argument('deposit_expiry', default=12)
@click.argument('house_address', default='HOUSE')
def main(wait_period,time_step,deposit_expiry,house_address):
    """
        This launches the application. 
        As of now all transactions will only be mixed as long as the application remains running until the end 
        because all metadata is stored locally.

        wait_period (int): Number of users using the same mixing pool until House gets unloaded
        time_step (int): time in seconds between every check if a transaction to the deposit addres has been made
        deposit_expiry (int): Number of checks
        house_address (str): The address of the House Account

    """

    click.echo('Welcome to the Jobcoin mixer!')

    period = 0  # counter

    house = jobcoin.House(house_address)

    while period < wait_period:
        click.echo('Transaction {} out of {} initiated.'.format(
            period+1, wait_period))

        # generate unique deposit_address for one time use
        deposit_address = uuid.uuid4().hex

        # initiate the mixer
        res = prompts.start(deposit_address, house_address,
                            deposit_expiry, time_step)

        if res:
            # add the receiving addresses and the exact amount to the House class
            house.addToWaitlist(res)
        else:
            # if not res, something went wrong
            sys.exit(0)

        period += 1

    # distribute all the amounts to the corresponding receiving addresses
    print('\n\n-\n\n')
    house.unloadHouse()
    print('Successfully mixed all transactions!')

    sys.exit(0)



if __name__ == '__main__':
    sys.exit(main())
