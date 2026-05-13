from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "requisiciones2024"

AREAS = [
    {"id": "direccion",      "name": "Dirección",                          "password": "dir123",       "budget": 74.83,    "cc": 1},
    {"id": "contabilidad",   "name": "Contabilidad y Administración",      "password": "conta123",     "budget": 2000.00,  "cc": 2},
    {"id": "licitaciones",   "name": "Licitaciones",                       "password": "licit123",     "budget": 14412.10, "cc": 4},
    {"id": "obras",          "name": "Obras",                              "password": "obras123",     "budget": 528.42,   "cc": 5},
    {"id": "almacen",        "name": "Almacén",                            "password": "almacen123",   "budget": 4853.33,  "cc": 6},
    {"id": "logistica",      "name": "Logística",                          "password": "logis123",     "budget": 0.00,     "cc": 7},
    {"id": "produccion",     "name": "Producción",                         "password": "prod123",      "budget": 947.33,   "cc": 8},
    {"id": "diseno",         "name": "Diseño",                             "password": "diseno123",    "budget": 1699.58,  "cc": 9},
    {"id": "compras",        "name": "Compras",                            "password": "compras123",   "budget": 3488.33,  "cc": 10},
    {"id": "proyectos",      "name": "Proyectos",                          "password": "proy123",      "budget": 380.00,   "cc": 11},
    {"id": "capital_humano", "name": "Capital Humano",                     "password": "rrhh123",      "budget": 2945.83,  "cc": 12},
    {"id": "seg_higiene",    "name": "Seguridad e Higiene y Mejora Cont.", "password": "seg123",       "budget": 140.00,   "cc": 13},
    {"id": "ti",             "name": "TI",                                 "password": "ti123",        "budget": 19295.83, "cc": 14},
]

COMPRAS_PASSWORD   = "compras2024"
DIRECCION_PASSWORD = "direccion2024"
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"requisitions": [], "catalog": [], "spent": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def current_month():
    return datetime.now().strftime("%Y-%m")

def get_area(area_id):
    return next((a for a in AREAS if a["id"] == area_id), None)

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        mode     = request.form.get("mode")
        password = request.form.get("password")
        if mode == "compras":
            if password == COMPRAS_PASSWORD:
                session["role"] = "compras"
                return redirect(url_for("compras"))
            else:
                error = "Contraseña incorrecta."
        else:
            area_id = request.form.get("area_id")
            area    = get_area(area_id)
            if not area:
                error = "Selecciona un área."
            elif password == area["password"]:
                session["role"]    = "area"
                session["area_id"] = area_id
                return redirect(url_for("catalogo"))
            else:
                error = "Contraseña incorrecta."
    return render_template("login.html", areas=AREAS, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/catalogo")
def catalogo():
    if session.get("role") != "area":
        return redirect(url_for("login"))
    data  = load_data()
    area  = get_area(session["area_id"])
    mo    = current_month()
    spent = data["spent"].get(session["area_id"], {}).get(mo, 0)
    return render_template("catalogo.html", area=area, catalog=data["catalog"], spent=spent)

@app.route("/carrito")
def carrito():
    if session.get("role") != "area":
        return redirect(url_for("login"))
    data  = load_data()
    area  = get_area(session["area_id"])
    mo    = current_month()
    spent = data["spent"].get(session["area_id"], {}).get(mo, 0)
    return render_template("carrito.html", area=area, catalog=data["catalog"], spent=spent)

@app.route("/enviar", methods=["POST"])
def enviar():
    if session.get("role") != "area":
        return redirect(url_for("login"))
    data       = load_data()
    area       = get_area(session["area_id"])
    cart       = json.loads(request.form.get("cart", "{}"))
    notes      = request.form.get("notes", "")
    authorized = request.form.get("authorized", "false") == "true"
    dir_pass   = request.form.get("dir_password", "")

    if authorized and dir_pass != DIRECCION_PASSWORD:
        return jsonify({"ok": False, "error": "Contraseña de Dirección incorrecta."})

    catalog_map = {p["id"]: p for p in data["catalog"]}
    items, total = [], 0
    for pid, qty in cart.items():
        p = catalog_map.get(pid)
        if p and qty > 0:
            subtotal = p["price"] * qty
            total   += subtotal
            items.append({**p, "qty": qty, "subtotal": subtotal})

    req = {
        "id":         "REQ-" + datetime.now().strftime("%y%m%d%H%M%S"),
        "area":       area["name"],
        "area_id":    area["id"],
        "cc":         area["cc"],
        "items":      items,
        "notes":      notes,
        "total":      total,
        "authorized": authorized,
        "status":     "pendiente",
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    data["requisitions"].insert(0, req)

    mo = current_month()
    if area["id"] not in data["spent"]:
        data["spent"][area["id"]] = {}
    data["spent"][area["id"]][mo] = data["spent"][area["id"]].get(mo, 0) + total
    save_data(data)
    return jsonify({"ok": True})

@app.route("/compras")
def compras():
    if session.get("role") != "compras":
        return redirect(url_for("login"))
    data   = load_data()
    mo     = current_month()
    spent  = {a["id"]: data["spent"].get(a["id"], {}).get(mo, 0) for a in AREAS}
    alerts = [a for a in AREAS if spent[a["id"]] >= a["budget"] and a["budget"] > 0]
    return render_template("compras.html", requisitions=data["requisitions"],
                           areas=AREAS, catalog=data["catalog"],
                           spent=spent, alerts=alerts)

@app.route("/actualizar_status", methods=["POST"])
def actualizar_status():
    if session.get("role") != "compras":
        return jsonify({"ok": False})
    data   = load_data()
    req_id = request.form.get("id")
    status = request.form.get("status")
    for r in data["requisitions"]:
        if r["id"] == req_id:
            r["status"] = status
            break
    save_data(data)
    return jsonify({"ok": True})

@app.route("/guardar_presupuesto", methods=["POST"])
def guardar_presupuesto():
    if session.get("role") != "compras":
        return jsonify({"ok": False})
    area_id = request.form.get("area_id")
    budget  = float(request.form.get("budget", 0))
    for a in AREAS:
        if a["id"] == area_id:
            a["budget"] = budget
            break
    return jsonify({"ok": True})

@app.route("/guardar_producto", methods=["POST"])
def guardar_producto():
    if session.get("role") != "compras":
        return jsonify({"ok": False})
    data = load_data()
    prod = {
        "id":       request.form.get("id"),
        "name":     request.form.get("name"),
        "category": request.form.get("category"),
        "unit":     request.form.get("unit"),
        "img":      request.form.get("img", "📦"),
        "price":    float(request.form.get("price", 0)),
    }
    existing = next((i for i,p in enumerate(data["catalog"]) if p["id"]==prod["id"]), None)
    if existing is not None:
        data["catalog"][existing] = prod
    else:
        data["catalog"].append(prod)
    save_data(data)
    return jsonify({"ok": True})

@app.route("/eliminar_producto", methods=["POST"])
def eliminar_producto():
    if session.get("role") != "compras":
        return jsonify({"ok": False})
    data    = load_data()
    prod_id = request.form.get("id")
    data["catalog"] = [p for p in data["catalog"] if p["id"] != prod_id]
    save_data(data)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)