# CoreVault

CoreVault creates an M-of-N Bitcoin multisig wallet on an offline Tails computer. You choose how many signatures are required—for example, two out of three—and Bitcoin Core creates a separate wallet for each signer plus a watch-only wallet.

The project has one central goal: **make multisig generation a small, repeatable procedure that people can review and trust.** Bitcoin Core handles the keys and wallet operations. CoreVault connects the steps, checks their results, and keeps the generation code separate from the operating system and instructions.

## Why trust a random GitHub script?

You should not trust CoreVault because of who wrote it. The design is meant to make the author's identity much less important. The security-critical generator is intentionally small, contains no custom cryptography, and delegates key generation, derivation, descriptor validation, and wallet storage to a pinned Bitcoin Core release. The launcher disables NetworkManager networking before Core is extracted or any keys are generated, verifies the exact Core archive it will use, and runs only the freshly extracted binaries.

That does not make the project automatically safe. It makes the trust problem **small enough to inspect**. A reviewer does not need to audit a new cryptographic library or a large wallet application; they can review a short generator, a small launcher, and the specific assumptions CoreVault makes about Bitcoin Core. Exact executable revisions and hashes are recorded in [AUDIT.md](AUDIT.md), and the generator is treated as frozen unless a Core behavior change requires it to be reviewed again.

The intended security model is therefore not “trust an anonymous maintainer.” It is: **verify a small procedure that mostly asks Bitcoin Core to perform standard wallet operations.** Users can inspect the exact source, pin an exact commit, test the complete workflow with disposable funds, and have an independent Bitcoin expert review the same revision. If a security-relevant behavior cannot be explained in terms of Bitcoin Core or simple operating-system plumbing, it should be treated skeptically.

This still requires trust in the verified Tails environment, the pinned Bitcoin Core release, the host hardware and entropy source, and the exact CoreVault revision being run. CoreVault tries to make those trust boundaries explicit rather than hide them.

## Demo

https://github.com/user-attachments/assets/fae51512-3197-4d1b-b880-21e0152dc246

## Getting started

Read [PRE-CREATION-GUIDE.txt](PRE-CREATION-GUIDE.txt) before starting. It covers software verification, preparing the offline computer, choosing a quorum, and getting the backup process ready.

1. Download CoreVault and the official [Bitcoin Core v32.0rc2 Linux x86_64 archive](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/): `bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz`.
2. Put the `CoreVault` folder next to the **unextracted archive**. Any parent folder works—Home, Downloads, or another folder.
3. In the **Tails File Explorer**, open `CoreVault`. Right-click `tails.sh`, choose **Properties**, and enable **Allow executing file as program**. Close Properties, then right-click `tails.sh` again and choose **Run as a Program**.
4. Enter your policy when prompted. For example, `2-3` creates three signer wallets and requires two signatures to spend. Immediately after you press Enter, the launcher disables NetworkManager networking and confirms it is disabled before verifying or extracting Bitcoin Core or starting wallet creation.

The launcher finds the archive relative to its own folder, so you do not need to extract Bitcoin Core or launch from a particular working directory.

**Use Bitcoin Core v32.0rc2 exactly.** The generator depends on wallet RPCs introduced after v31. Another release must be tested before the version pin changes.

### What to expect

The pre-creation guide opens in a separate window while the console asks for your policy. As soon as you enter the M-of-N policy, the launcher runs `nmcli networking off` and confirms NetworkManager reports networking as disabled. Only then does it check the archive, create a brand-new uniquely named Bitcoin Core directory next to it, extract the verified release there, and start only that copy.

Wallets are written directly to **`CoreVault/multisig-backups`**. Each signer wallet contains that signer's private key material and the shared multisig configuration; the watch-only wallet contains the public configuration.

After generation, the launcher stops Core and removes only the temporary runtime data. The freshly extracted Bitcoin Core directory is left next to the archive for the user. The backups stay in CoreVault, and [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt) opens with the backup, verification, test-spend, shutdown, and storage procedure. The console completes without waiting for either guide window to close. Both guides can be reopened from the project folder.

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

1. Check the adjacent archive against the hardcoded official SHA-256 for v32.0rc2 Linux x86_64.
2. Create a new empty directory with a unique name such as `bitcoin-32.0rc2-corevault.A1B2C3`.
3. Extract the verified archive into that new directory and use only its `bitcoin-cli` and `bitcoind`, by absolute path.

