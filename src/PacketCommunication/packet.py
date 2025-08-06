import uuid
import sys
import os

# Agregar el directorio padre al path para importar DataEstructures
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DataEstructures import LinkedList


class Packet:
    """Clase que representa un paquete de red"""
    
    def __init__(self, sourceIp, destinationIp, content, ttl=64):
        self.id = str(uuid.uuid4())[:8]  # Identificador único (8 caracteres)
        self.sourceIp = sourceIp
        self.destinationIp = destinationIp
        self.content = content
        self.ttl = ttl  # Time To Live
        self.pathTrace = LinkedList()  # Lista enlazada de nodos traversados
        self.hops = 0  # Contador de saltos
        self.status = "active"  # "active", "delivered", "expired", "dropped"
    
    def decrementTtl(self):
        """Decrementa TTL y retorna True si el paquete sigue siendo válido"""
        self.ttl -= 1
        if self.ttl <= 0:
            self.status = "expired"
            return False
        return True
    
    def addToTrace(self, deviceName):
        """Agrega el dispositivo actual al rastro del path"""
        self.pathTrace.add_node(deviceName)
        self.hops += 1
        print(f"Packet {self.id}: Passed through {deviceName} (Hop {self.hops}, TTL={self.ttl})")
    
    def markDelivered(self):
        """Marca el paquete como entregado exitosamente"""
        self.status = "delivered"
        print(f"Packet {self.id}: DELIVERED to {self.destinationIp}")
    
    def markDropped(self, reason="Unknown"):
        """Marca el paquete como descartado"""
        self.status = "dropped"
        print(f"Packet {self.id}: DROPPED - {reason}")
    
    def getPathString(self):
        """Retorna el path como string legible"""
        if self.pathTrace.is_empty():
            return "No path traced"
        path_elements = self.pathTrace.traverse()
        return " -> ".join(path_elements)
    
    def isActive(self):
        """Verifica si el paquete está activo (no expirado ni entregado)"""
        return self.status == "active"
    
    def getInfo(self):
        """Retorna información completa del paquete"""
        return {
            'id': self.id,
            'sourceIp': self.sourceIp,
            'destinationIp': self.destinationIp,
            'content': self.content,
            'ttl': self.ttl,
            'hops': self.hops,
            'status': self.status,
            'pathTrace': self.pathTrace.traverse(),
            'pathString': self.getPathString()
        }
    
    def __str__(self):
        return f"Packet[{self.id}] {self.sourceIp}->{self.destinationIp} TTL={self.ttl} Status={self.status}"
    
    def __repr__(self):
        return f"Packet(id='{self.id}', src='{self.sourceIp}', dst='{self.destinationIp}', ttl={self.ttl})" 