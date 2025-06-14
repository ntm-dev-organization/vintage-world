from sqlalchemy import Column, Integer, String, Float, ARRAY, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    sizes = Column(ARRAY(String))
    category = Column(String)
    stripe_num = Column(String)
    stock = Column(Integer)
    principal = Column(String)
    secundarias = Column(ARRAY(String))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "sizes": self.sizes,
            "category": self.category,
            "stripe_num": self.stripe_num,
            "stock": self.stock,
            "principal": self.principal,
            "secundarias": self.secundarias
        }


class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<Status(id={self.id}, name='{self.name}')>"

class LojaEstado(Base):
    __tablename__ = "loja_estado"

    id = Column(Integer, primary_key=True)
    status_id = Column(Integer, ForeignKey("status.id"), nullable=False)

    status = relationship("Status")

    def __repr__(self):
        return f"<LojaEstado(id={self.id}, status={self.status.name})>"
    

class CarrosselImagem(Base):
    __tablename__ = "carrossel_imagens"
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    filename = Column(String, nullable=False)