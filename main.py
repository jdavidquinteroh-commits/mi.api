from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, Producto, crear_tablas

app = FastAPI()

crear_tablas()

from pydantic import BaseModel, validator, Field

class ProductoSchema(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    precio: int = Field(..., gt=0)
    descripcion: str = Field(None, max_length=300)
    categoria: str = Field(None)

    @validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip().title()
        
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a mi API con base de datos"}

@app.get("/productos")
def ver_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return {"productos": productos}

@app.get("/productos/{id}")
def ver_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        return {"error": "Producto no encontrado"}
    return {"producto": producto}

@app.post("/productos")
def crear_producto(producto: ProductoSchema, db: Session = Depends(get_db)):
    nuevo = Producto(nombre=producto.nombre, precio=producto.precio)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Producto creado", "producto": nuevo}

@app.put("/productos/{id}")
def actualizar_producto(id: int, producto: ProductoSchema, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == id).first()
    if not p:
        return {"error": "Producto no encontrado"}
    p.nombre = producto.nombre
    p.precio = producto.precio
    db.commit()
    db.refresh(p)
    return {"mensaje": "Producto actualizado", "producto": p}

@app.delete("/productos/{id}")
def eliminar_producto(id: int, db: Session = Depends(get_db)):
    p = db.query(Producto).filter(Producto.id == id).first()
    if not p:
        return {"error": "Producto no encontrado"}
    db.delete(p)
    db.commit()
    return {"mensaje": f"Producto {id} eliminado"}