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

## Compared with Yeti 2.0

This project was influenced by the same general philosophy as [Yeti 2.0](https://github.com/bowlarbear/yeti-2.0): use Bitcoin Core for the security-critical Bitcoin functions, use an air-gapped commodity computer, make durable offline backups, and require a test spend before relying on the wallet.

The main difference is architectural. **Core Multisig Minimal is designed around a small, frozen wallet generator with the operating system, user interface, and human procedure kept outside of that audit boundary.** This project considers that structure an improvement for auditability, maintenance, and reproducibility. It is not a claim that Yeti 2.0 is inherently insecure.

| | Core Multisig Minimal | Yeti 2.0 |
| --- | --- | --- |
| **Security-critical audit target** | A small `multisig.py` intended to be frozen after review | Wallet construction is expressed as shell commands embedded throughout an evolving procedure |
| **Policy** | User selects M-N without changing generator source | Intentionally fixed to 3-of-7 |
| **Key structure** | BIP87 account keys derived by Core at `m/87h/0h/0h` | Extracts Core's default single-signature `wpkh` descriptors and rewrites their derivation suffix for the multisig |
| **Descriptor construction** | Current Core multisig-wizard-style `wsh(sortedmulti())` multipath descriptor using `/<0;1>/*` | Also uses `wsh(sortedmulti())`, assembled from shell-parsed descriptor output |
| **Descriptor tooling** | Bitcoin Core RPC + Python standard library | Bitcoin Core RPC plus shell processing with tools including `jq`, `grep`, and `sed` |
| **Descriptor timestamp** | `timestamp: 0`, so wallet history does not depend on the offline computer's clock | Current guide constructs the import request using `date +%s` |
| **User execution** | Launch once and enter M-N | User copies and pastes a sequence of individual CLI commands |
| **Deployment layer** | Tails is isolated in `tails.sh`; the generator itself is environment-neutral | Ubuntu setup and wallet procedure are integrated into the guide |
| **Human instructions** | Pre- and post-creation guides are separate files that can evolve without touching the generator | Operational guidance and wallet-construction commands live together in the main procedure |
| **Audit invalidation** | A change to `multisig.py` explicitly requires re-review | Changes to security-relevant commands in the procedure change the effective implementation |

### Why freeze the generator?

A security audit is most useful when the thing being audited has a clear boundary and does not keep changing.

The intended rule here is simple:

- `multisig.py` is frozen.
- Bitcoin Core performs the key generation, derivation, descriptor parsing, wallet storage, and signing primitives.
- User-interface or operating-system changes belong in `tails.sh`.
- Wording, backup instructions, and operational improvements belong in the pre- and post-creation guides.
- If Bitcoin Core changes in a way that requires modifying `multisig.py`, that modification should be small, explicit, and reviewed again.

That means an auditor can review one exact commit of one small generator and know that future changes to a Tails window, a CD-burning instruction, or guide wording do not silently change the multisig construction they reviewed.

For someone deciding where to spend limited audit effort on the **wallet-construction logic**, this project deliberately presents a smaller and more stable target.

### Why not require the user to copy and paste the Core commands?

Copying and pasting commands can be educational because the user can see each operation individually. Yeti 2.0 deliberately uses that model.

For this project, however, manual copy/paste is not treated as a security control. It provides no additional cryptographic assurance over executing the same reviewed Bitcoin Core RPC sequence from a frozen script. It also introduces another place for transcription mistakes, skipped commands, stale commands, shell-state differences, or version-specific edits.

The source remains fully visible. An auditor or advanced user can read every RPC call in `multisig.py`; the ordinary user simply does not have to manually reproduce the audited sequence.

### Current Bitcoin Core descriptor model

Both projects ultimately create native SegWit `wsh(sortedmulti())` descriptors. The difference is how the keys used in that descriptor are obtained.

The current Yeti 2.0 guide creates normal Core wallets, calls `listdescriptors`, selects their default `wpkh` descriptors, and uses shell tools to extract and rewrite those key expressions before building a hard-coded 3-of-7 descriptor.

Core Multisig Minimal instead follows the newer upstream Bitcoin Core multisig-wizard work: Core creates the HD key, derives the BIP87 multisig account key at `m/87h/0h/0h`, and that account key is used directly in the shared multipath descriptor. This avoids repurposing a default single-signature account descriptor to obtain the multisig keys.

### M-N instead of a fixed 3-of-7

Yeti 2.0 explicitly chooses 3-of-7 as part of its opinionated vault design. That is a legitimate design choice and its FAQ explains the reasoning.

Core Multisig Minimal separates the **wallet-construction mechanism** from that policy choice. The same frozen generator can create, for example, a 2-3 or 3-5 wallet without editing the code or maintaining separate command sequences.

This does not mean every M-N policy is equally appropriate. It means changing the quorum does not require changing the audited implementation.

### Separate launchers

Tails is the reference deployment for this repository, not part of the multisig construction itself.

Someone who prefers another environment can create a different launcher—an `ubuntu.sh`, for example—while leaving `multisig.py` unchanged. That launcher would be responsible for the environment-specific details, such as Core paths, temporary storage, networking assumptions, and ensuring suitable optical-disc burning software is available. Yeti 2.0's current Ubuntu procedure, for example, explicitly installs Brasero.

This separation is intentional: disagreement about Tails should not require a fork of the wallet algorithm.

### Invitation to Yeti and other projects

Yeti 2.0 maintainers, users, or other Bitcoin projects are welcome to adopt, fork, or use this architecture as a reference.

In particular, the useful pattern is not the Tails launcher itself. It is the separation of:

1. a **small frozen multisig generator**,
2. an **environment-specific launcher**, and
3. **pre- and post-creation human guides** that can improve without modifying the audited wallet construction.

A Yeti-style project could retain its preferred Ubuntu environment, backup philosophy, or 3-of-7 recommendation while using the same frozen-generator boundary.

### Scope of this comparison

Yeti 2.0 has advantages of its own. Its command-by-command procedure is highly explicit and educational, and its fixed 3-of-7 policy intentionally removes a user decision. This project's claim is narrower: **the frozen-generator architecture creates a cleaner audit target and allows UX, deployment, and documentation to evolve without continually changing the security-critical multisig construction.**

Neither architecture should be treated as professionally audited merely because it is easy to read. Core Multisig Minimal still recommends independent expert review before relying on it for substantial value.

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
