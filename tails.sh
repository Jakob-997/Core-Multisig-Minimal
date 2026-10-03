#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PATH="$here/../bin:$PATH"
cd "$here"

bitcoind -daemonwait -networkactive=0 -listen=0
python3 multisig.py
bitcoin-cli stop
