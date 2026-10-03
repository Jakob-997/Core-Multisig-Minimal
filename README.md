# Core Multisig Minimal

Create an M-N Bitcoin Core multisig wallet with N separate signer wallets and one watch-only wallet. You choose the M-N policy at the start, and Bitcoin Core handles the key generation, BIP87 derivation, multisig descriptor, and wallet backups.

The goal is a small, easy-to-audit multisig generator with as little custom wallet logic as possible.

## Use

Download and verify Tails and Bitcoin Core v32. Verify Bitcoin Core's release signatures, and independently verify the trusted signer key fingerprints rather than simply trusting keys that came with the download.

On Tails, put the extracted Bitcoin Core folder in your Home folder. Put the `Core-Multisig-Minimal` folder inside the outer extracted folder, beside the inner Bitcoin Core folder:

```text
Home/
└── bitcoin-32.0rc2-x86_64-linux-gnu/
    ├── bitcoin-32.0rc2/
    │   └── bin/
    └── Core-Multisig-Minimal/
        ├── multisig.py
        └── tails.sh
```

If this will be a wallet you actually use, permanently air-gap the computer first. Remove its network card(s), including Wi-Fi/Bluetooth and any WWAN/cellular hardware if present, disconnect Ethernet, and never connect the computer to a network again.

To run it in Tails:

1. Right-click `tails.sh` and open its properties.
2. Enable **Allow executing file as program**.
3. Close the properties window.
4. Right-click `tails.sh` again and choose **Run as a Program**.

A Console window opens and asks:

```text
M-N (example 2-3):
```

The script creates N signer wallets and 1 watch-only wallet.

## Finished

When generation finishes, close the Console window. In the same `Core-Multisig-Minimal` directory you launched the program from, you will now see a new folder:

```text
Core-Multisig-Minimal/
├── multisig.py
├── tails.sh
└── multisig-backups/
    ├── watch_only/
    │   └── wallet.dat
    ├── signer_1/
    │   └── wallet.dat
    ├── signer_2/
    │   └── wallet.dat
    └── ...
```

Each `signer_N` folder is a separate Bitcoin Core wallet containing that signer's private key and the multisig wallet information. The `watch_only` wallet contains no private signing key and is for watching the wallet and creating unsigned transactions.

These backups are **not encrypted**. Anyone who gets a signer backup can copy that signer key, and anyone who gets any of these wallet backups can learn the public information needed to follow the multisig wallet on-chain. Store the signer backups accordingly and keep enough signers physically separated so that one loss or theft does not compromise your M-N policy.

If you plan to use CD-Rs, prepare **N + 1 blank discs** and label them before burning. For a 2-3 wallet, for example:

```text
SIGNER 1 OF 3 — PRIVATE
SIGNER 2 OF 3 — PRIVATE
SIGNER 3 OF 3 — PRIVATE
WATCH ONLY — PUBLIC
```

Use **Brasero**, included with Tails, to burn each folder to its matching labeled disc:

- `signer_1` → SIGNER 1
- `signer_2` → SIGNER 2
- continue through `signer_N`
- `watch_only` → WATCH ONLY

CD-R is a write-once format and is useful for durable offline storage when stored carefully. Keep each private signer disc in a separate secure location.

**Do not fund the wallet until you have completed the entire test and backup process. Keep the computer and every backup disc attended from this point until the computer is powered off and the discs are stored.**

Burn each signer folder and the watch-only folder to its matching labeled CD-R. Verify every disc can be read and that every wallet backup loads correctly. Confirm that every signer wallet and the watch-only wallet derive the same multisig receive addresses.

Then perform a disposable **test spend**. Try signing with **every signer wallet** so you know every signer backup works, and confirm that the intended M-of-N threshold can complete the transaction.

Once the test spend succeeds and every CD-R has been verified, **immediately shut the computer down and remove the Tails USB**. Do not leave the computer unattended before it has been fully powered off.

Put each labeled CD-R in a protective, durable case, then take the discs **directly to their intended storage locations**. Do not leave the backup discs sitting around or unattended at any point in this process.

Bitcoin Core uses a temporary RAM-only working directory while the generator is running. Powering off Tails clears the remaining session state from RAM. The intended long-term copies are the verified backup discs.

## Audit

`multisig.py` is the generic Bitcoin Core multisig generator. It contains the wallet-construction logic only; Tails-specific safety and operating instructions are kept out of it to make the code easier to audit.

`tails.sh` handles the Tails runtime environment, temporary RAM-only Bitcoin Core state, and the user-facing setup, backup, testing, shutdown, and storage instructions.

The wallet is fixed to BIP87 native SegWit `wsh(sortedmulti())`. Bitcoin Core generates the keys, descriptors, and wallet backups. No custom cryptography is used.

This project has not received an independent professional security audit.
