from web3 import Web3
import os
import logging
import sys
import time
from pushover import Client
from utils import eth2wei, wei2eth, pancakeswap_api_get_price, read_json_file, to_checksum
from dotenv import load_dotenv

DRIP_TOKEN_ADDRESS = "0xFFE811714ab35360b67eE195acE7C10D93f89D8C"
DRIP_FAUCET_ABI_FILE = "./abis/Faucet.json"
VERSION = '0.3'

class DripCompundClass:
    def __init__(self, perform_compounding=False, txn_timeout=120, gas_price=5, rpc_host="https://bsc-dataseed.binance.org:443",min_balance=0.015, rounding=3, **kwargs):

        MANDATORY_ENV_VARS = ["PRIVATE_KEY",'WALLET_FRIENDLY_NAME']

        for var in MANDATORY_ENV_VARS:
            if var not in os.environ:
                raise EnvironmentError("Failed because '{}' env var is not set.".format(var))

        self.private_key = os.getenv('PRIVATE_KEY')
        self.wallet_friendly_name = os.getenv('WALLET_FRIENDLY_NAME')
        self.perform_write_tx = perform_compounding # By default don't do the compounding, just display stuff.
        logging.info('"%s" Selected for processing' % self.wallet_friendly_name)
        self.rounding = rounding
        self.min_balance = min_balance
        self.txn_timeout = txn_timeout
        self.gas_price = gas_price
        self.rpc_host = rpc_host
        self.InitDripBalance = 0

        # Init the pushover client if defined
        self.pushover_api_key = os.getenv('PUSHOVER_API_KEY', False)
        self.pushover_user_key = os.getenv('PUSHOVER_USER_KEY', False)
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
        if self.BNBbalance > self.min_balance:
            logging.info('BNB Balance is %s' % round(self.BNBbalance,self.rounding))
        else:
            logging.info('Your current BNB balance(%s) is below min required (%s)' % (self.BNBbalance, self.min_balance))
            self.sendMessage('BNB Balance issue','Your current BNB balance(%s) is below min required (%s) for %s' % (self.BNBbalance, self.min_balance, self.wallet_friendly_name))
            sys.exit()

    def nonce(self):
        return self.w3.eth.getTransactionCount(self.address)

    def compundDrip(self):
        if self.perform_write_tx.lower() == "true":
            tx = self.drip_contract.functions.roll().buildTransaction({
                                "gasPrice": eth2wei(self.gas_price, "gwei"), "nonce": self.nonce()})

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            txn = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            logging.info("Transaction: %s" % (self.w3.toHex(txn)))
            time.sleep(10)
            self.getDripBalance()
            logging.info("Updated Drip balance is: %s (Increase %s)" % (self.DripBalance,self.getDripBalanceIncrease()))
            self.sendMessage("Compounding Complete","Updated Balance %s (Increase %s) - tx %s" % (self.DripBalance,self.getDripBalanceIncrease(),self.w3.toHex(txn)))
        else:
            logging.info("Compunding is set to False, only outputting some messages")
            self.getDripBalance()
            logging.info("Updated Drip balance is: %s (Increase %s)" % (self.DripBalance,self.getDripBalanceIncrease()))
            self.sendMessage("Compounding Complete","Updated Balance %s (Increase %s) - tx %s" % (self.DripBalance,self.getDripBalanceIncrease(),'test:aaaabbbbccccdddd'))



    def sendMessage(self, title_txt, body):
        if self.pushover_api_key and self.pushover_user_key:
            title_txt = ("%s: %s" % (self.wallet_friendly_name,title_txt) )
            print("PushOver Notification\n\rTitle: %s\n\rBody: %s" % (title_txt,body))
            self.client.send_message(body, title=title_txt)

    def PushOverClientInit(self):
        if self.pushover_api_key and self.pushover_user_key:
            self.client = Client(self.pushover_user_key, api_token=self.pushover_api_key)

    def setWalletFriendlyName(self,wallet_name="Default Wallet"):
        self.wallet_name = wallet_name


def main():
    # Setup logger.
    log_format = '%(asctime)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)
    logging.info('Dripping Work v%s Started!' % VERSION)
    logging.info('----------------')

    # Import the env file we're using for testing - if running from CLI - we use docker so don't need it.
    # load_dotenv(dotenv_path="drip_wallet.env")

    perform_compounding = os.environ.pop('PERFORM_DRIP_COMPOUNDING', "False")

    dripwallet = DripCompundClass(perform_compounding)

    logging.info("Current Balance %s" % dripwallet.DripBalance)
    logging.info("Available to compound %s" % dripwallet.claimsAvailable)
    dripwallet.sendMessage("Drip Compounding","Current Balance %s - Compound %s" % (dripwallet.DripBalance,dripwallet.claimsAvailable))

    # Actually do the compound step
    dripwallet.compundDrip()

main()
