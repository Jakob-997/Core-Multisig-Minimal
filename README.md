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

## Project structure

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

## Compared with Yeti 2.0

CoreVault shares [Yeti 2.0's](https://github.com/bowlarbear/yeti-2.0) basic approach: use Bitcoin Core to create multisig wallets on an offline computer. CoreVault exists to make the **generation procedure easier to review and repeat**, while keeping the operating instructions separate.

Yeti presents wallet generation as commands within its guide. CoreVault organizes the same kind of work into three layers:

- **Generator:** a small script containing the wallet-creation procedure.
- **Operating-system launcher:** startup, verified Bitcoin Core selection, temporary state, and cleanup.
- **Guides:** preparation, backups, recovery, and everyday use.

This gives reviewers a clear executable procedure to inspect, test, and pin to an exact revision. Users run that procedure consistently instead of reconstructing it from command blocks. Guides and operating-system support can evolve while the reviewed generator stays stable; launcher changes remain a separate security review target.

We consider this a better structure for reusable wallet generation: it makes audits more focused, reduces opportunities for operator mistakes, and makes security-relevant changes easier to identify. Yeti's commands are also public and reviewable; CoreVault's advantage is the separation and repeatability, rather than different cryptography. Both still depend on a trusted creation environment and careful testing.

Yeti's operating guides can complement this generator. Developers can adapt the launcher or improve the documentation without redesigning wallet creation.
