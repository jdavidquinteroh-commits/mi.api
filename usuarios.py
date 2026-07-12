from database import SessionLocal, Usuario
from auth import hashear_password

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def crear_usuario(db, username, email, password):
    usuario = Usuario(
        username=username,
        email=email,
        password_hash=hashear_password(password)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def obtener_usuario(db, username):
    return db.query(Usuario).filter(Usuario.username == username).first()