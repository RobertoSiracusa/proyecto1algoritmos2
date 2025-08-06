import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .packet import Packet
from Devices_Network.network import Network
from Devices_Network.device import Device
from Devices_Network.interface import Interface
from DataEstructures.linked_list import LinkedList


class CommunicationManager:
    """Gestor de comunicaciones de paquetes en la red"""
    
    def __init__(self, network):
        self.network = network
        self.packetHistory = LinkedList()  # Historial de todos los paquetes
        self.activePackets = LinkedList()  # Paquetes actualmente en tránsito
        self.deliveredPackets = LinkedList()  # Paquetes entregados
        self.droppedPackets = LinkedList()  # Paquetes descartados
        self.tickCount = 0  # Contador de ticks de procesamiento
    
    def send(self, sourceIp, destinationIp, content, ttl=64):
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
        self.packetHistory.add_node(packet)
        self.activePackets.add_node(packet)
        
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
    
    def tick(self):
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
    
    def _extractPacketsFromQueues(self):
        """Extrae todos los paquetes Packet de las colas de interfaces"""
        packetsToProcess = []
        
        # Iterar sobre la LinkedList de dispositivos
        current = self.network.devices.head
        while current:
            device = current.data
            if device.isOffline():
                current = current.next
                continue
                
            # Iterar sobre la LinkedList de interfaces
            interface_current = device.interfaces.head
            while interface_current:
                interface = interface_current.data
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
                
                interface_current = interface_current.next
            
            current = current.next
        
        return packetsToProcess
    
    def _findDeviceByIp(self, ip):
        """Encuentra un dispositivo que tenga una interfaz con la IP especificada"""
        current = self.network.devices.head
        while current:
            device = current.data
            interface_current = device.interfaces.head
            while interface_current:
                interface = interface_current.data
                if interface.ipAddress == ip:
                    return device
                interface_current = interface_current.next
            current = current.next
        return None
    
    def _findInterfaceByIp(self, device, ip):
        """Encuentra una interfaz en un dispositivo con la IP especificada"""
        interface_current = device.interfaces.head
        while interface_current:
            interface = interface_current.data
            if interface.ipAddress == ip:
                return interface
            interface_current = interface_current.next
        return None
    
    def _isDestinationReached(self, packet, currentDevice):
        """Verifica si el paquete llegó a su destino"""
        interface_current = currentDevice.interfaces.head
        while interface_current:
            interface = interface_current.data
            if interface.ipAddress == packet.destinationIp:
                return True
            interface_current = interface_current.next
        return False
    
    def _determineNextHop(self, packet, currentDevice, currentInterface):
        """
        Determina el siguiente salto basado en la topología de red.
        Implementación básica: usa la primera interfaz conectada disponible.
        """
        # Si la interfaz actual está conectada, usar esa conexión
        if currentInterface.isConnected():
            connectedInterface = currentInterface.connectedTo
            
            # Buscar el dispositivo propietario de la interfaz conectada
            current = self.network.devices.head
            while current:
                device = current.data
                if device.isOnline():
                    interface_current = device.interfaces.head
                    while interface_current:
                        interface = interface_current.data
                        if interface == connectedInterface:
                            return device, interface
                        interface_current = interface_current.next
                current = current.next
        
        # Buscar alternativas en otras interfaces del dispositivo actual
        interface_current = currentDevice.interfaces.head
        while interface_current:
            interface = interface_current.data
            if interface != currentInterface and interface.isUp() and interface.isConnected():
                connectedInterface = interface.connectedTo
                
                # Buscar el dispositivo propietario
                current = self.network.devices.head
                while current:
                    device = current.data
                    if device.isOnline():
                        device_interface_current = device.interfaces.head
                        while device_interface_current:
                            deviceInterface = device_interface_current.data
                            if deviceInterface == connectedInterface:
                                return device, deviceInterface
                            device_interface_current = device_interface_current.next
                    current = current.next
            interface_current = interface_current.next
        
        return None, None
    
    def _findBestForwardingInterface(self, device, packet):
        """
        Encuentra la mejor interfaz de salida para reenviar un paquete
        """
        # Lógica simple: buscar una interfaz conectada que no sea la de entrada
        interface_current = device.interfaces.head
        while interface_current:
            interface = interface_current.data
            if interface.isUp() and interface.isConnected():
                # Verificar que no sea la interfaz por donde llegó el paquete
                connectedDevice = self._getConnectedDevice(interface)
                # Obtener los últimos 2 elementos del pathTrace
                path_list = []
                current = packet.pathTrace.head
                while current:
                    path_list.append(current.data)
                    current = current.next
                
                if connectedDevice and connectedDevice.name not in path_list[-2:]:
                    return interface
            interface_current = interface_current.next
        
        # Si no encuentra una interfaz ideal, usar cualquier interfaz conectada
        interface_current = device.interfaces.head
        while interface_current:
            interface = interface_current.data
            if interface.isUp() and interface.isConnected():
                return interface
            interface_current = interface_current.next
        
        return None
    
    def _getConnectedDevice(self, interface):
        """Obtiene el dispositivo conectado a una interfaz"""
        if not interface.isConnected():
            return None
        
        connectedInterface = interface.connectedTo
        current = self.network.devices.head
        while current:
            device = current.data
            interface_current = device.interfaces.head
            while interface_current:
                deviceInterface = interface_current.data
                if deviceInterface == connectedInterface:
                    return device
                interface_current = interface_current.next
            current = current.next
        return None
    
    def _moveToDelivered(self, packet):
        """Mueve un paquete de activos a entregados"""
        # Buscar y remover de activePackets
        self.activePackets.remove_node(packet)
        # Agregar a deliveredPackets
        self.deliveredPackets.add_node(packet)
    
    def _moveToDropped(self, packet):
        """Mueve un paquete de activos a descartados"""
        # Buscar y remover de activePackets
        self.activePackets.remove_node(packet)
        # Agregar a droppedPackets
        self.droppedPackets.add_node(packet)
    
    def showStatistics(self):
        """Muestra estadísticas completas de comunicación"""
        print(f"\n{'='*60}")
        print(f"ESTADÍSTICAS DE COMUNICACIÓN")
        print(f"{'='*60}")
        print(f"Ticks procesados: {self.tickCount}")
        print(f"Total de paquetes: {self.packetHistory.size}")
        print(f"Paquetes activos: {self.activePackets.size}")
        print(f"Paquetes entregados: {self.deliveredPackets.size}")
        print(f"Paquetes descartados: {self.droppedPackets.size}")
        
        if self.deliveredPackets.size > 0:
            print(f"\nPaquetes entregados exitosamente:")
            # Mostrar últimos 5 paquetes entregados
            delivered_list = []
            current = self.deliveredPackets.head
            while current:
                delivered_list.append(current.data)
                current = current.next
            
            for packet in delivered_list[-5:]:  # Últimos 5
                print(f"  {packet.id}: {packet.sourceIp} -> {packet.destinationIp} ({packet.hops} hops)")
        
        if self.droppedPackets.size > 0:
            print(f"\nPaquetes descartados:")
            # Mostrar últimos 5 paquetes descartados
            dropped_list = []
            current = self.droppedPackets.head
            while current:
                dropped_list.append(current.data)
                current = current.next
            
            for packet in dropped_list[-5:]:  # Últimos 5
                print(f"  {packet.id}: {packet.sourceIp} -> {packet.destinationIp} (Reason: TTL expired or no route)")
        
        if self.activePackets.size > 0:
            print(f"\nPaquetes en tránsito:")
            current = self.activePackets.head
            while current:
                packet = current.data
                print(f"  {packet.id}: {packet.sourceIp} -> {packet.destinationIp} (TTL={packet.ttl})")
                current = current.next
        
        print(f"{'='*60}")
    
    def getPacketTrace(self, packetId):
        """Obtiene el rastro completo de un paquete"""
        current = self.packetHistory.head
        while current:
            packet = current.data
            if packet.id == packetId:
                return packet.getInfo()
            current = current.next
        return None
    
    def listActivePackets(self):
        """Lista todos los paquetes activos"""
        active_list = []
        current = self.activePackets.head
        while current:
            active_list.append(current.data.getInfo())
            current = current.next
        return active_list
    
    def clearHistory(self):
        """Limpia el historial de paquetes (mantiene activos)"""
        # Limpiar listas de paquetes entregados y descartados
        self.deliveredPackets = LinkedList()
        self.droppedPackets = LinkedList()
        
        # Mantener solo paquetes activos en el historial
        new_history = LinkedList()
        current = self.packetHistory.head
        while current:
            packet = current.data
            if packet.isActive():
                new_history.add_node(packet)
            current = current.next
        
        self.packetHistory = new_history
        print("Historial de paquetes limpiado") 