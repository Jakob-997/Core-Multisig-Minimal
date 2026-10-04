# CoreVault

Create an M-N Bitcoin Core multisig wallet with N separate signer wallets and one watch-only wallet. You choose the M-N policy at the start, and Bitcoin Core handles the key generation, BIP87 derivation, multisig descriptor, and wallet storage.

The goal is a small, easy-to-audit multisig generator with as little custom wallet logic as possible.

## Short demonstration

https://github.com/user-attachments/assets/6942f638-588e-437c-9999-db534ad24bf6

## Use

Download and verify Tails and Bitcoin Core before creating a wallet.

- **Tails:** use the official [Tails Download and Verify](https://tails.net/install/download/) page.
- **Bitcoin Core verification:** use Bitcoin Core's official [Verify your download](https://bitcoincore.org/en/download/#verify-your-download) instructions.
- **Bitcoin Core v32.0 release-candidate binaries:** use the official [Bitcoin Core 32.0 directory](https://bitcoincore.org/bin/bitcoin-core-32.0/). At the time of writing, the tested build for this project is [v32.0rc2](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/).

> [!IMPORTANT]
> **This project currently requires Bitcoin Core v32.0rc2. Bitcoin Core v31.x and older will not work.**
>
> The generator uses the new `addhdkey` and `derivehdkey` wallet RPCs. These RPCs are present in Bitcoin Core v32.0rc2 and absent from v31.0. Until another v32 release candidate or the final v32.0 release has been tested with this project, use v32.0rc2 exactly.

On Tails, extract the Bitcoin Core download into your **Home** folder. Then place the `CoreVault` folder inside that extracted Bitcoin Core folder, next to the inner `bitcoin-32.0rc2` folder:

```text
Home/
└── bitcoin-32.0rc2-x86_64-linux-gnu/
    ├── bitcoin-32.0rc2/
    │   └── bin/
    └── CoreVault/
        ├── multisig.py
        ├── tails.sh
        ├── PRE-CREATION-GUIDE.txt
        └── POST-CREATION-GUIDE.txt
```

To run it in Tails:

1. Right-click `tails.sh` and open its properties.
2. Enable **Allow executing file as program**.
3. Close the properties window.
4. Right-click `tails.sh` again and choose **Run as a Program**.

`PRE-CREATION-GUIDE.txt` opens first in a Zenity text window with the preparation and security instructions. The Console continues independently, so the guide can remain open while you create the wallet. Both guide files remain in the project folder and can be reopened manually at any time.

The Console then starts Bitcoin Core and asks:

```text
Enter M-N (example 2-3):
```

The script creates N signer wallets and 1 watch-only wallet directly inside `multisig-backups`. Bitcoin Core's separate runtime data is kept in a temporary RAM-backed directory and removed after generation.

After generation succeeds, Bitcoin Core is stopped, the temporary runtime directory is removed, and `POST-CREATION-GUIDE.txt` opens independently in a Zenity text window with the backup, verification, test-spend, shutdown, and storage procedure. The Console does not wait for the Zenity window to close; it immediately displays `Complete. You may now close this window.`

## Design

CoreVault is intentionally a thin layer over Bitcoin Core. It does not implement key generation, derivation, descriptor parsing, wallet storage, signing, or custom cryptography itself. It asks Bitcoin Core to perform those operations through its RPC interface.

The project is split so each kind of change has a clear place:

- `multisig.py` — the small wallet-construction layer.
- `tails.sh` — Tails-specific startup, temporary runtime state, cleanup, and guide display.
- `PRE-CREATION-GUIDE.txt` — preparation and safety instructions.
- `POST-CREATION-GUIDE.txt` — backup, verification, test-spend, and storage instructions.

This separation keeps operating-system details and human instructions out of the wallet-construction code.

## Change and audit policy

`multisig.py` is the frozen, security-critical component. Once reviewed, it should not change for UX improvements, documentation changes, Tails changes, convenience features, or policy preferences.

If Bitcoin Core changes in a way that requires modifying `multisig.py`, the change should be as small as possible and the modified generator should be reviewed again.

`tails.sh` is the environment layer and may change when Tails or Bitcoin Core startup/runtime behavior changes.

`PRE-CREATION-GUIDE.txt` and `POST-CREATION-GUIDE.txt` are living operational documentation and are expected to evolve.

`README.md` defines the project architecture and audit boundary and should normally remain stable once the design is settled.
