FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY drip_compound.py .
COPY utils.py .
COPY abis/ abis/

CMD [ "python", "drip_compound.py" ]

# docker build -f dockerfile -t dripcompound:1.0 .
# For each wallet create a new .env file as per drip_wallet.env.example
# Configure in cron for this image to run when you want to compound
# docker start my_wallet_name || docker run -v /etc/localtime:/etc/localtime --env-file drip_wallet.env.example --name my_wallet_name -d dripcompound:1.0
