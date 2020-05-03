import plaid

class plaid_client:
    def __init__(self, pid, psecret, ppubkey, penv='development', papiv='2019-05-29'):
        self.pid = pid
        self.psecret = psecret
        self.ppubkey = ppubkey
        self.penv = penv
        self.papiv = papiv
        self.c = None

    def connect(self):
        if self.c is not None:
            print('client already connected')
            return
        self.c = plaid.Client(
            client_id = self.pid,
            secret=self.psecret,
            public_key=self.ppubkey,
            environment=self.penv,
            api_version=self.papiv
        )

    def get_balance(self, key):
        '''
        key is a tuple of key name, api key
        '''
        if self.c is None:
            self.connect()
        print('+ ', key[0], '...')
        try:
            bal = self.c.Accounts.balance.get(key[1])
        except plaid.errors.InstitutionError as e:
            print("OH NO!!!!!!")
            print(e)
            pass
        except plaid.errors.PlaidError as e:
            raise Exception(e)
        err = bal['item']['error']
        if err is not None:
            raise Exception(err)
        return bal
