#!/usr/bin/env python3
"""
03_flatbuffer_walker.py — FlatBuffer vtable walker 实验

实验流程:
  1. 用 flatbuffers 库自造一个 5 字段 schema 的 buffer
  2. 假装不知道 schema, 用 vtable walker 反推
  3. 比对反推结果 vs 原始 schema

依赖: pip install flatbuffers
"""
import struct
import flatbuffers
from pathlib import Path

# === Step 1: 自造 FlatBuffer ===
# Schema (假设):
#   table Demo {
#     a: int;       // field 0
#     b: string;    // field 1
#     c: [float];   // field 2
#     d: bool;      // field 3
#     e: long;      // field 4
#   }
#   root_type Demo;

def build_demo_buffer(a=42, b="hello world", c=None, d=True, e=2718281828):
    """自造 FlatBuffer(用底层 API, 不依赖 schema 代码生成)"""
    if c is None:
        c = [1.5, 2.5, 3.5]
    
    builder = flatbuffers.Builder(1024)
    
    # 1. 先建子对象(FlatBuffer 要求自底向上)
    b_str = builder.CreateString(b)
    
    # vector of float
    builder.StartVector(4, len(c), 4)  # elem_size=4, count=len(c), align=4
    for x in reversed(c):
        builder.PrependFloat32(x)
    c_vec = builder.EndVector()
    
    # 2. 建 table(字段顺序从后往前, FlatBuffer 怪癖)
    builder.StartObject(5)  # 5 fields
    builder.PrependInt32Slot(0, a, 0)
    builder.PrependUOffsetTRelativeSlot(1, b_str, 0)
    builder.PrependUOffsetTRelativeSlot(2, c_vec, 0)
    builder.PrependBoolSlot(3, d, False)
    builder.PrependInt64Slot(4, e, 0)
    demo = builder.EndObject()
    
    builder.Finish(demo)
    return bytes(builder.Output())


# === Step 2: vtable walker 反推 ===

def parse_flatbuffer_unknown_schema(data: bytes):
    """对未知 schema 的 FlatBuffer 反推字段结构
    
    启发式优先级(从最具体到最宽泛):
        1. BOOL  (u8 ∈ {0,1})
        2. STRING(u32 offset → 指向位置有合法 string 结构)
        3. VECTOR(u32 offset → 指向位置有合法 float vector 结构)
        4. LONG  (u64 且 高 4 字节非零 → 真的是 64-bit)
        5. INT   (u32,默认 fallback)
    """
    root_offset = struct.unpack_from('<I', data, 0)[0]
    root_table_pos = root_offset
    
    vtable_soffset = struct.unpack_from('<i', data, root_table_pos)[0]
    vtable_pos = root_table_pos - vtable_soffset
    
    vtable_size = struct.unpack_from('<H', data, vtable_pos)[0]
    table_size = struct.unpack_from('<H', data, vtable_pos + 2)[0]
    
    n_fields = (vtable_size - 4) // 2
    fields = []
    for i in range(n_fields):
        offset_in_table = struct.unpack_from('<H', data, vtable_pos + 4 + i * 2)[0]
        if offset_in_table == 0:
            fields.append(None)
            continue
        field_pos = root_table_pos + offset_in_table
        
        # 拿原始 candidates
        candidates = {}
        if field_pos + 1 <= len(data):
            candidates['u8'] = struct.unpack_from('<B', data, field_pos)[0]
        if field_pos + 2 <= len(data):
            candidates['u16'] = struct.unpack_from('<H', data, field_pos)[0]
        if field_pos + 4 <= len(data):
            candidates['u32'] = struct.unpack_from('<I', data, field_pos)[0]
        if field_pos + 8 <= len(data):
            candidates['u64'] = struct.unpack_from('<Q', data, field_pos)[0]
        
        # 按启发式优先级判定类型
        inferred = None
        
        # 1. BOOL: u8 ∈ {0,1} 且 u16 低字节 == u8
        if 'u8' in candidates:
            u8v = candidates['u8']
            if u8v in (0, 1):
                # 进一步验证: 如果 u16/u32 都 0 或都含这个 u8 字节
                if candidates.get('u16', 0) == u8v:
                    inferred = {'type': 'BOOL', 'value': bool(u8v)}
        
        # 2. STRING: u32 是 offset, 指向位置是 u32 length + ASCII bytes
        if inferred is None and 'u32' in candidates:
            u32v = candidates['u32']
            s = maybe_string_at(data, u32v)
            if s is not None:
                inferred = {'type': 'STRING', 'value': s, 'offset_to': u32v}
        
        # 3. VECTOR[float32]: 同上
        if inferred is None and 'u32' in candidates:
            u32v = candidates['u32']
            v = maybe_f32_vector_at(data, u32v)
            if v is not None:
                inferred = {'type': 'VECTOR_F32', 'value': v, 'offset_to': u32v}
        
        # 4. LONG: u64 且高 4 字节非零(u32 不够装)
        if inferred is None and 'u64' in candidates:
            u64v = candidates['u64']
            u32v = candidates.get('u32', 0)
            if u64v > 0xFFFFFFFF:  # 高 4 字节非零
                inferred = {'type': 'LONG', 'value': u64v}
        
        # 5. INT: 默认 fallback
        if inferred is None and 'u32' in candidates:
            inferred = {'type': 'INT', 'value': candidates['u32']}
        
        fields.append({
            'offset': offset_in_table,
            'pos': field_pos,
            'candidates': candidates,
            'inferred': inferred,
        })
    
    return {
        'root_offset': root_offset,
        'vtable_pos': vtable_pos,
        'vtable_size': vtable_size,
        'table_size': table_size,
        'n_fields': n_fields,
        'fields': fields,
    }


