from flask import request
from gtm import app, client
from gtm.config import Config
from gtm.helpers.ihelper import IHelper
import sys


@app.route("/inv_start_up")
def welcome():

    coin_code = request.args.get("coin")
    parity_code = request.args.get("parity")
    value = request.args.get("value")

    print(type(value), file=sys.stdout)
    if IHelper.inputExistControl(coin_code, parity_code) and type(value) != int:
        return "success"
    else:
        return "failed"

    # print(client.get_symbol_info('BNBBTC'), file=sys.stdout)

    # print console
    # print("", file=sys.stdout)