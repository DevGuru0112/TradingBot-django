from flask import Flask
from binance.client import Client
from gtm.config import Config
import sys

app = Flask(__name__)

client = Client(Config.API_KEY, Config.API_SECRET_KEY)

import gtm.route.innovation

if __name__ == "__main__":
    app.run(debug=True)
