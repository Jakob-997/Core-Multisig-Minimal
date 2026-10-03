#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin=$(find "$here/.." -maxdepth 2 -type d -path '*/bitcoin-*/bin' -print -quit)
state=$(mktemp -d /dev/shm/core-multisig.XXXXXX)

export PATH="$bitcoin_bin:$PATH"
export HOME="$state"
cd "$here"

trap 'bitcoin-cli stop >/dev/null 2>&1 || true; rm -rf "$state"' EXIT

bitcoind -daemonwait -networkactive=0 -listen=0
python3 multisig.py
bitcoin-cli stop
