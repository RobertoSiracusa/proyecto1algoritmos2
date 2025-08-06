import sys
import os

# Agregar el directorio padre al path para importar las estructuras de datos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataEstructures.queue import Queue


class Interface:
    """Clase que representa una interfaz de red"""
    
    def __init__(self, name, ipAddress="", macAddress="", status="down"):
        self.name = name  # e.g., "g0/0", "eth0"
        self.ipAddress = ipAddress  # Dirección IP simulada
        self.macAddress = macAddress  # Dirección MAC
        self.status = status  # "up"/"down" o "shutdown"/"no shutdown"
        self.connectedTo = None  # Referencia a otra interfaz
        self.outgoingQueue = Queue()  # Cola de paquetes salientes
    
    def assignIpAddress(self, ip):
        """Asigna una dirección IP simulada"""
        self.ipAddress = ip
        print(f"Interface {self.name}: IP address asignada - {ip}")
    
    def setIpAddress(self, ipAddress):
        """Establece la dirección IP de la interfaz (método compatible con versión anterior)"""
        self.assignIpAddress(ipAddress)
    
    def setMacAddress(self, macAddress):
        """Establece la dirección MAC de la interfaz"""
        self.macAddress = macAddress
        print(f"Interface {self.name}: MAC address asignada - {macAddress}")
    
    def setStatus(self, status):
        """Activa/desactiva la interfaz ("shutdown"/"no shutdown" o "up"/"down")"""
        valid_statuses = ["up", "down", "shutdown", "no shutdown"]
        if status in valid_statuses:
            old_status = self.status
            self.status = status
            print(f"Interface {self.name}: Estado cambiado de '{old_status}' a '{status}'")
        else:
            print(f"Error: Estado '{status}' no válido. Opciones: {valid_statuses}")
    
    def connect(self, otherInterface):
        """Establece una conexión física con otra interfaz"""
        if self.connectedTo is not None:
            print(f"Warning: Interface {self.name} ya está conectada a {self.connectedTo.name}")
            return False
        
        if otherInterface.connectedTo is not None:
            print(f"Warning: Interface {otherInterface.name} ya está conectada a {otherInterface.connectedTo.name}")
            return False
        
        # Establecer conexión bidireccional
        self.connectedTo = otherInterface
        otherInterface.connectedTo = self
        
        print(f"Conexión establecida: {self.name} <--> {otherInterface.name}")
        return True
    
    def disconnect(self):
        """Rompe la conexión física"""
        if self.connectedTo is not None:
            otherInterface = self.connectedTo
            
            # Romper conexión bidireccional
            self.connectedTo = None
            otherInterface.connectedTo = None
            
            print(f"Conexión removida: {self.name} -X- {otherInterface.name}")
        else:
            print(f"Interface {self.name} no está conectada")
    
    def addPacketToQueue(self, packet):
        """Agrega un paquete a la cola de salida de la interfaz"""
        if not self.isUp():
            print(f"Warning: No se puede agregar paquete. Interface {self.name} está inactiva")
            return False
        
        if not self.isConnected():
            print(f"Warning: No se puede agregar paquete. Interface {self.name} no está conectada")
            return False
        
        self.outgoingQueue.enqueue(packet)
        print(f"Interface {self.name}: Paquete agregado a cola de salida - {packet}")
        return True
    
    def processOutgoingQueue(self):
        """Procesa la cola de salida de la interfaz"""
        processedPackets = []
        
        if not self.isUp() or not self.isConnected():
            return processedPackets
        
        while not self.outgoingQueue.is_empty():
            packet = self.outgoingQueue.dequeue()
            processedPackets.append(packet)
            
            # Simular envío a la interfaz conectada
            connectedInterface = self.connectedTo
            if connectedInterface and connectedInterface.isUp():
                print(f"Interface {self.name} --> {connectedInterface.name}: {packet}")
            else:
                print(f"Warning: Paquete perdido - interfaz destino {connectedInterface.name if connectedInterface else 'None'} no disponible")
        
        return processedPackets
    
    def isUp(self):
        """Verifica si la interfaz está activa"""
        return self.status in ["up", "no shutdown"]
    
    def isDown(self):
        """Verifica si la interfaz está inactiva"""
        return self.status in ["down", "shutdown"]
    
    def isConnected(self):
        """Verifica si la interfaz está conectada a otra"""
        return self.connectedTo is not None
    
    # ===== NUEVO: Módulo 6 Configuration Persistence - Métodos de serialización =====
    
    def to_dict(self):
        """
        Serializa la interfaz a un diccionario para guardado JSON
        
        Returns:
            dict: Representación serializable de la interfaz
        """
        interface_dict = {
            'name': self.name,
            'ipAddress': self.ipAddress,
            'macAddress': self.macAddress,
            'status': self.status,
            'connectedTo': None  # Se manejará durante la reconstrucción de conexiones
        }
        
        # Guardar referencia a interfaz conectada (solo el nombre, no la referencia completa)
        if self.connectedTo:
            # Esto se resolverá durante la carga usando el mapeo global de interfaces
            interface_dict['connectedTo'] = {
                'name': self.connectedTo.name,
                'device': None  # Se completará durante la reconstrucción
            }
        
        # Serializar cola de salida (opcional, solo strings)
        queue_items = []
        if not self.outgoingQueue.is_empty():
            for item in self.outgoingQueue:
                if isinstance(item, str):
                    queue_items.append(item)
                else:
                    queue_items.append(str(item))
        
        interface_dict['outgoing_queue'] = queue_items
        
        return interface_dict
    
    @classmethod  
    def from_dict(cls, interface_dict):
        """
        Crea una interfaz desde un diccionario deserializado
        
        Args:
            interface_dict: Diccionario con datos de la interfaz
            
        Returns:
            Interface: Nueva instancia de la interfaz
        """
        # Crear interfaz
        interface = cls(
            name=interface_dict['name'],
            ipAddress=interface_dict.get('ipAddress', ''),
            macAddress=interface_dict.get('macAddress', ''),
            status=interface_dict.get('status', 'down')
        )
        
        # Restaurar cola de salida
        if 'outgoing_queue' in interface_dict:
            for item_str in interface_dict['outgoing_queue']:
                interface.outgoingQueue.enqueue(item_str)
        
        # Las conexiones se restaurarán después en un paso separado
        return interface
    
    def get_connection_info(self):
        """
        Retorna información de conexión para serialización
        
        Returns:
            dict: Información de la conexión o None si no está conectada
        """
        if not self.isConnected():
            return None
        
        return {
            'interface_name': self.connectedTo.name,
            'interface_ip': self.connectedTo.ipAddress,
            'interface_status': self.connectedTo.status
        }
    
    def __str__(self):
        connection_info = ""
        if self.isConnected():
            connection_info = f" <-> {self.connectedTo.name}"
        
        ip_info = f" [{self.ipAddress}]" if self.ipAddress else ""
        mac_info = f" MAC:{self.macAddress}" if self.macAddress else ""
        
        return f"{self.name}{ip_info}{mac_info} ({self.status}){connection_info}" 