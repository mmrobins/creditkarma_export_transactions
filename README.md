# Export CreditKarma Transactions

A ruby script to export transactions from
[creditKarma](https://www.creditkarma.com) to json and csv.  Especially useful
if you forgot to export your [Mint](https://mint.intuit.com/) data before being forced to move.  Easily importable to [Monarch Money](https://help.monarchmoney.com/hc/en-us/articles/9163024504468-Exporting-data-from-Mint#h_01HGBPJ7YTJDHZSZEJ4BA2Z511)

I didn't use anything not in the Ruby stdlib, so should be easy to get running
even for those not too familiar with Ruby.

I was able to get my transactions that had previously been in Mint all the way
back to 2008 when I started using it.

## Usage

```bash
git clone https://github.com/mmrobins/creditkarma_export_transactions.git
cd creditkarma_export_transactions
```

Or if you don't want to have to mess with using `git`, you can just copy the
code in the [fetch_credit_karma_transactions](fetch_credit_karma_transactions) file in this repository, and
paste it into a local file with the same name.

Then [get the access token](#access-token), and in the directory with the
[fetch_credit_karma_transactions](fetch_credit_karma_transactions) file run

```
export MY_ACCESS_TOKEN=eyJetc
ruby fetch_credit_karma_transactions
```

Example output

```
    total transactions: 100, last date: 2024-04-20
    getting next page cursor: dHhuIzIwMjQtMDQtMjAjMTg5ODI0MTU1MV8w
    total transactions: 200, last date: 2024-03-31
    ...
    getting next page cursor: dHhuIzIwMDgtMDgtMjIjMjM5OTM2MzNfMA==
    total transactions: 27455, last date: 2008-05-14

    done
```

Now do what you want with the `creditkarma_transactions.csv` and
`creditkarma_transactions.json` files that were generated.  The CSV is in the
format Mint used to use so can be uploaded fairly easily to other services.
The JSON file is a verbose dump of the GraphQL API results that creditKarma
returns, just in case there's data in there that isn't correctly parsed and
dumped to the CSV

### With Docker
If you don't have Ruby installed locally or don't want to install the required gems, you can run the script with [Docker](https://docs.docker.com/get-started/get-docker/).

First create a `.env` file in this directory (or rename `sample.env` to `.env`) and add your environment variables (`MY_ACCESS_TOKEN` is the only required one):

```.dotenv
DEBUG=1
MY_ACCESS_TOKEN=eyJra...kA2Uh
START_CURSOR=dHhuIzIwMjMtMDItMjEjMTgzODQ4MzIzMF8w
```

Then, in the terminal, run `docker-compose up`.

## Access Token

You can get your access token by logging into credit karma, visiting https://www.creditkarma.com/networth/transactions, and copying the
`authorization` header value (minus the word 'Bearer') using the browser's dev
tools in the Network section

You can get the token from anywhere on the site, but if you have second factor auth (2FA) you might have to visit https://www.creditkarma.com/networth/transactions specifically and make sure you can see transactions before the token will work.

Here's an example of what the would look like in Chrome's Dev Tools

![image](https://github.com/mmrobins/creditkarma_export_transactions/assets/9961/d990e1ca-0f0d-4101-a115-4e04071218bf)

This token expires after as few minutes (10ish?), so you might have to grab it
again and [restart](#resuming-after-token-expiration)

## Resuming after token expiration

After the token expires, you can restart where you left off by setting the `START_CURSOR`
environment variable to the last attempted cursor value

Example:

```bash
$ export MY_ACCESS_TOKEN=eyJMyNewtoken
$ ruby fetch_credit_karma_transactions
total transactions: 100, last date: 2024-01-10
...
total transactions: 1900, last date: 2023-02-21
getting next page cursor: dHhuIzIwMjMtMDItMjEjMTgzODQ4MzIzMF8w
fetch_credit_karma_transactions:42:in `get_transactions': error: 401 body: {"errorCode":"TOKEN_NEEDS_REFRESH"} (RuntimeError)

$ START_CURSOR=dHhuIzIwMjMtMDItMjEjMTgzODQ4MzIzMF8w ruby fetch_credit_karma_transactions
```

## Debugging

Set the env var `DEBUG=1` to see the json entries for each transaction printed
as they're processed.  This uses `awesome_print`, so you might need to run `gem
install awesome_print`

## TODO

Might be nice to handle the `TOKEN_NEEDS_REFRESH` automatically, but that'd
require setting the refresh token initially as well, which is probably just as
much work as setting the `START_CURSOR` value from where it left off.

Would be nice to cleanup the gigantic graphql query I copied to just what's
needed, but who cares, it works, and it's tedious to modify
