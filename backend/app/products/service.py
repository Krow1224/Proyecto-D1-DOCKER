"""Catalog business logic.

This layer knows nothing about HTTP: it takes plain values, raises plain
exceptions and returns plain objects, which is what makes it unit testable
without starting a server.
"""

from sqlalchemy.orm import Session

from app.products import repository
from app.core.rediscache import redis_client, CACHE_TTL
from app.products.models import Product
from app.products import schemas
import json

class ProductNotFoundError(Exception):
    """No product carries the requested barcode."""

    def __init__(self, ean: str) -> None:
        super().__init__(f"No product found for EAN {ean}")
        self.ean = ean


def get_product(session: Session, ean: str) -> schemas.ProductResponse:
    """Return the product for this barcode, or raise ProductNotFoundError."""

    #obtener datos de Redis
    product_cache= redis_client.get(str(ean))

    #si está en el cache de redis
    if product_cache:
        print(f"se obtuvo el producto {ean} en Redis", flush = True)
        product_data= json.loads(product_cache)
        return schemas.ProductResponse(
            ean= ean,
            name = product_data["name"],
            price= float(product_data["price"])
            
        )
        #por qué no se usa return schemas.ProductResponse.model_validate_json(product_cache) en lugar del json.loads manual?

    #ya se comunica aquí con base de datos si no está en redis
    print(f"no se obtuvo el producto {ean} de redis, procede a sonsultar a postgreSQL", flush= True)
    product = repository.find_product_by_ean(session, ean)
    if product is None:
        print(f"el producto {ean} no existe en la db", flush=True)
        raise ProductNotFoundError(ean)

    #guardar en redis para otras consulatas
    product_dict = {
        "name" : str(product.name),
        "price": float(product.price)
    }

    redis_client.setex(str(ean), CACHE_TTL, json.dumps(product_dict, default=str) )
    print(f"el producto {ean} se guardó en el cache", flush= True)
    return schemas.ProductResponse(
        ean=ean,
        name=product.name,
        price=float(product.price)
    )


def get_products_by_eans(session: Session, eans: list[str]) -> dict[str, Product]:
    """Return the requested products keyed by EAN, omitting unknown ones.

    The payment package prices a cart through this rather than reaching into
    the catalog's repository, so package talks to package at the service
    level.
    """
    return repository.find_products_by_eans(session, eans)
