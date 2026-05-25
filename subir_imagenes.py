import os
import json
import base64, urllib.request, urllib.parse, ssl
ssl._create_default_https_context = ssl._create_unverified_context
import urllib.request
import urllib.parse
import time

IMGBB_API_KEY = "9d97d0d356aaf6b933b1a8ebab8ab14a"
IMAGENES_DIR  = "IMÁGENES"
DATA_FILE     = "data.json"

# Cargar catálogo
with open(DATA_FILE, "r") as f:
    data = json.load(f)

catalog = data["catalog"]
total   = len(catalog)
updated = 0
skipped = 0

for i, prod in enumerate(catalog):
    name = prod["name"]
    
    # Buscar imagen con ese nombre
    img_path = None
    for ext in ["jpg","jpeg","png","webp"]:
        path = os.path.join(IMAGENES_DIR, f"{name}.{ext}")
        if os.path.exists(path):
            img_path = path
            break
    
    if not img_path:
        print(f"[{i+1}/{total}] ⚠️  Sin imagen: {name}")
        skipped += 1
        continue
    
    # Si ya tiene URL de imagen, saltar
    if prod["img"].startswith("http"):
        print(f"[{i+1}/{total}] ✓ Ya tiene imagen: {name}")
        updated += 1
        continue
    
    # Subir a ImgBB
    try:
        with open(img_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        post_data = urllib.parse.urlencode({
            "key":   IMGBB_API_KEY,
            "image": image_data,
            "name":  name
        }).encode()
        
        req = urllib.request.Request("https://api.imgbb.com/1/upload", data=post_data)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
        
        if result.get("success"):
            catalog[i]["img"] = result["data"]["url"]
            updated += 1
            print(f"[{i+1}/{total}] ✅ {name}")
        else:
            print(f"[{i+1}/{total}] ❌ Error: {name} — {result}")
        
        time.sleep(0.5)  # pausa para no saturar la API
        
    except Exception as e:
        print(f"[{i+1}/{total}] ❌ Excepción: {name} — {e}")

# Guardar datos actualizados
data["catalog"] = catalog
with open(DATA_FILE, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Listo: {updated} actualizadas, {skipped} sin imagen")