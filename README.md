# CoreVault

Create an M-N Bitcoin Core multisig wallet with N separate signer wallets and one watch-only wallet. You choose the M-N policy at the start, and Bitcoin Core handles the key generation, BIP87 derivation, multisig descriptor, and wallet storage.

The goal is a small, easy-to-audit multisig generator with as little custom wallet logic as possible.

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

After generation succeeds, Bitcoin Core is stopped, the temporary runtime directory is removed, and `POST-CREATION-GUIDE.txt` opens in a Zenity text window with the backup, verification, test-spend, shutdown, and storage procedure. The Console then displays `Complete. You may now close this window.`

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

An audit should reference an exact Git commit, not simply the moving `main` branch.

The generator has received AI-assisted code review and safety testing, but it has **not** received an independent professional security audit. Independent review by an experienced Bitcoin developer or security reviewer is strongly encouraged before relying on it for substantial value.

## Audit notes

The generator is fixed to:

- Bitcoin mainnet
- BIP87 account path `m/87h/0h/0h`
- native SegWit `wsh(sortedmulti())`
- receive/change derivation `/<0;1>/*`
- `timestamp: 0`

Bitcoin Core generates the keys, descriptors, and wallet databases. No custom cryptography is used.

The launcher resolves the Bitcoin Core binaries from the adjacent extracted Bitcoin Core folder and passes the exact `bitcoin-cli` path into `multisig.py`. CoreVault does not resolve `bitcoin-cli` or `bitcoind` from the user's `PATH`.

`timestamp: 0` is intentional so restoration cannot miss wallet history because of an incorrect offline system clock.

Because of the current Bitcoin Core descriptor-import behavior discussed in [bitcoin/bitcoin#35377](https://github.com/bitcoin/bitcoin/pull/35377), the generator substitutes each signer's Core-derived xprv only into that signer's descriptor during import. Bitcoin Core still performs the key generation and derivation.

The implementation uses the upstream Bitcoin Core multisig wizard work as its primary reference, including [bitcoin/bitcoin#36325](https://github.com/bitcoin/bitcoin/pull/36325) and the related behavior discussed in [bitcoin/bitcoin#35377](https://github.com/bitcoin/bitcoin/pull/35377).

A meaningful audit should include functional testing of wallet creation, address derivation, restoration, PSBT signing, and the intended M-of-N spending threshold.

If you review or audit the generator, sharing the findings would be greatly appreciated. Help funding an independent audit is also welcome.

## Compared with Yeti 2.0

CoreVault shares the same broad philosophy as [Yeti 2.0](https://github.com/bowlarbear/yeti-2.0): use Bitcoin Core for security-critical Bitcoin functions, use an air-gapped commodity computer, make durable offline backups, and complete a test spend before relying on the wallet.

The main difference is how the procedure is structured. CoreVault separates the small wallet generator from the operating system and human instructions, while Yeti 2.0 expresses the wallet-construction procedure as commands within its larger operational guide.

| | CoreVault | Yeti 2.0 |
| --- | --- | --- |
| **Audit target** | Small `multisig.py`, intended to remain frozen after review | Security-relevant wallet commands are part of the evolving operational guide |
| **Policy** | User selects M-N without changing the generator | Intentionally fixed to 3-of-7 |
| **Key structure** | Core derives BIP87 account keys at `m/87h/0h/0h` | Uses key expressions extracted from Core's default `wpkh` descriptors and adapts them for the multisig |
| **Descriptor tooling** | Bitcoin Core RPC + Python standard library | Bitcoin Core RPC plus shell processing including `jq`, `grep`, and `sed` |
| **Descriptor timestamp** | `timestamp: 0` | Current guide constructs the timestamp from `date +%s` |
| **Operational model** | Review the generator once, then execute that exact version repeatedly | Each operator manually reproduces the wallet-construction procedure from command blocks |
| **Approx. wallet-creation time after prerequisites** | Roughly **1–3 minutes** for the generator itself | Roughly **10–20 minutes** for a careful first-time user to work through the construction commands |
| **Environment** | Tails behavior is isolated in `tails.sh`; another launcher can replace it | Ubuntu setup and wallet procedure are integrated into the guide |
| **Documentation changes** | Pre/post guides can evolve without changing wallet construction | Operational instructions and wallet-construction commands live together |

The timing figures are operator-time estimates, not benchmarks, and exclude software setup, node sync, disc burning, and the test spend.

### Reviewed automation instead of operator transcription

CoreVault's approach is closer to a common pattern in mature security engineering: **put the security-relevant procedure in version-controlled code, review that code, pin the exact revision, and execute the reviewed artifact repeatedly.**

Bitcoin Core itself uses this model for security-sensitive engineering work. Its [Guix build system](https://github.com/bitcoin/bitcoin/blob/master/contrib/guix/README.md) packages the reproducible release-build procedure into version-controlled scripts such as `guix-build`, and its [CI system](https://github.com/bitcoin/bitcoin/blob/master/ci/README.md) likewise keeps build and test stages in scripts. Reviewers inspect the implementation; individual builders do not manually reconstruct the entire build by copying a long sequence of commands every time.

The broader secure-software ecosystem follows the same direction. [NIST's Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) emphasizes source control, peer review, recorded review results, and automated analysis in the development workflow. [SLSA](https://slsa.dev/spec/v1.2/source-requirements) likewise treats version-controlled source history and provenance for exact revisions as foundations for trustworthy software processes.

CoreVault applies that principle on a much smaller scale. `multisig.py` is the procedure to review. Once an exact revision has been reviewed, the operator executes that same sequence instead of becoming a second implementation layer by manually copying commands, maintaining shell variables, and carrying intermediate state from one step to the next.

This is not an argument that automation is automatically secure. A script can contain a bug or a backdoor just as a written command can. The security advantage comes from having **one small executable procedure that can be reviewed, tested, hashed, pinned to a commit, and executed consistently**.

The user still has important responsibilities—verifying the software, maintaining the air gap, making and testing backups, verifying receive addresses, and checking transactions before signing. What CoreVault removes is unnecessary human participation in the deterministic wallet-construction sequence itself.

Yeti 2.0's command-by-command procedure is more educational, and its fixed 3-of-7 policy deliberately removes a user choice. CoreVault makes a different tradeoff: the security-critical procedure is treated more like reviewed automation—small, versioned, repeatable, and separate from the operator-facing instructions.

Yeti 2.0 maintainers or other projects are welcome to reuse this architecture while keeping their own operating system, backup policy, or preferred quorum. For example, an `ubuntu.sh` launcher could replace `tails.sh` without changing `multisig.py`.
