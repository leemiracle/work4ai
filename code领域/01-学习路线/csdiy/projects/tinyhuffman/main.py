#!/usr/bin/env python3
"""tinyhuffman — 参照 zlib/deflate 的 Huffman 编码
参照：DEFLATE / Huffman 1952 / csapp Ch2
csdiy 对应：tinycompress(LZ77+Huffman=DEFLATE) + csapp(位运算)
核心：频率统计 → 构建树 → 编码/解码"""
import heapq
from collections import Counter
from dataclasses import dataclass

@dataclass(order=True)
class HuffNode:
    freq:int
    char:object=None
    left:object=None
    right:object=None

class Huffman:
    """Huffman 编码（参照 DEFLATE 中的 Huffman 步骤）"""
    def __init__(self): self.tree=None; self.codes={}
    def build(self,data):
        freq=Counter(data)
        if len(freq)==1: # 单字符
            char=list(freq.keys())[0]; self.codes={char:"0"}; self.tree=HuffNode(freq[char],char); return
        heap=[HuffNode(f,c) for c,f in freq.items()]; heapq.heapify(heap)
        while len(heap)>1:
            left=heapq.heappop(heap); right=heapq.heappop(heap)
            merged=HuffNode(left.freq+right.freq,None,left,right)
            heapq.heappush(heap,merged)
        self.tree=heap[0]; self.codes={}; self._gen_codes(self.tree,"")
    def _gen_codes(self,node,prefix):
        if node.char is not None: self.codes[node.char]=prefix; return
        if node.left: self._gen_codes(node.left,prefix+"0")
        if node.right: self._gen_codes(node.right,prefix+"1")
    def encode(self,data):
        return "".join(self.codes[c] for c in data)
    def decode(self,bits):
        result=[]; node=self.tree
        for bit in bits:
            node=node.left if bit=="0" else node.right
            if node.char is not None: result.append(node.char); node=self.tree
        return result

def main():
    print("tinyhuffman — Huffman 编码（参照 DEFLATE）\n")
    text="aaaabbbccd"
    huff=Huffman(); huff.build(text)
    print(f"  原文: {text}")
    print(f"  频率: {Counter(text)}")
    print(f"  编码表: {huff.codes}")
    encoded=huff.encode(text)
    print(f"  编码后: {encoded}")
    print(f"  原始: {len(text)*8} bits")
    print(f"  压缩: {len(encoded)} bits ({len(encoded)/(len(text)*8)*100:.0f}%)")
    decoded=huff.decode(encoded)
    print(f"  解码: {''.join(decoded)} {'✅' if ''.join(decoded)==text else '❌'}")

if __name__=="__main__": main()
