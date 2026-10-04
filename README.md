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

`PRE-CREATION-GUIDE.txt` opens first in a Zenity text window with the preparation and security instructions. Read it before creating the wallet, then close it and return to the Console. Both guide files remain in the project folder and can be reopened manually at any time. If Tails has a compatible window-control utility available, the launcher also attempts to maximize the guide window.

The Console then starts Bitcoin Core and asks:

```text
Enter M-N (example 2-3):
```

The script creates N signer wallets and 1 watch-only wallet directly inside `multisig-backups`. Bitcoin Core's separate runtime data is kept in a temporary RAM-backed directory and removed after generation.

After generation succeeds, Bitcoin Core is stopped, the temporary runtime directory is removed, and `POST-CREATION-GUIDE.txt` opens in a Zenity text window with the backup, verification, test-spend, shutdown, and storage procedure. The Console then displays `Complete. You may now close this window.`

## Audit

`multisig.py` is the generic Bitcoin Core multisig generator. It contains only the wallet-construction logic; Tails-specific safety, storage, and operating instructions are kept out of it to make the security-critical code easier to audit.

`tails.sh` handles only the Tails environment, Bitcoin Core process/runtime setup and cleanup, and displaying the two static guide files with Zenity. Preparation instructions are in `PRE-CREATION-GUIDE.txt`; the post-generation procedure is in `POST-CREATION-GUIDE.txt`.

The wallet is fixed to BIP87 native SegWit `wsh(sortedmulti())`. Bitcoin Core generates the keys, descriptors, and wallet databases. No custom cryptography is used.

The implementation uses the upstream Bitcoin Core multisig wizard work as its primary reference, including Bitcoin Core PR #36325 and the related Core behavior discussed in #35377.

The generator has received AI-assisted code review and safety testing, but it has **not** received an independent professional security audit. If you plan to rely on it for a wallet and that level of review does not satisfy you, having an experienced Bitcoin developer or security reviewer inspect `multisig.py` is strongly recommended.

The generator is intentionally small and delegates the cryptographic and wallet primitives to Bitcoin Core, so an experienced reviewer should be able to inspect the relevant logic relatively quickly. A meaningful audit should still include functional testing of wallet creation, address derivation, restoration, PSBT signing, and the intended M-of-N spending threshold.

If you review or audit the multisig generator, sharing the findings would be greatly appreciated. Help funding an independent audit is also welcome.
