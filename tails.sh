#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin="$here/../bin"
state=/dev/shm/core-multisig

mkdir "$state"
export HOME="$state"
export PATH="$bitcoin_bin:$PATH"
cd "$state"

bitcoind -daemonwait -networkactive=0 -listen=0
python3 "$here/multisig.py"
bitcoin-cli stop
