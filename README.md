# Core Multisig Minimal

A small Bitcoin Core M-of-N multisig generator.

## Use

Download and verify Tails and Bitcoin Core v32.

On Tails, put the extracted Bitcoin Core folder in your Home folder, then put this whole folder inside it:

```text
Home/
└── bitcoin-32.0/
    ├── bin/
    └── Core-Multisig-Minimal/
```

For real storage, use a physically air-gapped computer. Remove the Wi-Fi/Bluetooth card and any WWAN/cellular hardware if possible, disconnect Ethernet, and do not reconnect the machine to a network after it has generated or loaded private signer keys. Treat it as permanently offline.

Open a terminal in `Core-Multisig-Minimal` and run:

```bash
sh tails.sh
```

Enter the multisig you want:

```text
M-of-N (example 2-of-3):
```

The script creates N signer wallets and 1 watch-only wallet.

The backups appear right inside the helper folder:

```text
Core-Multisig-Minimal/
├── multisig.py
├── tails.sh
└── multisig-backups/
    ├── watch_only/
    ├── signer_1/
    ├── signer_2/
    └── ...
```

Burn each wallet folder to its matching labeled CD-R, then shut the computer down. In a normal non-persistent Tails session, the working files disappear when the machine powers off.

## Audit

`multisig.py` is the generic Bitcoin Core multisig generator.

`tails.sh` is only the small Tails launcher.

The wallet is fixed to BIP87 native SegWit `wsh(sortedmulti())`. Bitcoin Core generates the keys, descriptors, and wallet backups. No custom cryptography is used.

This project has not received an independent professional security audit.
