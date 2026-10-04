#!/usr/bin/env python3
import json
import subprocess
import sys

bitcoin_cli = sys.argv[1]

threshold, signer_count = map(
    int, input("Enter M-N (example 2-3): ").split("-")
)

if signer_count < 2 or signer_count > 20:
    raise ValueError("Signer count must be between 2 and 20")
if threshold < 1 or threshold > signer_count:
    raise ValueError("Threshold must be between 1 and the signer count")

def command(method, wallet=None):
    cmd = [bitcoin_cli]
    if wallet:
        cmd.append(f"-rpcwallet={wallet}")
    return cmd + ["-stdin", method]

def rpc(method, *args, wallet=None, sensitive=False):
    stdin = "".join(f"{arg}\n" for arg in args)
    try:
        output = subprocess.check_output(
            command(method, wallet=wallet),
            input=stdin,
            text=True,
            stderr=subprocess.PIPE if sensitive else None,
        )
    except subprocess.CalledProcessError:
        if sensitive:
            raise RuntimeError(
                f"{method} failed while processing private descriptor data; "
                "error details suppressed"
            ) from None
        raise
    return json.loads(output)

def import_descriptor(wallet, descriptor_body, *, sensitive=False):
    checksum = rpc(
        "getdescriptorinfo",
        descriptor_body,
        sensitive=sensitive,
    )["checksum"]
    descriptor = f"{descriptor_body}#{checksum}"
    request = json.dumps([{"desc": descriptor, "active": True, "timestamp": 0}])
    result = rpc(
        "importdescriptors",
        request,
        wallet=wallet,
        sensitive=sensitive,
    )[0]
    if not result["success"]:
        if sensitive:
            raise RuntimeError(
                "Signer descriptor import failed; private error details suppressed"
            )
        raise RuntimeError(result["error"]["message"])

def public_multisig_descriptors(wallet):
    descriptors = rpc("listdescriptors", wallet=wallet)["descriptors"]
    return sorted(
        item["desc"]
        for item in descriptors
        if item["desc"].startswith("wsh(sortedmulti(")
    )

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

descriptor_info = rpc("getdescriptorinfo", descriptor_body)
if len(descriptor_info.get("multipath_expansion", [])) != 2:
    raise RuntimeError(
        "Multisig descriptor did not expand to exactly receive and change paths"
    )

rpc("createwallet", "watch_only", "true", "true")
import_descriptor("watch_only", descriptor_body)

for number, key in enumerate(keys, 1):
    private_body = descriptor_body.replace(key["xpub"], key["xprv"])
    import_descriptor(
        f"signer_{number}",
        private_body,
        sensitive=True,
    )

expected_descriptors = public_multisig_descriptors("watch_only")
if len(expected_descriptors) != 2:
    raise RuntimeError(
        "Watch-only wallet does not contain exactly two multisig descriptors"
    )

for number in range(1, signer_count + 1):
    wallet = f"signer_{number}"
    if public_multisig_descriptors(wallet) != expected_descriptors:
        raise RuntimeError(
            f"{wallet} public multisig descriptors do not match watch_only"
        )
