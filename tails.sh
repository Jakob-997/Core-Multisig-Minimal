#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin="$here/../bitcoin-32.0rc2/bin"
bitcoin_cli="$bitcoin_bin/bitcoin-cli"
bitcoind_bin="$bitcoin_bin/bitcoind"

[ -x "$bitcoin_cli" ] && [ -x "$bitcoind_bin" ] || {
    echo "Bitcoin Core v32.0rc2 binaries not found in the expected folder."
    exit 1
}

case "$("$bitcoin_cli" -version 2>/dev/null)" in
    *"Bitcoin Core RPC client version v32.0.0rc2"*) ;;
    *)
        echo "CoreVault requires Bitcoin Core v32.0rc2."
        exit 1
        ;;
esac

case "$("$bitcoind_bin" -version 2>/dev/null)" in
    *"Bitcoin Core daemon version v32.0.0rc2"*) ;;
    *)
        echo "CoreVault requires Bitcoin Core v32.0rc2."
        exit 1
        ;;
esac

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

export HOME="$state"
cd "$here"

stop_core() {
    "$bitcoin_cli" stop >/dev/null 2>&1 || true
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

"$bitcoind_bin" -daemonwait -networkactive=0 -listen=0 -walletdir="$backup_dir"
printf '\n'
python3 multisig.py "$bitcoin_cli"

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
