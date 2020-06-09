import sqlite3
import tempfile
from pathlib import Path
import os
import pyAesCrypt
import io
import sys

def isSQLite3(filename):
    with open(filename, 'rb') as fd:
        header = fd.read(100)
    return header[0:16] == b'SQLite format 3\000'


class money_db:

    BALANCE_TYPES = ['cur','avail','lim']

    def __init__(self, key, database):
        self.key = key
        self.tmp_db = tempfile.NamedTemporaryFile()
        print(self.tmp_db.name)
        self.enc_db = Path(database)
        self.buff = 64 * 1024
        self.db = None

    def connect(self):
        if self.db is not None:
            print('db already connected')
            return
        if self.enc_db.exists():
            print('found existing database!')
            if isSQLite3(self.enc_db):
                print('this file is not encrypted!!!')
                self.flush()
                print('will encrypt on exit')
                print('removing database')
                os.remove(self.enc_db)
            else:
                print('this might be encrypted. or just junk')
                self.decrypt()
        else:
            print('no existing db found. creating a new one...')
            self.enc_db.touch(mode=0o600)
        print('connecting...')
        self.db = sqlite3.connect(self.tmp_db.name, check_same_thread=False)
        self.db.execute('PRAGMA foreign_keys = 1')


    def disconnect(self):
        if not self.db:
            raise Exception('The database is already disconnected')
        self.encrypt()
        self.db.close()

    def encrypt(self):
        print('encrypting db...')
        self.tmp_db.seek(0)
        with open(self.tmp_db.name, mode='rb', buffering=self.buff) as fIn:
            with open(self.enc_db, mode='wb', buffering=self.buff) as fOut:
                pyAesCrypt.encryptStream(fIn, fOut, self.key, self.buff)

    def decrypt(self):
        print('decrypting db...')
        encFileSize = os.stat(self.enc_db).st_size
        with open(self.enc_db, mode='rb', buffering=self.buff) as fIn:
            try:
                with open(self.tmp_db.name, mode='wb', buffering=self.buff) as fOut:
                    pyAesCrypt.decryptStream(fIn, fOut, self.key, self.buff, encFileSize)
            except ValueError as e:
                print('error during decryption :(')
                print(e)
                self.tmp_db.close()
                sys.exit(1)

    def flush(self):
        with self.enc_db.open(mode='rb', buffering=0) as enc:
            print('saving temp data')
            self.tmp_db.seek(0)
            self.tmp_db.write(enc.read())

    def get_keys(self):
        c = self.db.cursor()
        try:
            c.execute("SELECT * from keys")
        except sqlite3.OperationalError as e:
            print(e)
            print('please run the SQL in the README')
            sys.exit(1)
        return c.fetchall()

    def get_accounts(self):
        c = self.db.cursor()
        c.execute('SELECT * FROM accounts')
        return c.fetchall()

    def add_account(self, account):
        c = self.db.cursor()
        c.execute('INSERT OR IGNORE INTO accounts (id, name, type, subtype, key_name) VALUES (?, ?, ?, ?, ?)', account)
        self.db.commit()

    def add_balance(self, mamount):
        if mamount[0] not in self.BALANCE_TYPES:
            raise Exception('bad balance type')
        amount = (mamount[1], int(mamount[2] * 100))
        c = self.db.cursor()
        c. execute('INSERT INTO ' + mamount[0] +' (account_id, amount) VALUES (?, ?)', amount)
        self.db.commit()

    def get_balance_by_account(self, balance_type, account_id):
        if balance_type not in self.BALANCE_TYPES:
            raise Exception('bad balance type')
        c = self.db.cursor()
        q = """
            SELECT
                bt.amount,
                bt.at,
                k.name,
                a.name,
                a.type,
                a.subtype
            FROM {bt} bt
            JOIN accounts a ON bt.account_id = a.id
            JOIN keys k ON a.key_name = k.name
            WHERE a.id = ?
            ORDER BY bt.at DESC
        """.format(bt=balance_type)
        c.execute(q, (account_id,))
        return c.fetchall()
