import money
import pendulum

def prep_account(account, key_name):
    name = account['name'] if account['official_name'] is None else account['official_name']
    a = (account['account_id'], name, account['type'], account['subtype'], key_name)

    print('\t', a)

    return a

def prep_balances(account):
    cur = money.Money(
        0 if account['balances']['current'] is None else account['balances']['current'],
        account['balances']['iso_currency_code']
    )
    avail = money.Money(
        0 if account['balances']['available'] is None else account['balances']['available'],
        account['balances']['iso_currency_code']
    )
    lim = money.Money(
        0 if account['balances']['limit'] is None else account['balances']['limit'],
        account['balances']['iso_currency_code']
    )

    print('\t', 'cur\tavail\tlim')
    print('\t', '\t'.join([cur.format(), avail.format(), lim.format()]))

    return [
        ('cur', account['account_id'], cur),
        ('avail', account['account_id'], avail),
        ('lim', account['account_id'], lim),
    ]


def prep_balance(bal):
    formatted = []
    for b in bal:
        db_amount = b[0]
        if b[4] == 'credit':
            db_amount = db_amount * -1
        amount = money.Money(db_amount / 100, 'USD')

        db_at = b[1]
        gmt_at = pendulum.parse(db_at)
        tz = pendulum.timezone('US/Eastern')
        est_at = tz.convert(gmt_at)

        formatted.append([amount.format(), str(est_at), b[2], b[3], b[4], b[5]])

    return formatted
