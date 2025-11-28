from edatos.services.notices import NoticesClient, buildNotice

if __name__ == '__main__':

    client = NoticesClient('https://estadisticas.arte-consultores.com/notices-internal/apis/notices-internal/v1.0')   
    notice = buildNotice("holi")
    
    try:
        response = client.create_notice(notice)
        print(f"Notificación creada exitosamente. Status: {response.status_code}")
        print(f"Respuesta: {response.text}")
    except Exception as e:
        print(f"Error al crear notificación: {e}")