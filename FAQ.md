# CoreVault FAQ

## Why should I trust this?

You should not trust CoreVault because of the maintainer's identity. Review the exact code you intend to run, verify Tails and Bitcoin Core, test the full procedure with disposable funds, and preferably obtain an independent Bitcoin-specific review.

CoreVault's design goal is to make that review practical by keeping project-specific executable logic small and delegating Bitcoin operations to Bitcoin Core.

## Is CoreVault professionally audited?

No. It has received AI-assisted source review and testing, documented in [AUDIT.md](AUDIT.md), but no independent professional security audit.

Independent audits and published findings are explicitly encouraged.

## Does CoreVault implement cryptography?

No. Bitcoin Core performs key generation, HD derivation, descriptor validation, signing, and wallet storage.

## Why BIP87?

BIP87 is specifically designed for deterministic multisig wallets. CoreVault uses `m/87h/0h/0h` and puts the script policy in the descriptor.

Bitcoin Core's older multisig tutorial intentionally uses a different path as a compatibility choice and notes that it does not conform to BIP87. The newer proposed multisig wizard uses the BIP87 approach that CoreVault follows.

## Why does every signer import the multisig descriptor?

It makes each signer a real participant in the multisig wallet rather than merely a generic single-signature key wallet that happens to recognize a key referenced by a PSBT.

Each signer knows the complete public policy but contains only its own private key material.

## Can I sign through Bitcoin-Qt?

Yes. The intended workflow is to create an unsigned PSBT with the online watch-only wallet, move it to the offline computer, then use Bitcoin-Qt's **Load PSBT from file... → Sign Tx → Save...** flow with successive signer wallets until the threshold is reached.

See [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt).

## Can the online node be pruned?

Yes, provided it still has every block Bitcoin Core needs to synchronize or rescan the copied wallet. Because CoreVault uses `timestamp: 0`, a node that has already pruned required historical blocks may need to redownload/reindex or use a node with the missing history.

## Does `nmcli networking off` make the machine air-gapped?

No. It is an additional software control. The documented security model still calls for a physical air gap.

## Why pin Bitcoin Core v32.0rc2?

CoreVault depends on the specific wallet RPC behavior reviewed for that release, including the newer HD-key workflow. Changing the version is a security-relevant maintenance event and requires testing before the pin moves.

## Are signer backups encrypted?

No. Possession of a signer backup exposes that signer's private key. Any wallet backup also exposes the multisig public graph and therefore the wallet's addresses.

Follow the physical-storage procedure in [POST-CREATION-GUIDE.txt](POST-CREATION-GUIDE.txt).

## Can one compromised setup machine defeat the multisig?

Yes. All signer roots are generated in one creation session, so a compromised creation environment is a common-mode risk. The multisig protects against later loss or theft of separately stored signer backups; it does not make a malicious setup machine safe.
