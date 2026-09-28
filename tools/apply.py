#!/usr/bin/env python3
"""把翻译结果合并进 resources/frontend-zh-CN.json。

用法:
    python apply.py out/translated.json
    python apply.py out/translated.json --dry-run    # 只看会改什么，不落盘

translated.json 格式: {key: 中文译文}
- 已存在的 key 会被覆盖
- 新 key 会被追加
- 合并前自动备份 frontend-zh-CN.json 到 out/backup-<时间戳>/
- 合并后自动跑占位符校验，不一致会拒绝写入
"""
from __future__ import annotations
import argparse, json, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / 'resources'
ZH = RES / 'zh-CN.json'
EN_CACHE = ROOT / 'out' / 'en-cache.json'

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import signature  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('translated')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    new = json.load(open(args.translated, encoding='utf-8'))
    zh = json.load(open(ZH, encoding='utf-8-sig')) if ZH.exists() else {}

    added = sum(1 for k in new if k not in zh)
    updated = sum(1 for k in new if k in zh and zh[k] != new[k])

    # 占位符校验：需要英文原文做对照
    problems = []
    if EN_CACHE.exists():
        en = json.load(open(EN_CACHE, encoding='utf-8'))
        for k, v in new.items():
            if k in en and signature(en[k]) != signature(v):
                problems.append(k)
        if problems:
            print(f'!! 有 {len(problems)} 条占位符/标签不一致，拒绝写入（先修 translated.json）:')
            for k in problems[:20]:
                print(f'   {k}')
                print(f'     en: {str(en[k])[:140]}')
                print(f'     zh: {str(new[k])[:140]}')
            return 1
    else:
        print('(未找到 out/en-cache.json，跳过占位符校验；建议先跑 sync.py)')

    print(f'新增 {added} 条，更新 {updated} 条，合计写入 {len(new)} 条')
    if args.dry_run:
        print('dry-run，未写入。')
        return 0

    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    bak = ROOT / 'out' / f'backup-{stamp}'
    bak.mkdir(parents=True, exist_ok=True)
    if ZH.exists():
        shutil.copy2(ZH, bak / ZH.name)

    merged = dict(zh)
    merged.update(new)
    ZH.write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'已写入 {ZH}（{len(merged)} 条），备份在 {bak}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
