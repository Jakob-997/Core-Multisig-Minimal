# CoreVault

**Bitcoin Core multisig, reduced to a small procedure you can actually review.**

Built with the [**Bitcoin Core Feature Overlay**](https://github.com/Jakob-997/Bitcoin-Core-Feature-Overlay) template.

CoreVault creates an M-of-N native SegWit multisig wallet on an offline Tails computer. It produces one signer wallet per participant plus a watch-only wallet for receiving, monitoring, and creating unsigned PSBTs.

## Demo

https://github.com/user-attachments/assets/fae51512-3197-4d1b-b880-21e0152dc246

## Design at a glance

- Bitcoin Core generates, derives, validates, and stores the keys.
- CoreVault uses BIP87 and `wsh(sortedmulti())`.
- The signer wallets contain the shared multisig descriptor and only their own private key material.
- The watch-only wallet contains the public multisig configuration.
- CoreVault contains **no custom cryptography**.

## Why this design

The question is not “why trust a random GitHub author?” You should not.

The design instead tries to make the trust surface small enough to verify: a short generator, a small Tails launcher, a pinned Bitcoin Core release, explicit failure checks, and exact reviewed revisions. Before wallet creation, the launcher disables NetworkManager networking, verifies the official Core archive, extracts it into a fresh directory, and runs only those binaries.

**CoreVault has received AI-assisted review, but no independent professional security audit.** See [AUDIT.md](AUDIT.md).

## Quick start

> **For a real wallet:** use a dedicated computer, preferably a laptop, that is physically air-gapped with its network hardware removed and never reconnected to any network afterward. CoreVault's software networking shutdown is defense in depth, not a substitute for permanent physical isolation.

```text
1. Verify Tails and Bitcoin Core v32.0rc2.
2. Put CoreVault next to:
   bitcoin-32.0rc2-x86_64-linux-gnu.tar.gz
3. Read PRE-CREATION-GUIDE.txt.
4. In Tails, make tails.sh executable and choose "Run as a Program".
5. Enter your policy, e.g. 2-3.
6. Follow POST-CREATION-GUIDE.txt to burn, verify, test, and store backups.
```

Use **Bitcoin Core v32.0rc2 exactly**. Another Core release must be tested before changing the version pin.

## Read more

- [DESIGN.md](DESIGN.md) — architecture, trust model, Core verification, wallet construction, and comparison with Yeti 2.0
- [FAQ.md](FAQ.md) — common design and usage questions
- [AUDIT.md](AUDIT.md) — exact reviewed revisions, findings, limitations, and upstream references
- [PRE-CREATION-GUIDE.txt](PRE-CREATION-GUIDE.txt) — preparation checklist
- [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt) — backup, restore, GUI PSBT test spend, and storage procedure
