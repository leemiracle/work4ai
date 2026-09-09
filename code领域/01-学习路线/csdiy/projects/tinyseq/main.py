#!/usr/bin/env python3
"""tinyseq — 参照 Snowflake/ULID 的分布式唯一 ID 生成器
参照：Twitter Snowflake / ULID / Sonyflake / UUIDv7
csdiy 对应：分布式 + tinydb(rowid) + tinykafka(offset)
核心：时间戳+机器ID+序列号 → 全局唯一有序ID"""
import time, threading, os

class Snowflake:
    """Twitter Snowflake ID（参照 twitter-archive/snowflake）
    64-bit: [1bit sign][41bit timestamp][10bit machine][12bit sequence]
    每毫秒可生成 4096 个 ID"""
    def __init__(self,machine_id=1,epoch=1609459200000):  # epoch=2021-01-01
        self.epoch=epoch; self.machine_id=machine_id&0x3FF
        self.last_ts=0; self.seq=0; self.lock=threading.Lock()
    def next_id(self)->int:
        with self.lock:
            ts=int(time.time()*1000)-self.epoch
            if ts==self.last_ts:
                self.seq=(self.seq+1)&0xFFF
                if self.seq==0:  # 同毫秒序列耗尽
                    while ts<=self.last_ts: ts=int(time.time()*1000)-self.epoch
            else:
                self.seq=0
            self.last_ts=ts
            return (ts<<22)|(self.machine_id<<12)|self.seq
    def parse(self,id:int):
        """解析 ID（参照 snowflake 解析工具）"""
        ts=(id>>22)+self.epoch; machine=(id>>12)&0x3FF; seq=id&0xFFF
        return {"timestamp":time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ts/1000)),
                "machine_id":machine,"sequence":seq}

class ULID:
    """ULID（参照 ulid/javascript）
    128-bit: [48bit timestamp][80bit random]"""
    CROCKFORD="0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    def __init__(self): pass
    def generate(self)->str:
        ts=int(time.time()*1000); random_part=os.urandom(10)
        raw=ts.to_bytes(6,'big')+random_part
        return self._encode(raw)
    def _encode(self,data:bytes)->str:
        result=[]; buffer=0; bits=0
        for b in data:
            buffer=(buffer<<8)|b; bits+=8
            while bits>=5:
                result.append(self.CROCKFORD[(buffer>>(bits-5))&31]); bits-=5
        if bits>0: result.append(self.CROCKFORD[(buffer<<(5-bits))&31])
        return ''.join(result)[:26]
    def extract_time(self,ulid_str:str)->float:
        """从 ULID 提取时间戳（前 10 字符）"""
        ts_chars=ulid_str[:10]; ts=0
        for c in ts_chars:
            ts=ts*32+self.CROCKFORD.index(c.upper())
        return ts/1000

def main():
    print("tinyseq — 分布式 ID 生成器（参照 Snowflake/ULID）\n")
    sf=Snowflake(machine_id=42)
    ids=[sf.next_id() for _ in range(5)]
    print("  Snowflake IDs:")
    for id in ids:
        info=sf.parse(id)
        print(f"    {id:>20d} → {info}")
    print(f"  唯一性: {len(set(ids))}/{len(ids)} ✅")

    ulid=ULID()
    ulids=[ulid.generate() for _ in range(3)]
    print(f"\n  ULID:")
    for u in ulids:
        ts=ulid.extract_time(u)
        print(f"    {u} → time={time.strftime('%H:%M:%S',time.localtime(ts))}")

    print(f"\n  对比: Snowflake=数字(有序), ULID=字符串(排序友好), UUID=随机(无序)")

if __name__=="__main__": main()
