import json
with open("./data/index.json",mode="r", encoding="utf-8") as f:
    data = json.loads(f.read())
    data = json.dumps(data, indent=4, ensure_ascii=False)
    print(data)