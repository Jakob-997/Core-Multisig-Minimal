#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin=$(find "$here/.." -maxdepth 2 -type d -path '*/bitcoin-*/bin' -print -quit)

export PATH="$bitcoin_bin:$PATH"
cd "$here"

bitcoind -daemonwait -networkactive=0 -listen=0
python3 multisig.py
bitcoin-cli stop
