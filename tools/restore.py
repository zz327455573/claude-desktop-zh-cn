#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Claude Desktop 还原成官方原版（撤销汉化）。

用法:
    python restore.py                 # 自动识别当前版本
    python restore.py --app-dir <path>
    python restore.py --dry-run

两种还原来源，按优先级：

1. **汉化时的备份**（`out/original-backup/<版本>/`）。install.py 在写入前
   会把原文件复制到这里。有备份就copy回去，这是最忠实的还原。

2. **没有备份时直接删除**。汉化是"往官方目录里加文件 + 改两个地方"：
   - 加的文件：`ion-dist/i18n/{zh-Hans,zh-CN}.json`、
     `ion-dist/i18n/dynamic/{zh-Hans,zh-CN}.json`
     这些官方本身没有，删掉即恢复原状（新版会重新走 Squirrel 安装官方文件）
   - 改的地方：JS 白名单里多出来的 `"zh-Hans"`、config.json 的 locale。
     白名单用反向替换去掉；locale 改回 `en-US`

第 2 条路径让"只下载了 ZIP、没在本机跑过安装"的用户也能还原，
所以还原不依赖备份一定存在。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANTHROPIC = Path(os.environ['LOCALAPPDATA']) / 'AnthropicClaude'
CONFIG = Path(os.environ['LOCALAPPDATA']) / 'Claude-3p' / 'config.json'
ROAMING_CONFIG = Path(os.environ['APPDATA']) / 'Claude-3p' / 'config.json'
BACKUP = ROOT / 'out' / 'original-backup'

LOCALE = 'zh-Hans'
COMPAT_LOCALE = 'zh-CN'
DEFAULT_LOCALE = 'en-US'


def version_key(name: str) -> tuple:
    m = re.search(r'app-([\d.]+)', name)
    if not m:
        return (0,)
    try:
        return tuple(int(x) for x in m.group(1).split('.'))
    except ValueError:
        return (0,)


def find_app_dir() -> Path | None:
    dirs = [p for p in ANTHROPIC.glob('app-*')
            if (p / 'resources' / 'ion-dist' / 'i18n' / 'en-US.json').is_file()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: version_key(p.name), reverse=True)[0]


def injected_files(res: Path) -> list[Path]:
    """列出汉化注入的语言包文件（官方原版没有这些）。"""
    i18n = res / 'ion-dist' / 'i18n'
    out = []
    for loc in (LOCALE, COMPAT_LOCALE):
        out.append(i18n / f'{loc}.json')
        out.append(i18n / 'dynamic' / f'{loc}.json')
    return out


def strip_locale_from_js(text: str) -> tuple[str, bool]:
    """把白名单数组里我们加的 "zh-Hans" 去掉，只动语言白名单数组。"""
    changed = False
    pattern = re.compile(r',\s*"zh-Hans"')

    def fix(m: 're.Match') -> str:
        nonlocal changed
        raw = m.group(0)
        try:
            locs = json.loads(raw)
        except json.JSONDecodeError:
            return raw
        if not isinstance(locs, list) or LOCALE not in locs:
            return raw
        changed = True
        return json.dumps([x for x in locs if x != LOCALE], separators=(',', ':'))

    arr_re = re.compile(
        r'\[\s*"[a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,4})*"'
        r'(?:\s*,\s*"[a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,4})*")+\s*\]'
    )
    return arr_re.sub(fix, text), changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--app-dir', default=None)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    app_dir = Path(args.app_dir) if args.app_dir else find_app_dir()
    if not app_dir or not app_dir.exists():
        print('没找到 Claude 版本目录，用 --app-dir 指定')
        return 1

    res = app_dir / 'resources'
    bak = BACKUP / app_dir.name
    print(f'目标版本: {app_dir.name}')
    print(f'备份目录: {bak}  {"(存在)" if bak.exists() else "(不存在，将直接删除注入文件)"}')

    restored = deleted = 0

    # 1. 语言包：有备份就还原，没有就删除
    for path in injected_files(res):
        b = bak / path.relative_to(res)
        if b.is_file():
            if not args.dry_run:
                shutil.copy2(b, path)
            print(f'  还原 {path.name}  <- 备份')
            restored += 1
        elif path.exists():
            if not args.dry_run:
                path.unlink()
            print(f'  删除 {path.relative_to(res)}')
            deleted += 1

    # 2. JS 白名单去掉 zh-Hans
    js_changed = 0
    for path in sorted((res / 'ion-dist' / 'assets').rglob('*.js')):
        try:
            text = path.read_text(encoding='utf-8')
        except OSError:
            continue
        new, changed = strip_locale_from_js(text)
        if not changed:
            continue
        b = bak / path.relative_to(res)
        if b.is_file():
            # 有备份直接用原版，比反向替换更可靠
            if not args.dry_run:
                shutil.copy2(b, path)
            print(f'  还原 {path.name}  <- 备份')
        else:
            if not args.dry_run:
                path.write_text(new, encoding='utf-8')
            print(f'  移除白名单条目 {path.name}')
        js_changed += 1

    # 3. locale 改回 en-US
    for cfg in (ROAMING_CONFIG, CONFIG):
        if not cfg.exists():
            continue
        try:
            d = json.loads(cfg.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            continue
        old = d.get('locale')
        if old == DEFAULT_LOCALE:
            continue
        d['locale'] = DEFAULT_LOCALE
        if not args.dry_run:
            cfg.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n',
                           encoding='utf-8')
        print(f'  locale: {old} -> {DEFAULT_LOCALE}  ({cfg.parent.name})')

    if args.dry_run:
        print('\ndry-run，未写入任何内容。')
        return 0

    print(f'\n完成：还原 {restored} 个文件、删除 {deleted} 个注入文件、'
          f'处理 {js_changed} 个 JS。')
    print('请完全退出 Claude Desktop（托盘右键 -> 退出）再打开。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
