# CoreVault

Create an M-of-N Bitcoin multisig wallet with a separate wallet for each signer and one watch-only wallet. You choose how many signatures are needed; Bitcoin Core creates the keys, descriptors, and wallet files.

CoreVault is a small, easy-to-audit helper designed for an offline Tails computer. Its goal is to make wallet creation repeatable while keeping custom wallet logic to a minimum.

## Quick start

1. Download CoreVault and the official [Bitcoin Core v32.0rc2 Linux x86_64 archive](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/) (`bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz`).
2. Put the `CoreVault` folder next to the **unextracted archive**. Any parent folder works—Home, Downloads, or another folder.
3. In Tails, enable **Allow executing file as program** in `tails.sh` properties, then choose **Run as a Program**.
4. Enter your policy when prompted, for example `2-3` for two signatures out of three signers.

Wallets are saved in `CoreVault/multisig-backups`.

Read [PRE-CREATION-GUIDE.txt](PRE-CREATION-GUIDE.txt) before starting and follow [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt) afterward. These guides cover preparation, backups, verification, a disposable test spend, shutdown, and storage. [Software verification](#software-verification) is explained below.

## What happens when you run it

The launcher finds the archive next to the CoreVault folder, verifies it, and extracts a fresh copy into a private RAM-backed directory. You do not need to extract Bitcoin Core yourself.

The pre-creation guide then opens in a separate window. The console continues independently, starts Bitcoin Core with networking disabled, and asks:

```text
Enter M-N (example 2-3):
```

Bitcoin Core creates N signer wallets and one watch-only wallet directly in `CoreVault/multisig-backups`. Use non-persistent storage for the intended offline Tails workflow, because these backups stay inside the CoreVault folder.

When generation finishes, the launcher stops Bitcoin Core and removes the temporary binaries and runtime data. It keeps the wallet backups and opens the post-creation guide independently. The console immediately displays `Complete. You may now close this window.`; neither guide needs to be closed for the console to proceed. Both guides can also be reopened from the project folder.

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

## Design and maintenance

CoreVault is a thin layer over Bitcoin Core's RPC interface. Bitcoin Core handles key generation, derivation, descriptor validation, wallet storage, and signing. CoreVault contains no custom cryptography.

The project separates wallet construction, the operating environment, and the human procedure:

| File | Purpose |
| --- | --- |
| `multisig.py` | Small, security-critical wallet-construction procedure |
| `tails.sh` | Tails startup, archive verification, temporary state, cleanup, and guide display |
| `PRE-CREATION-GUIDE.txt` | Preparation and safety instructions |
| `POST-CREATION-GUIDE.txt` | Backup, recovery checks, test spend, shutdown, and storage |
| `AUDIT.md` | Review targets, findings, checks, and limitations |

**Treat `multisig.py` as frozen after review.** UX improvements, guide edits, and operating-system changes belong in the launcher or documentation. If a Core change requires modifying the generator, keep the change small and review it again. Retest the exact Core release before changing the version pin.

The guides can evolve with the operating procedure. The README explains the architecture and review boundary. Another launcher, such as `ubuntu.sh`, can support a different environment without changing wallet construction.

### Why a reviewed script?

CoreVault puts the deterministic creation procedure in version-controlled code so reviewers can inspect, test, hash, and pin one implementation. Operators then execute that reviewed procedure consistently.

Bitcoin Core uses version-controlled procedures in its [Guix build system](https://github.com/bitcoin/bitcoin/blob/master/contrib/guix/README.md) and [CI system](https://github.com/bitcoin/bitcoin/blob/master/ci/README.md). The broader emphasis on source control, review, and provenance is also reflected in [NIST's Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) and [SLSA source requirements](https://slsa.dev/spec/v1.2/source-requirements).

Automation earns trust through review and testing. Users still need to verify software, maintain the air gap, make and test backups, verify receive addresses, and check transactions before signing.

## Review status and wallet details

CoreVault has received AI-assisted source review and safety testing. It has **not received an independent professional security audit**. [AUDIT.md](AUDIT.md) records exact executable hashes, tested revisions, findings, and remaining validation, including Tails testing for the new launcher flow.

A review should target an exact Git commit rather than the moving `main` branch, and include wallet creation, address derivation, restoration, PSBT signing, and the intended M-of-N threshold. Independent review by an experienced Bitcoin developer or security reviewer is strongly encouraged before relying on the wallet for substantial value. Findings and help funding an independent audit are welcome.

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

CoreVault shares the broad philosophy of [Yeti 2.0](https://github.com/bowlarbear/yeti-2.0): use Bitcoin Core for security-critical functions, create wallets on an air-gapped commodity computer, make durable offline backups, and complete a test spend before relying on the wallet.

The main difference is how the procedure is organized. CoreVault separates a reviewed wallet generator from the launcher and guides. Yeti 2.0 presents wallet creation as commands within a larger operational guide.

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

Yeti 2.0's command-by-command procedure is more educational, and its fixed 3-of-7 policy removes a user choice. CoreVault lets the user choose a quorum and runs the creation sequence as a small, repeatable script.

Yeti maintainers and other projects are welcome to reuse this architecture with their preferred operating system, backup policy, or quorum.
