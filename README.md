# CoreVault

CoreVault creates an M-of-N Bitcoin multisig wallet on an offline Tails computer. You choose how many signatures are required—for example, two out of three—and Bitcoin Core creates a separate wallet for each signer plus a watch-only wallet.

The project has one central goal: **make multisig generation a small, repeatable procedure that people can review and trust.** Bitcoin Core handles the keys and wallet operations. CoreVault connects the steps, checks their results, and keeps the generation code separate from the operating system and instructions.

## Getting started

Read [PRE-CREATION-GUIDE.txt](PRE-CREATION-GUIDE.txt) before starting. It covers software verification, preparing the offline computer, choosing a quorum, and getting the backup process ready.

1. Download CoreVault and the official [Bitcoin Core v32.0rc2 Linux x86_64 archive](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/): `bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz`.
2. Put the `CoreVault` folder next to the **unextracted archive**. Any parent folder works—Home, Downloads, or another folder.
3. In the **Tails File Explorer**, open `CoreVault`. Right-click `tails.sh`, choose **Properties**, and enable **Allow executing file as program**. Close Properties, then right-click `tails.sh` again and choose **Run as a Program**.
4. Enter your policy when prompted. For example, `2-3` creates three signer wallets and requires two signatures to spend.

The launcher finds the archive relative to its own folder, so you do not need to extract Bitcoin Core or launch from a particular working directory.

**Use Bitcoin Core v32.0rc2 exactly.** The generator depends on wallet RPCs introduced after v31. Another release must be tested before the version pin changes.

### What to expect

The launcher checks the archive, extracts a fresh copy, and starts Bitcoin Core with networking disabled. The pre-creation guide opens in a separate window while the console asks for your policy.

Wallets are written directly to **`CoreVault/multisig-backups`**. Each signer wallet contains that signer's private key material and the shared multisig configuration; the watch-only wallet contains the public configuration.

After generation, the launcher stops Core and removes the temporary binaries and runtime data. The backups stay in CoreVault, and [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt) opens with the backup, verification, test-spend, shutdown, and storage procedure. The console completes without waiting for either guide window to close. Both guides can be reopened from the project folder.

For the intended offline Tails workflow, keep CoreVault in non-persistent storage. Its signer backups are unencrypted and must be protected until they have been backed up and the computer is shut down.

## A design with three layers

CoreVault separates the creation procedure from the environment that runs it and the instructions people follow.

| Layer | File | Responsibility |
| --- | --- | --- |
| **Generator** | [multisig.py](multisig.py) | Create signer keys and construct and import the shared multisig wallet configuration through Bitcoin Core |
| **Operating-system launcher** | [tails.sh](tails.sh) | Verify and start the required Core release, manage temporary state, stop Core, and display the guides |
| **Guides** | [Pre-creation](PRE-CREATION-GUIDE.txt) and [post-creation](POST-CREATION-GUIDE.txt) | Explain preparation, backups, checks, and storage |

Bitcoin Core performs key generation, derivation, descriptor validation, and wallet storage. CoreVault contains no custom cryptography. The generator checks RPC failures and descriptor-import results, and passes sensitive RPC parameters through standard input rather than putting private descriptors in command-line arguments.

This separation gives reviewers a defined executable procedure to inspect and test. The guides can improve without changing wallet creation, and another launcher can support a different operating system. The launcher is also security-critical and needs its own review.

**Treat the reviewed generator as frozen.** Keep UX changes, operating-system changes, and instructions in their respective layers. If a Core release requires a generator change, make it small and review it again. Retest the exact release before changing the version pin.

## How Bitcoin Core is verified

