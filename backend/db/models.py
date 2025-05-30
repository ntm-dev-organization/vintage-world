from sqlalchemy import Column, Integer, String, Float, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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