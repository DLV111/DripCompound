# DripCompound
Automation to compound drip

This is some basic automation I put together to perform my daily drip compounding.

If you like this please buy me a coffee &/or beer :-) - Airdrop some DRIP or send some BNB/BUSD to my wallet address

`0x1007aaf4b214622155de89546486a070eb731dc0`

If you have any questions you can reach me at https://t.me/Zobah111 or just say thanks :-)

You can run the script at any time to get the help guide

```
$ /bin/python3 drip_compound.py -h
2022-04-30 14:25:32,838: Drip Automation v1.1 Started!
2022-04-30 14:25:32,838: ----------------
usage: drip_compound.py [-h] [-n] config_file

Automatic Drip Compounding

You can use this script to compound drip automatically.
See the readme at https://github.com/DLV111/DripCompound for more details.
If you like this please consider buying me a beer/coffee

positional arguments:
  config_file       Path to the config file

optional arguments:
  -h, --help        show this help message and exit
  -n, --new-config  Create a new config file at the location specified - If file exists no action is taken
```

## Configure the .ini file

This file has a prescribed format of the following. To create the default layout pass in -n to the script.

Update the config and follow the guidance in the template

```
[default]
private_key =   # Mandatory - gives write access to your wallet KEEP THIS SECRET!!
wallet_friendly_name = Test Drip Wallet  # Mandatory - Friendly name to display in output
#pushover_api_key =   # Optional - If you have an account on https://pushover.net/ you can set this up to send notfications to your phone.
#pushover_user_key =   # Optional - If you have an account on https://pushover.net/ you can set this up to send notfications to your phone.

[drip]
perform_drip_compounding = False  # Set to true to actually perform compounding
max_tries = 2  # Number of retries on a transaction failure - will cost gas each time. 2 means try once more if there is a failure.
max_tries_delay = 180  # Seconds between retries on a transaction failure. Wait this long before trying again.
#min_bnb_balance = 0.02  # Optional -  Min BNB Balance to have in your wallet to allow compounding action - default 0.02
```

### Python

```
/bin/python3 drip_compound.py /path/to/my_wallet_details.ini -n
```

### Docker

Note: Make sure to use --rm on this one, as its just to create the wallet config

```
docker run --rm -v /etc/localtime:/etc/localtime -v /path/to/drip_configs/:/config/ --name my_wallet_name -d dripcompound:1.1 /config/my_wallet_name.ini -n
```

## Running the program

My preferred way of running stuff is in docker, makes it easy to ensure it runs everywhere! but you can also adapt this script to run from python directly.

### Python

```
/bin/python3 drip_compound.py /path/to/my_wallet_details.ini
```

### Docker

First you'll need to build the image

```
docker build -f dockerfile -t dripcompound:1.1 .
```

Then run it using the following command

If you have multiple wallets, have a unique name for each docker image.

This will start an existing docker image, or create a new one if one does not exist.

```
docker start my_wallet_name || docker run -v /etc/localtime:/etc/localtime  -v /path/to/configs/:/config/ --name my_wallet_name -d dripcompound:1.1 /config/my_wallet_details.ini
```

### Cron usage example

Run at 9 am every day

```
0 9 * * * docker start my_wallet_name || docker run -v /etc/localtime:/etc/localtime  -v /path/to/configs/:/config/ --name my_wallet_name -d dripcompound:1.1 /config/my_wallet_details.ini
```

### View the logs

```
$ docker logs -f drip_test
2022-04-30 14:12:02,175: Drip Automation v1.1 Started!
2022-04-30 14:12:02,175: ----------------
2022-04-30 14:12:02,176: "My Drip Wallet" Selected for processing
2022-04-30 14:12:03,376: BNB Balance is x.xxx
2022-04-30 14:12:03,376: Current Balance xx.xxx
2022-04-30 14:12:03,376: Available to compound xx.xxx
2022-04-30 14:12:03,376: PushOver Notification
Title: My Drip Wallet: Drip Compounding
Body: Current Balance xx.xxx - Compound x.xxx
2022-04-30 14:12:04,426: Compounding is set to False, only outputting some messages
2022-04-30 14:12:04,730: Updated Drip balance is: xx.xxx (Increase 0.000)  <-- Note on False this will always be 0.000
2022-04-30 14:12:04,730: PushOver Notification
Title: My Drip Wallet: Compounding Complete
Body: Updated Balance xx.xxx (Increase 0.000) - tx test:aaaabbbbccccdddd
```

## Docker Tips

```
docker rm my_docker_run_name
```

If you want to remove the image every time - use the ``--rm`` command in your docker run - If you do this you won't get a log history - it'll be fresh logs every time - can be useful for testing and the likes!

### Running multipe wallets

Create all the config files as per normal, but run each container with a new name and .ini file eg..

This will run one wallet at 9am, and the other at 9:10

```
0 9 * * * docker start my_wallet_name_1111 || docker run -v /etc/localtime:/etc/localtime  -v /path/to/configs/:/config/ --name my_wallet_name_1111 -d dripcompound:1.1 /config/my_wallet_details_1111.ini
10 9 * * * docker start my_wallet_name_2222 || docker run -v /etc/localtime:/etc/localtime  -v /path/to/configs/:/config/ --name my_wallet_name_2222 -d dripcompound:1.1 /config/my_wallet_details_2222.ini
```
