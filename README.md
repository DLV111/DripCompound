# DripCompound
Automation to compound drip

This is some basic automation I put together to perform my daily drip compounding.

If you like this please buy me a coffee &/or beer :-) - Airdrop some DRIP or send some BNB/BUSD to my wallet address

`0x1007aaf4b214622155de89546486a070eb731dc0`

If you have any questions you can reach me at https://t.me/Zobah111 

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
| MIN_BNB_BALANCE             | Min BNB balance to have in your wallet to perform compounding. If less than this it will not perform any actions               | MIN_BNB_BALANCE=0.05            | No - Default 0.02  |


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

### Cron usage example

Run at 9 am every day

```
0 9 * * * docker start my_docker_run_name || docker run -v /etc/localtime:/etc/localtime --env-file /path/to/my/wallet_info.env --name my_docker_run_name -d dripcompound:1.0
```

### View the logs

```
$ docker logs -f drip_test
2022-04-20 21:57:14,248: Dripping Work v1.0 Started!
2022-04-20 21:57:14,248: ----------------
2022-04-20 21:57:14,248: "My Drip Wallet" Selected for processing
2022-04-20 21:57:15,643: BNB Balance is x.xxx
2022-04-20 21:57:15,643: Current Balance xx.xxx
2022-04-20 21:57:15,643: Available to compound xx.xxx
PushOver Notification
Title: My Drip Wallet: Drip Compounding
Body: Current Balance xx.xxx - Compound x.xxx
2022-04-20 21:57:16,703: Compounding is set to False, only outputting some messages
2022-04-20 21:57:16,997: Updated Drip balance is: xx.xxx (Increase 0.000)  <-- Note on False this will alway be 0
PushOver Notification
Title: My Drip Wallet: Compounding Complete
Body: Updated Balance xx.xxx (Increase 0.000) - tx test:aaaabbbbccccdddd
```

## Docker Tips

If you update your env file, make sure you delete the old image eg

```
docker rm my_docker_run_name
```

If you want to remove the image every time - use the ``--rm`` command in your docker run - If you do this you won't get a log history - it'll be fresh logs every time - can be useful for testing and the likes!