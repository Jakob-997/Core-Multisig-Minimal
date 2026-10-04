#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin=$(find "$here/.." -maxdepth 2 -type d -path '*/bitcoin-*/bin' -print -quit)
[ -n "$bitcoin_bin" ] || {
    echo "Bitcoin Core bin directory not found."
    exit 1
}

backup_dir="$here/multisig-backups"

original_home=$HOME
state=$(mktemp -d /dev/shm/core-multisig.XXXXXX)

export PATH="$bitcoin_bin:$PATH"
export HOME="$state"
cd "$here"

stop_core() {
    bitcoin-cli stop >/dev/null 2>&1 || true
    pkill -x bitcoind >/dev/null 2>&1 || true
    pkill -x bitcoin-qt >/dev/null 2>&1 || true
}

cleanup() {
    stop_core
    rm -rf "$state"
}

trap cleanup EXIT
trap 'exit 1' HUP INT TERM

stop_core
mkdir "$backup_dir"

cat <<'EOF'
Create your M-N Bitcoin Core multisig wallet.

Before continuing:
- Make sure you verified the Tails ISO and the Bitcoin Core release before running this.
  Verify Bitcoin Core's release signatures and independently verify the signer key
  fingerprints you trust.
- If this will be a wallet you actually use, permanently air-gap this computer:
  remove its network card(s) and never connect it to a network again.
EOF

bitcoind -daemonwait -networkactive=0 -listen=0 -walletdir="$backup_dir"
python3 multisig.py

cleanup
trap - EXIT HUP INT TERM
export HOME="$original_home"

gnome-text-editor "$here/POST-CREATION-GUIDE.txt" >/dev/null 2>&1 &
