#!/usr/bin/env python3
"""tinyblob — 参照 S3/MinIO 的对象存储
参照：AWS S3 / MinIO / OpenStack Swift
csdiy 对应：tinydb + tinykafka + 分布式
核心：Bucket + Object CRUD + 多种元数据 + 范围读"""
import os, hashlib, time, json, shutil
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class ObjectMeta:
    key: str; size: int; etag: str; content_type: str = "application/octet-stream"
    created: float = field(default_factory=time.time)
    custom: dict = field(default_factory=dict)

class TinyBlob:
    """对象存储（参照 MinIO/S3）
    bucket → objects（文件）+ metadata"""
    def __init__(self, storage_dir="/tmp/tinyblob"):
        self.root=Path(storage_dir); self.root.mkdir(parents=True,exist_ok=True)
        self.meta_dir=self.root/"_meta"; self.meta_dir.mkdir(exist_ok=True)

    def create_bucket(self,bucket):
        (self.root/bucket).mkdir(exist_ok=True)
        return f"Bucket '{bucket}' created"

    def list_buckets(self):
        return [d.name for d in self.root.iterdir() if d.is_dir() and not d.name.startswith("_")]

    def put_object(self,bucket,key,data:bytes,content_type="application/octet-stream",**custom):
        path=self.root/bucket/key
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        meta=ObjectMeta(key=key,size=len(data),
                        etag=hashlib.md5(data).hexdigest(),
                        content_type=content_type,custom=custom)
        (self.meta_dir/f"{bucket}__{key.replace('/','_')}.json").write_text(json.dumps(meta.__dict__,default=str))
        return meta

    def get_object(self,bucket,key):
        path=self.root/bucket/key
        if not path.exists(): return None
        return path.read_bytes()

    def get_meta(self,bucket,key):
        meta_path=self.meta_dir/f"{bucket}__{key.replace('/','_')}.json"
        if not meta_path.exists(): return None
        return json.loads(meta_path.read_text())

    def list_objects(self,bucket,prefix=""):
        b=self.root/bucket
        if not b.exists(): return []
        return [{"key":str(p.relative_to(b)),"size":p.stat().st_size}
                for p in b.rglob("*") if p.is_file() and str(p.relative_to(b)).startswith(prefix)]

    def delete_object(self,bucket,key):
        path=self.root/bucket/key
        if path.exists(): path.unlink()
        meta_path=self.meta_dir/f"{bucket}__{key.replace('/','_')}.json"
        if meta_path.exists(): meta_path.unlink()
        return True

    def range_get(self,bucket,key,start,end):
        """范围读（参照 S3 Range header）"""
        data=self.get_object(bucket,key)
        if not data: return None
        return data[start:end]

    def stats(self):
        total=0; count=0
        for b in self.root.iterdir():
            if b.is_dir() and not b.name.startswith("_"):
                for f in b.rglob("*"):
                    if f.is_file(): total+=f.stat().st_size; count+=1
        return {"buckets":len(self.list_buckets()),"objects":count,"total_bytes":total}

def main():
    print("tinyblob — 对象存储（参照 MinIO/S3）\n")
    shutil.rmtree("/tmp/tinyblob",ignore_errors=True)
    s3=TinyBlob()
    s3.create_bucket("photos"); s3.create_bucket("docs")
    print(f"  buckets: {s3.list_buckets()}")

    meta=s3.put_object("photos","vacation/beach.jpg",b"\x89PNG fake image data\x00"*100,
                        content_type="image/jpeg",author="alice",geo="Hawaii")
    print(f"  put photos/vacation/beach.jpg → etag={meta.etag[:8]}, size={meta.size}")

    s3.put_object("docs","readme.md",b"# Hello\nThis is a test.",content_type="text/markdown")
    s3.put_object("docs","api/v1.yaml",b"openapi: 3.0\n",content_type="text/yaml")

    print(f"\n  list_objects('docs'): {s3.list_objects('docs')}")
    print(f"  list_objects('photos'): {s3.list_objects('photos','vacation')}")

    data=s3.get_object("photos","vacation/beach.jpg")
    print(f"\n  get_object photos/vacation/beach.jpg → {len(data)} bytes")
    ranged=s3.range_get("photos","vacation/beach.jpg",0,16)
    print(f"  range_get [0:16] → {ranged}")

    print(f"\n  stats: {s3.stats()}")

if __name__=="__main__": main()