def maybe_string_at(data, pos):
    if pos + 4 > len(data):
        return None
    length = struct.unpack_from('<I', data, pos)[0]
    if length == 0 or length > 1000:
        return None
    if pos + 4 + length > len(data):
        return None
    raw = data[pos + 4 : pos + 4 + length]
    if all(0x20 <= b < 0x7F or b in (0x0a, 0x0d, 0x09) for b in raw):
        try:
            return raw.decode('utf-8')
        except UnicodeDecodeError:
            return None
    return None


def maybe_f32_vector_at(data, pos, max_elements=10):
    import math
    if pos + 4 > len(data):
        return None
    length = struct.unpack_from('<I', data, pos)[0]
    if length == 0 or length > 1_000_000:
        return None
    if pos + 4 + length * 4 > len(data):
        return None
    n = min(length, max_elements)
    floats = struct.unpack_from(f'<{n}f', data, pos + 4)
    if not all(math.isfinite(f) for f in floats):
        return None
    return {'length': length, 'samples': list(floats)}


# === Step 3: 对拍 ===

def main():
    print('=' * 60)
    print('FlatBuffer vtable walker 实验')
    print('=' * 60)
    
    # 真实值
    truth = {'a': 42, 'b': 'hello world', 'c': [1.5, 2.5, 3.5], 'd': True, 'e': 2718281828}
    print(f'\n[真实值] {truth}')
    
    # Step 1: 自造 buffer
    buf = build_demo_buffer(**truth)
    print(f'\n[Step 1] 自造 buffer: {len(buf)} bytes')
    Path('/tmp/demo_flatbuffer.bin').write_bytes(buf)
    
    # Step 2: 反推
    print(f'\n[Step 2] vtable walker 反推:')
    result = parse_flatbuffer_unknown_schema(buf)
    print(f'  root_offset: {result["root_offset"]}')
    print(f'  vtable_size: {result["vtable_size"]} bytes')
    print(f'  n_fields: {result["n_fields"]}')
    print(f'  字段:')
    inferred_map = {0: 'a (int)', 1: 'b (string)', 2: 'c (vector)', 3: 'd (bool)', 4: 'e (long)'}
    correct = 0
    for i, f in enumerate(result['fields']):
        if f is None:
            print(f'    field[{i}]: absent')
            continue
        inf = f['inferred']
        if inf is None:
            print(f'    field[{i}] at +{f["offset"]} (pos={f["pos"]}): UNKNOWN, candidates={f["candidates"]}')
            continue
        print(f'    field[{i}] at +{f["offset"]} (pos={f["pos"]}): {inf["type"]} = {inf["value"]!r}')
        # 对拍
        truth_key = inferred_map[i].split(' ')[0]
        truth_val = truth[truth_key]
        if inf['type'] == 'BOOL':
            if inf['value'] == truth_val: correct += 1
        elif inf['type'] in ('STRING', 'INT', 'LONG'):
            if inf['value'] == truth_val: correct += 1
        elif inf['type'] == 'VECTOR_F32':
            if inf['value']['samples'] == truth_val: correct += 1
    
    # Step 3: 对拍
    print(f'\n[Step 3] 对拍: {correct}/{len(inferred_map)} 字段反推正确')
    if correct == len(inferred_map):
        print(f'  🎉 5/5 全部正确反推!')
    else:
        print(f'  ⚠️  有 {len(inferred_map) - correct} 个字段未正确识别 — 调启发式优先级')
    
    print(f'\n💡 启示:')
    print(f'  - FlatBuffer 自带 schema (vtable), 不需要 .fbs 文件')
    print(f'  - 字符串和向量的探测: u32 值 = offset, 指向位置有 length 前缀')
    print(f'  - bool 探测: u8 ∈ {{0,1}} 且与 u16/u32 一致')


if __name__ == '__main__':
    main()