Verify [Tails](https://tails.net/install/download/) and follow Bitcoin Core's official [download-verification instructions](https://bitcoincore.org/en/download/#verify-your-download), including release signatures and independent verification of the signing-key fingerprints you trust.

The launcher adds an offline check every time it runs:

1. Copy the adjacent archive into a fresh private directory under `/dev/shm`.
2. Check that copy against the hardcoded official SHA-256 for v32.0rc2 Linux x86_64.
3. Extract the same verified copy and use only its `bitcoin-cli` and `bitcoind`, by absolute path.

A missing archive, failed check, or extraction failure stops execution before Core runs. Existing extracted Core folders and installations on `PATH` are ignored. The generator receives the exact path to the freshly extracted `bitcoin-cli`.

The pinned digest from the official [SHA256SUMS](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/SHA256SUMS) is:

```text
0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1
```

This supplements signature verification and depends on trustworthy CoreVault files, system utilities, and the host. `/dev/shm` must have enough space for the archive and extraction and permit execution; a `noexec` mount causes the launcher to stop.

All signer keys are generated on one machine. Multisig protects against later loss or theft of separately stored backups, but a compromised creation environment can compromise every key. A checksum and an air gap do not remove that assumption.

## Audit and design status

CoreVault has received **AI-assisted source review and safety testing**, but **no independent professional security audit**. [AUDIT.md](AUDIT.md) records the exact executable hashes, review findings, tested revisions, and limitations.

The generator remains unchanged from its recorded review baseline. The launcher has been re-reviewed for the verified-archive flow. An earlier launcher revision passed 13 Linux integration cases, including disposable wallet creation and failure handling. The final three-command simplification passed shell syntax and control-flow checks; its Linux integration retest and validation on Tails remain outstanding. Optical-media recovery and test spends also remain to be validated for this flow.

The architecture is intended to stay stable while the launcher and operating guides improve. The current release-candidate dependency is deliberate: `addhdkey` and `derivehdkey` provide the Core-native key workflow used here. A later release requires testing, not simply a filename change.

An external audit should target an **exact commit**, review both executable files, and test creation, address agreement, restoration, PSBT signing, and the intended signature threshold. Independent reviews, published findings, and help funding an audit are welcome.

<details>
<summary>Technical wallet details</summary>

| Setting | Value |
| --- | --- |
| Network | Bitcoin mainnet |
| BIP87 account path | `m/87h/0h/0h` |
| Descriptor | Native SegWit `wsh(sortedmulti())` |
| Receive/change branches | `/<0;1>/*` |
| Descriptor timestamp | `0` |

The zero timestamp avoids relying on the offline machine's clock to determine how much history to scan during restoration. The documented recovery workflow uses a fully synced, unpruned online node.

For v32.0rc2's descriptor-import behavior discussed in [bitcoin/bitcoin#35377](https://github.com/bitcoin/bitcoin/pull/35377), each signer imports the shared descriptor with only its own account xpub replaced by its Core-derived xprv.

The proposed [Bitcoin Core multisig wizard](https://github.com/bitcoin/bitcoin/pull/36325) served as a structural reference. It is not part of v32.0rc2 or a runtime dependency; CoreVault uses RPCs and descriptor behavior available in the pinned release.

</details>

## Compared with Yeti 2.0

CoreVault shares [Yeti 2.0's](https://github.com/bowlarbear/yeti-2.0) foundation: Bitcoin Core, an offline computer, and separately stored multisig backups. This comparison concerns **wallet generation**, rather than the breadth of either project's operating documentation.

Yeti presents generation as command blocks within a guide. CoreVault puts it in a small executable script, supported by a separate operating-system launcher and guides. Reviewers can inspect, test, hash, and pin that script; operators then run the same procedure consistently.

**For a reusable multisig generator, we consider CoreVault's structure the stronger design.** It reduces opportunities to omit or reorder creation steps, checks failures in code, and makes changes to the trusted procedure easier to identify. Documentation can evolve without altering generation, and operating-system support can change without rewriting the generator.

Yeti's commands are public and reviewable too, and its fixed 3-of-7 policy offers a clear default. CoreVault lets users choose their quorum and focuses on making the generation procedure a stable review target. Its advantage is a clearer structure for review and execution, rather than stronger cryptography or proven immunity to compromise.

Yeti's operating guidance can complement CoreVault. Contributors can improve the guides, adapt the launcher, and independently test the generator while preserving the separation that makes the project easy to audit.