A missing archive, failed check, or extraction failure stops execution before Core runs. Existing extracted Core folders and installations on `PATH` are ignored because each run creates its own fresh directory. The generator receives the exact path to that newly extracted `bitcoin-cli`. The extracted Core directory is intentionally left in place afterward; only Core's temporary runtime state is removed.

The pinned digest from the official [SHA256SUMS](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/SHA256SUMS) is:

```text
0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1
```

This supplements signature verification and depends on trustworthy CoreVault files, system utilities, and the host. The extraction itself is placed beside the archive in a fresh directory; `/dev/shm` is used only for Bitcoin Core's temporary runtime state. The automatic `nmcli networking off` step is defense in depth and does not replace the documented physical air gap.

All signer keys are generated on one machine. Multisig protects against later loss or theft of separately stored backups, but a compromised creation environment can compromise every key. A checksum and an air gap do not remove that assumption.

## Audit and design status

CoreVault has received **AI-assisted source review and safety testing**, but **no independent professional security audit**. [AUDIT.md](AUDIT.md) records the exact executable hashes, review findings, tested revisions, and limitations.

The generator remains unchanged from its recorded review baseline. The launcher has been re-reviewed for the verified-archive flow. Earlier launcher revisions passed Linux integration cases including disposable wallet creation and failure handling. The current fresh-directory extraction change is intentionally small, but should still receive an end-to-end Tails retest before the next release candidate. Optical-media recovery and test spends also remain to be validated for this flow.

The architecture is intended to stay stable while the launcher and operating guides improve. The current release-candidate dependency is deliberate: `addhdkey` and `derivehdkey` provide the Core-native key workflow used here. A later release requires testing, not simply a filename change.

An external audit should target an **exact commit**, review both executable files, and test creation, address agreement, restoration, PSBT signing, and the intended signature threshold.

If you are considering using CoreVault, we strongly encourage an independent review by someone who understands Bitcoin Core wallets, descriptors, multisig, and PSBTs. If you perform an audit, please consider sharing the findings publicly or contacting the project so the results can be incorporated here. Funding or organizing a professional review is also welcome. The security-critical code surface is intentionally small, so a focused expert review should be substantially narrower than auditing a full wallet application.

<details>
<summary>Technical wallet details</summary>

| Setting | Value |
| --- | --- |
| Network | Bitcoin mainnet |
| BIP87 account path | `m/87h/0h/0h` |
| Descriptor | Native SegWit `wsh(sortedmulti())` |
| Receive/change branches | `/<0;1>/*` |
| Descriptor timestamp | `0` |

The zero timestamp avoids relying on the offline machine's clock to determine how much history to scan during restoration. The online node may be pruned, but it must still have every block Core needs to bring the copied wallet current. If required history has already been pruned, Core may require a reindex/redownload or a node with the missing block history.

For v32.0rc2's descriptor-import behavior discussed in [bitcoin/bitcoin#35377](https://github.com/bitcoin/bitcoin/pull/35377), each signer imports the shared descriptor with only its own account xpub replaced by its Core-derived xprv.

