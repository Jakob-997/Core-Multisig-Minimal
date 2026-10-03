# Core Multisig Minimal

A small Bitcoin Core M-of-N multisig generator.

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
M-of-N (example 2-of-3):
```

The script creates N signer wallets and 1 watch-only wallet.

The backups appear in the same helper folder:

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
