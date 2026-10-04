#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin=$(find "$here/.." -maxdepth 2 -type d -path '*/bitcoin-*/bin' -print -quit)
[ -n "$bitcoin_bin" ] || {
    echo "Bitcoin Core bin directory not found."
    exit 1
}

zenity --text-info \
    --title="Pre-Creation Guide" \
    --filename="$here/PRE-CREATION-GUIDE.txt" \
    --width=800 \
    --height=700 \
    >/dev/null 2>&1 &

echo "Please read PRE-CREATION-GUIDE.txt in the folder you launched this from before creating your wallet, if you have not already done so."

backup_dir="$here/multisig-backups"

original_home=$HOME
state=$(mktemp -d /dev/shm/core-multisig.XXXXXX)

export PATH="$bitcoin_bin:$PATH"
export HOME="$state"
cd "$here"

stop_core() {
    bitcoin-cli stop >/dev/null 2>&1 || true
    pkill -TERM -x bitcoind >/dev/null 2>&1 || true
    pkill -TERM -x bitcoin-qt >/dev/null 2>&1 || true

    while pgrep -x bitcoind >/dev/null 2>&1 || pgrep -x bitcoin-qt >/dev/null 2>&1; do
        sleep 1
    done
}

cleanup() {
    stop_core
    rm -rf "$state"
}

trap cleanup EXIT
trap 'exit 1' HUP INT TERM

stop_core
mkdir "$backup_dir"

bitcoind -daemonwait -networkactive=0 -listen=0 -walletdir="$backup_dir"
printf '\n'
python3 multisig.py

cleanup
trap - EXIT HUP INT TERM
export HOME="$original_home"

zenity --text-info \
    --title="Post-Creation Guide" \
    --filename="$here/POST-CREATION-GUIDE.txt" \
    --width=800 \
    --height=700 || true

echo "Please read POST-CREATION-GUIDE.txt in the folder you launched this from."

printf '\nComplete. You may now close this window.\n'
