from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a mi primera API"}

@app.get("/saludo/{nombre}")
def saludar(nombre: str):
    return {"mensaje": f"Hola {nombre}, bienvenido a FastAPI"}

productos = [
    {"id": 1, "nombre": "Asado al barril", "precio": 35000},
    {"id": 2, "nombre": "Tacos de birria", "precio": 15000},
    {"id": 3, "nombre": "Costillas BBQ", "precio": 28000}
]

@app.get("/productos")
def ver_productos():
    return {"productos": productos}

@app.get("/productos/{id}")
def ver_producto(id: int):
    for producto in productos:
        if producto["id"] == id:
            return {"producto": producto}
    return {"error": "Producto no encontrado"}    
from fastapi import FastAPI
from pydantic import BaseModel

class Producto(BaseModel):
    nombre: str
    precio: int

@app.post("/productos")
def crear_producto(producto: Producto):
    nuevo = {
        "id": len(productos) + 1,
        "nombre": producto.nombre,
        "precio": producto.precio
    }
    productos.append(nuevo)
    return {"mensaje": "Producto creado", "producto": nuevo}    