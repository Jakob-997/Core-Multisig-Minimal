#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
state=/dev/shm/core-multisig
mkdir -p "$state/data" "$state/backups"

"$here/bitcoind" -datadir="$state/data" -daemonwait -networkactive=0 -listen=0

PATH="$here:$PATH" \
BITCOIN_DATADIR="$state/data" \
MULTISIG_BACKUP_DIR="$state/backups" \
python3 "$here/multisig.py"

"$here/bitcoin-cli" -datadir="$state/data" stop
echo "Backups: $state/backups"
