#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin=$(find "$here/.." -maxdepth 2 -type d -path '*/bitcoin-*/bin' -print -quit)
[ -n "$bitcoin_bin" ] || {
    echo "Bitcoin Core bin directory not found."
    exit 1
}

open_guide() {
    guide="$1"
    opened=0

    if command -v gio >/dev/null 2>&1; then
        if gio open "$guide"; then
            opened=1
        fi
    elif command -v gnome-text-editor >/dev/null 2>&1; then
        gnome-text-editor "$guide" >/dev/null 2>&1 &
        opened=1
    else
        echo "Could not open $(basename "$guide") automatically."
        echo "Open it manually from this folder."
    fi

    if [ "$opened" -eq 1 ] && command -v wmctrl >/dev/null 2>&1; then
        sleep 1
        wmctrl -r "$(basename "$guide")" -b add,maximized_vert,maximized_horz \
            >/dev/null 2>&1 || true
    fi
}

open_guide "$here/PRE-CREATION-GUIDE.txt"

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

bitcoind -daemonwait -networkactive=0 -listen=0 -walletdir="$backup_dir"
printf '\n'
python3 multisig.py

cleanup
trap - EXIT HUP INT TERM
export HOME="$original_home"

open_guide "$here/POST-CREATION-GUIDE.txt"

printf '\nComplete. You may now close this window.\n'
