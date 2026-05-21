from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

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

def get_default_catalog():
    return [
        {"id":"1","name":"CUTTER 18MM","category":"ALMACÉN","unit":"PIEZA","img":"✂️","price":0},
        {"id":"2","name":"NAVAJAS DE CUTTER","category":"ALMACÉN","unit":"PIEZA","img":"✂️","price":0},
        {"id":"3","name":"PAPEL PARA ETIQUETA PARA LÁSER","category":"ALMACÉN","unit":"PAQUETE","img":"📄","price":0},
        {"id":"4","name":"PLAYO TRANSPARENTE","category":"ALMACÉN","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"5","name":"CINTA ADHESIVA TRANSPARENTE 48MM X 150M","category":"ALMACÉN","unit":"PAQUETE","img":"🎞️","price":0},
        {"id":"6","name":"CINTA ADHESIVA CANELA 48MM X 150M","category":"ALMACÉN","unit":"PAQUETE","img":"🎞️","price":0},
        {"id":"7","name":"TARIMA DE MADERA 120 X 100 CM","category":"ALMACÉN","unit":"PIEZA","img":"📦","price":0},
        {"id":"8","name":"CAJA DE CARTÓN 53X40X54","category":"ALMACÉN","unit":"PIEZA","img":"📦","price":0},
        {"id":"9","name":"CAJA DE PAQUETERÍA 50X27X29","category":"ALMACÉN","unit":"PIEZA","img":"📦","price":0},
        {"id":"10","name":"BOLSA DE 1 KG DE CAFÉ","category":"CAFETERÍA","unit":"PIEZA","img":"☕","price":0},
        {"id":"11","name":"CAJA DE TÉ","category":"CAFETERÍA","unit":"PIEZA","img":"🍵","price":0},
        {"id":"12","name":"BOTELLAS DE AGUA DE 335ML","category":"CAFETERÍA","unit":"PIEZA","img":"💧","price":0},
        {"id":"13","name":"CREMA EN POLVO","category":"CAFETERÍA","unit":"PAQUETE","img":"🍬","price":0},
        {"id":"14","name":"CUCHARAS DE PLÁSTICO","category":"CAFETERÍA","unit":"PAQUETE","img":"🍴","price":0},
        {"id":"15","name":"CUCHILLOS DE PLÁSTICO","category":"CAFETERÍA","unit":"PAQUETE","img":"🍴","price":0},
        {"id":"16","name":"ENDULZANTE SPLENDA","category":"CAFETERÍA","unit":"PAQUETE","img":"🍬","price":0},
        {"id":"17","name":"PLATOS DESECHABLES NO. 2","category":"CAFETERÍA","unit":"PAQUETE","img":"🍽️","price":0},
        {"id":"18","name":"PLATOS DESECHABLES NO. 7","category":"CAFETERÍA","unit":"PAQUETE","img":"🍽️","price":0},
        {"id":"19","name":"SERVILLETAS","category":"CAFETERÍA","unit":"PAQUETE","img":"🍽️","price":0},
        {"id":"20","name":"AZÚCAR","category":"CAFETERÍA","unit":"PIEZA","img":"🍬","price":0},
        {"id":"21","name":"TENEDORES DE PLÁSTICO","category":"CAFETERÍA","unit":"PIEZA","img":"🍴","price":0},
        {"id":"22","name":"VASOS TÉRMICOS","category":"CAFETERÍA","unit":"PAQUETE","img":"🥤","price":0},
        {"id":"23","name":"ALGODÓN","category":"HSE","unit":"PAQUETE","img":"🩺","price":0},
        {"id":"24","name":"ALCOHOL ETÍLICO","category":"HSE","unit":"PIEZA","img":"🧪","price":0},
        {"id":"25","name":"BOTIQUÍN","category":"HSE","unit":"PIEZA","img":"🩺","price":0},
        {"id":"26","name":"CHALECO DE SEGURIDAD AMARILLO","category":"HSE","unit":"PIEZA","img":"🦺","price":0},
        {"id":"27","name":"CHALECO DE SEGURIDAD AZUL","category":"HSE","unit":"PIEZA","img":"🦺","price":0},
        {"id":"28","name":"CHALECO DE SEGURIDAD NARANJA","category":"HSE","unit":"PIEZA","img":"🦺","price":0},
        {"id":"29","name":"CHALECO DE SEGURIDAD NEGRO","category":"HSE","unit":"PIEZA","img":"🦺","price":0},
        {"id":"30","name":"CHALECO DE SEGURIDAD VERDE","category":"HSE","unit":"PIEZA","img":"🦺","price":0},
        {"id":"31","name":"CONOS DE SEGURIDAD","category":"HSE","unit":"PIEZA","img":"⚠️","price":0},
        {"id":"32","name":"GRASA","category":"HSE","unit":"LITRO","img":"🔧","price":0},
        {"id":"33","name":"JERINGAS","category":"HSE","unit":"PIEZA","img":"💉","price":0},
        {"id":"34","name":"SEÑALÉTICA","category":"HSE","unit":"PIEZA","img":"⚠️","price":0},
        {"id":"35","name":"PILAS RECARGABLES AA","category":"IT","unit":"PIEZA","img":"🔋","price":0},
        {"id":"36","name":"PILAS RECARGABLES AAA","category":"IT","unit":"PIEZA","img":"🔋","price":0},
        {"id":"37","name":"BOTELLA DE TINTA GI-190 NEGRA","category":"IT","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"38","name":"CALCULADORA","category":"IT","unit":"PIEZA","img":"🧮","price":0},
        {"id":"39","name":"CARGADOR DE BATERÍAS AA","category":"IT","unit":"PIEZA","img":"🔋","price":0},
        {"id":"40","name":"CARGADOR DE BATERÍAS AAA","category":"IT","unit":"PIEZA","img":"🔋","price":0},
        {"id":"41","name":"CARTUCHOS DE TINTA 954 XL","category":"IT","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"42","name":"DISCO SÓLIDO DE 480 GB","category":"IT","unit":"PIEZA","img":"💾","price":0},
        {"id":"43","name":"EXTENSIÓN DE LUZ","category":"IT","unit":"PIEZA","img":"🔌","price":0},
        {"id":"44","name":"HUB","category":"IT","unit":"PIEZA","img":"🔌","price":0},
        {"id":"45","name":"MEMORIA USB 32GB","category":"IT","unit":"PIEZA","img":"💾","price":0},
        {"id":"46","name":"MOUSE ALÁMBRICO","category":"IT","unit":"PIEZA","img":"🖱️","price":0},
        {"id":"47","name":"MOUSE INALÁMBRICO","category":"IT","unit":"PIEZA","img":"🖱️","price":0},
        {"id":"48","name":"MOUSE PAD","category":"IT","unit":"PIEZA","img":"🖱️","price":0},
        {"id":"49","name":"MULTICONTACTOS","category":"IT","unit":"PIEZA","img":"🔌","price":0},
        {"id":"50","name":"PASTA TÉRMICA","category":"IT","unit":"PIEZA","img":"💻","price":0},
        {"id":"51","name":"PILAS AA","category":"IT","unit":"PIEZA","img":"🔋","price":0},
        {"id":"52","name":"PILAS AAA","category":"IT","unit":"PIEZA","img":"🔋","price":0},
        {"id":"53","name":"REMOVEDOR DE POLVO","category":"IT","unit":"PIEZA","img":"💨","price":0},
        {"id":"54","name":"TINTA AMARILLA","category":"IT","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"55","name":"TINTA AZUL","category":"IT","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"56","name":"TINTA NEGRA","category":"IT","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"57","name":"TINTA ORIGINAL HP NEGRA","category":"IT","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"58","name":"TINTA ROJA","category":"IT","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"59","name":"TONER RICOH COLOR NEGRO","category":"IT","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"60","name":"AROMATIZANTE DE BAÑO","category":"LIMPIEZA","unit":"PIEZA","img":"✨","price":0},
        {"id":"61","name":"BOLSA DE BASURA CHICA","category":"LIMPIEZA","unit":"CAJA","img":"🗑️","price":0},
        {"id":"62","name":"BOLSA DE BASURA JUMBO","category":"LIMPIEZA","unit":"CAJA","img":"🗑️","price":0},
        {"id":"63","name":"BOLSA DE JABÓN","category":"LIMPIEZA","unit":"PIEZA","img":"🧴","price":0},
        {"id":"64","name":"CEPILLO PARA BAÑO","category":"LIMPIEZA","unit":"PIEZA","img":"🧹","price":0},
        {"id":"65","name":"CLORO","category":"LIMPIEZA","unit":"LT","img":"🧪","price":0},
        {"id":"66","name":"CUBETA","category":"LIMPIEZA","unit":"PIEZA","img":"🪣","price":0},
        {"id":"67","name":"DESINFECTANTE","category":"LIMPIEZA","unit":"PIEZA","img":"🧴","price":0},
        {"id":"68","name":"DESINFECTANTE EN AEROSOL 354G","category":"LIMPIEZA","unit":"PIEZA","img":"🧴","price":0},
        {"id":"69","name":"DESTAPACAÑO LÍQUIDO","category":"LIMPIEZA","unit":"PIEZA","img":"🪠","price":0},
        {"id":"70","name":"DESTAPACAÑOS","category":"LIMPIEZA","unit":"PIEZA","img":"🪠","price":0},
        {"id":"71","name":"ESCOBA","category":"LIMPIEZA","unit":"PIEZA","img":"🧹","price":0},
        {"id":"72","name":"ESPONJAS","category":"LIMPIEZA","unit":"PIEZA","img":"🧽","price":0},
        {"id":"73","name":"ESPONJERO","category":"LIMPIEZA","unit":"PIEZA","img":"🧽","price":0},
        {"id":"74","name":"FIBRA DE USO GENERAL","category":"LIMPIEZA","unit":"PIEZA","img":"🧽","price":0},
        {"id":"75","name":"FIBRA DE USO RUDO","category":"LIMPIEZA","unit":"PIEZA","img":"🧽","price":0},
        {"id":"76","name":"GUANTES","category":"LIMPIEZA","unit":"PAR","img":"🧤","price":0},
        {"id":"77","name":"JABÓN DE TRASTES","category":"LIMPIEZA","unit":"LT","img":"🧴","price":0},
        {"id":"78","name":"JABÓN PARA MANOS","category":"LIMPIEZA","unit":"LT","img":"🧴","price":0},
        {"id":"79","name":"JABÓN ROMA","category":"LIMPIEZA","unit":"LT","img":"🧴","price":0},
        {"id":"80","name":"JABÓN ZOTE","category":"LIMPIEZA","unit":"PIEZA","img":"🧴","price":0},
        {"id":"81","name":"JERGA","category":"LIMPIEZA","unit":"PIEZA","img":"🧹","price":0},
        {"id":"82","name":"LIMPIADOR MULTIUSOS","category":"LIMPIEZA","unit":"PIEZA","img":"🧴","price":0},
        {"id":"83","name":"PAÑO MICROFIBRA","category":"LIMPIEZA","unit":"PIEZA","img":"🧹","price":0},
        {"id":"84","name":"PASTILLA PARA WC","category":"LIMPIEZA","unit":"PIEZA","img":"🚽","price":0},
        {"id":"85","name":"REPUESTO PARA MOP 90CM","category":"LIMPIEZA","unit":"PIEZA","img":"🧹","price":0},
        {"id":"86","name":"ROLLOS DE PAPEL HIGIÉNICO","category":"LIMPIEZA","unit":"PIEZA","img":"🧻","price":0},
        {"id":"87","name":"TOALLA INTERDOBLADA","category":"LIMPIEZA","unit":"CAJA","img":"🧻","price":0},
        {"id":"88","name":"TOALLAS PARA LIMPIAR","category":"LIMPIEZA","unit":"PIEZA","img":"🧻","price":0},
        {"id":"89","name":"TRAPEADOR","category":"LIMPIEZA","unit":"PIEZA","img":"🧹","price":0},
        {"id":"90","name":"ADHESIVO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"91","name":"AFLOJATODO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"92","name":"VÁLBULA DE LLENADO PARA SANITARIO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔩","price":0},
        {"id":"93","name":"BOMBA PARA GARRAFÓN DE AGUA","category":"MANTENIMIENTO","unit":"PIEZA","img":"💧","price":0},
        {"id":"94","name":"BOTE DE PINTURA BLANCO ESMALTE","category":"MANTENIMIENTO","unit":"PIEZA","img":"🪣","price":0},
        {"id":"95","name":"BOTES DE LÍQUIDO DE PERFORACIÓN","category":"MANTENIMIENTO","unit":"PIEZA","img":"🪣","price":0},
        {"id":"96","name":"SEGUETA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"97","name":"CHAPA SIN LLAVE","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔐","price":0},
        {"id":"98","name":"CINCEL Y LLAVE DE 3/4 COMBINADA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"99","name":"CINTA ANTIDERRAPANTE","category":"MANTENIMIENTO","unit":"PIEZA","img":"⚠️","price":0},
        {"id":"100","name":"CINTA ESQUINERA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"101","name":"CINTA MASKING","category":"MANTENIMIENTO","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"102","name":"CINTA MÉTRICA DE 20 METROS","category":"MANTENIMIENTO","unit":"PIEZA","img":"📏","price":0},
        {"id":"103","name":"CINTAS DELIMITADORAS","category":"MANTENIMIENTO","unit":"PIEZA","img":"⚠️","price":0},
        {"id":"104","name":"CUCHARA DE ALBAÑIL","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"105","name":"DESARMADOR DE CRUZ","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"106","name":"DESARMADOR PLANO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"107","name":"DETECTOR DE VOLTAJE","category":"MANTENIMIENTO","unit":"PIEZA","img":"⚡","price":0},
        {"id":"108","name":"ESCALERA ALTA DE 7 ESCALONES ALUMINIO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🪜","price":0},
        {"id":"109","name":"ESCALERAS TRUPPER 3 ESCALONES","category":"MANTENIMIENTO","unit":"PIEZA","img":"🪜","price":0},
        {"id":"110","name":"ESMALTE PINTURA NEGRA DE ACEITE","category":"MANTENIMIENTO","unit":"GALÓN","img":"🪣","price":0},
        {"id":"111","name":"ESMALTE ROJO","category":"MANTENIMIENTO","unit":"GALÓN","img":"🪣","price":0},
        {"id":"112","name":"ESMALTE VERDE","category":"MANTENIMIENTO","unit":"PIEZA","img":"🪣","price":0},
        {"id":"113","name":"ESMERILADORA DE 4.5 PULGADAS ELÉCTRICA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"114","name":"LLAVE STILSON","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"115","name":"EXTENSIÓN ELÉCTRICA DE USO RUDO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔌","price":0},
        {"id":"116","name":"FLEXÓMETRO DE 5 METROS","category":"MANTENIMIENTO","unit":"PIEZA","img":"📏","price":0},
        {"id":"117","name":"FUMIGADOR TIPO MOCHILA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🌿","price":0},
        {"id":"118","name":"HIZAYAS","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"119","name":"INSECTICIDA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🌿","price":0},
        {"id":"120","name":"JUEGO DE 11 LLAVES COMBINADAS","category":"MANTENIMIENTO","unit":"JUEGO","img":"🔧","price":0},
        {"id":"121","name":"JUEGO DE 22 LLAVES COMBINADAS","category":"MANTENIMIENTO","unit":"JUEGO","img":"🔧","price":0},
        {"id":"122","name":"JUEGO DE HERRAMIENTAS","category":"MANTENIMIENTO","unit":"JUEGO","img":"🔧","price":0},
        {"id":"123","name":"LUMINARIAS","category":"MANTENIMIENTO","unit":"PIEZA","img":"💡","price":0},
        {"id":"124","name":"MÁQUINA TERMO CON CABLE","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"125","name":"MARTILLO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔨","price":0},
        {"id":"126","name":"MINI ROLLIDOS","category":"MANTENIMIENTO","unit":"PIEZA","img":"🖌️","price":0},
        {"id":"127","name":"MINIPULIDORA PORTÁTIL SIN PILA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"128","name":"PAPEL PARA TABLA PARA TABLAROCA","category":"MANTENIMIENTO","unit":"PIEZA","img":"📄","price":0},
        {"id":"129","name":"PEGAMENTO PARA PVC","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"130","name":"PEGAMENTO RESISTOL","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"131","name":"PEGAMENTO UNIVERSAL","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"132","name":"LLAVE PERICO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"133","name":"PINTURA ACRÍLICA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🖌️","price":0},
        {"id":"134","name":"PINTURA ACRÍLICA BLANCA","category":"MANTENIMIENTO","unit":"CUBETA","img":"🪣","price":0},
        {"id":"135","name":"PINTURA ACRÍLICA COLOR BLANCO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🖌️","price":0},
        {"id":"136","name":"PINTURA COLOR GRIS","category":"MANTENIMIENTO","unit":"PIEZA","img":"🖌️","price":0},
        {"id":"137","name":"PINTURA ESMALTE","category":"MANTENIMIENTO","unit":"PIEZA","img":"🖌️","price":0},
        {"id":"138","name":"PINTURA PARA PIZARRÓN","category":"MANTENIMIENTO","unit":"PIEZA","img":"🖌️","price":0},
        {"id":"139","name":"PINZA PELACABLE","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"140","name":"PINZAS DE ELECTRICISTAS PEQUEÑAS","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"141","name":"PINZAS DE PRESIÓN","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"142","name":"PINZAS DE PUNTA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"143","name":"RATONERAS","category":"MANTENIMIENTO","unit":"PIEZA","img":"🐭","price":0},
        {"id":"144","name":"RESANADOR","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"145","name":"RESISTOL 5000","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"146","name":"RIDE","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"147","name":"TALADRO DE MEDIA INALÁMBRICO","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"148","name":"TAPETE PARA COLADERA","category":"MANTENIMIENTO","unit":"PIEZA","img":"🔧","price":0},
        {"id":"149","name":"ZOCLO","category":"MANTENIMIENTO","unit":"PAQUETE","img":"🔧","price":0},
        {"id":"150","name":"ACEITE PARA MOP","category":"PAPELERÍA","unit":"PIEZA","img":"🧴","price":0},
        {"id":"151","name":"ACETATOS","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"152","name":"ADHESIVO ESCOLAR","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"153","name":"ARCHIVERO METÁLICO 4 CAJONES","category":"PAPELERÍA","unit":"PIEZA","img":"🗂️","price":0},
        {"id":"154","name":"BÁNDOLA CON SEGURO","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"155","name":"BITÁCORA","category":"PAPELERÍA","unit":"PIEZA","img":"📓","price":0},
        {"id":"156","name":"BLOCK DE COMPROBANTE DE GASTOS","category":"PAPELERÍA","unit":"PIEZA","img":"📒","price":0},
        {"id":"157","name":"BLOCK DE NOTAS ADHESIVAS 7.62X10.2 CM","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"158","name":"BLOCK DE NOTAS 7.62X7.62 CM","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"159","name":"BLOCK DE NOTAS DE SALIDA","category":"PAPELERÍA","unit":"PIEZA","img":"📒","price":0},
        {"id":"160","name":"BLOCK DE VALE PROVISIONAL","category":"PAPELERÍA","unit":"PIEZA","img":"📒","price":0},
        {"id":"161","name":"BOLÍGRAFO AZUL","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"162","name":"BOLÍGRAFO NEGRO","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"163","name":"BOLÍGRAFO ROJO","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"164","name":"BOLÍGRAFO VERDE","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"165","name":"BROCHE LAMINADO","category":"PAPELERÍA","unit":"PAQUETE","img":"📎","price":0},
        {"id":"166","name":"BROCHE METÁLICO PARA ARCHIVO","category":"PAPELERÍA","unit":"PAQUETE","img":"📎","price":0},
        {"id":"167","name":"CARPETA PANORÁMICA T. CARTA 1","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"168","name":"CARPETA PANORÁMICA T. CARTA 2","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"169","name":"CARPETA PANORÁMICA T. CARTA 3","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"170","name":"CARPETA PANORÁMICA T. CARTA 4","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"171","name":"CHAROLA PAPELERA ORGANIZADORA 3 NIVELES","category":"PAPELERÍA","unit":"PIEZA","img":"🗂️","price":0},
        {"id":"172","name":"CHINCHETAS","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"173","name":"CHUPONES","category":"PAPELERÍA","unit":"PIEZA","img":"📌","price":0},
        {"id":"174","name":"CINTA ADHESIVA 110","category":"PAPELERÍA","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"175","name":"CINTA ADHESIVA 119","category":"PAPELERÍA","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"176","name":"CINTA ADHESIVA 48MM X 150 MTS","category":"PAPELERÍA","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"177","name":"CINTA ADHESIVA CORTE FÁCIL 12MM X 10 MTS","category":"PAPELERÍA","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"178","name":"CINTA ADHESIVA CORTE FÁCIL 12MM X 33 MTS","category":"PAPELERÍA","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"179","name":"CINTA CORRECTORA","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"180","name":"CINTA MASKING 18MM X 54.8 MTS","category":"PAPELERÍA","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"181","name":"CLIP MARIPOSA NO.1","category":"PAPELERÍA","unit":"PAQUETE","img":"📎","price":0},
        {"id":"182","name":"CLIP MARIPOSA NO.2","category":"PAPELERÍA","unit":"PAQUETE","img":"📎","price":0},
        {"id":"183","name":"CLIP NO. 2 RECTANGULAR","category":"PAPELERÍA","unit":"PAQUETE","img":"📎","price":0},
        {"id":"184","name":"CLIPS NO. 1","category":"PAPELERÍA","unit":"PAQUETE","img":"📎","price":0},
        {"id":"185","name":"CLIPS NO. 2","category":"PAPELERÍA","unit":"PAQUETE","img":"📎","price":0},
        {"id":"186","name":"CORRECTOR LÍQUIDO","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"187","name":"CORTA CINTAS","category":"PAPELERÍA","unit":"PIEZA","img":"✂️","price":0},
        {"id":"188","name":"NOTAS ADHESIVAS 51MM X 51MM","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"189","name":"NOTAS ADHESIVAS 76MM X 76MM","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"190","name":"DEDAL","category":"PAPELERÍA","unit":"PIEZA","img":"📌","price":0},
        {"id":"191","name":"DESENGRAPADORA","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"192","name":"DESHEBRADOR","category":"PAPELERÍA","unit":"PIEZA","img":"✂️","price":0},
        {"id":"193","name":"DESPACHADOR DE CINTA","category":"PAPELERÍA","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"194","name":"DIRECTORIO","category":"PAPELERÍA","unit":"PIEZA","img":"📒","price":0},
        {"id":"195","name":"ENGRAPADORA","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"196","name":"ENTINTADOR DE COJINES 600ML","category":"PAPELERÍA","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"197","name":"ETIQUETAS ADHESIVAS REDONDAS COLORES 19MM","category":"PAPELERÍA","unit":"PIEZA","img":"📌","price":0},
        {"id":"198","name":"FOLDER CARTA","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"199","name":"FOLDER COLGANTE AMARILLO","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"200","name":"FOLDER COLGANTE VERDE","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"201","name":"FOLDER COLGANTE AZUL","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"202","name":"FOLDER DE PLÁSTICO","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"203","name":"FOLDER OFICIO","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"204","name":"FOLDER PARA ARCHIVO EXPANDIBLE","category":"PAPELERÍA","unit":"PIEZA","img":"📁","price":0},
        {"id":"205","name":"GOMA","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"206","name":"GRAPAS","category":"PAPELERÍA","unit":"PAQUETE","img":"📎","price":0},
        {"id":"207","name":"HOJA DE COLOR AMARILLO","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"208","name":"HOJA DE COLOR NARANJA","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"209","name":"HOJA DE COLOR ROSA","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"210","name":"HOJA DE COLOR VERDE","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"211","name":"HOJAS CARTA BLANCAS","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"212","name":"HOJAS OFICIO BLANCAS","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"213","name":"LÁPIZ","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"214","name":"LÁPIZ ADHESIVO","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"215","name":"LÁPIZ CORRECTOR","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"216","name":"LIBRETA FORMA FRANCESA CUADRO GRANDE","category":"PAPELERÍA","unit":"PIEZA","img":"📓","price":0},
        {"id":"217","name":"LIGAS DE HULE NO. 12","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"218","name":"LIGAS DE HULE NO. 18","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"219","name":"LIGAS DE HULE NO. 64","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"220","name":"MARCADOR BASE DE AGUA","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"221","name":"MARCADOR DE CERA","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"222","name":"MARCADOR PARA VIDRIO","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"223","name":"MARCADOR PERMANENTE","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"224","name":"MARCADORES PARA PIZARRÓN VARIOS COLORES","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"225","name":"MARCATEXTOS VERDE","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"226","name":"MARCATEXTOS AMARILLO","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"227","name":"MARCATEXTOS NARANJA","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"228","name":"MICA TÉRMICA","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"229","name":"MULTIMICAS CON VENTANA","category":"PAPELERÍA","unit":"PIEZA","img":"📄","price":0},
        {"id":"230","name":"NOTAS ADHESIVAS ÍNDICE","category":"PAPELERÍA","unit":"PAQUETE","img":"📌","price":0},
        {"id":"231","name":"ORGANITODO","category":"PAPELERÍA","unit":"PIEZA","img":"🗂️","price":0},
        {"id":"232","name":"ORGANIZADOR DE MALLA METÁLICA","category":"PAPELERÍA","unit":"PIEZA","img":"🗂️","price":0},
        {"id":"233","name":"ORGANIZADOR DE TARJETAS","category":"PAPELERÍA","unit":"PIEZA","img":"🗂️","price":0},
        {"id":"234","name":"ORGANIZADOR PORTALÁPICES","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"235","name":"PAPEL CARBÓN","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"236","name":"PAPEL DE SEGURIDAD","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"237","name":"PAPEL OPALINA","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"238","name":"PAQUETE CON 100 PROTECTORES DE HOJAS","category":"PAPELERÍA","unit":"PAQUETE","img":"📄","price":0},
        {"id":"239","name":"PAQUETE DE CINTA INVISIBLE 18MM X 33MM","category":"PAPELERÍA","unit":"PIEZA","img":"🎞️","price":0},
        {"id":"240","name":"PERFORADORA","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"241","name":"PISTOLAS PARA SILICÓN","category":"PAPELERÍA","unit":"PIEZA","img":"🔧","price":0},
        {"id":"242","name":"PIZARRÓN DE CORCHO 40X60CM","category":"PAPELERÍA","unit":"PIEZA","img":"📋","price":0},
        {"id":"243","name":"PLUMÓN SHARPIE PAQ 4 PZAS COLORES","category":"PAPELERÍA","unit":"PIEZA","img":"🖊️","price":0},
        {"id":"244","name":"PORTACLIPS MAGNÉTICO","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"245","name":"PUNTILLAS DE GRAFITO","category":"PAPELERÍA","unit":"PAQUETE","img":"✏️","price":0},
        {"id":"246","name":"REGLA","category":"PAPELERÍA","unit":"PIEZA","img":"📏","price":0},
        {"id":"247","name":"SACAGRAPAS","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"248","name":"SACAPUNTAS","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"249","name":"SACAPUNTAS ELÉCTRICO","category":"PAPELERÍA","unit":"PIEZA","img":"✏️","price":0},
        {"id":"250","name":"SEPARADOR ALFABÉTICO","category":"PAPELERÍA","unit":"PIEZA","img":"📄","price":0},
        {"id":"251","name":"SEPARADOR DE HOJAS TAMAÑO CARTA","category":"PAPELERÍA","unit":"PIEZA","img":"📄","price":0},
        {"id":"252","name":"SEPARADOR POR COLOR","category":"PAPELERÍA","unit":"PIEZA","img":"📄","price":0},
        {"id":"253","name":"SEPARADOR POR ORDEN NUMÉRICO","category":"PAPELERÍA","unit":"PIEZA","img":"📄","price":0},
        {"id":"254","name":"SOBRES MONEDA","category":"PAPELERÍA","unit":"PIEZA","img":"✉️","price":0},
        {"id":"255","name":"SOBRES PARA ARCHIVOS","category":"PAPELERÍA","unit":"PIEZA","img":"✉️","price":0},
        {"id":"256","name":"SUJETA DOCUMENTO 15 MM","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"257","name":"SUJETA DOCUMENTO 19 MM","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"258","name":"SUJETA DOCUMENTO 32 MM","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"259","name":"SUJETA DOCUMENTO 41 MM","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"260","name":"SUJETA DOCUMENTOS 51 MM","category":"PAPELERÍA","unit":"PIEZA","img":"📎","price":0},
        {"id":"261","name":"TABLA PARA SUJETAR DOCUMENTOS","category":"PAPELERÍA","unit":"PIEZA","img":"📋","price":0},
        {"id":"262","name":"TARJETERO","category":"PAPELERÍA","unit":"PIEZA","img":"🗂️","price":0},
        {"id":"263","name":"TIJERAS","category":"PAPELERÍA","unit":"PIEZA","img":"✂️","price":0},
        {"id":"264","name":"TINTA PARA SELLO","category":"PAPELERÍA","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"265","name":"TINTA PROTECTORA","category":"PAPELERÍA","unit":"PIEZA","img":"🖨️","price":0},
        {"id":"266","name":"VALE DE HOJAS","category":"PAPELERÍA","unit":"PIEZA","img":"📄","price":0},
    ]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"requisitions": [], "catalog": get_default_catalog(), "spent": {}}

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
    @app.route("/subir_imagen", methods=["POST"])
def subir_imagen():
    if session.get("role") != "compras":
        return jsonify({"ok": False})
    if "imagen" not in request.files:
        return jsonify({"ok": False, "error": "No se recibió imagen"})
    file = request.files["imagen"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "No se seleccionó archivo"})
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp", "gif"]:
        return jsonify({"ok": False, "error": "Formato no permitido"})
    filename = f"prod_{datetime.now().strftime('%y%m%d%H%M%S')}.{ext}"
    file.save(os.path.join("static", filename))
    return jsonify({"ok": True, "url": f"/static/{filename}"})

if __name__ == "__main__":
    app.run(debug=True)