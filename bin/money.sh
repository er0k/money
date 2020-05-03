#!/bin/bash

if [ -z $BW_SESSION ]; then
    BW_SESSION=$(bw unlock --raw)
fi

PLAID_CREDS=$(bw --session "$BW_SESSION" get item plaid.com)
PLAID_PUBLIC_KEY=$(echo "$PLAID_CREDS" | jq -r '.fields[] | select (.name | contains("pubkey")) | .value')
PLAID_CLIENT_ID=$(echo "$PLAID_CREDS" | jq -r '.fields[] | select (.name | contains("clientid")) | .value')
PLAID_SECRET=$(echo "$PLAID_CREDS" | jq -r '.fields[] | select (.name | contains("secret")) | .value')
DB_KEY=$(bw --session "$BW_SESSION" get password money.r0k)


MONEY_HOST=127.0.0.1 \
MONEY_PORT=8888 \
MONEY_DB=money.db \
DB_KEY="$DB_KEY" \
PLAID_CLIENT_ID="$PLAID_CLIENT_ID" \
PLAID_PUBLIC_KEY="$PLAID_PUBLIC_KEY" \
PLAID_SECRET="$PLAID_SECRET" \
python3 mon.py
