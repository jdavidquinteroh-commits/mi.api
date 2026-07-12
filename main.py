from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database import SessionLocal, Producto, crear_tablas
from auth import verificar_token, crear_token, verificar_password, hashear_password
from usuarios import crear_usuario, obtener_usuario, get_db

app = FastAPI(title="Barril And Grill API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
crear_tablas()

class ProductoSchema(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    precio: int = Field(..., gt=0)
    descripcion: str = None
    categoria: str = None

class UsuarioSchema(BaseModel):
    username: str
    email: str
    password: str

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a la API de Barril And Grill"}

@app.post("/registro")
def registro(usuario: UsuarioSchema, db: Session = Depends(get_db)):
    if obtener_usuario(db, usuario.username):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    nuevo = crear_usuario(db, usuario.username, usuario.email, usuario.password)
    return {"mensaje": "Usuario creado", "username": nuevo.username}

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = obtener_usuario(db, form.username)
    if not usuario or not verificar_password(form.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = crear_token({"sub": usuario.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/productos")
def ver_productos(
    categoria: str = None,
    buscar: str = None,
    db: Session = Depends(get_db),
    username: str = Depends(verificar_token)
):
    usuario = obtener_usuario(db, username)
    query = db.query(Producto).filter(Producto.usuario_id == usuario.id)
    
    if categoria:
        query = query.filter(Producto.categoria == categoria)
    if buscar:
        query = query.filter(Producto.nombre.contains(buscar))
    
    productos = query.all()
    return {"productos": productos, "total": len(productos)}

@app.get("/productos/{id}")
def ver_producto(id: int, db: Session = Depends(get_db), username: str = Depends(verificar_token)):
    usuario = obtener_usuario(db, username)
    producto = db.query(Producto).filter(Producto.id == id, Producto.usuario_id == usuario.id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"producto": producto}

@app.post("/productos")
def crear_producto(
    producto: ProductoSchema,
    db: Session = Depends(get_db),
    username: str = Depends(verificar_token)
):
    usuario = obtener_usuario(db, username)
    nuevo = Producto(
        nombre=producto.nombre,
        precio=producto.precio,
        descripcion=producto.descripcion,
        categoria=producto.categoria,
        usuario_id=usuario.id
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Producto creado", "producto": nuevo}

@app.put("/productos/{id}")
def actualizar_producto(
    id: int,
    producto: ProductoSchema,
    db: Session = Depends(get_db),
    usuario: str = Depends(verificar_token)
):
    p = db.query(Producto).filter(Producto.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    p.nombre = producto.nombre
    p.precio = producto.precio
    p.descripcion = producto.descripcion
    p.categoria = producto.categoria
    db.commit()
    db.refresh(p)
    return {"mensaje": "Producto actualizado", "producto": p}

@app.delete("/productos/{id}")
def eliminar_producto(
    id: int,
    db: Session = Depends(get_db),
    usuario: str = Depends(verificar_token)
):
    p = db.query(Producto).filter(Producto.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(p)
    db.commit()
    return {"mensaje": f"Producto {id} eliminado"}