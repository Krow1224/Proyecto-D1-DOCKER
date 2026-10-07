"""Background worker to consume invoice batches from RabbitMQ."""
import json
import time
import pika
import logging

from app.ingestion.schemas import BatchRequest
from app.ingestion import service
from app.core.database import get_session

# Configuración básica de logs para la consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def callback(ch, method, properties, body):
    mensaje_str = body.decode()
    logger.info(f" [x] Lote recibido. Procesando inserción asíncrona...")
    
    try:
        # Convertir el string JSON nuevamente al modelo BatchRequest de Pydantic
        datos_facturas = json.loads(mensaje_str)
        batch = BatchRequest(**datos_facturas)
        
        # Obtener sesión de base de datos
        session_generator = get_session()
        db_session = next(session_generator)
        
        try:
            # Reutilizar tu lógica de negocio intacta para la inserción real
            result = service.ingest_batch(db_session, batch)
            logger.info(f" [v] Inserción finalizada: {len(result.accepted)} aceptadas, {len(result.duplicates)} duplicadas.")
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f" [!] Error procesando lote desde RabbitMQ: {e}")

def main():
    logger.info("Esperando a que RabbitMQ inicie (10s)...")
    time.sleep(10)
    
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq', credentials=credentials)
    )
    channel = connection.channel()

    # Asegurarnos de que la cola exista antes de consumir
    channel.queue_declare(queue='facturas')
    
    # Comenzar a consumir
    channel.basic_consume(queue='facturas', on_message_callback=callback, auto_ack=True)

    logger.info(' [*] Esperando mensajes en la cola "facturas". Para salir presiona CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()