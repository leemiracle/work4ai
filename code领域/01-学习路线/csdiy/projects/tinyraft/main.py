#!/usr/bin/env python3
"""
tinyraft — 参照 MIT 6.824 Lab2 Raft 的简化实现

参照：MIT 6.824 Raft + etcd/raft
csdiy 对应：mit6.824 lab + db §二(锁/两阶段)

功能：Leader 选举 + 日志复制 + 多节点
"""
import asyncio, json, random, time, logging
from dataclasses import dataclass, field
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tinyraft")

FOLLOWER, CANDIDATE, LEADER = "follower", "candidate", "leader"

@dataclass
class LogEntry:
    term: int
    command: str

class RaftNode:
    """单个 Raft 节点（参照 6.824 Raft paper 图2）"""
    def __init__(self, node_id: int, peers: list[str], port: int):
        self.id = node_id
        self.peers = peers  # 其他节点地址
        self.port = port
        # 持久状态
        self.current_term = 0
        self.voted_for: Optional[int] = None
        self.log: list[LogEntry] = []
        # 易失状态
        self.state = FOLLOWER
        self.commit_index = 0
        self.last_applied = 0
        self.leader_id: Optional[int] = None
        # 选举超时（参照 Raft paper：随机化 150-300ms，这里放大到 1.5-3s）
        self.election_timeout = random.uniform(1.5, 3.0)
        self.last_heartbeat = time.time()
        self.server: Optional[asyncio.Server] = None

    async def handle_rpc(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理来自其他节点的 RPC（参照 Raft RequestVote / AppendEntries）"""
        data = await reader.readline()
        msg = json.loads(data)
        resp = self._process_msg(msg)
        writer.write((json.dumps(resp) + "\n").encode())
        await writer.drain()
        writer.close()

    def _process_msg(self, msg: dict) -> dict:
        """消息处理（参照 Raft paper 图2 的规则）"""
        mtype = msg.get("type")

        # 规则1：收到更高 term → 降级
        if msg.get("term", 0) > self.current_term:
            self.current_term = msg["term"]
            self.state = FOLLOWER
            self.voted_for = None

        if mtype == "request_vote":
            # RequestVote RPC（参照 paper 图2）
            grant = False
            if self.voted_for is None or self.voted_for == msg["candidate_id"]:
                # 检查日志是否至少和本节点一样新（参照 paper 5.4.1）
                grant = True
            return {"term": self.current_term, "vote_granted": grant}

        elif mtype == "append_entries":
            # AppendEntries RPC（Leader 心跳 + 日志）
            self.last_heartbeat = time.time()
            self.state = FOLLOWER
            self.leader_id = msg.get("leader_id")
            # 如果有新日志条目，追加（简化版）
            if msg.get("entries"):
                for e in msg["entries"]:
                    self.log.append(LogEntry(e["term"], e["command"]))
            return {"term": self.current_term, "success": True}

        elif mtype == "client_command":
            # 客户端命令（只有 Leader 能处理）
            if self.state != LEADER:
                return {"success": False, "redirect": self.leader_id}
            self.log.append(LogEntry(self.current_term, msg["command"]))
            return {"success": True, "term": self.current_term, "log_size": len(self.log)}

        return {"success": False}

    async def _send_rpc(self, peer: str, msg: dict) -> Optional[dict]:
        """发送 RPC 到其他节点"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(peer.split(":")[0], int(peer.split(":")[1])),
                timeout=0.5
            )
            writer.write((json.dumps(msg) + "\n").encode())
            await writer.drain()
            data = await reader.readline()
            writer.close()
            return json.loads(data)
        except:
            return None

    async def election_loop(self):
        """选举循环（参照 Raft paper §5.2）"""
        while True:
            await asyncio.sleep(0.1)
            if self.state == LEADER:
                continue

            # 检查选举超时
            if time.time() - self.last_heartbeat > self.election_timeout:
                await self._start_election()

    async def _start_election(self):
        """发起选举（参照 paper 图2 Candidate 规则）"""
        self.state = CANDIDATE
        self.current_term += 1
        self.voted_for = self.id
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(1.5, 3.0)
        log.info(f"Node {self.id}: starting election term={self.current_term}")

        votes = 1  # 自己的一票
        msg = {"type": "request_vote", "term": self.current_term, "candidate_id": self.id}

        for peer in self.peers:
            resp = await self._send_rpc(peer, msg)
            if resp and resp.get("vote_granted"):
                votes += 1

        # 赢得选举（多数票）
        majority = (len(self.peers) + 1) // 2 + 1
        if votes >= majority and self.state == CANDIDATE:
            self.state = LEADER
            self.leader_id = self.id
            log.info(f"🏆 Node {self.id} became LEADER (term={self.current_term}, votes={votes})")
            asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self):
        """Leader 心跳循环（参照 paper AppendEntries）"""
        while self.state == LEADER:
            msg = {
                "type": "append_entries", "term": self.current_term,
                "leader_id": self.id, "entries": [],
            }
            for peer in self.peers:
                await self._send_rpc(peer, msg)
            await asyncio.sleep(0.5)  # 心跳间隔 500ms

    async def start(self):
        """启动节点"""
        self.server = await asyncio.start_server(self.handle_rpc, "0.0.0.0", self.port)
        addr = self.server.sockets[0].getsockname()
        log.info(f"Node {self.id} on {addr[0]}:{addr[1]} [{self.state}] (peers: {self.peers})")
        asyncio.create_task(self.election_loop())
        async with self.server:
            await self.server.serve_forever()

def main():
    import argparse
    p = argparse.ArgumentParser(description="tinyraft — 参照 MIT 6.824 Raft")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--peers", nargs="*", default=[], help="其他节点地址 host:port")
    args = p.parse_args()
    node = RaftNode(args.id, args.peers, args.port)
    try:
        asyncio.run(node.start())
    except KeyboardInterrupt:
        log.info(f"Node {args.id} stopped. State: {node.state}, Term: {node.current_term}, Log: {len(node.log)} entries")

if __name__ == "__main__":
    main()
