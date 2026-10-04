#!/bin/sh
set -e

here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
umask 077
state=$(mktemp -d /dev/shm/core-multisig.XXXXXX)
trap 'rm -rf "$state"' EXIT
trap 'exit 1' HUP INT TERM

# Pin the official Linux x86_64 release; verify the private copy we extract.
# https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/SHA256SUMS
cp -- "$here/../bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz" "$state/core.tar.gz"
printf '0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1  %s\n' "$state/core.tar.gz" | sha256sum --check
tar -xzf "$state/core.tar.gz" -C "$state" --no-same-owner
rm -- "$state/core.tar.gz"

bitcoin_bin="$state/bitcoin-32.0rc2/bin"
bitcoin_cli="$bitcoin_bin/bitcoin-cli"
bitcoind_bin="$bitcoin_bin/bitcoind"

if [ ! -x "$bitcoin_cli" ] || [ ! -x "$bitcoind_bin" ]; then
    echo "Bitcoin Core v32.0rc2 binaries missing or not executable in the verified extraction."
    exit 1
fi

zenity --text-info \
    --title="Pre-Creation Guide" \
    --filename="$here/PRE-CREATION-GUIDE.txt" \
    --width=800 \
    --height=700 \
    >/dev/null 2>&1 &

echo "Please read PRE-CREATION-GUIDE.txt in the folder you launched this from before creating your wallet, if you have not already done so."

backup_dir="$here/multisig-backups"

original_home=$HOME

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

stop_core
mkdir "$backup_dir"

"$bitcoind_bin" -daemonwait -networkactive=0 -listen=0 -walletdir="$backup_dir"
printf '\n'
python3 multisig.py "$bitcoin_cli"

cleanup
trap - EXIT HUP INT TERM
export HOME="$original_home"

setsid -f zenity --text-info \
    --title="Post-Creation Guide" \
    --filename="$here/POST-CREATION-GUIDE.txt" \
    --width=800 \
    --height=700 \
    </dev/null >/dev/null 2>&1

echo "Please read POST-CREATION-GUIDE.txt in the folder you launched this from."

printf '\nComplete. You may now close this window.\n'
