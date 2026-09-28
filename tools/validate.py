#!/usr/bin/env python3
"""校验 zh-CN 翻译与 en-US 原文的占位符/标签一致性。

用法:
    python validate.py <en.json> <zh.json> [--require-keys]

占位符不一致会在运行时炸（react-intl 抛错或显示原始 key），比翻译错误更致命，
所以每次合并翻译后必须过这一关。

判定口径（关键，改之前想清楚）：
  - 用花括号配对提取【顶层】占位符，ICU 嵌套表达式（plural/select）整体视为一个
  - 占位符身份 = 变量名 + ICU 类型 + plural/select 的【键名集合】
    （键名集合一致即可，键里的文字本来就该被翻译）
  - 行内 XML 标签按标签名集合比对，不限次数
  - 正常中文翻译不会误判：one/other 文字不同、标签内文字不同都不算问题
"""
from __future__ import annotations
import json, re, sys

TAG_RE = re.compile(r'<(/?)([A-Za-z][\w-]*)')
NUMFMT_RE = re.compile(r',\s*number\b')
ICU_KINDS = {'plural', 'select', 'selectordinal'}


def top_level_placeholders(text: str) -> list[str]:
    """提取顶层 {...} 内容（括号配对，ICU 嵌套表达式保持完整）。"""
    out, depth, start = [], 0, -1
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == '}' and depth > 0:
            depth -= 1
            if depth == 0:
                out.append(text[start:i])
    return out


def icu_block_count(inner: str, kind: str) -> int:
    """统计 plural/select 顶层分支块数（= 键的数量）。

    不用键名比对：英文键名可能和句子里的普通单词撞车（如 "is {verbs}"），
    而中文无空格让键名提取更不可靠。块数能抓住"漏了一个分支"这种真问题，
    又不会误判正常翻译。
    """
    rest = re.sub(r'^\s*[\w.]+\s*,\s*' + kind + r'\s*,\s*', '', inner)
    depth, blocks = 0, 0
    for ch in rest:
        if ch == '{':
            if depth == 0:
                blocks += 1
            depth += 1
        elif ch == '}':
            depth -= 1
    return blocks


def norm_var(inner: str) -> str:
    inner = NUMFMT_RE.sub(', number', inner)
    parts = [p.strip() for p in split_top(inner, ',')]
    if not parts or not parts[0]:
        return '?'
    name = parts[0]
    if len(parts) < 2:
        return name
    kind = parts[1].split()[0]
    if kind in ICU_KINDS:
        return f'{name}/{kind}/x{icu_block_count(inner, kind)}'
    return f'{name}/{kind}'


def split_top(text: str, sep: str) -> list[str]:
    out, depth, cur = [], 0, ''
    for ch in text:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def signature(text) -> tuple:
    if not isinstance(text, str):
        return ('__nonstring__', type(text).__name__)
    vars_ = tuple(sorted(norm_var(p) for p in top_level_placeholders(text)))
    tags = tuple(sorted(m.group(2) for m in TAG_RE.finditer(text)))
    return (vars_, tags)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    require_keys = '--require-keys' in sys.argv
    if len(args) < 2:
        print('用法: python validate.py <en.json> <zh.json> [--require-keys]')
        return 2
    en = json.load(open(args[0], encoding='utf-8-sig'))
    zh = json.load(open(args[1], encoding='utf-8-sig'))

    missing = [k for k in zh if k not in en]
    same = [k for k in zh if k in en and zh[k] == en[k] and '{' not in str(en[k])]
    bad = [(k, en[k], zh[k]) for k, v in zh.items() if k in en and signature(en[k]) != signature(v)]

    print(f'译文条数: {len(zh)}  原文条数: {len(en)}')
    print(f'key 不在原文中(旧词条): {len(missing)}')
    print(f'与原文完全相同的疑似未翻译: {len(same)}')
    print(f'占位符/标签不一致: {len(bad)}')

    if require_keys and missing:
        print('\n!! 多余 key（新版已废弃，可清理）:')
        for k in missing[:20]:
            print(f'   {k}')
    if bad:
        print('\n!! 占位符不一致明细（前 30 条，必须修）:')
        for k, e, z in bad[:30]:
            print(f'   key={k}')
            print(f'     en: {str(e)[:150]}')
            print(f'     zh: {str(z)[:150]}')
    if same:
        print('\n-- 疑似未翻译样例（前 10 条，人工判断）:')
        for k in same[:10]:
            print(f'   {k}: {str(en[k])[:100]}')

    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
