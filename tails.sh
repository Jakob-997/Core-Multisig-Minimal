#!/bin/sh
set -e

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bitcoin_bin=$(find "$here/.." -maxdepth 2 -type d -path '*/bitcoin-*/bin' -print -quit)
state=$(mktemp -d /dev/shm/core-multisig.XXXXXX)

export PATH="$bitcoin_bin:$PATH"
export HOME="$state"
cd "$here"

trap 'bitcoin-cli stop >/dev/null 2>&1 || true; rm -rf "$state"' EXIT

cat <<'EOF'
Create your M-N Bitcoin Core multisig wallet.

Before continuing:
- Use a verified Bitcoin Core release. Verify the release signatures and independently
  verify the signer key fingerprints you trust.
- If this will be a wallet you actually use, permanently air-gap this computer:
  remove its network card(s) and never connect it to a network again.
EOF

bitcoind -daemonwait -networkactive=0 -listen=0
python3 multisig.py
bitcoin-cli stop

cat <<'EOF'

Finished.

A new "multisig-backups" folder is in the same directory you launched this from.
It contains one folder for each signer and one watch-only wallet.

Keep this computer and all backup media attended for the rest of the process.

1. Burn each signer folder and the watch-only folder to its matching labeled CD-R.
2. Verify every CD-R can be read and every wallet backup loads correctly.
3. Confirm every signer wallet and the watch-only wallet derive the same multisig addresses.
4. Do a disposable test spend. Try signing with every signer wallet and confirm the
   intended M-of-N threshold can complete the transaction.
5. Once the CDs are verified and the test spend succeeds, immediately power off the
   computer and remove the Tails USB.
6. Put each labeled CD-R in a protective case and take it directly to its intended
   storage location.

The signer backups are not encrypted. Anyone with a signer backup can copy that key.
Do not leave the computer or backup discs unattended during this process.
EOF