The proposed [Bitcoin Core multisig wizard](https://github.com/bitcoin/bitcoin/pull/36325) served as a structural reference. It is not part of v32.0rc2 or a runtime dependency; CoreVault uses RPCs and descriptor behavior available in the pinned release.

</details>

## References and upstream influences

CoreVault's design was informed by Bitcoin Core's own multisig work and reviewed against the pinned release. These references explain where the construction and review approach came from:

- **[bitcoin/bitcoin#36325 — proposed multisig wizard](https://github.com/bitcoin/bitcoin/pull/36325):** the main structural reference for a Python procedure that delegates wallet creation, BIP87 key generation, construction, and import to Core. The proposal includes explicit import-result checks. CoreVault narrows the workflow to its single-machine generation use case.
- **[Pinned wizard source reviewed](https://github.com/rxbryan/bitcoin/blob/2803e1518bb22394a80bac94e2435bb3982d0cde/contrib/multisig/wizard.py):** the exact upstream revision used as a reference, so reviewers can compare implementations without relying on a moving branch.
- **[bitcoin/bitcoin#35377 — descriptor import with existing private keys](https://github.com/bitcoin/bitcoin/pull/35377):** explains the import limitation behind the local private-key substitution used by the wizard and CoreVault for the pinned release.
- **[Bitcoin Core multisig tutorial](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/multisig-tutorial.md) and [offline-signing tutorial](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/offline-signing-tutorial.md):** references for wallet construction and the Core PSBT workflow.
- **[BIP87](https://github.com/bitcoin/bips/blob/master/bip-0087.mediawiki):** the multisig key-derivation convention used by the generator.
- **[Core's Guix build procedures](https://github.com/bitcoin/bitcoin/blob/master/contrib/guix/README.md) and [CI procedures](https://github.com/bitcoin/bitcoin/blob/master/ci/README.md):** examples of keeping repeatable executable procedures in version control, rather than requiring each operator to reconstruct them manually.

The wizard remains an upstream proposal and is not shipped in v32.0rc2. CoreVault depends only on behavior present in its pinned release. Referencing these projects does not imply Bitcoin Core endorsement or transfer their review coverage to CoreVault. [AUDIT.md](AUDIT.md) lists the implementation, tests, and additional references examined during the review.

## Compared with Yeti 2.0

CoreVault shares [Yeti 2.0's](https://github.com/bowlarbear/yeti-2.0) foundation: use Bitcoin Core to generate multisig wallets on an offline computer. CoreVault focuses on improving the **generation architecture**; operating guides and backup procedures can be developed separately.

**We consider CoreVault a better design for reusable multisig generation, with stronger security controls around execution and maintenance.** Its advantage is that the reviewed procedure becomes the program people run, with explicit failure checks and a verified runtime dependency.

### Why the structure is stronger

Yeti places generation commands inside its operating guide. CoreVault separates three responsibilities: the generator creates the wallets, the launcher manages the operating environment, and the guides explain the human procedure. That gives each security-relevant change a clear home.

Calling a command-by-command construction procedure “no code” can be misleading. A sequence of shell commands that derives keys, transforms descriptor material, assembles a multisig descriptor, and imports it into wallets is still an executable procedure with security-relevant logic. The important question is not whether that logic is written as a script or copied line-by-line from a guide, but how clearly it is defined, reviewed, tested, and reproduced. CoreVault accepts that a small amount of project-specific code exists and tries to handle it explicitly: keep it small, isolate responsibilities, pin dependencies, check failures, preserve exact reviewed revisions, and encourage independent audit.

- **One procedure to review and execute.** Reviewers can inspect, test, hash, and pin the generator. Users execute that exact sequence rather than recreate it through successive command blocks and persistent shell variables. This reduces opportunities to omit or reorder steps.
- **Failure handling is part of the code.** CoreVault stops on RPC failures and explicitly checks whether descriptor imports succeeded. The procedure does not rely solely on the operator noticing and correctly interpreting every returned result.
- **The intended Core binary is enforced.** The launcher verifies the pinned archive, extracts it into a brand-new uniquely named directory, and uses only that copy. An old extracted folder or another installation cannot be selected accidentally.
- **Instructions can improve without changing generation.** Preparation and backup guidance can evolve while the generator stays stable. Operating-system changes stay in the launcher and receive their own review, rather than being mixed into wallet construction.
- **Core remains responsible for Bitcoin operations.** The generator follows the Core-native key workflow reflected in the proposed upstream wizard and keeps custom transformations small. It uses structured RPC results and sends sensitive parameters over standard input. This concentrates the project-specific logic into a defined surface that can be tested directly.

This reflects a familiar security-engineering practice: put an important, repeatable procedure in version-controlled code, review an exact revision, and run that revision consistently. A short script still requires review; the benefit is a clearer connection between what was reviewed and what the user executes.

Yeti's commands are public and reviewable, and its fixed 3-of-7 policy provides a deliberate default. CoreVault offers a reusable generator with a user-selected quorum and a separate environment layer. We believe that separation is the better foundation for contributors who want to improve generation safety without continually reworking the creation procedure alongside the guides.

The claim is specific: CoreVault provides stronger enforcement of the creation sequence, failure handling, binary selection, and change boundaries. It does not establish stronger cryptography or protection against a compromised creation machine. Both designs trust that environment, and CoreVault's remaining validation and independent-audit status are recorded above.

Yeti's operating guidance can complement CoreVault. Developers and reviewers are welcome to adapt the launcher, improve the guides, and independently test the generator while preserving these boundaries.
