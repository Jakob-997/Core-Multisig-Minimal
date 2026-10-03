#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
M,N=map(int,sys.argv[1:3]); B=Path(sys.argv[3]); D=Path("/dev/shm/multisig"); D.mkdir()
subprocess.run([B/"bitcoind",f"-datadir={D}","-daemonwait","-networkactive=0","-listen=0"],check=True)
def cmd(*a,w=None):
    return [B/"bitcoin-cli",f"-datadir={D}"]+([f"-rpcwallet={w}"] if w else [])+list(a)
def rpc(*a,w=None):
    return json.loads(subprocess.check_output(cmd(*a,w=w),text=True))
keys=[]
for i in range(1,N+1):
    w=f"signer_{i}"; rpc("createwallet",w,"false","true"); x=rpc("addhdkey",w=w)["xpub"]
    keys.append(rpc("derivehdkey","m/87h/0h/0h",json.dumps({"hdkey":x,"private":True}),w=w))
body="wsh(sortedmulti("+str(M)+","+",".join(f"{k['origin']}{k['xpub']}/<0;1>/*" for k in keys)+"))"
def imp(w,b):
    d=b+"#"+rpc("getdescriptorinfo",b)["checksum"]
    rpc("importdescriptors",json.dumps([{"desc":d,"active":True,"timestamp":0}]),w=w)
rpc("createwallet","watch_only","true","true"); imp("watch_only",body)
for i,k in enumerate(keys,1): imp(f"signer_{i}",body.replace(k["xpub"],k["xprv"]))
for w in ["watch_only"]+[f"signer_{i}" for i in range(1,N+1)]:
    (D/w).mkdir(); subprocess.run(cmd("backupwallet",str(D/w/"wallet.dat"),w=w),check=True)
subprocess.run(cmd("stop"),check=True)
