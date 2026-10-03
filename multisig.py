#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
if len(sys.argv) != 4: raise SystemExit("usage: multisig.py M N /path/to/bitcoin/bin")
M, N = map(int, sys.argv[1:3]); BIN = Path(sys.argv[3]).resolve()
STATE = Path("/dev/shm/core-multisig")
if not 1 <= M <= N <= 20: raise SystemExit("require 1 <= M <= N <= 20")
if STATE.exists(): raise SystemExit("reboot before generating another wallet")
DATA, OUT = STATE/"data", STATE/"backups"
BITCOIND, CLI = BIN/"bitcoind", BIN/"bitcoin-cli"
DATA.mkdir(parents=True); OUT.mkdir()
subprocess.run([BITCOIND, f"-datadir={DATA}", "-daemon", "-networkactive=0", "-listen=0"], check=True)
def rpc(*args, wallet=None):
    cmd = [CLI, f"-datadir={DATA}", "-rpcwait"] + ([f"-rpcwallet={wallet}"] if wallet else [])
    return json.loads(subprocess.check_output(cmd + list(args), text=True))
def import_desc(wallet, body):
    desc = body + "#" + rpc("getdescriptorinfo", body)["checksum"]
    req = json.dumps([{"desc": desc, "active": True, "timestamp": 0}])
    if not rpc("importdescriptors", req, wallet=wallet)[0]["success"]:
        raise RuntimeError(f"{wallet} import failed")
try:
    if rpc("getblockchaininfo")["chain"] != "main": raise RuntimeError("mainnet only")
    keys = []
    for i in range(1, N + 1):
        w = f"signer_{i}"
        rpc("createwallet", w, "false", "true")
        root = rpc("addhdkey", wallet=w)["xpub"]
        keys.append(rpc("derivehdkey", "m/87h/0h/0h",
                        json.dumps({"hdkey": root, "private": True}), wallet=w))
    body = "wsh(sortedmulti(" + str(M) + "," + ",".join(
        f"{k['origin']}{k['xpub']}/<0;1>/*" for k in keys) + "))"
    rpc("createwallet", "watch_only", "true", "true"); import_desc("watch_only", body)
    for i, k in enumerate(keys, 1):
        import_desc(f"signer_{i}", body.replace(k["xpub"], k["xprv"]))
    for name in ["watch_only"] + [f"signer_{i}" for i in range(1, N + 1)]:
        (OUT/name).mkdir()
        rpc("backupwallet", str(OUT/name/"wallet.dat"), wallet=name)
    print(f"Done: {M}-of-{N}. Burn each folder in {OUT} to its matching CD-R.")
finally:
    subprocess.run([CLI, f"-datadir={DATA}", "stop"], stdout=subprocess.DEVNULL)
