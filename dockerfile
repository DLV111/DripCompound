FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /config

CMD [ "python" ]

# docker build -f dockerfile -t crypto_web3:1.0 .
# Configure in cron for this image to run when you want to compound
# docker start my_wallet_name || docker run -v /etc/localtime:/etc/localtime -v /path/to/my/config/:/config/ --name my_wallet_name -v "$PWD":/usr/src/myapp -w /usr/src/myapp -d crytpo_web3:1.0 python drip_compound.py /config/drip_config.ini
