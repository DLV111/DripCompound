from web3 import Web3
import os
import logging
import sys
import time
from pushover import Client
from utils import eth2wei, wei2eth, read_json_file, to_checksum
from dotenv import load_dotenv
import traceback
import argparse
import configparser


DRIP_TOKEN_ADDRESS = "0xFFE811714ab35360b67eE195acE7C10D93f89D8C"
DRIP_FAUCET_ABI_FILE = "./abis/Faucet.json"
VERSION = '1.1'

class DripCompoundClass:
    def __init__(self, txn_timeout=120, gas_price=5, rpc_host="https://bsc-dataseed.binance.org:443",rounding=3, **kwargs):

        self.config_args = self.argparser()
        self.config = self.readInConfig(self.config_args)
        self.validateConfig()

        logging.info('"%s" Selected for processing' % self.wallet_friendly_name)
        self.rounding = rounding
        self.txn_timeout = txn_timeout
        self.gas_price = gas_price
        self.rpc_host = rpc_host
        self.InitDripBalance = 0

        # Init the pushover client if defined
        self.PushOverClientInit()

        # Initialize web3, and load the smart contract objects.
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_host))
        self.account = self.w3.eth.account.privateKeyToAccount(self.private_key)
        self.address = self.account.address
        self.w3.eth.default_account = self.address

        self.drip_contract = self.w3.eth.contract(
            to_checksum(DRIP_TOKEN_ADDRESS),
            abi=read_json_file(DRIP_FAUCET_ABI_FILE))

        self.getDripBalance()
        self.getAvailableClaims()
        self.getBNBbalance()
        self.checkAvailableBNBBalance()

    def validateConfig(self):
        if self.private_key == "":
            logging.info("private_key is not set")
            sys.exit(1)
        if self.wallet_friendly_name == "":
            logging.info("wallet_friendly_name is not set")
            sys.exit(1)
        if self.perform_drip_compounding == "":
            logging.info("perform_drip_compounding is not set")
            sys.exit(1)
        if self.max_tries == "":
            logging.info("max_tries is not set")
            sys.exit(1)
        if self.max_tries_delay == "":
            logging.info("max_tries_delay is not set")
            sys.exit(1)
        if self.min_bnb_balance == 'False':
            self.min_bnb_balance = False
        else:
            self.min_bnb_balance = float(self.min_bnb_balance)
        if self.pushover_api_key == 'False':
            self.pushover_api_key = False
        if self.pushover_user_key == 'False':
            self.pushover_user_key = False


    def readInConfig(self, config_vars):
        config_file = config_vars['config_file']
        if config_vars['new_config'] == True:
            self.createDefaultConfig(config_file)
        try:
            config = configparser.ConfigParser({'min_bnb_balance': False, 'pushover_api_key': False, 'pushover_user_key': False}, inline_comment_prefixes="#")
            config.read(config_file)
            # [default]
            self.private_key = config['default']['private_key']
            self.wallet_friendly_name = config['default']['wallet_friendly_name']
            self.pushover_api_key = config['default']['pushover_api_key']
            self.pushover_user_key = config['default']['pushover_user_key']
            # [drip]
            self.perform_drip_compounding = config['drip']['perform_drip_compounding']
            self.max_tries = int(config['drip']['max_tries'])
            self.max_tries_delay = int(config['drip']['max_tries_delay'])
            self.min_bnb_balance = config['default']['min_bnb_balance']
        except:
            logging.info('There was an error opening the config file %s' % config_file)
            logging.info('If this config file does not exist yet, run with -n to create')
            print(traceback.format_exc())
            sys.exit(2)

    def createDefaultConfig(self, config_file):
        if os.path.exists(config_file):
            logging.info("File '%s' already exists, not overwriting" % config_file)
        else:
            config = configparser.ConfigParser()
            config['default'] = {
                'private_key': '  # Mandatory - gives write access to your wallet KEEP THIS SECRET!!',
                'wallet_friendly_name': 'Test Drip Wallet  # Mandatory - Friendly name to display in output',
                '#pushover_api_key': '  # Optional - If you have an account on https://pushover.net/ you can set this up to send notfications to your phone.',
                '#pushover_user_key': '  # Optional - If you have an account on https://pushover.net/ you can set this up to send notfications to your phone.'
                }
            config['drip'] = {
                'perform_drip_compounding': 'False  # Set to true to actually perform compounding',
                'max_tries': '2  # Number of retries on a transaction failure - will cost gas each time. 2 means try once more if there is a failure.',
                'max_tries_delay': '180  # Seconds between retries on a transaction failure. Wait this long before trying again.',
                '#min_bnb_balance': '0.02  # Optional -  Min BNB Balance to have in your wallet to allow compounding action - default 0.02'
            }
            # Open new file to write
            try:
                with open(config_file, "w") as f:
                    config.write(f)
                    logging.info("A new template file has been created at '%s'. Please review and update" % config_file)
                    sys.exit(0)
            except IOError:
                logging.info('Unable to write template file')
                sys.exit(5)


    def argparser(self):
        import textwrap
        description = textwrap.dedent('''
            Automatic Drip Compounding

            You can use this script to compound drip automatically.
            See the readme at https://github.com/DLV111/DripCompound for more details.
            If you like this please consider buying me a beer/coffee
        ''')
        parser = argparse.ArgumentParser(description=description,
                                        formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-n", "--new-config", action="store_true", help="Create a new config file at the location specified - If file exists no action is taken")
        parser.add_argument("config_file", help="Path to the config file")
        args = parser.parse_args()
        return(vars(args))

    def getDripBalance(self):
        self.userInfo = self.drip_contract.functions.userInfo(self.address).call()
        self.DripBalance = round(wei2eth((self.userInfo[2])),self.rounding)
        if self.InitDripBalance == 0:
            self.InitDripBalance = self.DripBalance

    def getDripBalanceIncrease(self):
        return (self.DripBalance - self.InitDripBalance)

    def getAvailableClaims(self):
        self.claimsAvailable = round(wei2eth(self.drip_contract.functions.claimsAvailable(self.address).call()),self.rounding)

    def getBNBbalance(self):
        self.BNBbalance = self.w3.eth.getBalance(self.address)
        self.BNBbalance = round(wei2eth(self.BNBbalance),self.rounding)

    def checkAvailableBNBBalance(self):
        logging.info('BNB Balance is %s' % round(self.BNBbalance,self.rounding))
        if self.min_bnb_balance:  # Do we have a min balance defined?
            if self.BNBbalance < self.min_bnb_balance:
                msg = 'Your current BNB balance(%s) is below min required (%s) for %s' % (self.BNBbalance, self.min_bnb_balance, self.wallet_friendly_name)
                logging.info(msg)
                self.sendMessage('BNB Balance issue',msg)
                sys.exit()

    def nonce(self):
        return self.w3.eth.getTransactionCount(self.address)

    def compoundDrip(self):
        max_tries = self.max_tries
        retry_sleep = self.max_tries_delay
        default_sleep_between_actions=30  # This ensures enough time for the network to settle and provide accurate results.

        remaining_retries = max_tries
        txn_receipt = None
        if self.perform_drip_compounding.lower() == "true":
            for _ in range(max_tries):
                try:
                    remaining_retries+=-1
                    tx = self.drip_contract.functions.roll().buildTransaction({
                                        "gasPrice": eth2wei(self.gas_price, "gwei"), "nonce": self.nonce()})
                    signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
                    txn = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                    txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
                    if txn_receipt and "status" in txn_receipt and txn_receipt["status"] == 1:
                        logging.info("Transaction Successful: %s" % (self.w3.toHex(txn)))
                        time.sleep(default_sleep_between_actions)
                        self.getDripBalance()
                        logging.info("Updated Drip balance is: %s (Increase %s) - tx %s" % (self.DripBalance,self.getDripBalanceIncrease(),self.w3.toHex(txn)))
                        self.sendMessage("Compounding Complete","Updated Balance %s (Increase %s) - tx %s" % (self.DripBalance,self.getDripBalanceIncrease(),self.w3.toHex(txn)))
                        break
                    else:
                        logging.info("Compounding Failed. %s retries remaining (%s seconds apart). Transaction status '%s' - tx %s" % (remaining_retries,retry_sleep,txn_receipt["status"],self.w3.toHex(txn)))
                        self.sendMessage("Compounding Failed","%s retries remaining (%s seconds apart). Transaction status '%s' - tx %s" % (remaining_retries,retry_sleep,txn_receipt["status"],self.w3.toHex(txn)))
                        logging.debug(txn_receipt)
                        if remaining_retries != 0:
                            time.sleep(retry_sleep)
                except:
                    logging.info(traceback.format_exc())
                    time.sleep(default_sleep_between_actions)
        else:
            logging.info("Compounding is set to False, only outputting some messages")
            self.getDripBalance()
            logging.info("Updated Drip balance is: %s (Increase %s)" % (self.DripBalance,self.getDripBalanceIncrease()))
            self.sendMessage("Compounding Complete","Updated Balance %s (Increase %s) - tx %s" % (self.DripBalance,self.getDripBalanceIncrease(),'test:aaaabbbbccccdddd'))



    def sendMessage(self, title_txt, body):
        if self.pushover_api_key and self.pushover_user_key:
            title_txt = ("%s: %s" % (self.wallet_friendly_name,title_txt) )
            logging.info("PushOver Notification\n\rTitle: %s\n\rBody: %s" % (title_txt,body))
            self.client.send_message(body, title=title_txt)

    def PushOverClientInit(self):
        if self.pushover_api_key and self.pushover_user_key:
            self.client = Client(self.pushover_user_key, api_token=self.pushover_api_key)

def main():
    # Setup logger.
    log_format = '%(asctime)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)
    logging.info('Drip Automation v%s Started!' % VERSION)
    logging.info('----------------')

    dripwallet = DripCompoundClass()

    logging.info("Current Balance %s" % dripwallet.DripBalance)
    logging.info("Available to compound %s" % dripwallet.claimsAvailable)
    dripwallet.sendMessage("Drip Compounding","Current Balance %s - Compound %s" % (dripwallet.DripBalance,dripwallet.claimsAvailable))

    # Actually do the compound step
    dripwallet.compoundDrip()


if __name__ == "__main__":
   main()
