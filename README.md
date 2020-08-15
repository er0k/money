# money

Uses [Plaid](https://plaid.com/) to fetch info from your bank(s), and store
balances in an encrypted database. Includes a rudimentary frontend with
[Plotly](https://plotly.com/javascript/) to show a pretty graph.

## Requirements

* python3 (`pip install -r requirements.txt`)
* [bw](https://github.com/bitwarden/cli)
* [jq](https://github.com/stedolan/jq)

## Install

1. Put your [Plaid credentials](https://dashboard.plaid.com/overview/development)
in your Bitwarden vault. It needs fields named `pubkey`, `clientid`, and `secret`.

2. Generate a sufficiently long random string and store it in your Bitwarden
vault under URI `money.r0k`. This will be used to encrypt the sqlite database.

3. The [plaid quickstart](https://github.com/plaid/quickstart) is a submodule of
this repo. Clone it by running:

```bash
git submodule init
git submodule update
```

4. Run `bin/quickstart.sh` to get your bank keys.

5. Initialize the database. This will be encrypted after the first run.

```bash
sqlite3 money.db
```

```sql
CREATE TABLE IF NOT EXISTS keys (
    name TEXT NOT NULL PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    subtype TEXT NOT NULL,
    key_name TEXT NOT NULL,
    FOREIGN KEY (key_name) REFERENCES keys(name)
);

CREATE TABLE IF NOT EXISTS cur (
    account_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS avail (
    account_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS lim (
    account_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

6. Add your plaid keys to the database:

```sql
INSERT INTO keys (name, value) VALUES
    ('bank1','access-123'),
    ('bank2','access-456'),
    ('bank3','access-789');
```

7. Start the server: `bin/money.sh`

9. Visit http://127.0.0.1:8888/refresh to get the latest balances and
http://127.0.0.1:8888/ to see the pretty graph


## Updating keys

After some time you might see an error like this:

`plaid.errors.ItemError: the login details of this item have changed (credentials, MFA, or required user action) and a user login is required to update this information`

Run `bin/quickstart.sh` again to get a new key.

Then, while mon.py is running (so the database can be decrypted), use sqlite to
update the key for `<bank>`:

```sql
UPDATE keys set value = '<access_token>' WHERE name = '<bank>';
```

Get the old item ID. We want to replace it with the new ID, or our charts will
not look right.

```sql
SELECT id FROM accounts WHERE key_name = '<bank>';
```

And then update the balance tables (`avail`, `cur`, and `lim` (`cur` is the only
table currently used, but might as well update the other as well, maybe we will
use them one day ¯\\\_(ツ)\_/¯ )):

```sql
UPDATE avail SET account_id = '<new_id>' WHERE account_id = '<old_id>';
UPDATE cur SET account_id = '<new_id>'WHERE account_id = '<old_id>';
UPDATE lim SET account_id = '<new_id>' WHERE account_id = '<old_id>';
```

Then you probably want to delete the old unused account key:

```sql
DELETE FROM accounts WHERE id = '<old_id>';
```

## Todo

* make this easier to update :)
