# Core Multisig Helper

A deliberately tiny Bitcoin Core multisig generator.

The helper does **one thing**: it asks Bitcoin Core to create an M-of-N native SegWit multisig wallet, then writes **N signer wallet backups plus one watch-only wallet backup** into RAM.

It does not implement cryptography, transaction construction, signing, networking controls, CD burning, seed formats, QR codes, or a wallet GUI. Bitcoin Core does the wallet work.

## Guide

1. Download and verify **Tails** and **Bitcoin Core**.
2. Use a dedicated laptop and physically remove its network card.
3. Boot Tails.
4. Copy the verified Bitcoin Core binaries and `multisig.py` onto the machine.
5. Label **N + 1 CD-Rs**:
   - `signer_1` through `signer_N`
   - `watch_only`
6. Run:

```bash
python3 multisig.py M N /path/to/bitcoin/bin
```

Example:

```bash
python3 multisig.py 2 3 ~/bitcoin-*/bin
```

7. The backups appear under:

```text
/dev/shm/core-multisig/backups/
```

Each folder contains one `wallet.dat`. Burn each folder to its matching CD-R.

8. Power the machine off when finished.

Tails clears the RAM-backed working directory on shutdown.

## Using the wallet

Load the **watch-only** wallet in Bitcoin Core on the online machine to receive funds and create unsigned PSBTs.

For signing, boot the offline machine, load one signer wallet in Bitcoin Core, import the PSBT, verify it, sign it, and save the partially signed PSBT. Repeat with different signer discs until the M-of-N threshold is reached.

## Construction

The generator follows the Bitcoin Core multisig wizard design:

```text
m/87h/0h/0h
wsh(sortedmulti(M,[origin]xpub/<0;1>/*,...))
```

Bitcoin Core generates the keys, derives the BIP87 account keys, checksums and parses the descriptor, imports it, and creates the wallet backups.

## Audit scope

The trusted helper is intentionally just `multisig.py`.

Before using real funds, review that file line by line and test the complete workflow with disposable funds. This project has not received an independent professional security audit.
