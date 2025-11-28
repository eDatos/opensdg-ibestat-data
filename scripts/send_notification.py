import sys
from edatos.services.notices import NoticesClient, buildNotice
from edatos.utils.logging import getLogger

logger = getLogger("send_notification")

if __name__ == '__main__':

    if len(sys.argv) < 2:
            print("Uso: poetry run python send_notification.py <archivo_texto>")
            sys.exit(1)

    archivo = sys.argv[1]

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
    except Exception as e:
        logger.error(f"Error al leer el archivo '{archivo}': {e}")
        sys.exit(1)


    client = NoticesClient('https://estadisticas.arte-consultores.com/notices-internal/apis/notices-internal/v1.0')   
    notice = buildNotice(contenido)
    
    try:
        response = client.create_notice(notice)
        logger.info(f"Notificación creada exitosamente. Status: {response.status_code}")
        logger.info(f"Respuesta: {response.text}")
    except Exception as e:
        logger.error(f"Error al crear notificación: {e}")