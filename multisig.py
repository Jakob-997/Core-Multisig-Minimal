#!/usr/bin/env python3
import json
import subprocess

threshold, signer_count = map(
    int, input("Enter M-N (example 2-3): ").split("-")
)

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
    result = rpc("importdescriptors", request, wallet=wallet)[0]
    if not result["success"]:
        raise RuntimeError(result["error"]["message"])

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
