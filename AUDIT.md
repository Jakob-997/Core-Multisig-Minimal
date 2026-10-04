# CoreVault Audit Log

## Verified-tarball launcher re-review — 2026-10-03

This AI-assisted re-review covers the launcher change based on commit
[`aae2e2a569845aeb62e037517237fe02162f1cc8`](https://github.com/Jakob-997/CoreVault/commit/aae2e2a569845aeb62e037517237fe02162f1cc8).
The exact executable Git blob SHAs for this review are:

- `tails.sh`: `9a8d639d9f0ba238b2d008502bd3fdc263b67ea7`
- `multisig.py`: `19f3988e32566f39e46c4feff1807175c17e06d4` — unchanged from the wallet-construction baseline.

### Trust flow and source of the pin

The user places `CoreVault/` alongside the compressed official
`bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz`. The launcher sets a restrictive umask,
creates a fresh private directory with `mktemp -d /dev/shm/core-multisig.XXXXXX`,
and installs cleanup traps before copying or verifying the archive.

The hardcoded SHA-256 is taken from the official
[v32.0rc2 SHA256SUMS](https://bitcoincore.org/bin/bitcoin-core-32.0/test.rc2/SHA256SUMS):

```text
0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1  bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz
```

During this review, the official checksum file and archive were downloaded over
HTTPS and the archive's digest matched this value. This review did not perform
independent release-signature authentication; the documented operator signature
and trusted-key-fingerprint verification remains required.

The launcher verifies its private archive copy before extracting that same copy.
Replacing the original adjacent tarball after verification cannot substitute the
bytes extracted. Failed copying, hashing, or extraction aborts before Core runs.
There is no network fetch, configurable digest, or fallback binary location.
Only absolute paths to `bitcoin-cli` and `bitcoind` inside the fresh extraction
are used, including version probes, shutdown RPC, and the path passed to the
unchanged generator. A pre-existing `bitcoin-32.0rc2` directory and Core binaries
on `PATH` are ignored.

Runtime HOME remains in that private directory. Wallet backups remain at
`CoreVault/multisig-backups`, outside temporary cleanup. An existing backup
directory still causes creation to stop rather than overwrite it. After Core
startup, cleanup retains the existing stop-and-wait behavior before deleting
temporary runtime state and extracted executables.

### Validation and result

- POSIX shell syntax checked with `dash -n`; ShellCheck passed without findings.
- Tested on Ubuntu under WSL with the actual hash-matching release archive.
- Missing/wrong archives, copy failure, checksum-tool failure, extraction failure,
  missing/non-executable extracted binaries, generator failure, and TERM during
  copying all exited unsuccessfully and removed their temporary directories.
- Rejection before verification did not invoke extraction or create backups.
- An existing backup directory and its sentinel file were preserved.
- Three successful disposable 2-of-3 creations produced three signer wallets and
  a watch-only wallet in the CoreVault folder. The generator received the exact
  fresh `/dev/shm/.../bitcoin-32.0rc2/bin/bitcoin-cli` path; temporary directories
  were removed and the test daemon exited. Repeated runs used fresh directories.
- Planted binaries in the adjacent extracted folder and on `PATH` never ran.
  Replacing the source tarball immediately after successful hashing still allowed
  creation from the verified private copy.
- `multisig.py` retains its original Git blob SHA; no wallet-construction changes.

No new unresolved implementation issue was found in this scoped launcher review
under the trusted-host assumptions below. This does not repeat or extend the
historical PSBT/restore review and is not an independent professional audit.

### Limits and retained assumptions

The execution tests stubbed Zenity/setsid and global `pkill` to avoid UI and
unrelated-process side effects; real Core startup, RPCs, wallet creation, shutdown,
and process-exit checks were exercised. The new flow has not been tested on Tails
or with optical-media recovery/test spends. The prior Tails guide-display test
recorded below applies to the previous launcher snapshot.

The host, system utilities, reviewed CoreVault files (including the digest),
official release, and same-user processes must be trusted. Private permissions
do not defend against root or hostile processes running as the same user.
The existing launcher intentionally stops user-owned `bitcoind`/`bitcoin-qt`
processes by name and waits for all such processes; it is intended for the
dedicated offline Tails session, not a shared running-node environment.

`/dev/shm` must have space for the archive plus extraction and permit executable
files. A `noexec` mount fails closed; the launcher does not remount it or use an
unverified installation. Cleanup traps cannot handle SIGKILL or power loss.
RAM-backed storage is not protection against host compromise or swap policy;
the documented non-persistent Tails environment remains an operational condition.

## Previous executable review target (historical)

**Wallet-construction audit baseline:**  
[`29a65f87f8070cba71458accf3a44a6f7d88b80b`](https://github.com/Jakob-997/CoreVault/commit/29a65f87f8070cba71458accf3a44a6f7d88b80b)

**Final pre-release executable snapshot re-reviewed:**  
[`d80b31a2dabd437022556936778b4a5427db2db5`](https://github.com/Jakob-997/CoreVault/commit/d80b31a2dabd437022556936778b4a5427db2db5)

Executable blob SHAs at that snapshot:

- `multisig.py`: `19f3988e32566f39e46c4feff1807175c17e06d4`
- `tails.sh`: `d0e3ebc2f9297fecc0455a6350fe1ff2d95af789`

Between the audit baseline and the final executable snapshot, `multisig.py` did not change. The only executable change was to the Tails launcher so the post-creation Zenity guide opens in a fully detached, nonblocking session. That behavior was then tested successfully on Tails. The other changes were documentation and the code of conduct.

Those blob SHAs identify the previous snapshot only. The verified-tarball launcher
review at the top of this file supersedes its launcher selection behavior; the
wallet-construction baseline remains unchanged.

**Bitcoin Core version reviewed:** `v32.0rc2`  
**Bitcoin Core commit:**  
[`bc795e60dbb2c6e9c9556949731912429290626a`](https://github.com/bitcoin/bitcoin/commit/bc795e60dbb2c6e9c9556949731912429290626a)

Review date: 2026-10-03.

This audit log records an AI-assisted source review of CoreVault against the Bitcoin Core implementation, tests, documentation, and relevant BIPs listed below. It is not an independent professional security audit.

## Scope

The review covered:

- `multisig.py`
- `tails.sh`
- the pre-creation procedure
- the post-creation backup, restore, and test-spend procedure
- Bitcoin Core v32.0rc2 wallet creation and HD-key RPC behavior
- descriptor parsing, checksums, multipath descriptors, `wsh()`, and `sortedmulti()`
- descriptor import into watch-only and signing wallets
- BIP87 derivation and key-origin information
- PSBT signing behavior
- wallet restoration/rescan assumptions
- the exact Bitcoin Core binary selection performed by the Tails launcher

A repository-wide search of Bitcoin Core v32.0rc2 was used to locate multisig-related documentation, tests, and implementation code. Closely related descriptor, wallet, HD-key, RPC, and PSBT code was then reviewed because the CoreVault construction depends on those components even when the filename does not contain the word “multisig.”

## Result

No unresolved critical, high, or medium severity implementation vulnerability was identified in the reviewed CoreVault wallet-construction logic after the fixes recorded below.

The construction is consistent with the reviewed Bitcoin Core v32.0rc2 behavior:

- Bitcoin Core generates each signer root key.
- The signer wallets are blank descriptor wallets with private keys enabled.
- `addhdkey` creates and stores a fresh Core HD root.
- `derivehdkey` derives the BIP87 account key at `m/87h/0h/0h`.
- The shared descriptor is native SegWit `wsh(sortedmulti())`.
- `/<0;1>/*` supplies external/receive and internal/change derivation.
- The watch-only wallet has private keys disabled.
- Each signing wallet imports the same multisig descriptor with only its own account xpub replaced by its corresponding xprv.
- Descriptor checksums are generated by Bitcoin Core.
- `timestamp: 0` deliberately preserves full-history restoration.
- Bitcoin Core, not CoreVault, validates descriptor syntax, M-of-N threshold validity, and the standard multisig key limit.
- Signing is compatible with Bitcoin Core's PSBT workflow.

The Python generator contains no custom cryptographic implementation.

## Issues resolved during review

### Sensitive private descriptor data in process arguments

An earlier revision passed RPC parameters directly as `bitcoin-cli` command-line arguments. For signer imports, that meant the private descriptor containing an xprv could temporarily be visible in the process command line.

CoreVault now invokes `bitcoin-cli -stdin` and sends RPC parameters over standard input. Bitcoin Core explicitly provides `-stdin` for reading extra RPC arguments from standard input and recommends stdin handling for sensitive information.

**Status:** fixed.

### Ambiguous Bitcoin Core binary selection

An earlier launcher prepended the adjacent Bitcoin Core directory to `PATH`. This normally selected the intended binary, but still depended on command-name resolution.

The previous launcher used the exact adjacent paths:

```text
../bitcoin-32.0rc2/bin/bitcoin-cli
../bitcoin-32.0rc2/bin/bitcoind
```

It also checked that both binaries report Bitcoin Core v32.0rc2 before wallet creation. This protected path selection but did not authenticate the binary contents. The verified-tarball change reviewed above replaces adjacent-folder trust with a pinned archive digest and fresh extraction. `multisig.py` still receives the exact `bitcoin-cli` path from the launcher.

**Status:** fixed.

### Descriptor-import failures were not originally checked

`importdescriptors` reports per-descriptor success in its returned JSON object. An earlier revision did not inspect that value.

CoreVault now aborts if the imported descriptor returns `"success": false`.

**Status:** fixed.

### Bitcoin Core shutdown before temporary-state deletion

The launcher previously requested shutdown and could proceed to delete temporary Core state before the daemon had definitely exited.

The launcher now waits for Core processes to exit before removing the temporary RAM-backed state.

**Status:** fixed.

### Full-history restoration requires available block history

CoreVault intentionally imports descriptors with `timestamp: 0`. When the watch-only wallet created offline is later loaded on an online node, Core must be able to scan the historical chain to discover old transactions.

The operating instructions now require a fully synced, **unpruned** online Bitcoin Core node for the initial restoration/test workflow.

**Status:** documented and required operationally.

### CD-R wallets must be copied to writable storage before loading

A CD-R is read-only, while a Bitcoin Core wallet database is intended to operate from writable storage.

The post-creation guide now instructs the user to copy each wallet folder from the CD-R to temporary writable storage before testing/loading it. The watch-only folder is likewise copied to writable storage on the online machine before it is loaded.

**Status:** fixed in operating procedure.

### Upstream multisig wizard status

The Bitcoin Core multisig wizard used as a structural reference is currently an open pull request, not part of Bitcoin Core v32.0rc2. Earlier wording could be read as though the wizard were already shipped.

The README now distinguishes the proposed wizard from functionality actually present in v32.0rc2.

**Status:** fixed in documentation.

### Nonblocking post-creation guide

The post-creation Zenity window originally blocked the console until the user closed it. A simple background launch then proved unreliable because the window could terminate with the launcher.

The Tails launcher now starts the post-creation guide with `setsid -f`, detached from the console session. The console completes immediately while the guide remains open independently.

**Status:** fixed and tested on Tails.

## Correctness checks

### BIP87 derivation

BIP87 defines:

```text
m / 87' / coin_type' / account' / change / address_index
```

For Bitcoin mainnet, coin type is 0. CoreVault uses account 0, giving `m/87h/0h/0h`, followed by the descriptor's `/<0;1>/*` receive/change and address-index derivation.

Each signer wallet receives a newly generated independent Core HD root, so account 0 is not being reused across multiple multisig configurations from the same master root in the CoreVault creation session.

**Result:** consistent with BIP87.

### HD-key generation and derivation

In v32.0rc2, `addhdkey` can generate a new random HD root and store it in the wallet. `derivehdkey` derives from a wallet HD key and can return private derived key material when requested.

CoreVault asks Core to perform both operations and does not implement BIP32 derivation itself.

**Result:** correct.

### Descriptor form

CoreVault constructs:

```text
wsh(sortedmulti(M,[origin]xpub/<0;1>/*,...))
```

Bitcoin Core supports `wsh()`, `sortedmulti()`, ranged key expressions, key origin information, and multipath expansion. `sortedmulti()` sorts the derived public keys lexicographically when constructing the script.

**Result:** correct.

### Receive/change multipath

Bitcoin Core expands `<0;1>` multipath descriptors into two descriptor branches. Imported active multipath descriptors use the first branch as external/receive and the second as internal/change.

**Result:** correct.

### Descriptor checksum

CoreVault obtains the checksum from `getdescriptorinfo` for the exact descriptor body it imports. Bitcoin Core's implementation returns the checksum for the input descriptor, including when the input contains private key material.

**Result:** correct.

### Watch-only wallet

CoreVault creates the watch-only wallet with private keys disabled and imports only the public multisig descriptor.

Bitcoin Core rejects private descriptor material in a wallet with private keys disabled, so this separation is enforced by Core as well as by CoreVault.

**Result:** correct.

### Signing-wallet descriptor import

Bitcoin Core v32.0rc2 currently rejects importing a descriptor containing no private keys into a private-key-enabled wallet. CoreVault therefore replaces only the local signer's account xpub with that signer's xprv before import.

This is the same workaround used by the proposed Bitcoin Core multisig wizard while bitcoin/bitcoin#35377 remains unmerged. Core may warn that not all private keys are present; this is expected because each signer intentionally holds only one of the N private keys.

**Result:** correct for v32.0rc2.

### Threshold and signer-count validation

CoreVault intentionally keeps the Python generator minimal and does not duplicate Core's descriptor validation.

Bitcoin Core's descriptor parser rejects a threshold below 1, a threshold larger than N, invalid descriptor syntax, and standard `multi/sortedmulti` constructions exceeding the supported 20-key limit.

A malformed policy may therefore create some blank signer wallets before descriptor construction fails, but it does not silently create a different valid policy.

**Result:** acceptable design choice; policy selection remains the user's responsibility.

### PSBT workflow

Bitcoin Core's multisig documentation and functional tests cover watch-only multisig wallet funding, PSBT creation, participant signing with `walletprocesspsbt`, signature combination/sequential signing, finalization, and broadcast.

CoreVault's operational model—online watch-only coordinator, offline signer wallets, unsigned PSBT transport, offline verification/signing—is compatible with that workflow.

**Result:** correct.

### Restore and address verification

BIP87 requires the multisig descriptor/configuration in addition to private key information for reliable restore. Each CoreVault signer wallet persists the shared multisig descriptor as well as its own private key material; the watch-only wallet persists the public descriptor.

The post-creation procedure requires checking that all restored wallets derive the same receive addresses and completing a disposable test spend before relying on the wallet.

**Result:** consistent with the reviewed multisig standards and Core behavior.

## Accepted architectural risks and assumptions

These are not hidden findings; they are properties of the chosen design.

### One-machine key generation

All N signer roots are generated by one verified Bitcoin Core process on one offline Tails machine during setup.

The resulting M-of-N wallet protects against later loss or theft of separately stored signer backups, but it does **not** provide independent key-generation diversity. A compromise of the creation environment, verified Bitcoin Core binary, operating system, or entropy source capable of compromising all generated keys is a common-mode risk.

CoreVault mitigates this through verified Tails, verified Bitcoin Core release signatures, an exact pinned Core version, a permanent physical air gap, and a disposable end-to-end test. It does not claim to eliminate creation-machine compromise.

### Unencrypted signer discs

Signer wallet backups are intentionally not encrypted. Possession of one signer disc gives access to that signer's private key.

This avoids adding a passphrase/recovery secret but places greater importance on physical storage and geographic separation.

### Multisig configuration privacy

Every signer wallet contains the multisig descriptor, and the watch-only wallet contains the public descriptor. Anyone who obtains any of these wallet backups can derive wallet addresses and monitor the wallet's on-chain activity.

### User-selected M-of-N policy

Core ensures that the chosen M-of-N is syntactically valid, but CoreVault does not decide whether a valid policy is appropriate for a user's threat model. A valid configuration such as 1-of-N may provide very different security properties from 2-of-3 or 3-of-5.

### Release-candidate dependency

This audit is tied specifically to Bitcoin Core v32.0rc2. CoreVault uses new HD-key RPC functionality introduced after v31.

A later release candidate or final v32.0 release should be functionally retested before the launcher version pin is changed. If Core behavior affecting wallet creation, HD keys, or descriptor import changes, the generator should be re-reviewed.

### Proposed upstream wizard

bitcoin/bitcoin#36325 is a useful structural reference but is open and unmerged. It is not part of the trusted runtime dependency for this audit.

bitcoin/bitcoin#35377 is also open and unmerged. If it lands, CoreVault's private-key substitution workaround may no longer be necessary.

### Operational environment

The review validates source logic and the documented workflow. It is not a substitute for an end-to-end test on the exact Tails release, optical drive/media, Bitcoin Core v32.0rc2 binary, and online recovery node that will actually be used.

## References reviewed

### Exact Bitcoin Core release

- [Bitcoin Core v32.0rc2 source tree](https://github.com/bitcoin/bitcoin/tree/v32.0rc2)
- [Bitcoin Core v32.0rc2 commit `bc795e60dbb2c6e9c9556949731912429290626a`](https://github.com/bitcoin/bitcoin/commit/bc795e60dbb2c6e9c9556949731912429290626a)

### Bitcoin Core documentation

- [Multisig tutorial — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/multisig-tutorial.md)
- [Offline signing tutorial — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/offline-signing-tutorial.md)
- [Output descriptors — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/descriptors.md)
- [PSBT documentation — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/psbt.md)
- [Managing wallets — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/managing-wallets.md)

### Bitcoin Core implementation

- [Wallet RPC implementation: createwallet, addhdkey, derivehdkey, gethdkeys — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/wallet/rpc/wallet.cpp)
- [Descriptor import / backup RPC implementation — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/wallet/rpc/backup.cpp)
- [Wallet spending and PSBT RPC implementation — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/wallet/rpc/spend.cpp)
- [Descriptor parser and sortedmulti implementation — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/script/descriptor.cpp)
- [getdescriptorinfo / deriveaddresses implementation — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/rpc/output_script.cpp)
- [Wallet storage, HD-key handling, loading, and chain synchronization — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/wallet/wallet.cpp)
- [bitcoin-cli implementation, including -stdin — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/bitcoin-cli.cpp)
- [bitcoind version/startup implementation — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/bitcoind.cpp)

### Bitcoin Core tests

- [HD-key derivation functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/wallet_derivehdkey.py)
- [HD-key listing functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/wallet_gethdkeys.py)
- [Descriptor-import functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/wallet_importdescriptors.py)
- [Multisig descriptor + PSBT functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/wallet_multisig_descriptor_psbt.py)
- [getdescriptorinfo functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/rpc_getdescriptorinfo.py)
- [createwallet functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/wallet_createwallet.py)
- [createwalletdescriptor functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/wallet_createwalletdescriptor.py)
- [bitcoin-cli stdin/argument functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/interface_bitcoin_cli.py)
- [createmultisig and BIP67 functional tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/test/functional/rpc_createmultisig.py)
- [Low-level multisig unit tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/test/multisig_tests.cpp)
- [Wallet PSBT unit tests — v32.0rc2](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/src/wallet/test/psbt_wallet_tests.cpp)

### BIPs

- [BIP32 — Hierarchical Deterministic Wallets](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
- [BIP67 — Deterministic multisig public-key sorting](https://github.com/bitcoin/bips/blob/master/bip-0067.mediawiki)
- [BIP87 — Hierarchy for Deterministic Multisig Wallets](https://github.com/bitcoin/bips/blob/master/bip-0087.mediawiki)
- [BIP129 — Bitcoin Secure Multisig Setup](https://github.com/bitcoin/bips/blob/master/bip-0129.mediawiki)
- [BIP174 — Partially Signed Bitcoin Transaction Format](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
- [BIP380 — Output Script Descriptors General Operation](https://github.com/bitcoin/bips/blob/master/bip-0380.mediawiki)
- [BIP382 — SegWit Output Script Descriptors](https://github.com/bitcoin/bips/blob/master/bip-0382.mediawiki)
- [BIP383 — Multisig Output Script Descriptors](https://github.com/bitcoin/bips/blob/master/bip-0383.mediawiki)

### Relevant Bitcoin Core pull requests and proposed wizard

- [bitcoin/bitcoin#22838 — multipath descriptors](https://github.com/bitcoin/bitcoin/pull/22838)
- [bitcoin/bitcoin#35377 — allow public descriptor import when wallet already holds the private key](https://github.com/bitcoin/bitcoin/pull/35377) — open/unmerged at review time
- [bitcoin/bitcoin#36325 — proposed multisig wizard](https://github.com/bitcoin/bitcoin/pull/36325) — open/unmerged at review time
- [Pinned proposed wizard source reviewed](https://github.com/rxbryan/bitcoin/blob/2803e1518bb22394a80bac94e2435bb3982d0cde/contrib/multisig/wizard.py)
- [Pinned proposed wizard README reviewed](https://github.com/rxbryan/bitcoin/blob/2803e1518bb22394a80bac94e2435bb3982d0cde/contrib/multisig/README.md)
- [bitcoin/bitcoin#36133 — multipath descriptor storage/listing behavior](https://github.com/bitcoin/bitcoin/pull/36133)
- [bitcoin/bitcoin#36126 — descriptor/key labeling work](https://github.com/bitcoin/bitcoin/pull/36126)

## Final maintenance rule

For this reviewed design:

1. Treat `multisig.py` as frozen.
2. Do not change the Bitcoin Core version pin without retesting against that exact Core release.
3. If Core wallet/HD-key/descriptor behavior requires a generator change, re-review `multisig.py`.
4. Keep Tails-specific changes in `tails.sh`.
5. Keep operational wording and procedure changes in the pre/post guides.
6. Preserve an exact Git commit as the target of any external audit.

The highest-value next step is an independent Bitcoin developer/security review of the exact executable blob SHAs identified at the top of this file, followed by a complete disposable-funds test on the exact intended hardware and media.
