"""HTTP surface for batch ingestion.

This layer only translates between HTTP and the service layer: it parses the
request, calls a service, and maps domain exceptions onto status codes. It
builds no queries.
"""
import pika
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.ingestion import service
from app.ingestion.schemas import BatchRequest, BatchResponse
from app.stores.service import UnknownStoreError
from app.stores import service as stores_service  # Importamos el servicio de tiendas para la validación

router = APIRouter(prefix="/sales", tags=["ingestion"])



@router.post("/batch", response_model=BatchResponse)
def ingest_batch(
    batch: BatchRequest,
    session: Session = Depends(get_session),
) -> BatchResponse:
    # 1. Validar la existencia de la tienda y la integridad del lote antes de encolar
    try:
        stores_service.require_store(session, batch.store_id)
        service.validate_batch(batch)
    except UnknownStoreError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error
    except service.InvalidBatchError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)
        ) from error

    # 2. Conectar a RabbitMQ y encolar el lote de facturas
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue='facturas')

    # Serializar el modelo de Pydantic a JSON
    # Se usa .model_dump_json() en Pydantic V2, o .json() en V1.
    mensaje = batch.json() if hasattr(batch, 'json') else batch.model_dump_json()

    # Publicar en la cola
    channel.basic_publish(
        exchange='',
        routing_key='facturas',
        body=mensaje
    )
    connection.close()

    # 3. Retornar una respuesta asíncrona. 
    # Como la inserción ocurre en segundo plano, asumimos temporalmente que todas son aceptadas.
    invoice_ids = [inv.store_invoice_id for inv in batch.invoices]
    
    return BatchResponse(
        store_id=batch.store_id,
        accepted=invoice_ids,
        duplicates=[],
        accepted_count=len(invoice_ids),
        duplicate_count=0,
    )