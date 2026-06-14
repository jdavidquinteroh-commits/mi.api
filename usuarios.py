from sqlalchemy import Column, Integer, String
from database import Base, engine, SessionLocal
from auth import hashear_password

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

Base.metadata.create_all(bind=engine)

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