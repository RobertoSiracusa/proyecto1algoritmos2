import sys
import os
import json
from datetime import datetime

# Agregar el directorio padre al path para importar las estructuras de datos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataEstructures import LinkedList

from .device import Device
from .interface import Interface


class Network:
    """Clase que representa una red completa con múltiples dispositivos"""
    
    def __init__(self, name="Red Principal"):
        self.name = name
        self.devices = LinkedList()  # Lista de dispositivos (simulando diccionario)
        self.connections = LinkedList()  # Lista de conexiones (device1, iface1, device2, iface2)
        self.totalPacketsProcessed = 0
        self.totalConnections = 0
        
        # ===== NUEVO: Módulo 5 StatsReports - Atributos de estadísticas =====
        self.total_packets_sent = 0         # Total de paquetes enviados
        self.delivered_packets = 0          # Paquetes entregados exitosamente
        self.dropped_packets_ttl = 0        # Paquetes descartados por TTL
        self.blocked_by_firewall = 0        # Paquetes bloqueados por firewall
        self.total_hops = 0                 # Total de saltos acumulados
        self.device_activity = LinkedList()  # Actividad por dispositivo (simulando diccionario)
        self.packet_paths = LinkedList()    # Rutas de paquetes para estadísticas
    
    def _find_device_by_name(self, device_name):
        """Busca un dispositivo por nombre en la lista enlazada"""
        current = self.devices.head
        while current is not None:
            if current.data.name == device_name:
                return current.data
            current = current.next
        return None
    
    def _find_activity_by_device_name(self, device_name):
        """Busca la actividad de un dispositivo por nombre"""
        current = self.device_activity.head
        while current is not None:
            if current.data['device_name'] == device_name:
                return current.data
            current = current.next
        return None
    
    def addDevice(self, device):
        """Agrega un nuevo dispositivo a la red"""
        if self._find_device_by_name(device.name):
            print(f"Error: Ya existe un dispositivo con el nombre '{device.name}' en la red")
            return False
        
        self.devices.add_node(device)
        # Inicializar contador de actividad para el nuevo dispositivo
        activity_data = {'device_name': device.name, 'count': 0}
        self.device_activity.add_node(activity_data)
        print(f"Dispositivo '{device.name}' agregado a la red '{self.name}'")
        return True
    
    def getDevice(self, deviceName):
        """Recupera un dispositivo por nombre"""
        return self._find_device_by_name(deviceName)
    
    def removeDevice(self, deviceName):
        """Remueve un dispositivo de la red"""
        device = self.getDevice(deviceName)
        if not device:
            print(f"Error: Dispositivo '{deviceName}' no encontrado en la red")
            return False
        
        # Desconectar todas las interfaces del dispositivo antes de removerlo
        for interface in device.interfaces:
            if interface.isConnected():
                connectedInterface = interface.connectedTo
                interface.disconnect()
                print(f"Interfaz {interface.name} desconectada antes de remover dispositivo")
        
        # Remover de la lista de conexiones
        connections_to_remove = []
        current = self.connections.head
        while current is not None:
            d1, i1, d2, i2 = current.data
            if d1 == deviceName or d2 == deviceName:
                connections_to_remove.append(current.data)
            current = current.next
        
        for connection in connections_to_remove:
            self.connections.remove_node(connection)
        
        # Remover dispositivo
        self.devices.remove_node(device)
        
        # Remover contador de actividad
        activity_data = self._find_activity_by_device_name(deviceName)
        if activity_data:
            self.device_activity.remove_node(activity_data)
        
        print(f"Dispositivo '{deviceName}' removido de la red")
        return True
    
    def establishConnection(self, device1Name, interface1Name, 
                           device2Name, interface2Name):
        """Establece una conexión física entre dos interfaces de dispositivos diferentes"""
        # Obtener dispositivos
        device1 = self.getDevice(device1Name)
        device2 = self.getDevice(device2Name)
        
        if not device1:
            print(f"Error: Dispositivo '{device1Name}' no encontrado")
            return False
        
        if not device2:
            print(f"Error: Dispositivo '{device2Name}' no encontrado")
            return False
        
        # Verificar que no sean el mismo dispositivo
        if device1Name == device2Name:
            print(f"Error: No se puede conectar un dispositivo consigo mismo")
            return False
        
        # Obtener interfaces
        interface1 = device1.getInterface(interface1Name)
        interface2 = device2.getInterface(interface2Name)
        
        if not interface1:
            print(f"Error: Interfaz '{interface1Name}' no encontrada en dispositivo '{device1Name}'")
            return False
        
        if not interface2:
            print(f"Error: Interfaz '{interface2Name}' no encontrada en dispositivo '{device2Name}'")
            return False
        
        # Verificar que las interfaces no estén ya conectadas
        if interface1.isConnected():
            print(f"Error: Interfaz '{interface1Name}' en '{device1Name}' ya está conectada")
            return False
        
        if interface2.isConnected():
            print(f"Error: Interfaz '{interface2Name}' en '{device2Name}' ya está conectada")
            return False
        
        # Verificar que las interfaces estén activas
        if not interface1.isUp():
            print(f"Warning: Interfaz '{interface1Name}' en '{device1Name}' está inactiva")
        
        if not interface2.isUp():
            print(f"Warning: Interfaz '{interface2Name}' en '{device2Name}' está inactiva")
        
        # Establecer conexión bidireccional
        success1 = interface1.connect(interface2)
        success2 = interface2.connect(interface1)
        
        if success1 and success2:
            # Agregar a la lista de conexiones
            connection = (device1Name, interface1Name, device2Name, interface2Name)
            self.connections.add_node(connection)
            self.totalConnections += 1
            
            print(f"Conexión establecida: {device1Name}:{interface1Name} <--> {device2Name}:{interface2Name}")
            return True
        else:
            print(f"Error: No se pudo establecer la conexión")
            return False
    
    def removeConnection(self, device1Name, interface1Name, 
                        device2Name, interface2Name):
        """Desconecta dos interfaces de dispositivos"""
        # Obtener dispositivos
        device1 = self.getDevice(device1Name)
        device2 = self.getDevice(device2Name)
        
        if not device1 or not device2:
            print(f"Error: Uno o ambos dispositivos no encontrados")
            return False
        
        # Obtener interfaces
        interface1 = device1.getInterface(interface1Name)
        interface2 = device2.getInterface(interface2Name)
        
        if not interface1 or not interface2:
            print(f"Error: Una o ambas interfaces no encontradas")
            return False
        
        # Verificar que estén conectadas entre sí
        if interface1.connectedTo != interface2 or interface2.connectedTo != interface1:
            print(f"Error: Las interfaces especificadas no están conectadas entre sí")
            return False
        
        # Desconectar
        interface1.disconnect()
        interface2.disconnect()
        
        # Remover de la lista de conexiones
        connection1 = (device1Name, interface1Name, device2Name, interface2Name)
        connection2 = (device2Name, interface2Name, device1Name, interface1Name)
        
        # Buscar y remover la conexión
        current = self.connections.head
        while current is not None:
            if current.data == connection1 or current.data == connection2:
                self.connections.remove_node(current.data)
                break
            current = current.next
        
        self.totalConnections -= 1
        print(f"Conexión removida: {device1Name}:{interface1Name} <--> {device2Name}:{interface2Name}")
        return True
    
    def listDevices(self):
        """Retorna una lista de todos los dispositivos y su estado"""
        deviceList = []
        
        current = self.devices.head
        while current is not None:
            device = current.data
            deviceInfo = {
                'name': device.name,
                'type': device.type,
                'status': device.status,
                'interfaces': len(device.interfaces),
                'active_interfaces': len([i for i in device.interfaces if i.isUp()]),
                'connected_interfaces': len([i for i in device.interfaces if i.isConnected()])
            }
            deviceList.append(deviceInfo)
            current = current.next
        
        return deviceList
    
    def processAllQueues(self):
        """Itera a través de todos los dispositivos y sus interfaces para procesar paquetes"""
        stats = {
            'devicesProcessed': 0,
            'interfacesProcessed': 0, 
            'totalPacketsProcessed': 0,
            'onlineDevices': 0,
            'offlineDevices': 0
        }
        
        current = self.devices.head
        while current is not None:
            device = current.data
            stats['devicesProcessed'] += 1
            
            if device.isOnline():
                stats['onlineDevices'] += 1
                
                # Procesar cola saliente del dispositivo
                processedPackets = device.processOutgoingQueue()
                stats['totalPacketsProcessed'] += len(processedPackets)
                
                # Procesar interfaces del dispositivo
                for interface in device.interfaces:
                    stats['interfacesProcessed'] += 1
                    
                    if interface.isUp() and interface.isConnected():
                        # Procesar cola de salida de la interfaz
                        interfaceProcessed = interface.processOutgoingQueue()
                        stats['totalPacketsProcessed'] += len(interfaceProcessed)
            else:
                stats['offlineDevices'] += 1
            
            current = current.next
        
        self.totalPacketsProcessed += stats['totalPacketsProcessed']
        return stats
    
    def updateTopology(self):
        """Asegura la consistencia de las conexiones"""
        inconsistencies = 0
        
        print("Verificando consistencia de la topología...")
        
        # Verificar que todas las conexiones registradas sean válidas
        validConnections = []
        
        for device1Name, interface1Name, device2Name, interface2Name in self.connections:
            device1 = self.getDevice(device1Name)
            device2 = self.getDevice(device2Name)
            
            if not device1 or not device2:
                print(f"Conexión inválida encontrada: dispositivo inexistente ({device1Name} o {device2Name})")
                inconsistencies += 1
                continue
            
            interface1 = device1.getInterface(interface1Name)
            interface2 = device2.getInterface(interface2Name)
            
            if not interface1 or not interface2:
                print(f"Conexión inválida encontrada: interfaz inexistente ({interface1Name} o {interface2Name})")
                inconsistencies += 1
                continue
            
            # Verificar consistencia bidireccional
            if interface1.connectedTo != interface2 or interface2.connectedTo != interface1:
                print(f"Inconsistencia encontrada en conexión: {device1Name}:{interface1Name} <-> {device2Name}:{interface2Name}")
                # Corregir la conexión
                interface1.connect(interface2)
                interface2.connect(interface1)
                inconsistencies += 1
            
            validConnections.append((device1Name, interface1Name, device2Name, interface2Name))
        
        # Actualizar lista de conexiones con solo las válidas
        self.connections = validConnections
        self.totalConnections = len(validConnections)
        
        if inconsistencies > 0:
            print(f"Topología actualizada: {inconsistencies} inconsistencias corregidas")
        else:
            print("Topología consistente: no se encontraron problemas")
        
        return inconsistencies == 0
    
    def showStatistics(self):
        """Muestra estadísticas globales de la red"""
        print(f"\n=== Estadísticas de Red: {self.name} ===")
        print(f"Dispositivos totales: {len(self.devices)}")
        print(f"Conexiones activas: {self.totalConnections}")
        print(f"Paquetes procesados: {self.totalPacketsProcessed}")
        
        # Contar dispositivos por tipo y estado
        devicesByType = {}
        devicesByStatus = {}
        
        current = self.devices.head
        while current:
            device = current.data
            devicesByType[device.type] = devicesByType.get(device.type, 0) + 1
            devicesByStatus[device.status] = devicesByStatus.get(device.status, 0) + 1
            current = current.next
        
        print("\nDispositivos por tipo:")
        for deviceType, count in devicesByType.items():
            print(f"  {deviceType}: {count}")
        
        print("\nDispositivos por estado:")
        for status, count in devicesByStatus.items():
            print(f"  {status}: {count}")
        
        # Mostrar estadísticas de interfaces
        totalInterfaces = 0
        activeInterfaces = 0
        connectedInterfaces = 0
        
        current = self.devices.head
        while current:
            device = current.data
            # Contar interfaces totales
            interface_current = device.interfaces.head
            while interface_current:
                totalInterfaces += 1
                if interface_current.data.isUp():
                    activeInterfaces += 1
                if interface_current.data.isConnected():
                    connectedInterfaces += 1
                interface_current = interface_current.next
            current = current.next
        
        print(f"\nInterfaces totales: {totalInterfaces}")
        print(f"Interfaces activas: {activeInterfaces}")
        print(f"Interfaces conectadas: {connectedInterfaces}")
        
        # ===== NUEVO: Módulo 5 StatsReports - Mostrar estadísticas extendidas =====
        print(f"\n=== Estadísticas de Paquetes ===")
        print(f"Paquetes enviados: {self.total_packets_sent}")
        print(f"Paquetes entregados: {self.delivered_packets}")
        print(f"Paquetes descartados (TTL): {self.dropped_packets_ttl}")
        print(f"Paquetes bloqueados (Firewall): {self.blocked_by_firewall}")
        print(f"Saltos totales: {self.total_hops}")
        
        # Mostrar promedio de saltos
        avg_hops = self.calculate_average_hops()
        if avg_hops > 0:
            print(f"Promedio de saltos por paquete: {avg_hops:.2f}")
        
        # Mostrar top talker
        top_talker = self.identify_top_talker()
        if top_talker:
            print(f"Dispositivo más activo: {top_talker['device']} ({top_talker['activity']} actividades)")
        
        print("=" * 50)
    
    # ===== NUEVO: Módulo 5 StatsReports - Métodos de estadísticas =====
    
    def update_statistics(self, packet_status: str, device_name: str = None, hops: int = 0):
        """
        Incrementa contadores relevantes basado en el estado del paquete
        
        Args:
            packet_status: Estado del paquete ('sent', 'delivered', 'dropped_ttl', 'blocked_firewall')
            device_name: Nombre del dispositivo involucrado
            hops: Número de saltos del paquete
        """
        if packet_status == 'sent':
            self.total_packets_sent += 1
        elif packet_status == 'delivered':
            self.delivered_packets += 1
            if hops > 0:
                self.total_hops += hops
        elif packet_status == 'dropped_ttl':
            self.dropped_packets_ttl += 1
            if hops > 0:
                self.total_hops += hops
        elif packet_status == 'blocked_firewall':
            self.blocked_by_firewall += 1
        
        # Actualizar actividad del dispositivo
        if device_name and device_name in self.device_activity:
            self.device_activity[device_name] += 1
    
    def calculate_average_hops(self) -> float:
        """
        Calcula el promedio de saltos por paquete entregado/descartado
        
        Returns:
            float: Promedio de saltos (0 si no hay paquetes procesados)
        """
        total_processed_packets = self.delivered_packets + self.dropped_packets_ttl
        
        if total_processed_packets == 0:
            return 0.0
        
        return self.total_hops / total_processed_packets
    
    def identify_top_talker(self):
        """
        Determina el dispositivo con más actividad
        
        Returns:
            Dict con información del dispositivo más activo, None si no hay actividad
        """
        if not self.device_activity:
            return None
        
        # Encontrar el dispositivo con mayor actividad
        top_device = max(self.device_activity.items(), key=lambda x: x[1])
        
        if top_device[1] == 0:  # No hay actividad
            return None
        
        device = self.getDevice(top_device[0])
        
        return {
            'device': top_device[0],
            'activity': top_device[1],
            'type': device.type if device else 'unknown',
            'status': device.status if device else 'unknown'
        }
    
    def get_detailed_statistics(self):
        """
        Retorna estadísticas detalladas de la red en formato diccionario
        
        Returns:
            Dict con todas las estadísticas de la red
        """
        # Calcular estadísticas de dispositivos
        devices_by_type = {}
        devices_by_status = {}
        
        current = self.devices.head
        while current:
            device = current.data
            devices_by_type[device.type] = devices_by_type.get(device.type, 0) + 1
            devices_by_status[device.status] = devices_by_status.get(device.status, 0) + 1
            current = current.next
        
        # Calcular estadísticas de interfaces
        total_interfaces = 0
        active_interfaces = 0
        connected_interfaces = 0
        
        current = self.devices.head
        while current:
            device = current.data
            interface_current = device.interfaces.head
            while interface_current:
                total_interfaces += 1
                if interface_current.data.isUp():
                    active_interfaces += 1
                if interface_current.data.isConnected():
                    connected_interfaces += 1
                interface_current = interface_current.next
            current = current.next
        
        return {
            'network_name': self.name,
            'devices': {
                'total': len(self.devices),
                'by_type': devices_by_type,
                'by_status': devices_by_status
            },
            'interfaces': {
                'total': total_interfaces,
                'active': active_interfaces,
                'connected': connected_interfaces
            },
            'connections': {
                'total': self.totalConnections,
                'active': len([c for c in self.connections if self._is_connection_active(c)])
            },
            'packets': {
                'sent': self.total_packets_sent,
                'delivered': self.delivered_packets,
                'dropped_ttl': self.dropped_packets_ttl,
                'blocked_firewall': self.blocked_by_firewall,
                'processed': self.totalPacketsProcessed,
                'total_hops': self.total_hops,
                'average_hops': self.calculate_average_hops()
            },
            'top_talker': self.identify_top_talker(),
            'device_activity': self.device_activity.copy()
        }
    
    def _is_connection_active(self, connection):
        """Verifica si una conexión está activa (ambos dispositivos online y interfaces up)"""
        device1_name, interface1_name, device2_name, interface2_name = connection
        
        device1 = self.getDevice(device1_name)
        device2 = self.getDevice(device2_name)
        
        if not device1 or not device2 or not device1.isOnline() or not device2.isOnline():
            return False
        
        interface1 = device1.getInterface(interface1_name)
        interface2 = device2.getInterface(interface2_name)
        
        if not interface1 or not interface2 or not interface1.isUp() or not interface2.isUp():
            return False
        
        return True
    
    def reset_statistics(self):
        """Reinicia todas las estadísticas de la red"""
        self.total_packets_sent = 0
        self.delivered_packets = 0
        self.dropped_packets_ttl = 0
        self.blocked_by_firewall = 0
        self.total_hops = 0
        self.totalPacketsProcessed = 0
        
        # Reiniciar actividad de dispositivos
        for device_name in self.device_activity:
            self.device_activity[device_name] = 0
        
        self.packet_paths.clear()
        print("Estadísticas de red reiniciadas")
    
    # ===== NUEVO: Módulo 6 Configuration Persistence - Métodos de serialización =====
    
    def to_dict(self):
        """
        Serializa la red completa a un diccionario para guardado JSON
        
        Returns:
            dict: Representación serializable de toda la red
        """
        network_dict = {
            'metadata': {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'simulator_module': 'Network Simulator v1.0'
            },
            'network': {
                'name': self.name,
                'totalPacketsProcessed': self.totalPacketsProcessed,
                'totalConnections': self.totalConnections
            },
            'statistics': {
                'total_packets_sent': self.total_packets_sent,
                'delivered_packets': self.delivered_packets,
                'dropped_packets_ttl': self.dropped_packets_ttl,
                'blocked_by_firewall': self.blocked_by_firewall,
                'total_hops': self.total_hops,
                'device_activity': self.device_activity.copy(),
                'packet_paths': self.packet_paths.copy()
            },
            'devices': [],
            'connections': []
        }
        
        # Serializar dispositivos
        for device_name, device in self.devices.items():
            network_dict['devices'].append(device.to_dict())
        
        # Serializar conexiones
        for connection in self.connections:
            device1_name, interface1_name, device2_name, interface2_name = connection
            network_dict['connections'].append({
                'device1': device1_name,
                'interface1': interface1_name,
                'device2': device2_name,
                'interface2': interface2_name
            })
        
        return network_dict
    
    @classmethod
    def from_dict(cls, network_dict: dict):
        """
        Crea una red completa desde un diccionario deserializado
        
        Args:
            network_dict: Diccionario con datos de la red
            
        Returns:
            Network: Nueva instancia de la red completamente configurada
        """
        # Crear red
        network_data = network_dict['network']
        network = cls(network_data['name'])
        
        # Restaurar estadísticas básicas
        network.totalPacketsProcessed = network_data.get('totalPacketsProcessed', 0)
        network.totalConnections = network_data.get('totalConnections', 0)
        
        # Restaurar estadísticas extendidas
        if 'statistics' in network_dict:
            stats = network_dict['statistics']
            network.total_packets_sent = stats.get('total_packets_sent', 0)
            network.delivered_packets = stats.get('delivered_packets', 0)
            network.dropped_packets_ttl = stats.get('dropped_packets_ttl', 0)
            network.blocked_by_firewall = stats.get('blocked_by_firewall', 0)
            network.total_hops = stats.get('total_hops', 0)
            network.device_activity = stats.get('device_activity', {})
            network.packet_paths = stats.get('packet_paths', [])
        
        # Mapeo global de interfaces para resolver conexiones
        interface_mapping = {}
        
        # Recrear dispositivos
        for device_data in network_dict['devices']:
            device = Device.from_dict(device_data, interface_mapping)
            network.addDevice(device)
        
        # Recrear conexiones
        print("\nReconstruyendo conexiones...")
        for connection_data in network_dict['connections']:
            device1_name = connection_data['device1']
            interface1_name = connection_data['interface1']
            device2_name = connection_data['device2']
            interface2_name = connection_data['interface2']
            
            # Obtener dispositivos e interfaces
            device1 = network.getDevice(device1_name)
            device2 = network.getDevice(device2_name)
            
            if device1 and device2:
                interface1 = device1.getInterface(interface1_name)
                interface2 = device2.getInterface(interface2_name)
                
                if interface1 and interface2:
                    # Establecer conexión
                    success = network.establishConnection(
                        device1_name, interface1_name,
                        device2_name, interface2_name
                    )
                    if not success:
                        print(f"Warning: No se pudo reconstruir conexión {device1_name}:{interface1_name} <-> {device2_name}:{interface2_name}")
                else:
                    print(f"Warning: Interfaces no encontradas para conexión {device1_name}:{interface1_name} <-> {device2_name}:{interface2_name}")
            else:
                print(f"Warning: Dispositivos no encontrados para conexión {device1_name} <-> {device2_name}")
        
        return network
    
    def save_running_config(self, filename: str = None) -> str:
        """
        Guarda la configuración actual de la red en un archivo JSON
        
        Args:
            filename: Nombre del archivo (opcional, se genera automáticamente si no se proporciona)
            
        Returns:
            str: Ruta del archivo guardado
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"running-config_{timestamp}.json"
        
        # Asegurar que el archivo tenga extensión .json
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Crear directorio configs si no existe
        configs_dir = 'configs'
        if not os.path.exists(configs_dir):
            os.makedirs(configs_dir)
        
        filepath = os.path.join(configs_dir, filename)
        
        try:
            # Serializar y guardar
            config_data = self.to_dict()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuración guardada exitosamente: {filepath}")
            print(f"   Dispositivos: {len(self.devices)}")
            print(f"   Conexiones: {len(self.connections)}")
            print(f"   Estadísticas preservadas: Sí")
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error guardando configuración: {str(e)}")
            raise
    
    def load_config(self, filename):
        """
        Carga configuración desde un archivo JSON
        
        Args:
            filename: Nombre del archivo de configuración
            
        Returns:
            bool: True si la carga fue exitosa
        """
        # Buscar archivo en directorio configs
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = filename
        if not os.path.exists(filepath):
            filepath = os.path.join('configs', filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Archivo de configuración no encontrado: {filename}")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Limpiar configuración actual
            self._clear_current_config()
            
            # Cargar nueva configuración
            loaded_network = Network.from_dict(config_data)
            
            # Copiar datos a la instancia actual
            self.name = loaded_network.name
            self.devices = loaded_network.devices
            self.connections = loaded_network.connections
            self.totalPacketsProcessed = loaded_network.totalPacketsProcessed
            self.totalConnections = loaded_network.totalConnections
            self.total_packets_sent = loaded_network.total_packets_sent
            self.delivered_packets = loaded_network.delivered_packets
            self.dropped_packets_ttl = loaded_network.dropped_packets_ttl
            self.blocked_by_firewall = loaded_network.blocked_by_firewall
            self.total_hops = loaded_network.total_hops
            self.device_activity = loaded_network.device_activity
            self.packet_paths = loaded_network.packet_paths
            
            print(f"✅ Configuración cargada exitosamente: {filepath}")
            print(f"   Red: {self.name}")
            print(f"   Dispositivos: {len(self.devices)}")
            print(f"   Conexiones: {len(self.connections)}")
            
            # Mostrar información de metadatos si está disponible
            if 'metadata' in config_data:
                metadata = config_data['metadata']
                print(f"   Versión: {metadata.get('version', 'N/A')}")
                print(f"   Creado: {metadata.get('created', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando configuración: {str(e)}")
            return False
    
    def _clear_current_config(self):
        """Limpia la configuración actual"""
        # Desconectar todas las interfaces
        current = self.devices.head
        while current:
            device = current.data
            interface_current = device.interfaces.head
            while interface_current:
                if interface_current.data.isConnected():
                    interface_current.data.disconnect()
                interface_current = interface_current.next
            current = current.next
        
        # Limpiar todo
        self.devices = LinkedList()
        self.connections = LinkedList()
        self.device_activity.clear()
        self.packet_paths.clear()
        
        # Resetear contadores
        self.totalPacketsProcessed = 0
        self.totalConnections = 0
        self.total_packets_sent = 0
        self.delivered_packets = 0
        self.dropped_packets_ttl = 0
        self.blocked_by_firewall = 0
        self.total_hops = 0
    
    def list_saved_configs(self):
        """
        Lista archivos de configuración disponibles
        
        Returns:
            List[str]: Lista de archivos de configuración
        """
        configs_dir = 'configs'
        if not os.path.exists(configs_dir):
            return []
        
        config_files = []
        for filename in os.listdir(configs_dir):
            if filename.endswith('.json'):
                config_files.append(filename)
        
        return sorted(config_files)
    
    def get_config_info(self, filename):
        """
        Obtiene información de un archivo de configuración sin cargarlo
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            dict: Información del archivo o None si hay error
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join('configs', filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            info = {
                'filename': filename,
                'network_name': config_data['network']['name'],
                'devices_count': len(config_data['devices']),
                'connections_count': len(config_data['connections']),
                'created': config_data.get('metadata', {}).get('created', 'Unknown'),
                'version': config_data.get('metadata', {}).get('version', 'Unknown')
            }
            
            return info
            
        except Exception:
            return None
    
    def getAllDeviceNames(self):
        """Retorna una lista con los nombres de todos los dispositivos"""
        device_names = []
        current = self.devices.head
        while current is not None:
            device_names.append(current.data.name)
            current = current.next
        return device_names
    
    def getNetworkTopology(self):
        """Retorna un diccionario con la topología completa de la red"""
        topology = {
            'name': self.name,
            'devices': {},
            'connections': self.connections.traverse()
        }
        
        current = self.devices.head
        while current is not None:
            device = current.data
            deviceData = {
                'type': device.type,
                'status': device.status,
                'interfaces': {}
            }
            
            for interface in device.interfaces:
                interfaceData = {
                    'ipAddress': interface.ipAddress,
                    'macAddress': interface.macAddress,
                    'status': interface.status,
                    'connectedTo': interface.connectedTo.name if interface.connectedTo else None
                }
                deviceData['interfaces'][interface.name] = interfaceData
            
            topology['devices'][device.name] = deviceData
            current = current.next
        
        return topology
    
    def __str__(self):
        return f"Network '{self.name}' with {len(self.devices)} devices and {self.totalConnections} connections" 