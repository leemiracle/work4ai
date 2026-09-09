#!/usr/bin/env python3
"""
tinykafka — 参照 Apache Kafka 的迷你消息队列

参照：Kafka (分布式日志) + Redpanda
csdiy 对应：db-程序员视角(WAL/追加日志) + network-程序员视角(TCP) + os-程序员视角(page cache)

核心概念：
- Topic = 追加日志（参照 Kafka 的 commit log）
- Partition = 分区（并行度）
- Producer = 写消息
- Consumer = 读消息（offset 追踪）
- Consumer Group = 消费组（负载均衡）

功能：produce / consume / create topic / list topics
"""
import asyncio, json, os, time, logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tinykafka")

DATA_DIR = Path("/tmp/tinykafka-data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Message:
    offset: int
    timestamp: float
    key: str
    value: str

class Partition:
    """
    单个分区 = 追加日志（参照 Kafka Partition 的 commit log）

    存储：每个分区一个文件，消息追加写入。
    WAL 思想（参照 db §六）：先写日志再确认。
    """
    def __init__(self, topic: str, partition_id: int):
        self.topic = topic
        self.id = partition_id
        self.path = DATA_DIR / f"{topic}-{partition_id}.log"
        self.offset_file = DATA_DIR / f"{topic}-{partition_id}.offsets"
        self.next_offset = 0
        if self.path.exists():
            # 恢复 offset（参照 Kafka 启动时恢复 log）
            lines = self.path.read_text().strip().split("\n")
            self.next_offset = len([l for l in lines if l])

    async def append(self, key: str, value: str) -> int:
        """追加消息（参照 Kafka Producer send）"""
        msg = Message(offset=self.next_offset, timestamp=time.time(), key=key, value=value)
        with open(self.path, "a") as f:
            f.write(json.dumps(asdict(msg)) + "\n")
            f.flush()
            os.fsync(f.fileno())  # 参照 db §六：fsync 保证持久化
        self.next_offset += 1
        return msg.offset

    async def read(self, offset: int, max_messages: int = 100) -> list[Message]:
        """从指定 offset 读取（参照 Kafka Consumer poll）"""
        if not self.path.exists():
            return []
        messages = []
        with open(self.path) as f:
            for i, line in enumerate(f):
                if i < offset:
                    continue
                if len(messages) >= max_messages:
                    break
                data = json.loads(line)
                messages.append(Message(**data))
        return messages

    def latest_offset(self) -> int:
        return self.next_offset

class Topic:
    """Topic = 多个 Partition（参照 Kafka Topic）"""
    def __init__(self, name: str, num_partitions: int = 3):
        self.name = name
        self.partitions = [Partition(name, i) for i in range(num_partitions)]

    def _select_partition(self, key: str) -> int:
        """分区选择（参照 Kafka：key 的 hash % partition_count）"""
        if not key:
            import random
            return random.randint(0, len(self.partitions) - 1)
        return hash(key) % len(self.partitions)

class TinyKafka:
    """
    Kafka 服务端（参照 Kafka Broker）

    协议：JSON over TCP
    """
    def __init__(self):
        self.topics: dict[str, Topic] = {}
        self.consumer_offsets: dict[str, dict[int, int]] = {}  # group → {partition: offset}
        self._load_topics()

    def _load_topics(self):
        """恢复已有的 topic（参照 Kafka 启动恢复）"""
        files = set(DATA_DIR.glob("*.log"))
        for f in files:
            parts = f.stem.split("-")
            if len(parts) == 2:
                topic_name, pid = parts[0], int(parts[1])
                if topic_name not in self.topics:
                    self.topics[topic_name] = Topic(topic_name)
                # 确保 partition 数量正确
                while len(self.topics[topic_name].partitions) <= pid:
                    self.topics[topic_name].partitions.append(Partition(topic_name, len(self.topics[topic_name].partitions)))

    def create_topic(self, name: str, partitions: int = 3):
        if name in self.topics:
            return {"error": "topic exists"}
        self.topics[name] = Topic(name, partitions)
        log.info(f"created topic '{name}' with {partitions} partitions")
        return {"ok": True}

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理客户端请求（参照 Kafka 的 TCP 协议）"""
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                req = json.loads(line)
                resp = self._process(req)
                writer.write((json.dumps(resp) + "\n").encode())
                await writer.drain()
        except (ConnectionResetError, json.JSONDecodeError):
            pass
        finally:
            writer.close()

    def _process(self, req: dict) -> dict:
        action = req.get("action")

        if action == "create_topic":
            return self.create_topic(req["topic"], req.get("partitions", 3))

        elif action == "produce":
            topic_name = req["topic"]
            if topic_name not in self.topics:
                return {"error": "topic not found"}
            topic = self.topics[topic_name]
            # 同步写入（简化版；真实 Kafka 用异步+批量）
            offsets = []
            for msg in req.get("messages", []):
                pid = topic._select_partition(msg.get("key", ""))
                offset = asyncio.run(topic.partitions[pid].append(msg.get("key",""), msg["value"]))
                offsets.append({"partition": pid, "offset": offset})
            return {"offsets": offsets}

        elif action == "consume":
            topic_name = req["topic"]
            group = req.get("group", "default")
            if topic_name not in self.topics:
                return {"error": "topic not found"}
            topic = self.topics[topic_name]
            # 获取消费组的 offset
            group_offsets = self.consumer_offsets.setdefault(group, {})
            all_messages = []
            for i, partition in enumerate(topic.partitions):
                offset = group_offsets.get(i, 0)
                msgs = asyncio.run(partition.read(offset))
                for m in msgs:
                    all_messages.append({"partition": i, **asdict(m)})
                group_offsets[i] = offset + len(msgs)
            return {"messages": all_messages}

        elif action == "list_topics":
            topics_info = {}
            for name, topic in self.topics.items():
                topics_info[name] = {
                    "partitions": len(topic.partitions),
                    "total_messages": sum(p.latest_offset() for p in topic.partitions),
                }
            return {"topics": topics_info}

        return {"error": "unknown action"}

    async def start(self, host="0.0.0.0", port=9092):
        server = await asyncio.start_server(self.handle_client, host, port, reuse_address=True)
        addr = server.sockets[0].getsockname()
        log.info(f"tinykafka on {addr[0]}:{addr[1]} ({len(self.topics)} topics)")
        async with server:
            await server.serve_forever()

def main():
    import argparse
    p = argparse.ArgumentParser(description="tinykafka — 参照 Apache Kafka")
    p.add_argument("-p", "--port", type=int, default=9092)
    p.add_argument("--create", help="创建 topic: --create mytopic:3")
    args = p.parse_args()

    if args.create:
        name, _, npart = args.create.partition(":")
        kafka = TinyKafka()
        kafka.create_topic(name, int(npart or 3))
        return

    kafka = TinyKafka()
    asyncio.run(kafka.start(port=args.port))

if __name__ == "__main__": main()
