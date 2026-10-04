# Core Multisig Minimal

Create an M-N Bitcoin Core multisig wallet with N separate signer wallets and one watch-only wallet. You choose the M-N policy at the start, and Bitcoin Core handles the key generation, BIP87 derivation, multisig descriptor, and wallet storage.

The goal is a small, easy-to-audit multisig generator with as little custom wallet logic as possible.

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
        ├── tails.sh
        ├── PRE-CREATION-GUIDE.txt
        └── POST-CREATION-GUIDE.txt
```

To run it in Tails:

1. Right-click `tails.sh` and open its properties.
2. Enable **Allow executing file as program**.
3. Close the properties window.
4. Right-click `tails.sh` again and choose **Run as a Program**.

`PRE-CREATION-GUIDE.txt` opens first in a Zenity text window with the preparation and security instructions. Read it before creating the wallet, then close it and return to the Console. Both guide files remain in the project folder and can be reopened manually at any time.

The Console then starts Bitcoin Core and asks:

```text
Enter M-N (example 2-3):
```

The script creates N signer wallets and 1 watch-only wallet directly inside `multisig-backups`. Bitcoin Core's separate runtime data is kept in a temporary RAM-backed directory and removed after generation.

After generation succeeds, Bitcoin Core is stopped, the temporary runtime directory is removed, and `POST-CREATION-GUIDE.txt` opens in a Zenity text window with the backup, verification, test-spend, shutdown, and storage procedure. The Console then displays `Complete. You may now close this window.`

## Change policy

Treat `multisig.py` as the frozen, security-critical part of this project. Once it has been reviewed, it should not be changed for feature additions, user-interface changes, Tails changes, documentation changes, or convenience improvements. A change to `multisig.py` should be made only when Bitcoin Core behavior or the required wallet construction changes, and any such change should trigger a new review of the generator.

`tails.sh` is the environment and launcher layer. It may need occasional changes when Tails or Bitcoin Core startup/runtime behavior changes, without changing the multisig construction itself.

`PRE-CREATION-GUIDE.txt` and `POST-CREATION-GUIDE.txt` are operational documentation and are expected to evolve independently of the generator. Routine operational wording should be changed there rather than in the generator.

`README.md` is the project specification and audit boundary and should normally remain stable alongside `multisig.py`.

For an audit, review an exact Git commit rather than an unfrozen branch.

## Audit

`multisig.py` is the generic Bitcoin Core multisig generator. It contains only the wallet-construction logic; Tails-specific safety, storage, and operating instructions are kept out of it to make the security-critical code easier to audit.

`tails.sh` handles only the Tails environment, Bitcoin Core process/runtime setup and cleanup, and displaying the two static guide files with Zenity. Preparation instructions are in `PRE-CREATION-GUIDE.txt`; the post-generation procedure is in `POST-CREATION-GUIDE.txt`.

The wallet is fixed to **Bitcoin mainnet**, BIP87 account path `m/87h/0h/0h`, and native SegWit `wsh(sortedmulti())` with receive/change derivation `/<0;1>/*`. Bitcoin Core generates the keys, descriptors, and wallet databases. No custom cryptography is used.

`timestamp: 0` is intentional so restoration cannot miss wallet history because of an incorrect offline system clock. Because of the current Bitcoin Core descriptor-import behavior discussed in `bitcoin/bitcoin#35377`, the generator substitutes each signer's Core-derived xprv only into that signer's descriptor during import; Bitcoin Core still performs all key generation and derivation.

The implementation uses the upstream Bitcoin Core multisig wizard work as its primary reference, including `bitcoin/bitcoin#36325` and the related Core behavior discussed in `bitcoin/bitcoin#35377`.

The generator has received AI-assisted code review and safety testing, but it has **not** received an independent professional security audit. If you plan to rely on it for a wallet and that level of review does not satisfy you, having an experienced Bitcoin developer or security reviewer inspect `multisig.py` is strongly recommended.

The generator is intentionally small and delegates the cryptographic and wallet primitives to Bitcoin Core, so an experienced reviewer should be able to inspect the relevant logic relatively quickly. A meaningful audit should still include functional testing of wallet creation, address derivation, restoration, PSBT signing, and the intended M-of-N spending threshold.

If you review or audit the multisig generator, sharing the findings would be greatly appreciated. Help funding an independent audit is also welcome.
