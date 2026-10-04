#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin=$(find "$here/.." -maxdepth 2 -type d -path '*/bitcoin-*/bin' -print -quit)
[ -n "$bitcoin_bin" ] || {
    echo "Bitcoin Core bin directory not found."
    exit 1
}

backup_dir="$here/multisig-backups"
mkdir "$backup_dir"

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

instructions=$(cat <<'EOF'
Finished.

The "multisig-backups" folder in the directory you launched this from now contains
one folder for each signer and one watch-only wallet.

Keep this computer and all backup media attended for the rest of the process.

1. Burn each signer folder and the watch-only folder to its matching labeled CD-R.
2. Verify every CD-R can be read and every wallet loads correctly.
3. Confirm every signer wallet and the watch-only wallet derive the same multisig addresses.
4. Do a disposable test spend. Try signing with every signer wallet and confirm the
   intended M-of-N threshold can complete the transaction.
5. Once the CDs are verified and the test spend succeeds, immediately power off the
   computer and remove the Tails USB.
6. Put each labeled CD-R in a protective case and take it directly to its intended
   storage location.

The signer wallets are not encrypted. Anyone with a signer disc can copy that key.
Do not leave the computer or backup discs unattended during this process.

Finished. You can now close this window.
EOF
)

if command -v zenity >/dev/null 2>&1; then
    printf '%s\n' "$instructions" | zenity --text-info \
        --title="Core Multisig Minimal — Finished" \
        --width=700 --height=650 || true
else
    printf '\n%s\n' "$instructions"
fi
