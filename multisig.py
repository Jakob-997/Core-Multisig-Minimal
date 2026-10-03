#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

threshold, signer_count = map(
    int, input("M-of-N (example 2-of-3): ").replace("-of-", "-").split("-")
)

bitcoin_bin = Path(__file__).resolve().parent
state_dir = Path("/dev/shm/core-multisig")
data_dir = state_dir / "data"
backup_dir = state_dir / "backups"
data_dir.mkdir(parents=True)
backup_dir.mkdir()

def command(*args, wallet=None):
    cmd = [bitcoin_bin / "bitcoin-cli", f"-datadir={data_dir}"]
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

subprocess.run([
    bitcoin_bin / "bitcoind",
    f"-datadir={data_dir}",
    "-daemonwait",
    "-networkactive=0",
    "-listen=0",
], check=True)

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

subprocess.run(command("stop"), check=True)
print(f"Done. Backups are in {backup_dir}")
