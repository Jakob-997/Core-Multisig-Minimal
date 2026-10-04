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

## Architecture

The project is intentionally split into four layers:

- `multisig.py` — the small, security-critical wallet generator. This is the part intended to be frozen after review.
- `tails.sh` — the Tails-specific launcher and runtime layer. Environment changes belong here, not in the generator.
- `PRE-CREATION-GUIDE.txt` — preparation and safety instructions.
- `POST-CREATION-GUIDE.txt` — backup, verification, test-spend, and storage instructions.

Bitcoin Core performs the actual key generation, BIP87 derivation, descriptor parsing, wallet storage, and signing primitives. The project does not implement custom cryptography.

The design rule is simple: **freeze the thing that creates the wallet; allow the environment and human instructions around it to evolve independently.**

## Compared with Yeti 2.0

This project shares the same broad philosophy as [Yeti 2.0](https://github.com/bowlarbear/yeti-2.0): use Bitcoin Core for security-critical Bitcoin functions, use an air-gapped commodity computer, make durable offline backups, and complete a test spend before relying on the wallet.

The main difference is architectural. CoreVault turns wallet construction into a small, frozen program instead of asking the user to manually reproduce an evolving sequence of shell commands.

| | CoreVault | Yeti 2.0 |
| --- | --- | --- |
| **Audit target** | Small `multisig.py`, intended to remain frozen after review | Security-relevant wallet commands live throughout an evolving operational guide |
| **Policy** | User selects M-N without changing source | Intentionally fixed to 3-of-7 |
| **Key structure** | Core derives BIP87 account keys at `m/87h/0h/0h` | Extracts Core default `wpkh` descriptors and rewrites their derivation suffix for multisig use |
| **Descriptor construction** | Core multisig-wizard-style `wsh(sortedmulti())` multipath descriptor using `/<0;1>/*` | `wsh(sortedmulti())` assembled from shell-parsed descriptor output |
| **Extra descriptor tooling** | Bitcoin Core RPC + Python standard library | Bitcoin Core RPC plus `jq`, `grep`, and `sed` in the wallet-construction path |
| **Descriptor timestamp** | `timestamp: 0`; restoration does not depend on the offline clock | Current guide builds the import timestamp from `date +%s` |
| **User execution** | Launch once, enter M-N, let the reviewed sequence run | Copy/paste several individual command blocks and preserve shell state between them |
| **User burden** | Very few security-critical inputs or manual construction steps | More opportunities for skipped commands, stale commands, transcription mistakes, or shell-state differences |
| **Approx. wallet-creation time after prerequisites** | Roughly **1–3 minutes** for the generator itself on a typical machine; excludes reading, disc burning, and the test spend | Roughly **10–20 minutes** for a careful first-time user to work through the wallet-construction commands; excludes OS/Core setup, node sync, backups, and test spend |
| **Deployment** | Tails-specific behavior is isolated in `tails.sh`; another launcher can replace it | Ubuntu setup and wallet procedure are integrated into the main guide |
| **Human instructions** | Pre/post guides can change without changing the wallet generator | Operational instructions and wallet-construction commands live together |
| **Audit invalidation** | Any `multisig.py` change explicitly requires re-review | Changing a security-relevant command changes the effective implementation |

The timing row is an operator-time estimate, not a benchmark. Hardware speed, familiarity, and how carefully the user verifies each step can change it substantially.

### Lower user burden is a security feature

This project deliberately minimizes what the user has to get right during wallet creation.

After the environment is prepared, the user launches one file and chooses the M-N policy. The reviewed generator then performs the same Bitcoin Core RPC sequence every time. There are still important operational responsibilities—verifying software, maintaining the air gap, making and testing backups, checking receive addresses, and verifying transactions before signing—but the user is not asked to manually reconstruct the wallet logic.

Copying and pasting CLI commands can be educational, but it provides no additional cryptographic assurance over running the same reviewed commands from a frozen script. Automating that fixed sequence reduces opportunities for skipped steps, stale documentation, malformed shell variables, or commands executed in the wrong state.

This is not a claim that user error is impossible. It is a design choice to remove as many unnecessary opportunities for user error as practical.

### Current Bitcoin Core model

Both projects ultimately use native SegWit `wsh(sortedmulti())`. CoreVault follows the newer upstream Bitcoin Core multisig-wizard structure: Bitcoin Core creates the HD key, derives the BIP87 multisig account key at `m/87h/0h/0h`, and that account key is used directly in the shared multipath descriptor.

Yeti 2.0's current guide instead obtains keys by selecting Core's default single-signature `wpkh` descriptors with `listdescriptors` and shell-processing those key expressions before assembling its fixed 3-of-7 descriptor.

CoreVault also uses `timestamp: 0`, so restoring the wallet does not depend on the offline computer having a correct wall clock.

### Configurable M-N

Yeti 2.0 intentionally standardizes on 3-of-7, and its FAQ explains that choice.

CoreVault treats the quorum as policy rather than implementation. The same frozen generator can create 2-3, 3-5, or another valid M-N without editing the source or maintaining a different command sequence. This does not imply that every quorum is equally appropriate; it means the policy can change without changing the audited generator.

### Replaceable environment layer

Tails is the reference environment, not part of the multisig algorithm.

A project that prefers Ubuntu could write an `ubuntu.sh` launcher while leaving `multisig.py` unchanged. That launcher would handle Ubuntu-specific details such as Core paths, temporary storage, networking assumptions, and installing or providing disc-burning software. Yeti 2.0's current Ubuntu procedure, for example, explicitly installs Brasero.

Yeti 2.0 maintainers and other projects are welcome to fork or reuse this structure while keeping their own operating-system choice, backup policy, or recommended quorum. The reusable idea is the separation of a **frozen generator**, an **environment-specific launcher**, and **living human guides**.

This comparison is about auditability and maintenance architecture, not a claim that Yeti 2.0 is inherently insecure. Yeti's command-by-command approach is more educational, and its fixed 3-of-7 policy deliberately removes a user choice.

## Change and audit policy

`multisig.py` is the frozen, security-critical component. After review, it should not be changed for UX improvements, documentation changes, Tails changes, convenience features, or policy preferences. If Bitcoin Core changes in a way that requires modifying the generator, the change should be as small as possible and the modified generator should be reviewed again.

`tails.sh` is the environment layer and may change when Tails or Bitcoin Core startup/runtime behavior changes.

`PRE-CREATION-GUIDE.txt` and `POST-CREATION-GUIDE.txt` are operational documentation and are expected to evolve. Routine safety and usability wording belongs there.

`README.md` defines the architecture and audit boundary and should normally remain stable once the design is settled.

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

Because of the current Bitcoin Core descriptor-import behavior discussed in `bitcoin/bitcoin#35377`, the generator substitutes each signer's Core-derived xprv only into that signer's descriptor during import. Bitcoin Core still performs the key generation and derivation.

The implementation uses the upstream Bitcoin Core multisig wizard work as its primary reference, including `bitcoin/bitcoin#36325` and the related behavior discussed in `bitcoin/bitcoin#35377`.

A meaningful audit should include functional testing of wallet creation, address derivation, restoration, PSBT signing, and the intended M-of-N spending threshold.

If you review or audit the generator, sharing the findings would be greatly appreciated. Help funding an independent audit is also welcome.
