#!/usr/bin/env python3
"""一键应用中文本地化到当前运行的 Claude Desktop。

用法:
    python install.py                  # 自动识别当前版本
    python install.py --app-dir <path> # 指定版本目录
    python install.py --dry-run        # 只看会改什么，不写入

做的事:
    1. 备份原版语言包到 out/original-backup/
    2. 写入三份语言包（前端界面 / 原生菜单 / statsig）
    3. 给 JS 的语言白名单补上 zh-CN（否则设置里不显示简体中文）
    4. 把 Local 的 Claude-3p/config.json 的 locale 改成 zh-CN

打完后需要完全退出 Claude Desktop（托盘右键 -> 退出）再打开。
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

LOCALE_ARRAY_RE = re.compile(
    r'\[\s*"[a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,4})*"'
    r'(?:\s*,\s*"[a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,4})*")+\s*\]'
)


def find_app_dir() -> Path | None:
    """取 RELEASES 里最新版对应的 app-* 目录。"""
    dirs = [p for p in ANTHROPIC.glob('app-*')
            if (p / 'resources' / 'ion-dist' / 'i18n' / 'en-US.json').is_file()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: version_key(p.name), reverse=True)[0]


def version_key(name: str) -> tuple:
    m = re.search(r'app-([\d.]+)', name)
    if not m:
        return (0,)
    try:
        return tuple(int(x) for x in m.group(1).split('.'))
    except ValueError:
        return (0,)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--app-dir', default=None)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    app_dir = Path(args.app_dir) if args.app_dir else find_app_dir()
    if not app_dir or not app_dir.exists():
        print('没找到 Claude 版本目录，用 --app-dir 指定，例如：')
        print('  python install.py --app-dir '
              r'"%LOCALAPPDATA%\AnthropicClaude\app-2.9939.2"')
        return 1

    res = app_dir / 'resources'
    print(f'目标版本: {app_dir.name}')

    targets = [
        (ROOT / 'zh-CN.json', res / 'ion-dist' / 'i18n' / 'zh-CN.json'),
        (ROOT / 'menu-zh-CN.json', res / 'zh-CN.json'),
        (ROOT / 'statsig-zh-CN.json',
         res / 'ion-dist' / 'i18n' / 'statsig' / 'zh-CN.json'),
    ]

    # 1. 备份
    bak = ROOT / 'out' / 'original-backup' / app_dir.name
    for src, dst in targets:
        if dst.exists():
            b = bak / dst.relative_to(res)
            if not b.exists():
                if not args.dry_run:
                    b.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(dst, b)
            print(f'  备份 {dst.name} -> {b}')

    # 2. 写语言包
    for src, dst in targets:
        if not src.exists():
            print(f'  跳过 {src.name}（仓库里没有）')
            continue
        if args.dry_run:
            print(f'  [dry-run] 将写入 {dst}')
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        n = len(json.load(open(src, encoding='utf-8-sig')))
        print(f'  写入 {dst.name}（{n} 条）')

    # 3. JS 语言白名单补 zh-CN
    patched = 0
    if not args.dry_run:
        for path in sorted((res / 'ion-dist' / 'assets').rglob('*.js')):
            try:
                text = path.read_text(encoding='utf-8')
            except OSError:
                continue
            if '"en-US"' not in text and '"zh-CN"' in text:
                continue

            def fix(m: re.Match) -> str:
                raw = m.group(0)
                try:
                    locs = json.loads(raw)
                except json.JSONDecodeError:
                    return raw
                if not isinstance(locs, list) or 'en-US' not in locs:
                    return raw
                if 'zh-CN' in locs:
                    return raw
                return raw[:-1] + ',"zh-CN"]'

            new = LOCALE_ARRAY_RE.sub(fix, text)
            if new != text:
                bakp = bak / path.relative_to(res)
                if not bakp.exists():
                    bakp.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, bakp)
                path.write_text(new, encoding='utf-8')
                patched += 1
        print(f'  白名单补丁: {patched} 个 JS')

    # 4. locale
    if CONFIG.exists():
        d = json.loads(CONFIG.read_text(encoding='utf-8'))
        old = d.get('locale')
        d['locale'] = 'zh-CN'
        if not args.dry_run:
            CONFIG.write_text(
                json.dumps(d, ensure_ascii=False, indent=2) + '\n',
                encoding='utf-8')
        print(f'  locale: {old} -> zh-CN  ({CONFIG})')
    else:
        print(f'  没找到 {CONFIG}，跳过 locale')

    if args.dry_run:
        print('\ndry-run，未写入任何内容。')
        return 0

    print('\n完成。请完全退出 Claude Desktop（托盘右键 -> 退出）再打开。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
