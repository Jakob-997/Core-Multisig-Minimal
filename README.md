# CoreVault

CoreVault helps you create an M-of-N Bitcoin multisig wallet on an offline Tails computer. Choose how many signatures are needed—for example, two out of three—and Bitcoin Core creates a separate wallet for each signer plus a watch-only wallet.

The goal is a small, repeatable creation procedure that is easy to review. Bitcoin Core handles the keys, derivation, descriptors, and wallet storage; CoreVault coordinates the steps.

## Quick start

1. Download CoreVault and the official [Bitcoin Core v32.0rc2 Linux x86_64 archive](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/) (`bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz`).
2. Put the `CoreVault` folder next to the **unextracted archive**. Any parent folder works—Home, Downloads, or another folder.
3. In Tails’ **file manager (File Explorer)**, open the `CoreVault` folder. Right-click `tails.sh`, choose **Properties**, and enable **Allow executing file as program**. Close Properties, then right-click `tails.sh` again and choose **Run as a Program**.
4. Enter your policy when prompted, for example `2-3` for two signatures out of three signers.

Wallets are saved in `CoreVault/multisig-backups`.

Read [PRE-CREATION-GUIDE.txt](PRE-CREATION-GUIDE.txt) before starting and follow [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt) afterward. These guides cover preparation, backups, verification, a disposable test spend, shutdown, and storage. [Software verification](#software-verification) is explained below.

### During and after creation

The launcher finds the archive next to the CoreVault folder, verifies it, and extracts a fresh copy into a private RAM-backed directory. You do not need to extract Bitcoin Core yourself.

The pre-creation guide then opens in a separate window. The console continues independently, starts Bitcoin Core with networking disabled, and asks:

```text
Enter M-N (example 2-3):
```

Bitcoin Core creates N signer wallets and one watch-only wallet directly in `CoreVault/multisig-backups`. Use non-persistent storage for the intended offline Tails workflow, because these backups stay inside the CoreVault folder.

When generation finishes, the launcher stops Bitcoin Core and removes the temporary binaries and runtime data. It keeps the wallet backups and opens the post-creation guide independently. The console immediately displays `Complete. You may now close this window.`; neither guide needs to be closed for the console to proceed. Both guides can also be reopened from the project folder.

## Why build on CoreVault? A generation-only comparison with Yeti 2.0

CoreVault is intended to replace the **wallet-generation procedure**, not an entire cold-storage guide. Preparation, backup media, recovery, and spending instructions can evolve separately or be adapted from another project. The comparison here concerns the executable creation logic and the controls around it.

Both projects use Bitcoin Core for key generation and Bitcoin operations. The architectural difference is that [Yeti 2.0's creation procedure](https://github.com/bowlarbear/yeti-2.0/blob/main/README.md) is a sequence of shell commands that the operator runs from a guide, while CoreVault puts creation in a small executable generator with a separate launcher.

**We recommend CoreVault's architecture as the foundation for contributors who want a reusable, reviewable Bitcoin Core multisig generator.** It makes the sequence explicit, checks failures in code, and binds execution to a verified Core archive. Those are concrete improvements in generation safety and change control.

### The security advantage of a reviewed procedure

In a manual procedure, the operator must execute the intended blocks in the intended order, preserve shell variables between steps, and interpret the results. CoreVault records those dependencies in one program. Once an exact revision has been reviewed and tested, subsequent users execute that same implementation.

This reduces opportunities to omit, reorder, or incorrectly reconstruct creation steps. It also gives reviewers a stable target: the generator can be inspected, hashed, pinned to a commit, and tested directly. Changes to prose do not silently change the executable procedure.

The benefit comes from **reviewing the code that actually runs**, rather than from automation or a low line count alone. Bitcoin Core similarly keeps its [Guix build](https://github.com/bitcoin/bitcoin/blob/master/contrib/guix/README.md) and [CI](https://github.com/bitcoin/bitcoin/blob/master/ci/README.md) procedures in version-controlled scripts. Review, change control, and provenance are also reflected in [NIST's Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) and [SLSA source requirements](https://slsa.dev/spec/v1.2/source-requirements).

### What the generation code enforces

| Control | CoreVault | Yeti 2.0 creation procedure |
| --- | --- | --- |
| **Execution sequence** | One generator records the order and carries state internally | Operator runs successive command blocks and maintains shell state |
| **Descriptor-import result** | Explicitly aborts when a descriptor reports failure | Import result is displayed for the operator to interpret |
| **Key and descriptor handling** | Core derives BIP87 account keys; Python reads structured RPC results | Shell pipelines extract and adapt key expressions from default `wpkh` descriptors using `jq`, `grep`, and `sed` |
| **Binary identity at launch** | Hardcoded archive digest, fresh private extraction, absolute binary paths | Guide instructs the user to verify and extract the release, then invoke that installation |
| **Descriptor timestamp** | `timestamp: 0` avoids dependence on the creation machine's clock for history coverage | Uses the creation machine's current timestamp |
| **Change boundary** | Generator, launcher, and operating instructions are separate files | Generation commands are maintained within the operating guide |
| **Quorum** | User selects M-N without editing construction code | Creation commands specify 3-of-7 |

CoreVault checks subprocess failures and the per-descriptor success result returned by `importdescriptors`. RPC parameters, including private descriptors, travel over standard input through `bitcoin-cli -stdin`, rather than appearing in command-line arguments. Each signer wallet stores its own private key material together with the shared multisig descriptor.

The launcher verifies the private archive copy that it subsequently extracts. It runs only that fresh copy of `bitcoin-cli` and `bitcoind`, keeps runtime state in a private RAM-backed directory, and stops Core before cleanup. An old extracted installation cannot become the generator's dependency by accident. The [verification section](#software-verification) explains the exact trust flow.

These choices concentrate the custom creation logic into a small, testable surface. They do not remove Python, the shell, system utilities, the launcher, or the host from the trusted environment. The launcher needs review alongside the generator.

### Why this is a fair comparison

The assessment applies the same criteria to both creation procedures: reproducibility of execution, failure handling, data transformations, binary selection, and isolation of executable changes. It does not count the length or completeness of either project's recovery documentation as a generation-security advantage, and it does not use unmeasured setup-time estimates.

Yeti's generation commands are public, version-controlled, and reviewable too. Its fixed quorum reduces policy decisions, and its current procedure uses a stable Core release; CoreVault's new HD-key RPCs require v32.0rc2. BIP87 derivation and a configurable quorum are design choices, not evidence of stronger cryptography.

Both designs trust one machine to generate all signer keys. Neither protects the entire key set against a sufficiently compromised creation environment. CoreVault's archive checksum also depends on a trustworthy pinned digest and does not replace release-signature verification.

Within that scope, our judgment is that **CoreVault offers a stronger structure for safe, repeatable generation and focused security review**. That is why we invite developers and reviewers to build on this generator, improve its launcher, and contribute independent tests. It is an architectural case for collaboration, not a claim that comparative exploit resistance has been proved. The [audit log](AUDIT.md) distinguishes reviewed revisions, completed tests, and remaining validation.

### How the project stays small

CoreVault uses Bitcoin Core's RPC interface and contains no custom cryptography. Bitcoin Core supplies key generation, derivation, descriptor validation, wallet storage, and signing. Each project file has a defined role:

| File | Purpose |
| --- | --- |
| `multisig.py` | Small, security-critical wallet-construction procedure |
| `tails.sh` | Tails startup, archive verification, temporary state, cleanup, and guide display |
| `PRE-CREATION-GUIDE.txt` | Preparation and safety instructions |
| `POST-CREATION-GUIDE.txt` | Backup, recovery checks, test spend, shutdown, and storage |
| `AUDIT.md` | Review targets, findings, checks, and limitations |

**Treat `multisig.py` as frozen after review.** UX improvements, guide edits, and operating-system changes belong in the launcher or documentation. If a Core change requires modifying the generator, keep the change small and review it again. Retest the exact release before changing the version pin.

The guides can evolve with the operating procedure, and the README explains the architecture and review boundary. Yeti maintainers and other projects are welcome to reuse this structure with their preferred operating system, backup policy, or quorum. An `ubuntu.sh` launcher, for example, could replace `tails.sh` without changing wallet construction.

## Software verification

Verify Tails and Bitcoin Core before creating a wallet:

- **Tails:** follow the official [Download and Verify](https://tails.net/install/download/) instructions.
- **Bitcoin Core:** follow the official [Verify your download](https://bitcoincore.org/en/download/#verify-your-download) instructions, including release-signature verification and independent verification of the signing-key fingerprints you trust.
- **Required release:** use [Bitcoin Core v32.0rc2](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/) from the official [v32.0 release directory](https://bitcoincore.org/bin/bitcoin-core-32.0/).

**Use v32.0rc2 exactly.** The generator requires the new `addhdkey` and `derivehdkey` wallet RPCs, which are absent from v31.0. Another release candidate or the final v32.0 release must be tested before the version pin changes.

### The launcher's archive check

The launcher copies `bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz` into a fresh private directory under `/dev/shm`, verifies that copy, and extracts those same verified bytes. The hardcoded SHA-256 comes from the official [v32.0rc2 SHA256SUMS](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/SHA256SUMS):

```text
0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1
```

A missing archive, failed checksum check, or extraction failure stops the launcher before any Core binary runs. Every invocation of `bitcoin-cli` and `bitcoind` uses an absolute path inside this fresh extraction. The generator receives that exact `bitcoin-cli` path. Existing extracted folders and Core binaries on `PATH` are ignored; the archive digest pins the release contents, making separate version-string checks unnecessary.

This check works offline and supplements release-signature verification. It still depends on trusted CoreVault files, the hardcoded digest, system utilities, and the Tails environment. It does not establish that the entire creation machine is uncompromised.

`/dev/shm` must have space for the archive and extracted release and allow execution. If it is mounted `noexec`, the launcher stops rather than using another Core installation.

## Review status


CoreVault has received AI-assisted source review and safety testing. It has **not received an independent professional security audit**. [AUDIT.md](AUDIT.md) records exact executable hashes, tested revisions, findings, and remaining validation, including Tails testing for the new launcher flow.

A review should target an exact Git commit rather than the moving `main` branch, and include wallet creation, address derivation, restoration, PSBT signing, and the intended M-of-N threshold. Independent review by an experienced Bitcoin developer or security reviewer is strongly encouraged before relying on the wallet for substantial value. Findings and help funding an independent audit are welcome.

### Wallet construction

The generator uses:

| Setting | Value |
| --- | --- |
| Network | Bitcoin mainnet |
| BIP87 account path | `m/87h/0h/0h` |
| Descriptor | Native SegWit `wsh(sortedmulti())` |
| Receive/change branches | `/<0;1>/*` |
| Descriptor timestamp | `0` |

The zero timestamp ensures restoration can scan the full wallet history even if the offline system clock was incorrect. The documented recovery workflow requires a fully synced, unpruned online node.

For the descriptor-import behavior in v32.0rc2 discussed in [bitcoin/bitcoin#35377](https://github.com/bitcoin/bitcoin/pull/35377), the generator substitutes each signer's Core-derived account xprv only into that signer's descriptor during import. Core performs the key generation and derivation; each signer wallet receives its own private key material and the shared multisig configuration.

The proposed [Bitcoin Core multisig wizard](https://github.com/bitcoin/bitcoin/pull/36325) served as a structural reference. It is not part of v32.0rc2 or a runtime dependency. CoreVault uses RPCs and descriptor behavior available in the pinned release. The upstream proposals' status and relevance to the reviewed release are documented in the audit log.

