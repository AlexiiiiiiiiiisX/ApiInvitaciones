from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Model de la tabla `guests`
class GuestDB(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guest_name = Column(String(100), nullable=False)
    confirmation = Column(Boolean, default=False)
    quotas = Column(Integer, nullable=False)

    # Relación con `accompanists`
    accompanists = relationship("AccompanistDB", back_populates="guest", cascade="all, delete-orphan")

# Model de la tabla `accompanists`
class AccompanistDB(Base):
    __tablename__ = "accompanists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    accompanist_name = Column(String(100), nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)

    # Relación con `guests`
    guest = relationship("GuestDB", back_populates="accompanists")