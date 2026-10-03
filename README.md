# Core Multisig Minimal

A small, auditable Bitcoin Core M-of-N multisig generator.

The repository contains two files:

- `multisig.py` — the platform-independent multisig generator.
- `tails.sh` — a tiny Tails launcher.

The security-critical wallet construction is kept separate from the operating-system setup.

## Multisig generator

`multisig.py` asks one question:

```text
M-of-N (example 2-of-3):
```

It then uses Bitcoin Core to:

1. Generate N independent keys.
2. Derive each BIP87 account key at `m/87h/0h/0h`.
3. Build `wsh(sortedmulti(M,.../<0;1>/*))`.
4. Create one watch-only wallet.
5. Create N signer wallets.
6. Back up each wallet separately.

It performs no custom cryptography.

The generator expects `bitcoin-cli` to be available. These optional environment variables only describe the surrounding Bitcoin Core instance:

```text
BITCOIN_CLI
BITCOIN_DATADIR
MULTISIG_BACKUP_DIR
```

Without them, it uses `bitcoin-cli` from PATH, Bitcoin Core's normal datadir, and `./multisig-backups`.

## Tails

For the Tails workflow, place `multisig.py` and `tails.sh` in the verified Bitcoin Core v32 `bin/` directory beside `bitcoind`, `bitcoin-cli`, and `bitcoin-qt`.

Run:

```bash
sh tails.sh
```

The launcher:

- starts Bitcoin Core with networking disabled,
- keeps the Core datadir and wallet backups under `/dev/shm/core-multisig`,
- runs the generic multisig generator,
- stops Bitcoin Core when generation finishes.

The backups are written to:

```text
/dev/shm/core-multisig/backups/
```

For an M-of-N wallet, burn the N signer folders and the one watch-only folder to N + 1 separately labeled CD-Rs.

## Audit scope

For review of the wallet construction itself, audit `multisig.py`.

`tails.sh` contains only the Tails-specific runtime setup and can be reviewed separately.

The generator intentionally fixes the wallet design to native SegWit BIP87 multisig rather than exposing additional address types, derivation paths, or descriptor options.

Before using real funds, test the complete workflow with disposable funds. This project has not received an independent professional security audit.
