import requests
from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import xml.etree.ElementTree as ET


@dataclass
class Message:
    text: str
    resources: Optional[List] = None


@dataclass
class Receiver:
    username: str


@dataclass
class Role:
    name: str


@dataclass
class Application:
    name: str


@dataclass
class StatisticalOperation:
    urn: str


@dataclass
class Notice:
    notice_type: str  # NOTIFICATION o ANNOUNCEMENT
    sending_application: str
    subject: str
    messages: List[Message]
    footer: Message
    sending_user: Optional[str] = None
    sending_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    roles: Optional[List[Role]] = None
    applications: Optional[List[Application]] = None
    statistical_operations: Optional[List[StatisticalOperation]] = None
    receivers: Optional[List[Receiver]] = None
    force_send: Optional[bool] = None


class NoticesClient:
    """Cliente para interactuar con la API REST de Notices"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Inicializa el cliente de Notices.
        
        Args:
            base_url: URL base de la API (ej: 'http://api.example.com')
            timeout: Timeout para las peticiones en segundos
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/xml',
            'Accept': 'application/xml'
        })
    
    def _build_notice_xml(self, notice: Notice) -> str:
        """Construye el XML para la notificación"""
        root = ET.Element('notice', {
            'xmlns': 'http://www.siemac.org/metamac/rest/notices/v1.0/domain',
            'kind': 'notice'
        })
        
        # Elementos obligatorios
        ET.SubElement(root, 'noticeType').text = notice.notice_type
        ET.SubElement(root, 'sendingApplication').text = notice.sending_application
        ET.SubElement(root, 'subject').text = notice.subject
        
        # Mensajes
        messages_elem = ET.SubElement(root, 'messages', {'total': str(len(notice.messages))})
        for msg in notice.messages:
            msg_elem = ET.SubElement(messages_elem, 'message')
            ET.SubElement(msg_elem, 'text').text = msg.text
        
        # Footer
        footer_elem = ET.SubElement(root, 'footer')
        ET.SubElement(footer_elem, 'text').text = notice.footer.text
        
        # Elementos opcionales
        if notice.sending_user:
            ET.SubElement(root, 'sendingUser').text = notice.sending_user
        
        if notice.sending_date:
            ET.SubElement(root, 'sendingDate').text = notice.sending_date.isoformat()
        
        if notice.expiration_date:
            ET.SubElement(root, 'expirationDate').text = notice.expiration_date.isoformat()
        
        if notice.roles:
            roles_elem = ET.SubElement(root, 'roles', {'total': str(len(notice.roles))})
            for role in notice.roles:
                role_elem = ET.SubElement(roles_elem, 'role')
                ET.SubElement(role_elem, 'name').text = role.name
        
        if notice.applications:
            apps_elem = ET.SubElement(root, 'applications', {'total': str(len(notice.applications))})
            for app in notice.applications:
                app_elem = ET.SubElement(apps_elem, 'application')
                ET.SubElement(app_elem, 'name').text = app.name
        
        if notice.statistical_operations:
            ops_elem = ET.SubElement(root, 'statisticalOperations', 
                                    {'total': str(len(notice.statistical_operations))})
            for op in notice.statistical_operations:
                op_elem = ET.SubElement(ops_elem, 'statisticalOperation')
                ET.SubElement(op_elem, 'urn').text = op.urn
        
        if notice.receivers:
            receivers_elem = ET.SubElement(root, 'receivers', {'total': str(len(notice.receivers))})
            for receiver in notice.receivers:
                receiver_elem = ET.SubElement(receivers_elem, 'receiver')
                ET.SubElement(receiver_elem, 'username').text = receiver.username
        
        if notice.force_send is not None:
            ET.SubElement(root, 'forceSend').text = str(notice.force_send).lower()
        
        return ET.tostring(root, encoding='unicode', method='xml')
    
    def create_notice(self, notice: Notice) -> requests.Response:
        """
        Crea una nueva notificación.
        
        Args:
            notice: Objeto Notice con los datos de la notificación
            
        Returns:
            Response object de requests con la respuesta del servidor
            
        Raises:
            requests.exceptions.RequestException: Si hay error en la petición
        """
        url = f"{self.base_url}/notices"
        xml_data = self._build_notice_xml(notice)
        
        response = self.session.put(
            url,
            data=xml_data.encode('utf-8'),
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response

def buildNotice(message_text: str) -> Notice:
    notice = Notice(
        notice_type='NOTIFICATION',
        sending_application='OBJETIVOS_DESARROLLO_SOSTENIBLE',
        subject='Resultado procesado indicadores desarrollo sostenible',
        messages=[
            Message(text=message_text)    
        ],
        footer=Message(text=''),
        sending_user='admin',
        applications=[
            Application(name='OBJETIVOS_DESARROLLO_SOSTENIBLE')
        ],
        roles=[Role(name='ADMINISTRADOR')],
        force_send=True
    )
    return notice