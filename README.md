# DripCompound
Automation to compound drip

This is some basic automation I put together to perform my daily drip compounding.

If you like this feel free to airdrop me some drip or send some BNB/BUSD to my wallet!

0x1007aaf4b214622155de89546486a070eb731dc0

## Configure the .env file

For every wallet you want to use, you must configure the <wallet_name>.env file

See `drip_wallet.env.example` for a full example

| Variable                    | Usage                                                                                                             | Example                        | Mandatory          |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------|--------------------------------|--------------------|
| PRIVATE_KEY                 | The private key of your wallet used to write                                                                      | PRIVATE_KEY=xxxxxxx            | Yes                |
| WALLET_FRIENDLY_NAME        | The friendly name of your wallet                                                                                  | WALLET_FRIENDLY_NAME=My Wallet | Yes                |
| PUSHOVER_API_KEY            | API key from your pushover.net account                                                                            | PUSHOVER_API_KEY=xxxx          | No                 |
| PUSHOVER_USER_KEY           | User key from your pushover.net account                                                                           | PUSHOVER_USER_KEY=xxx          | No                 |
| . IPERFORM_DRIP_COMPOUNDING | If set to True, will perform compounding. Default is not to compound and just test things like notifications etc. | PERFORM_DRIP_COMPOUNDING=True  | No - Default False |
| MAX_TRIES                   | Number of transaction retries on failure - Default of 1 means it will only try once                               | MAX_TRIES=2                    | No - Default 1     |


## Running the program

My preferred way of running stuff is in docker, makes it easy to ensure it runs everywhere! but you can also adapt this script to run from python with a little effort. If you are running it in native python - then you'll need to edit the code and import the file which has your wallet details in (``load_dotenv(dotenv_path="drip_wallet.env"``)

## Docker

First you'll need to build the image

```
docker build -f dockerfile -t dripcompound:1.0 .
```

Then run it using the following command

If you have multiple wallets, have a unique name for each docker image.

```
# docker start my_wallet_name || docker run -v /etc/localtime:/etc/localtime --env-file my_wallet_name.env --name my_wallet_name -d dripcompound:1.0
```

