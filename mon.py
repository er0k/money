import os
import signal
import sys
import threading

import util
from db import money_db
from client import plaid_client

from flask import Flask, jsonify, render_template


host = os.getenv('MONEY_HOST', '127.0.0.1')
port = os.getenv('MONEY_PORT', 8888)
money_database = os.getenv('MONEY_DB')
db_key = os.getenv('DB_KEY')
plaid_id = os.getenv('PLAID_CLIENT_ID')
plaid_pubkey = os.getenv('PLAID_PUBLIC_KEY')
plaid_secret = os.getenv('PLAID_SECRET')


mdb = money_db(db_key, money_database)
mdb.connect()

pc = plaid_client(plaid_id, plaid_secret, plaid_pubkey)
pc.connect()

refreshes = []

def refresh_thread():
    keys = mdb.get_keys()
    for key in keys:
        bal = pc.get_balance(key)
        for a in bal['accounts']:
            account = util.prep_account(a, key[0])
            mdb.add_account(account)
            bals = util.prep_balances(a)
            for b in bals:
                mdb.add_balance(b)
    mdb.encrypt()

def handler(signal, frame):
    print('closing down')
    mdb.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, handler)
app = Flask(__name__, static_url_path='', static_folder='static')

@app.route('/')
def index():
    data = 'sup'
    return render_template('index.ejs', data=data)

@app.route('/accounts')
def accounts():
    accounts = mdb.get_accounts();
    return jsonify(accounts)

@app.route('/keys')
def keys():
    keys = mdb.get_keys()
    return jsonify(keys)

@app.route('/refresh')
def refresh():
    if len(refreshes) > 0:
        if refreshes[0].is_alive():
            return jsonify('refresh in progress. please wait')
        else:
            del refreshes[0]
    t = threading.Thread(target=refresh_thread)
    refreshes.append(t)
    t.start()
    return jsonify('ok')

@app.route('/balance/<balance_type>/<account_id>')
def balance(balance_type, account_id):
    bal = mdb.get_balance_by_account(balance_type, account_id)
    return jsonify(util.prep_balance(bal))

app.run(host=host, port=port)
