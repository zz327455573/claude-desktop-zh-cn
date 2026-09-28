import json, re, os, glob, sys

v1_dir = r"C:/Users/Admin/AppData/Local/AnthropicClaude/app-1.52386.6/resources/ion-dist/assets/v1"
zh_path = r"C:/Users/Admin/AppData/Local/AnthropicClaude/app-1.52386.6/resources/ion-dist/i18n/zh-CN.json"

zh = json.load(open(zh_path, encoding="utf-8"))
before = len(zh)

added = {}
for part in [r"C:/Users/Admin/汉化/trans_part1.json", r"C:/Users/Admin/汉化/trans_part2.json"]:
    d = json.load(open(part, encoding="utf-8"))
    for k, v in d.items():
        if k in zh and zh[k] != v:
            # 已有不同翻译：保留新的（我们的），但记一笔
            pass
        if k not in zh:
            added[k] = v
            zh[k] = v
        else:
            # 已存在：用我们更准的翻译覆盖（谨慎，仅在我们明确更优时）
            # 这里选择不覆盖已有，避免破坏已验证的翻译
            pass

after = len(zh)
print(f"合并前条数: {before}")
print(f"新增条数: {after - before}")
print(f"合并后条数: {after}")

# 验证 JSON 合法性
json.dumps(zh, ensure_ascii=False)
print("JSON 合法性: OK")

# 备份原文件
import shutil, time
bak = zh_path + ".bak." + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(zh_path, bak)
print(f"原文件已备份: {bak}")

# 写入
with open(zh_path, "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=1)  # 保持原格式
print(f"已写入: {zh_path}")

# 重新扫描：现在还有多少缺失
pat_dm_id = re.compile(rb'defaultMessage:"((?:[^"\\]|\\.)*)"\s*,\s*id:"([^"]*)"')
pat_id_dm = re.compile(rb'id:"([^"]*)"\s*,\s*defaultMessage:"((?:[^"\\]|\\.)*)"')
pairs = {}
for fp in sorted(glob.glob(os.path.join(v1_dir, "*.js"))):
    with open(fp, "rb") as f:
        data = f.read()
    for m in pat_dm_id.finditer(data):
        pairs.setdefault(m.group(2).decode("utf-8","replace"), set()).add(m.group(1).decode("utf-8","replace"))
    for m in pat_id_dm.finditer(data):
        pairs.setdefault(m.group(1).decode("utf-8","replace"), set()).add(m.group(2).decode("utf-8","replace"))

missing = [k for k in pairs if k not in zh]
print(f"\n重新扫描后仍缺失: {len(missing)} 个 id")
if missing:
    print("前 10 个:", missing[:10])
