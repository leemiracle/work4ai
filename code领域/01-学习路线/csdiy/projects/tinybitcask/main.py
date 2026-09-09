#!/usr/bin/env python3
"""tinybitcask — 参照 Riak Bitcask 的日志结构存储
参照：Bitcask (Basho) / Riak / SQLite WAL
csdiy 对应：tinydb + leveldb-lsm精读 + db §六
核心：追加写日志 + 内存 keydir（文件偏移表）"""
import os,struct,time
from dataclasses import dataclass
from pathlib import Path

@dataclass
class KeyDirEntry: file_id:int; offset:int; size:int; timestamp:int

class Bitcask:
    """Bitcask 存储引擎（参照 Basho Riak Bitcask paper）
    磁盘：只追加的数据文件（key+value+timestamp）
    内存：keydir（key → 文件偏移）
    写=追加；读=查keydir→seek读取"""
    def __init__(self,data_dir="/tmp/bitcask"):
        self.dir=Path(data_dir); self.dir.mkdir(parents=True,exist_ok=True)
        self.keydir={}; self.active_file=None; self.active_id=0
        self._open_active(); self._rebuild_keydir()

    def _open_active(self):
        self.active_id=max((int(f.stem) for f in self.dir.glob("*.data") if f.stem.isdigit()),default=0)+1
        self.active_path=self.dir/f"{self.active_id}.data"
        self.active_file=open(self.active_path,"ab+")

    def _rebuild_keydir(self):
        """启动时扫描所有文件重建 keydir（参照 Bitcask startup）"""
        for f in sorted(self.dir.glob("*.data"),key=lambda x:int(x.stem) if x.stem.isdigit() else 999999):
            fid=int(f.stem); f.seek(0)
            offset=0
            while True:
                hdr=f.read(12)
                if len(hdr)<12: break
                ts,=struct.unpack("<I",hdr[:4]); klen,vlen=struct.unpack("<II",hdr[4:12])
                key=f.read(klen); val=f.read(vlen)
                if len(key)<klen or len(val)<vlen: break
                self.keydir[key]=KeyDirEntry(fid,offset+12,klen+vlen+12,ts)
                offset+=12+klen+vlen

    def put(self,key:bytes,value:bytes):
        """写入=追加（参照 Bitcask append-only writes）"""
        ts=int(time.time())
        entry=struct.pack("<III",ts,len(key),len(value))+key+value
        offset=self.active_file.tell()
        self.active_file.write(entry); self.active_file.flush(); os.fsync(self.active_file.fileno())
        self.keydir[key]=KeyDirEntry(self.active_id,offset,len(entry),ts)

    def get(self,key:bytes):
        """读取=查keydir→seek（参照 Bitcask lookup）"""
        entry=self.keydir.get(key)
        if not entry: return None
        path=self.dir/f"{entry.file_id}.data"
        with open(path,"rb") as f:
            f.seek(entry.offset)
            data=f.read(entry.size)
            ts,klen,vlen=struct.unpack("<III",data[:12])
            return data[12+klen:12+klen+vlen]

    def delete(self,key:bytes):
        """删除=追加墓碑（参照 Bitcask tombstone）"""
        self.put(key,b"\x00\x00\x00\x00TOMB")
        if key in self.keydir: del self.keydir[key]

    def keys(self): return list(self.keydir.keys())
    def stats(self): return {"keys":len(self.keydir),"files":len(list(self.dir.glob("*.data")))}

def main():
    print("tinybitcask — Bitcask 存储（参照 Riak）\n")
    import shutil; shutil.rmtree("/tmp/bitcask",ignore_errors=True)
    bc=Bitcask("/tmp/bitcask")
    for i in range(100):
        bc.put(f"key{i:03d}".encode(),f"value_{i}".encode())
    print(f"  写入 100 个 key")
    print(f"  get(key050) = {bc.get(b'key050').decode()}")
    print(f"  stats: {bc.stats()}")
    bc.delete(b"key050")
    print(f"  delete(key050) → get = {bc.get(b'key050')}")
    # 重启恢复
    del bc; bc2=Bitcask("/tmp/bitcask")
    print(f"\n  重启后重建 keydir:")
    print(f"  get(key049) = {bc2.get(b'key049').decode()}")
    print(f"  stats: {bc2.stats()}")

if __name__=="__main__": main()
