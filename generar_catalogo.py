import json

with open('data.json') as f:
    d = json.load(f)

catalog = d['catalog']

with open('catalog_output.txt', 'w') as out:
    for p in catalog:
        img = p['img'].replace('"', '\\"')
        line = f'        {{"id":"{p["id"]}","name":"{p["name"]}","category":"{p["category"]}","unit":"{p["unit"]}","img":"{img}","price":{p["price"]}}},\n'
        out.write(line)

print(f'Listo: {len(catalog)} productos generados en catalog_output.txt')
