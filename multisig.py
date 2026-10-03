#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

print("Create your M-N Bitcoin Core multisig wallet.")
print("This creates N signer wallets and one watch-only wallet.")
print()
print("Before continuing, use a verified Bitcoin Core release: verify the release signatures")
print("and independently verify the signer key fingerprints you trust.")
print()
print("If this will be a wallet you actually use, permanently air-gap this computer:")
print("remove its network card(s) and never connect it to a network again.")
threshold, signer_count = map(
    int, input("Enter M-N (example 2-3): ").split("-")
)

backup_dir = Path("multisig-backups").resolve()
backup_dir.mkdir()

def command(*args, wallet=None):
    cmd = ["bitcoin-cli"]
    if wallet:
        cmd.append(f"-rpcwallet={wallet}")
    return cmd + list(args)

def rpc(*args, wallet=None):
    output = subprocess.check_output(command(*args, wallet=wallet), text=True)
    return json.loads(output)

def import_descriptor(wallet, descriptor_body):
    checksum = rpc("getdescriptorinfo", descriptor_body)["checksum"]
    descriptor = f"{descriptor_body}#{checksum}"
    request = json.dumps([{"desc": descriptor, "active": True, "timestamp": 0}])
    rpc("importdescriptors", request, wallet=wallet)

keys = []
for number in range(1, signer_count + 1):
    wallet = f"signer_{number}"
    rpc("createwallet", wallet, "false", "true")
    root_xpub = rpc("addhdkey", wallet=wallet)["xpub"]
    keys.append(rpc(
        "derivehdkey",
        "m/87h/0h/0h",
        json.dumps({"hdkey": root_xpub, "private": True}),
        wallet=wallet,
    ))

descriptor_body = "wsh(sortedmulti(" + str(threshold) + "," + ",".join(
    f"{key['origin']}{key['xpub']}/<0;1>/*" for key in keys
) + "))"

rpc("createwallet", "watch_only", "true", "true")
import_descriptor("watch_only", descriptor_body)

for number, key in enumerate(keys, 1):
    private_body = descriptor_body.replace(key["xpub"], key["xprv"])
    import_descriptor(f"signer_{number}", private_body)

wallets = ["watch_only"] + [f"signer_{n}" for n in range(1, signer_count + 1)]
for wallet in wallets:
    wallet_backup = backup_dir / wallet
    wallet_backup.mkdir()
    subprocess.run(
        command("backupwallet", str(wallet_backup / "wallet.dat"), wallet=wallet),
        check=True,
    )

print()
print("Finished.")
print(f"Backups are in: {backup_dir}")
print("Burn and verify each backup, then shut this computer down to erase the temporary wallet state.")
print("Before storing the backups, do a test spend. Try signing with every signer wallet")
print("and confirm that all wallets derive the same multisig addresses.")
print("After the test spend succeeds, store each labeled CD-R in a protective case.")
print("Do not leave the backup discs unattended until they are stored in their intended locations.")
print("Do not leave this computer unattended until it is powered off and the Tails USB has been removed.")
