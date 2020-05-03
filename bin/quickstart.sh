#!/bin/bash

if [ -z $BW_SESSION ]; then
    BW_SESSION=$(bw unlock --raw)
fi

PLAID_CREDS=$(bw --session "$BW_SESSION" get item plaid.com)
PLAID_PUBLIC_KEY=$(echo "$PLAID_CREDS" | jq -r '.fields[] | select (.name | contains("pubkey")) | .value')
PLAID_CLIENT_ID=$(echo "$PLAID_CREDS" | jq -r '.fields[] | select (.name | contains("clientid")) | .value')
PLAID_SECRET=$(echo "$PLAID_CREDS" | jq -r '.fields[] | select (.name | contains("secret")) | .value')


PLAID_CLIENT_ID="$PLAID_CLIENT_ID" \
PLAID_PUBLIC_KEY="$PLAID_PUBLIC_KEY" \
PLAID_SECRET="$PLAID_SECRET" \
PLAID_OAUTH_NONCE=$(pwgen 64 1) \
PLAID_ENV=development \
PLAID_PRODUCTS=transactions \
PLAID_COUNTRY_CODES=US \
PLAID_OAUTH_REDIRECT_URI=http://localhost:3001/oauth-response.html \
PORT=3001 \
python3 quickstart/python/server.py
