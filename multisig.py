#!/usr/bin/env python3
import json, subprocess, sys, time
from pathlib import Path

if len(sys.argv) != 4:
    raise SystemExit("usage: ./multisig.py M N /path/to/bitcoin/bin")

M, N = map(int, sys.argv[1:3])
BIN = Path(sys.argv[3]).resolve()
STATE = Path("/dev/shm/core-multisig")
DATA, OUT = STATE / "data", STATE / "backups"
BITCOIND, CLI = BIN / "bitcoind", BIN / "bitcoin-cli"

if not (1 <= M <= N <= 20):
    raise SystemExit("require 1 <= M <= N <= 20")
if STATE.exists():
    raise SystemExit(f"{STATE} already exists; reboot before generating another wallet")
if not BITCOIND.is_file() or not CLI.is_file():
    raise SystemExit("bitcoin-cli and bitcoind not found in the supplied Bitcoin Core bin directory")

DATA.mkdir(parents=True)
OUT.mkdir()
subprocess.run([BITCOIND, f"-datadir={DATA}", "-daemon", "-networkactive=0", "-listen=0"], check=True)

def cli(*args, wallet=None):
    cmd = [CLI, f"-datadir={DATA}"]
    if wallet:
        cmd.append(f"-rpcwallet={wallet}")
    out = subprocess.check_output(cmd + list(args), text=True).strip()
    return None if not out else json.loads(out)

try:
    for _ in range(100):
        try:
            chain = cli("getblockchaininfo")
            break
        except subprocess.CalledProcessError:
            time.sleep(.1)
    else:
        raise RuntimeError("Bitcoin Core did not start")
    if chain["chain"] != "main":
        raise RuntimeError("this generator is intentionally mainnet-only")

    keys = []
    for i in range(1, N + 1):
        wallet = f"signer_{i}"
        cli("createwallet", wallet, "false", "true")
        root = cli("addhdkey", wallet=wallet)["xpub"]
        key = cli("derivehdkey", "m/87h/0h/0h",
                  json.dumps({"hdkey": root, "private": True}), wallet=wallet)
        keys.append(key)

    body = "wsh(sortedmulti(" + str(M) + "," + ",".join(
        f"{k['origin']}{k['xpub']}/<0;1>/*" for k in keys) + "))"
    info = cli("getdescriptorinfo", body)
    if len(info.get("multipath_expansion", [])) != 2:
        raise RuntimeError("descriptor did not expand to receive and change branches")
    desc = body + "#" + info["checksum"]

    cli("createwallet", "watch_only", "true", "true")
    request = json.dumps([{"desc": desc, "active": True, "timestamp": 0}])
    if not cli("importdescriptors", request, wallet="watch_only")[0]["success"]:
        raise RuntimeError("watch-only descriptor import failed")
    if cli("getwalletinfo", wallet="watch_only")["private_keys_enabled"]:
        raise RuntimeError("watch-only wallet unexpectedly has private keys")

    for i, key in enumerate(keys, 1):
        private_body = body.replace(key["xpub"], key["xprv"])
        private = private_body + "#" + cli("getdescriptorinfo", private_body)["checksum"]
        request = json.dumps([{"desc": private, "active": True, "timestamp": 0}])
        if not cli("importdescriptors", request, wallet=f"signer_{i}")[0]["success"]:
            raise RuntimeError(f"signer {i} descriptor import failed")

    for name in ["watch_only"] + [f"signer_{i}" for i in range(1, N + 1)]:
        folder = OUT / name
        folder.mkdir()
        cli("backupwallet", str(folder / "wallet.dat"), wallet=name)
        if not (folder / "wallet.dat").is_file():
            raise RuntimeError(f"{name} backup was not created")

    print(f"Done: {M}-of-{N}. Burn each folder in {OUT} to its matching CD-R.")
finally:
    subprocess.run([CLI, f"-datadir={DATA}", "stop"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
