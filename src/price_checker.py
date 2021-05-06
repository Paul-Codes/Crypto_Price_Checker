#!/usr/bin/python
from binance.client import Client
import sys
import time
import http.client, urllib
import logging
import hvac
import yaml

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


conf = yaml.load(open('conf/config.yaml'), Loader=yaml.SafeLoader)

#Set the HashiCorp Vault config
hv_url = conf['hashicorp_vault']['hv_url']
hv_userToken = conf['hashicorp_vault']['user_token']

#Get the configuration secrets from hashicorp vault
hvac_client = hvac.Client(url=hv_url)
hvac_client.token = hv_userToken

read_Binance_vaultData = hvac_client.secrets.kv.read_secret_version(mount_point='price_alert', path='/binance_api')
read_pushover_vaultData = hvac_client.secrets.kv.read_secret_version(mount_point='price_alert', path='/pushover_api')

#Set the api key and secret
api_key = read_Binance_vaultData['data']['data']['api_key']
api_secret = read_Binance_vaultData['data']['data']['api_secret']

pushover_userkey = read_pushover_vaultData['data']['data']['pushover_userkey']
pushover_apiKey = read_pushover_vaultData['data']['data']['pushover_apikey']

starting_price = 0
first_run = True
price_change = False

#Set Percentage Change Value
percentage_changeval = conf['script_config']['price_variable']

def send_pricealert(price, direction=None):
    #Do the Pushover Notification
    #set the context
    if direction is None:
        message = "Script Started. Current price is: " + str(price)
    else:
        message = "Price Change - New Balance is: " + direction + " " + str(price)
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": pushover_apiKey,
        "user": pushover_userkey,
        "message": message,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def send_scriptStopAlert(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": pushover_apiKey,
        "user": pushover_userkey,
        "message": message,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()


def main_pricecheck():
    while 1:
        global first_run
        global starting_price
        global price_change

        try:
            client = Client(api_key, api_secret)
            info = client.get_account()
        except:
            send_scriptStopAlert("Binance API Call Failed - Script Stopped")
            print >> sys.stderr, '\nExiting by failed connection to Binance.\n'
            sys.exit(0)

        balance = client.get_asset_balance(asset='ADA')
        avg_price = client.get_avg_price(symbol='ADAUSDT')
        current_value = float(avg_price["price"])*float(balance["free"])
        dollar_value = ('${:,.2f}'.format(current_value))

        #Update the starting price if first run or notification sent
        if first_run == True:
            logging.info("Script Starting")
            starting_price = current_value
            send_pricealert('${:,.2f}'.format(starting_price))
            first_run = False
        if price_change == True:
            starting_price = current_value
            price_change = False

        #Do the price comparison from the old price
        percentage_change = (abs(float(current_value) - starting_price) / starting_price) * 100.0
        if percentage_change > percentage_changeval:
            #work out if it's plus or minus
            change_direction = ""
            if current_value > starting_price:
                change_direction = "+"
            if current_value < starting_price:
                change_direction = "-"
            send_pricealert(dollar_value, change_direction)
            price_change = True
        #5 second polling time
        time.sleep(10)
        logging.info("Starting Price: " + str(starting_price))
        logging.info("Current Value: " + str(current_value))
        logging.info("Absolute Percentage Change: " + str(percentage_change))

if __name__ == '__main__':
    try:
        main_pricecheck()
    except KeyboardInterrupt:
        send_scriptStopAlert("Script exited by user")
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)
