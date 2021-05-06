# Crypto Price Checker
> Very basic Python 3 script for checking Crpyto currency on the Binance Exchange. Credentials are pulled from Hashicorp Vault, and the script uses Pushover to send iOS notifications.

This is a script developed for psersonal use, it is very simple, my instructions will be vague and it's really just reminders for me but I've made it public incase there are snippets that may be of use. The script collects the average price of a crypto/usd asset, then checks again every 10 seconds, if it finds the average price has moved above or below the base price, by the desired percentage, it sends an alert over pushover to ios.

There's very little effective error handling. That may improve later.

## Development setup
The setup requires a working Python 3 installation, hashicorp Vault, and pushover account for iOS notifications. 

I've included the docker requirements and config if you want to run it there.
Input your hashicorp config in /conf/config.yaml.bak and rename it to config.yaml

## Release History

* 0.0.1
    * Work in progress
