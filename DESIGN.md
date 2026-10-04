# CoreVault Design

This document explains the reasoning behind CoreVault. The short [README](README.md) is the project overview; the operational procedure lives in the [pre-creation](PRE-CREATION-GUIDE.txt) and [post-creation](POST-CREATION-GUIDE.txt) guides; exact review history lives in [AUDIT.md](AUDIT.md).

## Trust model

CoreVault is not meant to be trusted because of who wrote it. It is meant to make the security-critical procedure small enough that another person can inspect exactly what will run.

The generator contains no custom cryptography. Bitcoin Core performs key generation, BIP32 derivation, descriptor parsing and validation, wallet storage, PSBT signing, and transaction finalization. CoreVault connects those operations into a repeatable procedure and checks failure results.

The security model is therefore:

> Verify a small procedure that delegates Bitcoin operations to a pinned Bitcoin Core release.

That still requires trust in the verified Tails environment, the pinned Bitcoin Core release, the host hardware and entropy source, and the exact CoreVault revision being executed. A compromised creation machine can compromise every signer because all signer roots are generated during one setup session.

## Three layers

| Layer | File | Responsibility |
| --- | --- | --- |
| Generator | [multisig.py](multisig.py) | Create signer roots and construct/import the shared multisig descriptor |
| Tails launcher | [tails.sh](tails.sh) | Disable software networking, verify/extract Core, isolate runtime state, stop Core, and display the guides |
| Human procedure | [PRE-CREATION-GUIDE.txt](PRE-CREATION-GUIDE.txt) / [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt) | Preparation, backups, verification, test spend, and storage |

The generator is intentionally treated as frozen after review. Operating-system changes belong in the launcher; procedure changes belong in the guides.

## Wallet construction

Current wallet parameters:

| Setting | Value |
| --- | --- |
| Network | Bitcoin mainnet |
| Account derivation | `m/87h/0h/0h` |
| Descriptor | `wsh(sortedmulti())` |
| Receive/change | `/<0;1>/*` |
| Import timestamp | `0` |

Each signer starts as a blank descriptor wallet with private keys enabled. Bitcoin Core creates a fresh HD root with `addhdkey`, then derives the BIP87 account key at `m/87h/0h/0h`.

CoreVault combines the signer account keys into one shared descriptor:

```text
wsh(sortedmulti(M,[origin]xpub/<0;1>/*,...))
```

The watch-only wallet imports the public descriptor. Each signer imports the same descriptor with only its own account xpub replaced by its corresponding xprv. That means every signer wallet understands the actual multisig policy while holding only its own private key material.

For the pinned Core release, this substitution is necessary because of current descriptor-import behavior discussed in [bitcoin/bitcoin#35377](https://github.com/bitcoin/bitcoin/pull/35377).

### Why BIP87 instead of the path in Core's older multisig tutorial?

Bitcoin Core's current multisig tutorial deliberately uses an existing BIP44-style account path and explicitly notes that it does not conform to BIP87. That tutorial reflects an older practical limitation: a wallet could readily sign for paths already represented by its descriptors.

CoreVault instead follows the newer approach reflected in the proposed Bitcoin Core multisig wizard: generate/store an HD root, derive a dedicated BIP87 multisig account, and import the resulting multisig descriptor into each signer.

BIP87 is a better semantic fit for a new descriptor-based multisig wallet because the derivation path identifies the multisig account while the descriptor specifies the script construction.

## Bitcoin Core verification

The intended workflow requires users to verify Tails and independently verify the Bitcoin Core release/signing keys they trust.

The launcher then performs an additional offline enforcement step:

1. After the user enters M-of-N, run `nmcli networking off` and confirm NetworkManager reports networking disabled.
2. Check the adjacent `bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz` against the hardcoded official SHA-256.
3. Create a brand-new uniquely named extraction directory.
4. Extract the verified archive there.
5. Use only that extraction's `bitcoin-cli` and `bitcoind` by absolute path.

The pinned SHA-256 is:

```text
0255103718033e6aee15fa944717fc277e047b845bff1e7408af0ea732d8d0c1
```

Existing extracted Core directories and installations on `PATH` are ignored. The automatic NetworkManager shutdown is defense in depth and does not replace the documented physical air gap.

## Why code instead of a command-by-command guide?

A sequence of copied shell commands that derives keys, assembles a descriptor, and imports wallets still contains security-relevant logic. Calling that “no code” does not remove the need to review the procedure.

CoreVault accepts that there is project-specific logic and tries to handle it explicitly:

- keep the executable surface small;
- delegate Bitcoin behavior to Core;
- check failures;
- pin dependencies;
- preserve exact revisions for review;
- separate generator, environment, and human instructions.

The benefit is a direct connection between **what was reviewed** and **what the user executes**.

## Compared with Yeti 2.0

CoreVault and [Yeti 2.0](https://github.com/bowlarbear/yeti-2.0) share the same broad foundation: use Bitcoin Core on an offline computer to create and operate a multisig wallet.

Yeti places much of the construction procedure in a human-operated command sequence. Its signer wallets remain ordinary single-signature Core wallets whose keys can sign a multisig PSBT because the PSBT supplies the script and key-origin information.

CoreVault instead imports the complete multisig descriptor into every signer. Each signer therefore directly knows the multisig policy and contains its own private key within that policy. This also makes the normal Bitcoin-Qt **Load PSBT → Sign Tx → Save** workflow natural for each signer.

CoreVault's main architectural claims are narrower than “better cryptography.” It aims for stronger enforcement of:

- the exact creation sequence;
- failure handling;
- the Bitcoin Core binary being executed;
- separation between stable wallet construction and changeable operating instructions;
- an exact, compact review target.

Both approaches still trust the creation environment. Multisig does not protect against a machine that compromises every key during setup.

## Auditability

An external review should target an exact commit and examine both executable files plus the documented workflow. A useful review should test wallet creation, address agreement, backup restoration, PSBT signing, and the intended M-of-N threshold.

Independent reviews are welcome. If you audit CoreVault, please consider publishing the findings or opening an issue so they can be linked from the project. Funding or organizing a professional review is also welcome.

Because the security-critical surface is intentionally small, a focused Bitcoin expert review should be much narrower than auditing a full wallet application.

## Upstream references

CoreVault's construction and review were informed by:

- [Bitcoin Core proposed multisig wizard — bitcoin/bitcoin#36325](https://github.com/bitcoin/bitcoin/pull/36325)
- [Pinned wizard source used as a structural reference](https://github.com/rxbryan/bitcoin/blob/2803e1518bb22394a80bac94e2435bb3982d0cde/contrib/multisig/wizard.py)
- [Descriptor import behavior — bitcoin/bitcoin#35377](https://github.com/bitcoin/bitcoin/pull/35377)
- [Bitcoin Core multisig tutorial](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/multisig-tutorial.md)
- [Bitcoin Core offline-signing tutorial](https://github.com/bitcoin/bitcoin/blob/v32.0rc2/doc/offline-signing-tutorial.md)
- [BIP87](https://github.com/bitcoin/bips/blob/master/bip-0087.mediawiki)
- [BIP129](https://github.com/bitcoin/bips/blob/master/bip-0129.mediawiki)

The proposed wizard is not shipped in v32.0rc2 and is not a runtime dependency. Referencing upstream work does not transfer its review coverage or imply Bitcoin Core endorsement.
