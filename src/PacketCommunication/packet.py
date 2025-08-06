import uuid
from typing import List


class Packet:
    """Clase que representa un paquete de red"""
    
    def __init__(self, sourceIp: str, destinationIp: str, content: str, ttl: int = 64):
        self.id = str(uuid.uuid4())[:8]  # Identificador único (8 caracteres)
        self.sourceIp = sourceIp
        self.destinationIp = destinationIp
        self.content = content
        self.ttl = ttl  # Time To Live
        self.pathTrace: List[str] = []  # Lista de nodos traversados
        self.hops = 0  # Contador de saltos
        self.status = "active"  # "active", "delivered", "expired", "dropped"
    
    def decrementTtl(self) -> bool:
        """Decrementa TTL y retorna True si el paquete sigue siendo válido"""
        self.ttl -= 1
        if self.ttl <= 0:
            self.status = "expired"
            return False
        return True
    
    def addToTrace(self, deviceName: str):
        """Agrega el dispositivo actual al rastro del path"""
        self.pathTrace.append(deviceName)
        self.hops += 1
        print(f"Packet {self.id}: Passed through {deviceName} (Hop {self.hops}, TTL={self.ttl})")
    
    def markDelivered(self):
        """Marca el paquete como entregado exitosamente"""
        self.status = "delivered"
        print(f"Packet {self.id}: DELIVERED to {self.destinationIp}")
    
    def markDropped(self, reason: str = "Unknown"):
        """Marca el paquete como descartado"""
        self.status = "dropped"
        print(f"Packet {self.id}: DROPPED - {reason}")
    
    def getPathString(self) -> str:
        """Retorna el path como string legible"""
        if not self.pathTrace:
            return "No path traced"
        return " -> ".join(self.pathTrace)
    
    def isActive(self) -> bool:
        """Verifica si el paquete está activo (no expirado ni entregado)"""
        return self.status == "active"
    
    def getInfo(self) -> dict:
        """Retorna información completa del paquete"""
        return {
            'id': self.id,
            'sourceIp': self.sourceIp,
            'destinationIp': self.destinationIp,
            'content': self.content,
            'ttl': self.ttl,
            'hops': self.hops,
            'status': self.status,
            'pathTrace': self.pathTrace,
            'pathString': self.getPathString()
        }
    
    def __str__(self):
        return f"Packet[{self.id}] {self.sourceIp}->{self.destinationIp} TTL={self.ttl} Status={self.status}"
    
    def __repr__(self):
        return f"Packet(id='{self.id}', src='{self.sourceIp}', dst='{self.destinationIp}', ttl={self.ttl})" 