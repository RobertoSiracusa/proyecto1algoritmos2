from typing import Optional, List, Dict, Tuple
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .packet import Packet
from Devices_Network.network import Network
from Devices_Network.device import Device
from Devices_Network.interface import Interface


class CommunicationManager:
    """Gestor de comunicaciones de paquetes en la red"""
    
    def __init__(self, network: Network):
        self.network = network
        self.packetHistory: List[Packet] = []  # Historial de todos los paquetes
        self.activePackets: List[Packet] = []  # Paquetes actualmente en tránsito
        self.deliveredPackets: List[Packet] = []  # Paquetes entregados
        self.droppedPackets: List[Packet] = []  # Paquetes descartados
        self.tickCount = 0  # Contador de ticks de procesamiento
    
    def send(self, sourceIp: str, destinationIp: str, content: str, ttl: int = 64) -> Optional[Packet]:
        """
        Comando SEND: Crea un paquete y lo coloca en la cola de salida del dispositivo fuente
        """
        print(f"\n=== SEND COMMAND ===")
        print(f"Sending packet from {sourceIp} to {destinationIp}")
        print(f"Content: {content}")
        
        # Encontrar dispositivo fuente basado en source_ip
        sourceDevice = self._findDeviceByIp(sourceIp)
        if not sourceDevice:
            print(f"ERROR: No device found with IP {sourceIp}")
            return None
        
        # Encontrar interfaz fuente
        sourceInterface = self._findInterfaceByIp(sourceDevice, sourceIp)
        if not sourceInterface:
            print(f"ERROR: No interface found with IP {sourceIp} on device {sourceDevice.name}")
            return None
        
        # Verificar que el dispositivo fuente esté online
        if sourceDevice.isOffline():
            print(f"ERROR: Source device {sourceDevice.name} is offline")
            return None
        
        # Verificar que la interfaz esté up
        if not sourceInterface.isUp():
            print(f"ERROR: Source interface {sourceInterface.name} is down")
            return None
        
        # Crear el paquete
        packet = Packet(sourceIp, destinationIp, content, ttl)
        
        # Agregar al rastro el dispositivo fuente
        packet.addToTrace(sourceDevice.name)
        
        # Agregar a listas de seguimiento
        self.packetHistory.append(packet)
        self.activePackets.append(packet)
        
        # Colocar en la cola de salida de la interfaz fuente
        success = sourceInterface.addPacketToQueue(packet)
        if success:
            print(f"Packet {packet.id} queued successfully on {sourceDevice.name}:{sourceInterface.name}")
            return packet
        else:
            print(f"ERROR: Failed to queue packet on {sourceDevice.name}:{sourceInterface.name}")
            packet.markDropped("Failed to queue at source")
            self._moveToDropped(packet)
            return None
    
    def tick(self) -> Dict[str, int]:
        """
        Comando TICK/PROCESS: Procesa todas las colas y maneja el enrutamiento de paquetes
        """
        self.tickCount += 1
        print(f"\n=== TICK {self.tickCount} ===")
        
        stats = {
            'packetsProcessed': 0,
            'packetsDelivered': 0,
            'packetsDropped': 0,
            'packetsForwarded': 0
        }
        
        # Obtener todos los paquetes de las colas de interfaces
        packetsToProcess = self._extractPacketsFromQueues()
        
        print(f"Processing {len(packetsToProcess)} packets...")
        
        for packet, currentDevice, currentInterface in packetsToProcess:
            stats['packetsProcessed'] += 1
            
            # Decrementar TTL
            if not packet.decrementTtl():
                print(f"Packet {packet.id} expired (TTL=0)")
                packet.markDropped("TTL expired")
                self._moveToDropped(packet)
                
                # ===== NUEVO: Módulo 5 StatsReports - Actualizar estadísticas de TTL =====
                self.network.update_statistics('dropped_ttl', currentDevice.name, packet.hops)
                
                stats['packetsDropped'] += 1
                continue
            
            # Verificar si llegamos al destino
            if self._isDestinationReached(packet, currentDevice):
                print(f"Packet {packet.id} reached destination!")
                packet.markDelivered()
                currentDevice.receivePacket(f"DELIVERED: {packet}")
                self._moveToDelivered(packet)
                
                # ===== NUEVO: Módulo 5 StatsReports - Actualizar estadísticas de entrega =====
                self.network.update_statistics('delivered', currentDevice.name, packet.hops)
                
                stats['packetsDelivered'] += 1
                continue
            
            # Determinar siguiente salto
            nextDevice, nextInterface = self._determineNextHop(packet, currentDevice, currentInterface)
            
            if nextDevice and nextInterface:
                # Agregar al rastro
                packet.addToTrace(nextDevice.name)
                
                # ===== NUEVO: Módulo 5 StatsReports - Actualizar actividad del dispositivo =====
                self.network.update_statistics('forwarded', nextDevice.name)
                
                # Encontrar interfaz de salida apropiada en el dispositivo de destino
                forwardingInterface = self._findBestForwardingInterface(nextDevice, packet)
                
                if forwardingInterface and forwardingInterface.isUp() and forwardingInterface.isConnected():
                    # Reencolar el paquete en la interfaz de salida del siguiente dispositivo
                    forwardingInterface.addPacketToQueue(packet)
                    print(f"Packet {packet.id} forwarded to {nextDevice.name} via {forwardingInterface.name}")
                    stats['packetsForwarded'] += 1
                else:
                    # El siguiente dispositivo no tiene interfaz de salida disponible
                    nextDevice.receivePacket(f"RECEIVED: {packet}")
                    print(f"Packet {packet.id} received at {nextDevice.name} (no further forwarding)")
                    
                    # Verificar si este dispositivo es realmente el destino
                    if self._isDestinationReached(packet, nextDevice):
                        packet.markDelivered()
                        self._moveToDelivered(packet)
                        
                        # ===== NUEVO: Módulo 5 StatsReports - Actualizar estadísticas de entrega =====
                        self.network.update_statistics('delivered', nextDevice.name, packet.hops)
                        
                        stats['packetsDelivered'] += 1
                    else:
                        # Paquete se queda en el dispositivo pero sigue activo
                        stats['packetsForwarded'] += 1
            else:
                # No se pudo determinar siguiente salto
                print(f"Packet {packet.id} dropped - no route to destination")
                packet.markDropped("No route to destination")
                self._moveToDropped(packet)
                
                # ===== NUEVO: Módulo 5 StatsReports - Actualizar estadísticas de descarte =====
                self.network.update_statistics('dropped_ttl', currentDevice.name, packet.hops)
                
                stats['packetsDropped'] += 1
        
        # Procesar colas restantes (no-paquetes)
        networkStats = self.network.processAllQueues()
        
        print(f"Tick {self.tickCount} completed:")
        print(f"  - Packets processed: {stats['packetsProcessed']}")
        print(f"  - Packets delivered: {stats['packetsDelivered']}")
        print(f"  - Packets forwarded: {stats['packetsForwarded']}")
        print(f"  - Packets dropped: {stats['packetsDropped']}")
        print(f"  - Other items processed: {networkStats['totalPacketsProcessed']}")
        
        return stats
    
    def _extractPacketsFromQueues(self) -> List[Tuple[Packet, Device, Interface]]:
        """Extrae todos los paquetes Packet de las colas de interfaces"""
        packetsToProcess = []
        
        for deviceName, device in self.network.devices.items():
            if device.isOffline():
                continue
                
            for interface in device.interfaces:
                if not interface.isUp() or not interface.isConnected():
                    continue
                
                # Extraer paquetes de tipo Packet de la cola
                packetQueue = interface.outgoingQueue
                tempQueue = []
                
                while not packetQueue.is_empty():
                    item = packetQueue.dequeue()
                    if isinstance(item, Packet):
                        packetsToProcess.append((item, device, interface))
                    else:
                        # Re-encolar items que no son paquetes
                        tempQueue.append(item)
                
                # Reencolar items no-paquetes
                for item in tempQueue:
                    packetQueue.enqueue(item)
        
        return packetsToProcess
    
    def _findDeviceByIp(self, ip: str) -> Optional[Device]:
        """Encuentra un dispositivo que tenga una interfaz con la IP especificada"""
        for deviceName, device in self.network.devices.items():
            for interface in device.interfaces:
                if interface.ipAddress == ip:
                    return device
        return None
    
    def _findInterfaceByIp(self, device: Device, ip: str) -> Optional[Interface]:
        """Encuentra una interfaz en un dispositivo con la IP especificada"""
        for interface in device.interfaces:
            if interface.ipAddress == ip:
                return interface
        return None
    
    def _isDestinationReached(self, packet: Packet, currentDevice: Device) -> bool:
        """Verifica si el paquete llegó a su destino"""
        for interface in currentDevice.interfaces:
            if interface.ipAddress == packet.destinationIp:
                return True
        return False
    
    def _determineNextHop(self, packet: Packet, currentDevice: Device, currentInterface: Interface) -> Tuple[Optional[Device], Optional[Interface]]:
        """
        Determina el siguiente salto basado en la topología de red.
        Implementación básica: usa la primera interfaz conectada disponible.
        """
        # Si la interfaz actual está conectada, usar esa conexión
        if currentInterface.isConnected():
            connectedInterface = currentInterface.connectedTo
            
            # Buscar el dispositivo propietario de la interfaz conectada
            for deviceName, device in self.network.devices.items():
                if device.isOnline():
                    for interface in device.interfaces:
                        if interface == connectedInterface:
                            return device, interface
        
        # Buscar alternativas en otras interfaces del dispositivo actual
        for interface in currentDevice.interfaces:
            if interface != currentInterface and interface.isUp() and interface.isConnected():
                connectedInterface = interface.connectedTo
                
                # Buscar el dispositivo propietario
                for deviceName, device in self.network.devices.items():
                    if device.isOnline():
                        for deviceInterface in device.interfaces:
                            if deviceInterface == connectedInterface:
                                return device, deviceInterface
        
        return None, None
    
    def _findBestForwardingInterface(self, device: Device, packet: Packet) -> Optional[Interface]:
        """
        Encuentra la mejor interfaz de salida para reenviar un paquete
        """
        # Lógica simple: buscar una interfaz conectada que no sea la de entrada
        for interface in device.interfaces:
            if interface.isUp() and interface.isConnected():
                # Verificar que no sea la interfaz por donde llegó el paquete
                connectedDevice = self._getConnectedDevice(interface)
                if connectedDevice and connectedDevice.name not in packet.pathTrace[-2:]:
                    return interface
        
        # Si no encuentra una interfaz ideal, usar cualquier interfaz conectada
        for interface in device.interfaces:
            if interface.isUp() and interface.isConnected():
                return interface
        
        return None
    
    def _getConnectedDevice(self, interface: Interface) -> Optional[Device]:
        """Obtiene el dispositivo conectado a una interfaz"""
        if not interface.isConnected():
            return None
        
        connectedInterface = interface.connectedTo
        for deviceName, device in self.network.devices.items():
            for deviceInterface in device.interfaces:
                if deviceInterface == connectedInterface:
                    return device
        return None
    
    def _moveToDelivered(self, packet: Packet):
        """Mueve un paquete de activos a entregados"""
        if packet in self.activePackets:
            self.activePackets.remove(packet)
        self.deliveredPackets.append(packet)
    
    def _moveToDropped(self, packet: Packet):
        """Mueve un paquete de activos a descartados"""
        if packet in self.activePackets:
            self.activePackets.remove(packet)
        self.droppedPackets.append(packet)
    
    def showStatistics(self):
        """Muestra estadísticas completas de comunicación"""
        print(f"\n{'='*60}")
        print(f"ESTADÍSTICAS DE COMUNICACIÓN")
        print(f"{'='*60}")
        print(f"Ticks procesados: {self.tickCount}")
        print(f"Total de paquetes: {len(self.packetHistory)}")
        print(f"Paquetes activos: {len(self.activePackets)}")
        print(f"Paquetes entregados: {len(self.deliveredPackets)}")
        print(f"Paquetes descartados: {len(self.droppedPackets)}")
        
        if self.deliveredPackets:
            print(f"\nPaquetes entregados exitosamente:")
            for packet in self.deliveredPackets[-5:]:  # Últimos 5
                print(f"  {packet.id}: {packet.sourceIp} -> {packet.destinationIp} ({packet.hops} hops)")
        
        if self.droppedPackets:
            print(f"\nPaquetes descartados:")
            for packet in self.droppedPackets[-5:]:  # Últimos 5
                print(f"  {packet.id}: {packet.sourceIp} -> {packet.destinationIp} (Reason: TTL expired or no route)")
        
        if self.activePackets:
            print(f"\nPaquetes en tránsito:")
            for packet in self.activePackets:
                print(f"  {packet.id}: {packet.sourceIp} -> {packet.destinationIp} (TTL={packet.ttl})")
        
        print(f"{'='*60}")
    
    def getPacketTrace(self, packetId: str) -> Optional[Dict]:
        """Obtiene el rastro completo de un paquete"""
        for packet in self.packetHistory:
            if packet.id == packetId:
                return packet.getInfo()
        return None
    
    def listActivePackets(self) -> List[Dict]:
        """Lista todos los paquetes activos"""
        return [packet.getInfo() for packet in self.activePackets]
    
    def clearHistory(self):
        """Limpia el historial de paquetes (mantiene activos)"""
        self.deliveredPackets.clear()
        self.droppedPackets.clear()
        self.packetHistory = [packet for packet in self.packetHistory if packet.isActive()]
        print("Historial de paquetes limpiado") 