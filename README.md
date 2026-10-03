# Core Multisig Minimal

A small Bitcoin Core M-of-N multisig generator.

## Use

Download and verify Tails and Bitcoin Core v32.

Put this whole folder inside the extracted Bitcoin Core folder:

```text
bitcoin-32.0/
├── bin/
└── Core-Multisig-Minimal/
```

Boot Tails on the offline computer, open a terminal in `Core-Multisig-Minimal`, and run:

```bash
sh tails.sh
```

Enter the multisig you want:

```text
M-of-N (example 2-of-3):
```

The script creates:

- N signer wallets
- 1 watch-only wallet

The backups are here:

```text
/dev/shm/core-multisig/multisig-backups/
```

Burn each wallet folder to its matching labeled CD-R, then shut the computer down.

## Audit

`multisig.py` is the generic Bitcoin Core multisig generator.

`tails.sh` is only the small Tails launcher.

The wallet is fixed to BIP87 native SegWit `wsh(sortedmulti())`. Bitcoin Core generates the keys, descriptors, and wallet backups. No custom cryptography is used.

This project has not received an independent professional security audit.
