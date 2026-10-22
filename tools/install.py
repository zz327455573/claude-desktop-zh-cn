#!/usr/bin/env python3
"""一键应用中文本地化到当前运行的 Claude Desktop。

用法:
    python install.py                  # 自动识别当前版本
    python install.py --app-dir <path> # 指定版本目录
    python install.py --dry-run        # 只看会改什么，不写入

做的事:
    1. 备份原版语言包到 out/original-backup/
    2. 写入语言包（前端界面 + dynamic + 原生菜单）
    3. 给 JS 的语言白名单补上 zh-Hans（否则设置里不显示简体中文）
    4. 把 Local 的 Claude-3p/config.json 的 locale 改成 zh-Hans

关于语言代码：2.42304.0 起官方把中文代码从 zh-CN 改成了 zh-Hans
（主进程语言表、resources/zh-Hans.json、语言选择器显示名都只有 zh-Hans）。
locale 填 zh-CN 会匹配失败掉回 en-US，所以这里统一用 zh-Hans。
渲染层会把 zh-CN 请求归一化成 zh-hans，因此语言包文件两套都写、
白名单只加 zh-Hans（避免语言栏出现重复条目）。

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

# 主语言代码（官方 2.42304.0 起）。白名单只加这个，不加 zh-CN。
LOCALE = 'zh-Hans'
# 语言包文件按这套代码落盘，zh-CN 作为兼容兜底。
CATALOG_LOCALES = ('zh-Hans', 'zh-CN')

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
    i18n = res / 'ion-dist' / 'i18n'
    print(f'目标版本: {app_dir.name}')

    # 主包 + dynamic 两套都写。dynamic 是新版必需：渲染层会同时请求
    # /i18n/<locale>.json 和 /i18n/dynamic/<locale>.json，缺了会 404。
    targets = []
    for loc in CATALOG_LOCALES:
        targets.append((ROOT / 'zh-CN.json', i18n / f'{loc}.json'))
    dyn_src = ROOT / 'zh-CN-dynamic.json'
    if dyn_src.exists():
        for loc in CATALOG_LOCALES:
            targets.append((dyn_src, i18n / 'dynamic' / f'{loc}.json'))
    # 原生菜单：官方已自带 resources/zh-Hans.json，无需覆盖

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

    # 3. JS 语言白名单补 zh-Hans
    patched = 0
    if not args.dry_run:
        for path in sorted((res / 'ion-dist' / 'assets').rglob('*.js')):
            try:
                text = path.read_text(encoding='utf-8')
            except OSError:
                continue
            if '"en-US"' not in text and f'"{LOCALE}"' in text:
                continue

            def fix(m: re.Match) -> str:
                raw = m.group(0)
                try:
                    locs = json.loads(raw)
                except json.JSONDecodeError:
                    return raw
                if not isinstance(locs, list) or 'en-US' not in locs:
                    return raw
                if LOCALE in locs:
                    return raw
                return raw[:-1] + f',"{LOCALE}"]'

            new = LOCALE_ARRAY_RE.sub(fix, text)
            if new != text:
                bakp = bak / path.relative_to(res)
                if not bakp.exists():
                    bakp.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, bakp)
                path.write_text(new, encoding='utf-8')
                patched += 1
        print(f'  白名单补丁: {patched} 个 JS')

    # 4. locale（两份都写：Roaming 那份旧版写入、Local 那份应用实际读且每次启动重写）
    roaming = Path(os.environ['APPDATA']) / 'Claude-3p' / 'config.json'
    for cfg in (roaming, CONFIG):
        if not cfg.exists():
            print(f'  没找到 {cfg}，跳过')
            continue
        try:
            d = json.loads(cfg.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            print(f'  {cfg.name} 解析失败，跳过')
            continue
        old = d.get('locale')
        d['locale'] = LOCALE
        if not args.dry_run:
            cfg.write_text(
                json.dumps(d, ensure_ascii=False, indent=2) + '\n',
                encoding='utf-8')
        print(f'  locale: {old} -> {LOCALE}  ({cfg.parent.name})')

    if args.dry_run:
        print('\ndry-run，未写入任何内容。')
        return 0

    print('\n完成。请完全退出 Claude Desktop（托盘右键 -> 退出）再打开。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
