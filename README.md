# Core Multisig Minimal

A small, auditable Bitcoin Core M-of-N multisig generator.

The repository has two program files:

- `multisig.py` — the platform-independent multisig generator.
- `tails.sh` — a tiny Tails launcher.

The wallet construction is kept separate from the operating-system setup.

## Multisig generator

`multisig.py` asks one question:

```text
M-of-N (example 2-of-3):
```

It expects a running Bitcoin Core instance and `bitcoin-cli` on PATH. It then:

1. Generates N independent keys.
2. Derives each BIP87 account key at `m/87h/0h/0h`.
3. Builds `wsh(sortedmulti(M,.../<0;1>/*))`.
4. Creates one watch-only wallet.
5. Creates N signer wallets.
6. Writes each wallet backup under `./multisig-backups/`.

It performs no custom cryptography and contains no Tails-specific paths or setup.

## Tails

For the Tails workflow, place `multisig.py` and `tails.sh` in the verified Bitcoin Core v32 `bin/` directory beside `bitcoind`, `bitcoin-cli`, and `bitcoin-qt`.

Run:

```bash
sh tails.sh
```

The launcher sets a RAM-backed home directory under `/dev/shm/core-multisig`, puts the local Bitcoin Core binaries on PATH, starts Bitcoin Core with networking disabled, runs the generator, and stops Bitcoin Core.

The backups end up at:

```text
/dev/shm/core-multisig/multisig-backups/
```

For an M-of-N wallet, burn the N signer folders and the one watch-only folder to N + 1 separately labeled CD-Rs.

## Audit scope

For wallet-construction review, audit `multisig.py`.

`tails.sh` contains only the Tails-specific runtime setup and can be reviewed separately.

The generator intentionally fixes the wallet design to native SegWit BIP87 multisig rather than exposing extra address types, derivation paths, or descriptor options.

Before using real funds, test the complete workflow with disposable funds. This project has not received an independent professional security audit.
