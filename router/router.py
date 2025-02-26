from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import SessionLocal
from model.users import AccompanistDB, GuestDB
from schema.user_schema import Accompanist, AccompanistCreate, Guest, GuestCreate, GuestUpdate


# Aquí se crea un APIRouter con prefijo y etiquetas, osea las de guests -- invitadossss
user = APIRouter(prefix="/guests", tags=["guests"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para crear un invitado
@user.post("/", response_model=Guest)
def create_guest(guest: GuestCreate, db: Session = Depends(get_db)):
    db_guest = GuestDB(**guest.model_dump())
    db.add(db_guest)
    db.commit()
    db.refresh(db_guest)
    return db_guest

# Este endpoint obtiene un "invitado" al darle su id en la ruta
@user.get("/{guest_id}", response_model=Guest)
def read_guest(guest_id: int, db: Session = Depends(get_db)):
    db_guest = db.query(GuestDB).filter(GuestDB.id == guest_id).first()
    if db_guest is None:
        raise HTTPException(status_code=404, detail="Invitado no encontrado")
    return db_guest

# Este endpoint te muestra todos los invitados.
@user.get("/", response_model=list[Guest])
def read_all (db: Session = Depends(get_db)):
    db_guests = db.query(GuestDB).all()
    return db_guests

# Este endpoint añade un acompañante al invitado -- ocupa el id del invitado
@user.post("/{guest_id}/accompanists/", response_model=Guest)
def add_accompanist(guest_id: int, accompanist: AccompanistCreate, db: Session = Depends(get_db)):
    db_guest = db.query(GuestDB).filter(GuestDB.id == guest_id).first()
    if db_guest is None:
        raise HTTPException(status_code=404, detail="Invitado no encontrado")
    if len(db_guest.accompanists) >= db_guest.quotas:
        raise HTTPException(status_code=400, detail="No hay mas cupos disponibles")
    db_accompanist = AccompanistDB(**accompanist.dict(), guest_id=guest_id)
    db.add(db_accompanist)
    db.commit()
    db.refresh(db_guest)
    return db_guest

# Este endpoint me permite borrar un invitado, y por consecuencia del tipo de relacion, tambien se eliminaran los acompañantes.
@user.delete("/{guest_id}", response_model=dict)
def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    db_guest = db.query(GuestDB).filter(GuestDB.id == guest_id).first()
    if db_guest is None:
        raise HTTPException(status_code=404, detail="No se ha encontrado al invitado")
    
    db.delete(db_guest)
    db.commit()
    return {"mensaje": "El invitado se ha eliminado exitosamente."}


#Este endpoint eliminara a un acompañante en especifico --> dale un id :)
@user.delete("/{guest_id}/accompanists/{accompanist_id}", response_model=dict)
def delete_accompanist(guest_id: int, accompanist_id: int, db: Session = Depends(get_db)):
    db_accompanist = db.query(AccompanistDB).filter(
        AccompanistDB.id == accompanist_id,
        AccompanistDB.guest_id == guest_id
    ).first()
    
    if db_accompanist is None:
        raise HTTPException(status_code=404, detail="Acompañante no encontrado")
    
    db.delete(db_accompanist)
    db.commit()
    return {"mensaje": "El acompañante fue eliminado exitosamente"}


#Este enpoint de aca te permite actualizar el nombre de un colado, le tienes que proporcionar el id
@user.put("/{guest_id}/accompanists/{accompanist_id}", response_model=Accompanist)
def update_accompanist_name(guest_id: int, accompanist_id: int, accompanist_update: AccompanistCreate, db: Session = Depends(get_db)):
    db_accompanist = db.query(AccompanistDB).filter(
        AccompanistDB.id == accompanist_id,
        AccompanistDB.guest_id == guest_id
    ).first()
    
    if db_accompanist is None:
        raise HTTPException(status_code=404, detail="Accompanist not found")
    
    if accompanist_update.accompanist_name is not None:
        db_accompanist.accompanist_name = accompanist_update.accompanist_name
    
    db.commit()
    db.refresh(db_accompanist)
    return db_accompanist



# Este enpoint hace lo siguiente, puede actualizar los campos del invitado, y si de casualidad recuce su cupo, los acompañantes con los id de
# mayor valor se iran eliminando hasta no desbordar la cantidad de cupos. Si un invitado cancela su asistencia, los acompñates seran eliminados.

@user.patch("/{guest_id}", response_model=Guest)
def update_guest(guest_id: int, guest_update: GuestUpdate, db: Session = Depends(get_db)):
    db_guest = db.query(GuestDB).filter(GuestDB.id == guest_id).first()
    if db_guest is None:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    # Actualizar campos si se proporcionan
    if guest_update.guest_name is not None:
        db_guest.guest_name = guest_update.guest_name
    if guest_update.confirmation is not None:
        db_guest.confirmation = guest_update.confirmation
    if guest_update.quotas is not None:
        db_guest.quotas = guest_update.quotas
    
    # Eliminar acompañantes si el invitado cancela su asistencia
    if guest_update.confirmation is not None and guest_update.confirmation is False:
        for accompanist in db_guest.accompanists:
            db.delete(accompanist)
    
    # Eliminar acompañantes si se reducen los cupos
    if guest_update.quotas is not None and guest_update.quotas < len(db_guest.accompanists):
        # Ordenar acompañantes por id de mayor a menor
        accompanists_sorted = db.query(AccompanistDB).filter(
            AccompanistDB.guest_id == guest_id
        ).order_by(AccompanistDB.id.desc()).all()
        
        # Calcular cuántos acompañantes deben eliminarse
        num_to_delete = len(db_guest.accompanists) - guest_update.quotas
        
        # Eliminar los acompañantes con los id más altos
        for accompanist in accompanists_sorted[:num_to_delete]:
            db.delete(accompanist)
    
    db.commit()
    db.refresh(db_guest)
    return db_guest


# Todas las rutas (completas) las puedes encontrar en /docs que te permite usar swagger