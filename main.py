from fastapi import FastAPI
from router.router import user  # Importa el router desde router.router

app = FastAPI(
    title="API de Invitados",
    description="API para gestionar invitados y sus acompañantes",
    version="1.0.0",
)

# Incluye el router con un prefijo y etiquetas
app.include_router(user, prefix="/api/v1", tags=["guests"])



