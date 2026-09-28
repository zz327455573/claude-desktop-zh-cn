#!/usr/bin/env python3
"""增量同步：对比当前 Claude 版本的 en-US 与本地 zh-CN，导出「待翻译增量」。

这是本项目的核心工作流。Claude Desktop 每次更新都会新增/修改 UI 文案，
你不需要重译整包，只需要译这个脚本导出的增量，然后提交。

用法:
    python sync.py                     # 自动找当前运行的最新 app-* 版本
    python sync.py --app-dir <path>    # 指定版本目录
    python sync.py --json <en.json>    # 直接指定 en-US.json 路径

产物（写在 out/ 下）:
    todo.json    需要翻译的增量: {key: english, ...}
    new.json     需要新建的增量（同上，新功能词条）
    stats.txt    覆盖率统计
    stale.json   zh-CN 里已在新版消失的旧词条（可清理，不影响运行）

翻译流程:
    1. python sync.py                      -> 看 out/todo.json
    2. 把 todo.json 的 value 全部译成中文   -> 保存为 out/translated.json
    3. python apply.py                     -> 合并进 resources/frontend-zh-CN.json
    4. python validate.py                  -> 校验占位符一致性
    5. git commit & push                   -> 成为上游源头
"""
from __future__ import annotations
import argparse, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / 'resources'
OUT = ROOT / 'out'
ZH = RES / 'frontend-zh-CN.json'

ANTHROPIC = Path(os.environ.get('LOCALAPPDATA', '')) / 'AnthropicClaude'


def find_version_dirs() -> list[Path]:
    if not ANTHROPIC.exists():
        return []
    dirs = [p for p in ANTHROPIC.glob('app-*')
            if (p / 'resources' / 'ion-dist' / 'i18n' / 'en-US.json').is_file()]
    return sorted(dirs, key=lambda p: version_key(p.name), reverse=True)


def version_key(name: str) -> tuple:
    m = re.search(r'app-([\d.]+)', name)
    if not m:
        return (0,)
    try:
        return tuple(int(x) for x in m.group(1).split('.'))
    except ValueError:
        return (0,)


def load_english(i18n_dir: Path) -> dict[str, str]:
    """合并主包 + dynamic 两个英文源，得到该版本的完整文案需求。"""
    merged: dict[str, str] = {}
    for rel in ['en-US.json', 'dynamic/en-US.json']:
        p = i18n_dir / rel.replace('/', os.sep)
        if p.is_file():
            merged.update(json.load(open(p, encoding='utf-8-sig')))
    if not merged:
        raise SystemExit(f'在 {i18n_dir} 没找到 en-US.json')
    return merged


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--app-dir', default=None)
    ap.add_argument('--json', default=None, help='直接指定 en-US.json')
    args = ap.parse_args()

    if args.json:
        en = json.load(open(args.json, encoding='utf-8-sig'))
        version = Path(args.json).parent
    else:
        if args.app_dir:
            ver_dir = Path(args.app_dir)
        else:
            candidates = find_version_dirs()
            if not candidates:
                raise SystemExit('没找到任何 app-* 版本目录，用 --app-dir 指定')
            ver_dir = candidates[0]
            print(f'自动选中最新版本: {ver_dir.name}')
        version = ver_dir
        en = load_english(ver_dir / 'resources' / 'ion-dist' / 'i18n')

    zh = json.load(open(ZH, encoding='utf-8-sig')) if ZH.exists() else {}

    PLACEHOLDER = re.compile(r'^\s*(待翻译|待补充翻译)[：:]')
    todo, stale = {}, {}
    for k, v in en.items():
        cur = zh.get(k)
        if cur is None or cur == v or (isinstance(cur, str) and PLACEHOLDER.match(cur)):
            todo[k] = v
    for k in zh:
        if k not in en:
            stale[k] = zh[k]

    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(en, open(OUT / 'en-cache.json', 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(todo, open(OUT / 'todo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(stale, open(OUT / 'stale.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    covered = len(en) - len(todo)
    pct = 100.0 * covered / len(en) if en else 0.0
    lines = [
        f'版本目录: {version}',
        f'该版本英文总词条: {len(en)}',
        f'zh-CN 已覆盖:      {covered}  ({pct:.1f}%)',
        f'待翻译(含占位符):  {len(todo)}',
        f'旧词条(新版已删):  {len(stale)}',
        '',
        '下一步: 翻译 out/todo.json -> 存为 out/translated.json -> 跑 apply.py',
    ]
    (OUT / 'stats.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
