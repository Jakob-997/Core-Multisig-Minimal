# Core Multisig Minimal

A small Bitcoin Core M-N multisig generator.

## Use

Download and verify Tails and Bitcoin Core v32.

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

For real storage, use a physically air-gapped computer. Remove the Wi-Fi/Bluetooth card and any WWAN/cellular hardware if possible, disconnect Ethernet, and never reconnect the machine to a network after it has generated or loaded private signer keys. Treat it as permanently offline.

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

**Do not fund the wallet until you have tested the backups.** Reopen every signer backup and confirm that each signer can load successfully and contribute a signature to a disposable test PSBT. Confirm that the intended M-of-N threshold can complete a transaction, and confirm that the watch-only wallet derives the same receive addresses. Only after the complete backup and signing workflow has been tested should you use the wallet for real funds.

When you are finished burning and testing the backups, shut the Tails computer down. In a normal non-persistent Tails session, the working files disappear when the machine powers off.

## Audit

`multisig.py` is the generic Bitcoin Core multisig generator.

`tails.sh` is only the small Tails launcher.

The wallet is fixed to BIP87 native SegWit `wsh(sortedmulti())`. Bitcoin Core generates the keys, descriptors, and wallet backups. No custom cryptography is used.

This project has not received an independent professional security audit.
