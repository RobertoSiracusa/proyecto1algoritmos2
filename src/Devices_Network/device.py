#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Device - Dispositivo de Red
===========================

Implementación de la clase Device que representa un dispositivo de red genérico
en el simulador. Soporta diferentes tipos de dispositivos (router, switch, host, 
firewall) con interfaces de red, gestión de estado y procesamiento de paquetes.

Esta clase es el núcleo del sistema de dispositivos y proporciona:
- Gestión completa de interfaces de red
- Control de estado online/offline
- Procesamiento de colas de paquetes
- Historial de paquetes recibidos
- Validaciones robustas de datos
- Serialización para persistencia de configuración

Author: Network Simulator Project
Version: 1.0
Date: 2025
"""

from typing import List, Optional, Dict, Any, Union
import sys
import os

# Agregar el directorio padre al path para importar las estructuras de datos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataEstructures.stack import Stack
from DataEstructures.queue import Queue
from .interface import Interface
from .routing_table import RoutingTable
from .firewall_rules import FirewallManager
from .vlan_system import VLANManager
from .rip_protocol import RIPProtocol

# Importar validaciones si están disponibles
try:
    from core.validators import (
        ValidationError, DataValidator, DeviceType, DeviceStatus,
        safe_validate, get_validation_error_message
    )
    VALIDATORS_AVAILABLE = True
except ImportError:
    VALIDATORS_AVAILABLE = False
    ValidationError = Exception


class DeviceError(Exception):
    """
    Excepción base para errores específicos de dispositivos de red.
    """
    def __init__(self, message: str, device_name: str = None):
        self.device_name = device_name
        super().__init__(message)


class InterfaceNotFoundError(DeviceError):
    """
    Excepción lanzada cuando se intenta acceder a una interfaz que no existe.
    """
    def __init__(self, interface_name: str, device_name: str = None):
        self.interface_name = interface_name
        message = f"Interfaz '{interface_name}' no encontrada"
        if device_name:
            message += f" en dispositivo '{device_name}'"
        super().__init__(message, device_name)


class InterfaceDuplicateError(DeviceError):
    """
    Excepción lanzada cuando se intenta crear una interfaz con un nombre duplicado.
    """
    def __init__(self, interface_name: str, device_name: str = None):
        self.interface_name = interface_name
        message = f"Ya existe una interfaz con el nombre '{interface_name}'"
        if device_name:
            message += f" en dispositivo '{device_name}'"
        super().__init__(message, device_name)


class DeviceOfflineError(DeviceError):
    """
    Excepción lanzada cuando se intenta realizar operaciones en un dispositivo offline.
    """
    def __init__(self, operation: str, device_name: str = None):
        self.operation = operation
        message = f"No se puede realizar '{operation}' en dispositivo offline"
        if device_name:
            message += f" '{device_name}'"
        super().__init__(message, device_name)


class Device:
    """
    Clase que representa un dispositivo de red genérico con capacidades completas
    de networking, gestión de estado y procesamiento de paquetes.
    
    Un dispositivo puede ser un router, switch, host o firewall, cada uno con
    comportamientos específicos pero compartiendo la interfaz base común.
    
    Attributes:
        name (str): Nombre único del dispositivo en la red
        type (str): Tipo de dispositivo (router, switch, host, firewall)
        interfaces (List[Interface]): Lista de interfaces de red del dispositivo
        status (str): Estado actual del dispositivo (online/offline)
        receivedPacketsHistory (Stack): Historial de paquetes recibidos (LIFO)
        incomingQueue (Queue): Cola de paquetes entrantes (FIFO)
        outgoingQueue (Queue): Cola de paquetes salientes (FIFO)
        
    Private Attributes:
        _creation_time (float): Timestamp de creación del dispositivo
        _last_activity_time (float): Timestamp de última actividad
        _total_packets_processed (int): Contador total de paquetes procesados
        _interface_count (int): Contador de interfaces creadas
    """
    
    # Constantes de clase para validación
    VALID_DEVICE_TYPES = ["router", "switch", "host", "firewall"]
    VALID_DEVICE_STATUSES = ["online", "offline"]
    MAX_INTERFACES_PER_DEVICE = 100  # Límite razonable para simulación
    MAX_DEVICE_NAME_LENGTH = 50
    
    def __init__(self, name: str, deviceType: str):
        """
        Inicializa un nuevo dispositivo de red con validaciones robustas.
        
        Args:
            name (str): Nombre único del dispositivo. Debe seguir convenciones de naming.
            deviceType (str): Tipo de dispositivo (router, switch, host, firewall).
        
        Raises:
            ValidationError: Si el nombre o tipo de dispositivo no son válidos
            DeviceError: Si hay errores en la inicialización del dispositivo
            
        Example:
            >>> device = Device("Router-1", "router")
            >>> print(device.name)
            Router-1
            >>> print(device.type)
            router
        """
        # === VALIDACIONES DE ENTRADA ===
        self._validate_device_creation_parameters(name, deviceType)
        
        # === ATRIBUTOS PÚBLICOS ===
        self.name: str = name.strip()
        self.type: str = deviceType.lower()  # Normalizar a minúsculas
        self.interfaces: List[Interface] = []
        self.status: str = "offline"  # Dispositivos inician offline por seguridad
        
        # === ESTRUCTURAS DE DATOS PARA MANEJO DE PAQUETES ===
        self.receivedPacketsHistory: Stack = Stack(max_capacity=1000)  # Limitar historial
        self.incomingQueue: Queue = Queue(max_capacity=500)  # Limitar cola entrante
        self.outgoingQueue: Queue = Queue(max_capacity=500)  # Limitar cola saliente
        
        # === TABLA DE RUTAS (solo para routers) ===
        self.routing_table: Optional[RoutingTable] = None
        if self.type == "router":
            self.routing_table = RoutingTable()
        
        # === SISTEMA DE FIREWALL (solo para firewalls) ===
        self.firewall_manager: Optional[FirewallManager] = None
        if self.type == "firewall":
            self.firewall_manager = FirewallManager()
        
        # === SISTEMA DE VLANs (solo para switches) ===
        self.vlan_manager: Optional[VLANManager] = None
        if self.type == "switch":
            self.vlan_manager = VLANManager()
        
        # === PROTOCOLO RIP (solo para routers) ===
        self.rip_protocol: Optional[RIPProtocol] = None
        if self.type == "router":
            self.rip_protocol = RIPProtocol(self.name)
        
        # === ATRIBUTOS PRIVADOS PARA ESTADÍSTICAS Y CONTROL ===
        import time
        self._creation_time: float = time.time()
        self._last_activity_time: float = self._creation_time
        self._total_packets_processed: int = 0
        self._interface_count: int = 0  # Contador para nombres únicos de interfaces
        
        # Registrar creación en logs (si hay sistema de logging disponible)
        self._log_device_event("created", f"Device '{self.name}' of type '{self.type}' created")
    
    def _validate_device_creation_parameters(self, name: str, deviceType: str) -> None:
        """
        Valida los parámetros de creación del dispositivo usando el sistema de validaciones.
        
        Args:
            name (str): Nombre del dispositivo a validar
            deviceType (str): Tipo del dispositivo a validar
            
        Raises:
            ValidationError: Si algún parámetro no es válido
        """
        # Validar usando el sistema centralizado si está disponible
        if VALIDATORS_AVAILABLE:
            DataValidator.validate_device_name(name)
            DataValidator.validate_device_type(deviceType)
        else:
            # Validaciones básicas como fallback
            if not isinstance(name, str) or not name.strip():
                raise ValueError("El nombre del dispositivo debe ser un string no vacío")
            
            if not isinstance(deviceType, str) or deviceType.lower() not in self.VALID_DEVICE_TYPES:
                raise ValueError(f"Tipo de dispositivo debe ser uno de: {self.VALID_DEVICE_TYPES}")
    
    # === GESTIÓN DE INTERFACES ===
    
    def addInterface(self, interfaceName: str, autoActivate: bool = False) -> Interface:
        """
        Crea y agrega una nueva interfaz al dispositivo con validaciones completas.
        
        Args:
            interfaceName (str): Nombre de la interfaz (ej: "eth0", "gi0/0", "fa0/1")
            autoActivate (bool): Si True, activa automáticamente la interfaz
        
        Returns:
            Interface: La nueva interfaz creada y configurada
        
        Raises:
            ValidationError: Si el nombre de la interfaz no es válido
            InterfaceDuplicateError: Si ya existe una interfaz con ese nombre
            DeviceError: Si se excede el límite máximo de interfaces
            
        Example:
            >>> device = Device("Switch-1", "switch")
            >>> interface = device.addInterface("gi0/1", autoActivate=True)
            >>> print(interface.name)
            gi0/1
            >>> print(interface.status)
            up
        """
        # === VALIDACIONES PREVIAS ===
        self._validate_interface_addition(interfaceName)
        
        # === CREAR NUEVA INTERFAZ ===
        newInterface = Interface(
            name=interfaceName,
            ipAddress="",  # Se asignará después si es necesario
            macAddress="",  # Se asignará después si es necesario
            status="up" if autoActivate else "down"
        )
        
        # === AGREGAR A LA LISTA DE INTERFACES ===
        self.interfaces.append(newInterface)
        self._interface_count += 1
        
        # === ACTUALIZAR ACTIVIDAD ===
        self._update_last_activity()
        
        # === LOGGING ===
        self._log_device_event("interface_added", f"Interface '{interfaceName}' added to device '{self.name}'")
        
        return newInterface
    
    def _validate_interface_addition(self, interfaceName: str) -> None:
        """
        Valida que se pueda agregar una nueva interfaz con el nombre especificado.
        
        Args:
            interfaceName (str): Nombre de la interfaz a validar
            
        Raises:
            ValidationError: Si el nombre no es válido
            InterfaceDuplicateError: Si ya existe una interfaz con ese nombre
            DeviceError: Si se excede el límite máximo
        """
        # Validar nombre de interfaz
        if VALIDATORS_AVAILABLE:
            DataValidator.validate_interface_name(interfaceName)
        elif not isinstance(interfaceName, str) or not interfaceName.strip():
            raise ValueError("El nombre de la interfaz debe ser un string no vacío")
        
        # Verificar duplicados
        if self.getInterface(interfaceName) is not None:
            raise InterfaceDuplicateError(interfaceName, self.name)
        
        # Verificar límite máximo de interfaces
        if len(self.interfaces) >= self.MAX_INTERFACES_PER_DEVICE:
            raise DeviceError(
                f"Se ha alcanzado el límite máximo de {self.MAX_INTERFACES_PER_DEVICE} interfaces",
                self.name
            )
    
    def getInterface(self, interfaceName: str) -> Optional[Interface]:
        """
        Recupera una interfaz por su nombre con búsqueda optimizada.
        
        Args:
            interfaceName (str): Nombre de la interfaz a buscar
        
        Returns:
            Optional[Interface]: La interfaz encontrada o None si no existe
            
        Example:
            >>> device = Device("Router-1", "router")
            >>> device.addInterface("eth0")
            >>> interface = device.getInterface("eth0")
            >>> print(interface.name if interface else "No encontrada")
            eth0
        """
        if not isinstance(interfaceName, str):
            return None
        
        # Búsqueda lineal optimizada (para listas pequeñas es más eficiente que dict)
        for interface in self.interfaces:
            if interface.name == interfaceName:
                return interface
        
        return None
    
    def removeInterface(self, interfaceName: str) -> bool:
        """
        Remueve una interfaz del dispositivo de forma segura.
        
        Args:
            interfaceName (str): Nombre de la interfaz a remover
        
        Returns:
            bool: True si la interfaz fue removida exitosamente
            
        Raises:
            InterfaceNotFoundError: Si la interfaz no existe
        """
        interface = self.getInterface(interfaceName)
        if interface is None:
            raise InterfaceNotFoundError(interfaceName, self.name)
        
        # Desconectar la interfaz si está conectada
        if interface.isConnected():
            interface.disconnect()
        
        # Remover de la lista
        self.interfaces.remove(interface)
        
        # Actualizar actividad
        self._update_last_activity()
        
        # Logging
        self._log_device_event("interface_removed", f"Interface '{interfaceName}' removed from device '{self.name}'")
        
        return True
    
    def getInterfacesByStatus(self, status: str) -> List[Interface]:
        """
        Retorna todas las interfaces que tienen un estado específico.
        
        Args:
            status (str): Estado a buscar ("up", "down", "shutdown", "no shutdown")
        
        Returns:
            List[Interface]: Lista de interfaces con el estado especificado
        """
        return [iface for iface in self.interfaces if iface.status == status]
    
    def getActiveInterfaces(self) -> List[Interface]:
        """
        Retorna una lista de interfaces activas (up o no shutdown).
        
        Returns:
            List[Interface]: Lista de interfaces activas y funcionalmente disponibles
        """
        return [interface for interface in self.interfaces if interface.isUp()]
    
    def getConnectedInterfaces(self) -> List[Interface]:
        """
        Retorna una lista de interfaces que tienen conexiones físicas.
        
        Returns:
            List[Interface]: Lista de interfaces con conexiones establecidas
        """
        return [interface for interface in self.interfaces if interface.isConnected()]
    
    # === GESTIÓN DE ESTADO DEL DISPOSITIVO ===
    
    def setStatus(self, status: str, force: bool = False) -> None:
        """
        Cambia el estado online/offline del dispositivo con validaciones.
        
        Args:
            status (str): Nuevo estado ("online" o "offline")
            force (bool): Si True, fuerza el cambio ignorando ciertas validaciones
        
        Raises:
            ValidationError: Si el estado no es válido
            DeviceError: Si el cambio de estado no es permitido
            
        Example:
            >>> device = Device("Router-1", "router")
            >>> device.setStatus("online")
            >>> print(device.status)
            online
        """
        # === VALIDAR NUEVO ESTADO ===
        if VALIDATORS_AVAILABLE:
            DataValidator.validate_device_status(status)
        elif status not in self.VALID_DEVICE_STATUSES:
            raise ValueError(f"El estado debe ser uno de: {self.VALID_DEVICE_STATUSES}")
        
        # === VERIFICAR SI ES NECESARIO EL CAMBIO ===
        if self.status == status:
            return  # No hay cambio necesario
        
        # === VALIDACIONES ESPECÍFICAS DEL CAMBIO ===
        if not force:
            if status == "offline" and self._has_active_connections():
                # Advertencia pero permitir el cambio
                self._log_device_event(
                    "warning", 
                    f"Device '{self.name}' going offline with active connections"
                )
        
        # === REALIZAR EL CAMBIO ===
        old_status = self.status
        self.status = status
        
        # === EFECTOS SECUNDARIOS DEL CAMBIO DE ESTADO ===
        if status == "offline":
            self._handle_going_offline()
        elif status == "online":
            self._handle_going_online()
        
        # === ACTUALIZAR ACTIVIDAD Y LOGGING ===
        self._update_last_activity()
        self._log_device_event(
            "status_change", 
            f"Device '{self.name}' status changed from '{old_status}' to '{status}'"
        )
    
    def _has_active_connections(self) -> bool:
        """
        Verifica si el dispositivo tiene conexiones activas.
        
        Returns:
            bool: True si hay al menos una interfaz conectada y activa
        """
        return any(iface.isConnected() and iface.isUp() for iface in self.interfaces)
    
    def _handle_going_offline(self) -> None:
        """
        Maneja las acciones necesarias cuando el dispositivo se desconecta.
        """
        # Limpiar colas de paquetes para evitar procesamiento en estado offline
        self.incomingQueue.clear()
        self.outgoingQueue.clear()
        
        # Podrían agregarse más acciones específicas aquí
    
    def _handle_going_online(self) -> None:
        """
        Maneja las acciones necesarias cuando el dispositivo se conecta.
        """
        # Inicializar o reinicializar componentes necesarios
        # En una implementación más completa, aquí se podría:
        # - Reiniciar protocolos de routing
        # - Reestablecer sesiones de management
        # - Sincronizar con sistemas de monitoreo
        pass
    
    def isOnline(self) -> bool:
        """
        Verifica si el dispositivo está online de forma thread-safe.
        
        Returns:
            bool: True si el dispositivo está en estado online
        """
        return self.status == "online"
    
    def isOffline(self) -> bool:
        """
        Verifica si el dispositivo está offline de forma thread-safe.
        
        Returns:
            bool: True si el dispositivo está en estado offline
        """
        return self.status == "offline"
    
    # === PROCESAMIENTO DE PAQUETES ===
    
    def receivePacket(self, packet: Any, source_interface: Optional[str] = None) -> bool:
        """
        Recibe un paquete y lo agrega al historial con validaciones completas.
        
        Args:
            packet (Any): Paquete a recibir (puede ser string, Packet object, etc.)
            source_interface (Optional[str]): Nombre de la interfaz por donde llegó
        
        Returns:
            bool: True si el paquete fue recibido exitosamente
            
        Raises:
            DeviceOfflineError: Si el dispositivo está offline
        """
        # === VALIDACIONES PREVIAS ===
        if not self.isOnline():
            raise DeviceOfflineError("receive packet", self.name)
        
        if packet is None:
            return False
        
        # === AGREGAR AL HISTORIAL ===
        try:
            # Crear entrada de historial con metadatos
            history_entry = {
                "packet": packet,
                "timestamp": self._get_current_time(),
                "source_interface": source_interface,
                "device": self.name
            }
            
            self.receivedPacketsHistory.push(history_entry)
            
            # === ACTUALIZAR ESTADÍSTICAS ===
            self._total_packets_processed += 1
            self._update_last_activity()
            
            # === LOGGING ===
            self._log_device_event("packet_received", f"Packet received on device '{self.name}'")
            
            return True
            
        except Exception as e:
            self._log_device_event("error", f"Error receiving packet on device '{self.name}': {str(e)}")
            return False
    
    def processOutgoingQueue(self) -> List[Any]:
        """
        Procesa todos los paquetes en la cola de salida con manejo robusto de errores.
        
        Returns:
            List[Any]: Lista de paquetes procesados exitosamente
            
        Raises:
            DeviceOfflineError: Si el dispositivo está offline
        """
        if not self.isOnline():
            raise DeviceOfflineError("process outgoing queue", self.name)
        
        processed_packets = []
        errors_encountered = 0
        
        while not self.outgoingQueue.is_empty():
            try:
                packet = self.outgoingQueue.dequeue()
                
                # Simular procesamiento del paquete
                if self._process_single_packet(packet):
                    processed_packets.append(packet)
                    self._total_packets_processed += 1
                else:
                    errors_encountered += 1
                
            except Exception as e:
                errors_encountered += 1
                self._log_device_event("error", f"Error processing packet: {str(e)}")
                
                # Evitar bucle infinito en caso de errores persistentes
                if errors_encountered > 10:
                    self._log_device_event("error", "Too many processing errors, aborting queue processing")
                    break
        
        # === ACTUALIZAR ACTIVIDAD ===
        if processed_packets:
            self._update_last_activity()
        
        # === LOGGING DE RESULTADOS ===
        self._log_device_event(
            "queue_processed", 
            f"Processed {len(processed_packets)} packets, {errors_encountered} errors"
        )
        
        return processed_packets
    
    def _process_single_packet(self, packet: Any) -> bool:
        """
        Procesa un único paquete según el tipo de dispositivo.
        
        Args:
            packet (Any): Paquete a procesar
            
        Returns:
            bool: True si el procesamiento fue exitoso
        """
        # Procesamiento específico según tipo de dispositivo
        if self.type == "router":
            return self._router_process_packet(packet)
        elif self.type == "switch":
            return self._switch_process_packet(packet)
        elif self.type == "host":
            return self._host_process_packet(packet)
        elif self.type == "firewall":
            return self._firewall_process_packet(packet)
        else:
            # Procesamiento genérico
            return True
    
    def _router_process_packet(self, packet: Any) -> bool:
        """Procesamiento específico para routers."""
        try:
            # Verificar que tenemos tabla de rutas
            if not self.routing_table:
                print(f"⚠️  Router {self.name} no tiene tabla de rutas configurada")
                return False
            
            # Simular análisis de cabeceras IP
            if hasattr(packet, 'destination_ip') and hasattr(packet, 'source_ip'):
                dest_ip = packet.destination_ip
                source_ip = packet.source_ip
                
                # Buscar ruta en tabla de routing
                route = self.routing_table.lookup_route(dest_ip)
                
                if route:
                    # Simular decremento de TTL
                    if hasattr(packet, 'ttl'):
                        packet.ttl -= 1
                        if packet.ttl <= 0:
                            print(f"❌ Paquete descartado por TTL=0 en {self.name}")
                            return False
                    
                    # Reenviar a interfaz apropiada
                    target_interface = self.getInterface(route.interface)
                    if target_interface and target_interface.isActive():
                        print(f"🔄 Router {self.name} reenviando paquete a {route.interface}")
                        return True
                    else:
                        print(f"❌ Interfaz {route.interface} no disponible en {self.name}")
                        return False
                else:
                    print(f"❌ No se encontró ruta para {dest_ip} en {self.name}")
                    return False
            else:
                # Paquete sin información IP válida
                print(f"⚠️  Paquete sin información IP válida en {self.name}")
                return False
                
        except Exception as e:
            print(f"❌ Error procesando paquete en router {self.name}: {str(e)}")
            return False
    
    def _switch_process_packet(self, packet: Any) -> bool:
        """Procesamiento específico para switches."""
        # En una implementación completa, aquí iría:
        # - Análisis de cabeceras Ethernet
        # - Consulta/actualización de tabla MAC
        # - Flooding o forwarding según corresponda
        return True
    
    def _host_process_packet(self, packet: Any) -> bool:
        """Procesamiento específico para hosts."""
        # En una implementación completa, aquí iría:
        # - Verificar si el paquete es para este host
        # - Procesar por aplicación correspondiente
        # - Generar respuestas si es necesario
        return True
    
    def _firewall_process_packet(self, packet: Any) -> bool:
        """Procesamiento específico para firewalls."""
        if not self.firewall_manager:
            return True
        
        # Evaluar paquete contra reglas de firewall
        permitted, matched_rule, acl_name = self.firewall_manager.evaluate_packet(packet)
        
        if not permitted:
            print(f"🚫 Paquete {getattr(packet, 'id', 'unknown')} bloqueado por firewall {self.name}")
            print(f"   Regla: {matched_rule.id if matched_rule else 'N/A'} en ACL: {acl_name}")
            return False
        
        # Si está permitido, procesar normalmente
        print(f"✅ Paquete {getattr(packet, 'id', 'unknown')} permitido por firewall {self.name}")
        return True
    
    def addPacketToOutgoingQueue(self, packet: Any) -> bool:
        """
        Agrega un paquete a la cola de salida con validaciones.
        
        Args:
            packet (Any): Paquete a agregar a la cola
        
        Returns:
            bool: True si el paquete fue agregado exitosamente
        """
        if not self.isOnline():
            return False
        
        if packet is None:
            return False
        
        try:
            self.outgoingQueue.enqueue(packet)
            self._update_last_activity()
            return True
        except Exception:
            return False
    
    # === GESTIÓN DE NOMBRES ===
    
    def setHostname(self, newName: str) -> None:
        """
        Establece un nuevo nombre para el dispositivo con validaciones completas.
        
        Args:
            newName (str): Nuevo nombre para el dispositivo
        
        Raises:
            ValidationError: Si el nuevo nombre no es válido
            
        Example:
            >>> device = Device("Router-1", "router")
            >>> device.setHostname("Core-Router")
            >>> print(device.name)
            Core-Router
        """
        # === VALIDAR NUEVO NOMBRE ===
        if VALIDATORS_AVAILABLE:
            DataValidator.validate_device_name(newName)
        elif not isinstance(newName, str) or not newName.strip():
            raise ValueError("El nuevo nombre debe ser un string no vacío")
        
        # === REALIZAR EL CAMBIO ===
        oldName = self.name
        self.name = newName.strip()
        
        # === ACTUALIZAR ACTIVIDAD Y LOGGING ===
        self._update_last_activity()
        self._log_device_event("hostname_changed", f"Hostname changed from '{oldName}' to '{newName}'")
        
        print(f"Hostname cambiado de '{oldName}' a '{newName}'")
    
    # === MÉTODOS DE INFORMACIÓN Y ESTADÍSTICAS ===
    
    def showHistory(self, max_entries: int = 20) -> None:
        """
        Muestra el historial de paquetes recibidos con formato mejorado.
        
        Args:
            max_entries (int): Número máximo de entradas a mostrar
        """
        print(f"\n{'='*60}")
        print(f"HISTORIAL DE PAQUETES RECIBIDOS - {self.name}")
        print(f"{'='*60}")
        print(f"Estado: {self.status.upper()} | Tipo: {self.type.upper()}")
        print(f"Total procesados: {self._total_packets_processed}")
        print(f"{'='*60}")
        
        if self.receivedPacketsHistory.is_empty():
            print("📭 No hay paquetes en el historial")
        else:
            packets = self.receivedPacketsHistory.getAll()
            display_count = min(len(packets), max_entries)
            
            print(f"📦 Mostrando {display_count} de {len(packets)} paquetes más recientes:")
            print("-" * 60)
            
            for i, packet_entry in enumerate(packets[:display_count], 1):
                if isinstance(packet_entry, dict):
                    # Entrada con metadatos
                    packet = packet_entry.get("packet", "Unknown")
                    timestamp = packet_entry.get("timestamp", "Unknown")
                    source_iface = packet_entry.get("source_interface", "Unknown")
                    print(f"{i:3}. [{timestamp}] via {source_iface}: {packet}")
                else:
                    # Entrada simple (compatibilidad hacia atrás)
                    print(f"{i:3}. {packet_entry}")
            
            if len(packets) > max_entries:
                print(f"... y {len(packets) - max_entries} entradas más (use parámetro max_entries para ver más)")
        
        print("=" * 60)
    
    def showQueue(self) -> None:
        """
        Muestra los paquetes pendientes en las colas con información detallada.
        """
        print(f"\n{'='*50}")
        print(f"COLAS DE PAQUETES - {self.name}")
        print(f"{'='*50}")
        print(f"Estado: {self.status.upper()} | Tipo: {self.type.upper()}")
        print(f"{'='*50}")
        
        # === COLA DE ENTRADA ===
        print("📥 COLA DE ENTRADA:")
        if self.incomingQueue.is_empty():
            print("  ✅ Vacía")
        else:
            incoming_packets = self.incomingQueue.getAll()
            print(f"  📊 {len(incoming_packets)} paquetes pendientes:")
            for i, packet in enumerate(incoming_packets[:10], 1):  # Mostrar máximo 10
                print(f"    {i}. {packet}")
            if len(incoming_packets) > 10:
                print(f"    ... y {len(incoming_packets) - 10} paquetes más")
        
        print()
        
        # === COLA DE SALIDA ===
        print("📤 COLA DE SALIDA:")
        if self.outgoingQueue.is_empty():
            print("  ✅ Vacía")
        else:
            outgoing_packets = self.outgoingQueue.getAll()
            print(f"  📊 {len(outgoing_packets)} paquetes pendientes:")
            for i, packet in enumerate(outgoing_packets[:10], 1):  # Mostrar máximo 10
                print(f"    {i}. {packet}")
            if len(outgoing_packets) > 10:
                print(f"    ... y {len(outgoing_packets) - 10} paquetes más")
        
        print("=" * 50)
    
    def showInterfaces(self, detailed: bool = False) -> None:
        """
        Muestra la configuración de las interfaces con información completa.
        
        Args:
            detailed (bool): Si True, muestra información detallada de cada interfaz
        """
        print(f"\n{'='*60}")
        print(f"INTERFACES DE RED - {self.name}")
        print(f"{'='*60}")
        print(f"Dispositivo: {self.type.upper()} | Estado: {self.status.upper()}")
        print(f"Total interfaces: {len(self.interfaces)} | Activas: {len(self.getActiveInterfaces())} | Conectadas: {len(self.getConnectedInterfaces())}")
        print(f"{'='*60}")
        
        if not self.interfaces:
            print("🔌 No hay interfaces configuradas")
        else:
            for i, interface in enumerate(self.interfaces, 1):
                status_icon = "🟢" if interface.isUp() else "🔴"
                connection_icon = "🔗" if interface.isConnected() else "❌"
                
                print(f"{i:2}. {status_icon} {connection_icon} {interface}")
                
                if detailed:
                    # Información adicional en modo detallado
                    print(f"     📍 Estado: {interface.status}")
                    if interface.ipAddress:
                        print(f"     🌐 IP: {interface.ipAddress}")
                    if interface.macAddress:
                        print(f"     🏷️  MAC: {interface.macAddress}")
                    if interface.isConnected():
                        print(f"     🔗 Conectada a: {interface.connectedTo.name}")
                    
                    # Estadísticas de cola
                    queue_size = len(interface.outgoingQueue) if hasattr(interface.outgoingQueue, '__len__') else 0
                    print(f"     📊 Cola salida: {queue_size} paquetes")
                    print()
        
        print("=" * 60)
    
    def getInterfaceCount(self) -> int:
        """
        Retorna el número total de interfaces del dispositivo.
        
        Returns:
            int: Número de interfaces configuradas
        """
        return len(self.interfaces)
    
    def getDeviceStatistics(self) -> Dict[str, Any]:
        """
        Retorna estadísticas completas del dispositivo.
        
        Returns:
            Dict[str, Any]: Diccionario con estadísticas detalladas
        """
        return {
            "device_info": {
                "name": self.name,
                "type": self.type,
                "status": self.status,
                "creation_time": self._creation_time,
                "last_activity": self._last_activity_time
            },
            "interfaces": {
                "total": len(self.interfaces),
                "active": len(self.getActiveInterfaces()),
                "connected": len(self.getConnectedInterfaces()),
                "by_status": self._get_interfaces_by_status_count()
            },
            "packet_processing": {
                "total_processed": self._total_packets_processed,
                "history_size": len(self.receivedPacketsHistory),
                "incoming_queue_size": len(self.incomingQueue),
                "outgoing_queue_size": len(self.outgoingQueue)
            },
            "queue_statistics": {
                "history_stats": self.receivedPacketsHistory.get_statistics() if hasattr(self.receivedPacketsHistory, 'get_statistics') else {},
                "incoming_stats": self.incomingQueue.get_statistics() if hasattr(self.incomingQueue, 'get_statistics') else {},
                "outgoing_stats": self.outgoingQueue.get_statistics() if hasattr(self.outgoingQueue, 'get_statistics') else {}
            }
        }
        
        # Agregar estadísticas de routing si es un router
        if self.type == "router" and self.routing_table:
            stats["routing"] = self.routing_table.get_statistics()
        
        # Agregar estadísticas de firewall si es un firewall
        if self.type == "firewall" and self.firewall_manager:
            stats["firewall"] = self.firewall_manager.get_statistics()
        
        # Agregar estadísticas de VLANs si es un switch
        if self.type == "switch" and self.vlan_manager:
            stats["vlans"] = self.vlan_manager.get_statistics()
        
        # Agregar estadísticas de RIP si es un router
        if self.type == "router" and self.rip_protocol:
            stats["rip"] = self.rip_protocol.get_statistics()
        
        return stats
    
    # === MÉTODOS DE ROUTING (solo para routers) ===
    
    def add_route(self, destination: str, next_hop: str, interface: str, 
                  metric: int = 1, protocol: str = "static") -> bool:
        """
        Agrega una ruta a la tabla de routing (solo para routers).
        
        Args:
            destination: Red de destino (ej: "192.168.1.0/24")
            next_hop: Próximo salto (ej: "192.168.0.1")
            interface: Interfaz de salida
            metric: Métrica de la ruta
            protocol: Protocolo de routing
            
        Returns:
            bool: True si la ruta fue agregada exitosamente
        """
        if self.type != "router":
            print(f"❌ Solo los routers pueden tener tabla de rutas. {self.name} es un {self.type}")
            return False
        
        if not self.routing_table:
            print(f"❌ Router {self.name} no tiene tabla de rutas inicializada")
            return False
        
        return self.routing_table.add_route(destination, next_hop, interface, metric, protocol)
    
    def remove_route(self, destination: str) -> bool:
        """
        Elimina una ruta de la tabla de routing (solo para routers).
        
        Args:
            destination: Red de destino a eliminar
            
        Returns:
            bool: True si la ruta fue eliminada exitosamente
        """
        if self.type != "router" or not self.routing_table:
            return False
        
        return self.routing_table.remove_route(destination)
    
    def show_routing_table(self) -> str:
        """
        Muestra la tabla de rutas (solo para routers).
        
        Returns:
            str: Tabla de rutas formateada o mensaje de error
        """
        if self.type != "router":
            return f"❌ Solo los routers tienen tabla de rutas. {self.name} es un {self.type}"
        
        if not self.routing_table:
            return f"❌ Router {self.name} no tiene tabla de rutas configurada"
        
        return self.routing_table.show_routing_table()
    
    def set_default_route(self, next_hop: str, interface: str) -> bool:
        """
        Establece la ruta por defecto (solo para routers).
        
        Args:
            next_hop: Próximo salto para la ruta por defecto
            interface: Interfaz de salida
            
        Returns:
            bool: True si se estableció exitosamente
        """
        if self.type != "router" or not self.routing_table:
            return False
        
        return self.routing_table.set_default_route(next_hop, interface)
    
    def clear_routes(self, protocol: str = None) -> int:
        """
        Limpia rutas de la tabla (solo para routers).
        
        Args:
            protocol: Si se especifica, solo limpia rutas de ese protocolo
            
        Returns:
            int: Número de rutas eliminadas
        """
        if self.type != "router" or not self.routing_table:
            return 0
        
        return self.routing_table.clear_routes(protocol)
    
    # === MÉTODOS DE FIREWALL (solo para firewalls) ===
    
    def create_acl(self, name: str, acl_type: str = "extended") -> bool:
        """Crea una nueva ACL (solo para firewalls)."""
        if self.type != "firewall" or not self.firewall_manager:
            print(f"❌ Solo los firewalls pueden crear ACLs. {self.name} es un {self.type}")
            return False
        
        return self.firewall_manager.create_acl(name, acl_type)
    
    def add_firewall_rule(self, acl_name: str, action: str, protocol: str, 
                         source_ip: str, destination_ip: str, 
                         source_wildcard: str = "0.0.0.0",
                         destination_wildcard: str = "0.0.0.0",
                         description: str = "") -> bool:
        """Agrega una regla a una ACL (solo para firewalls)."""
        if self.type != "firewall" or not self.firewall_manager:
            print(f"❌ Solo los firewalls pueden agregar reglas. {self.name} es un {self.type}")
            return False
        
        acl = self.firewall_manager.get_acl(acl_name)
        if not acl:
            print(f"❌ ACL '{acl_name}' no encontrada")
            return False
        
        return acl.add_rule(action, protocol, source_ip, destination_ip, 
                           source_wildcard, destination_wildcard, description=description)
    
    def show_acl(self, acl_name: str = None) -> str:
        """Muestra las reglas de una ACL (solo para firewalls)."""
        if self.type != "firewall" or not self.firewall_manager:
            return f"❌ Solo los firewalls tienen ACLs. {self.name} es un {self.type}"
        
        if acl_name:
            acl = self.firewall_manager.get_acl(acl_name)
            if not acl:
                return f"❌ ACL '{acl_name}' no encontrada"
            return acl.show_rules()
        else:
            # Mostrar todas las ACLs
            if not self.firewall_manager.acls:
                return "No hay ACLs configuradas"
            
            output = [f"ACLs configuradas en {self.name}:"]
            for name, acl in self.firewall_manager.acls.items():
                output.append(f"\n{acl.show_rules()}")
            return "\n".join(output)
    
    def activate_acl(self, acl_name: str) -> bool:
        """Activa una ACL (solo para firewalls)."""
        if self.type != "firewall" or not self.firewall_manager:
            print(f"❌ Solo los firewalls pueden activar ACLs. {self.name} es un {self.type}")
            return False
        
        return self.firewall_manager.activate_acl(acl_name)
    
    def show_security_log(self, max_entries: int = 50) -> str:
        """Muestra el log de seguridad (solo para firewalls)."""
        if self.type != "firewall" or not self.firewall_manager:
            return f"❌ Solo los firewalls tienen logs de seguridad. {self.name} es un {self.type}"
        
        return self.firewall_manager.show_security_log(max_entries)
    
    def clear_security_log(self) -> int:
        """Limpia el log de seguridad (solo para firewalls)."""
        if self.type != "firewall" or not self.firewall_manager:
            print(f"❌ Solo los firewalls pueden limpiar logs. {self.name} es un {self.type}")
            return 0
        
        return self.firewall_manager.clear_security_log()
    
    # === MÉTODOS DE VLAN (solo para switches) ===
    
    def create_vlan(self, vlan_id: int, name: str, description: str = "") -> bool:
        """Crea una nueva VLAN (solo para switches)."""
        if self.type != "switch" or not self.vlan_manager:
            print(f"❌ Solo los switches pueden crear VLANs. {self.name} es un {self.type}")
            return False
        
        return self.vlan_manager.create_vlan(vlan_id, name, description)
    
    def delete_vlan(self, vlan_id: int) -> bool:
        """Elimina una VLAN (solo para switches)."""
        if self.type != "switch" or not self.vlan_manager:
            print(f"❌ Solo los switches pueden eliminar VLANs. {self.name} es un {self.type}")
            return False
        
        return self.vlan_manager.delete_vlan(vlan_id)
    
    def configure_interface_access(self, interface_name: str, vlan_id: int) -> bool:
        """Configura una interfaz en modo access (solo para switches)."""
        if self.type != "switch" or not self.vlan_manager:
            print(f"❌ Solo los switches pueden configurar VLANs. {self.name} es un {self.type}")
            return False
        
        return self.vlan_manager.configure_interface_access(interface_name, vlan_id)
    
    def configure_interface_trunk(self, interface_name: str, allowed_vlans: List[int] = None, 
                                 native_vlan: int = 1) -> bool:
        """Configura una interfaz en modo trunk (solo para switches)."""
        if self.type != "switch" or not self.vlan_manager:
            print(f"❌ Solo los switches pueden configurar VLANs. {self.name} es un {self.type}")
            return False
        
        return self.vlan_manager.configure_interface_trunk(interface_name, allowed_vlans, native_vlan)
    
    def show_vlans(self) -> str:
        """Muestra todas las VLANs (solo para switches)."""
        if self.type != "switch" or not self.vlan_manager:
            return f"❌ Solo los switches tienen VLANs. {self.name} es un {self.type}"
        
        return self.vlan_manager.show_vlans()
    
    def show_vlan_interfaces(self) -> str:
        """Muestra la configuración de VLAN de las interfaces (solo para switches)."""
        if self.type != "switch" or not self.vlan_manager:
            return f"❌ Solo los switches tienen VLANs. {self.name} es un {self.type}"
        
        return self.vlan_manager.show_vlan_interfaces()
    
    def show_vlan_detail(self, vlan_id: int) -> str:
        """Muestra detalles de una VLAN específica (solo para switches)."""
        if self.type != "switch" or not self.vlan_manager:
            return f"❌ Solo los switches tienen VLANs. {self.name} es un {self.type}"
        
        return self.vlan_manager.show_vlan_detail(vlan_id)
    
    # === MÉTODOS DE RIP (solo para routers) ===
    
    def enable_rip(self, version: int = 2) -> bool:
        """Habilita el protocolo RIP (solo para routers)."""
        if self.type != "router" or not self.rip_protocol:
            print(f"❌ Solo los routers pueden usar RIP. {self.name} es un {self.type}")
            return False
        
        self.rip_protocol.enable(version)
        print(f"✅ RIP v{version} habilitado en {self.name}")
        return True
    
    def disable_rip(self) -> bool:
        """Deshabilita el protocolo RIP (solo para routers)."""
        if self.type != "router" or not self.rip_protocol:
            print(f"❌ Solo los routers pueden usar RIP. {self.name} es un {self.type}")
            return False
        
        self.rip_protocol.disable()
        print(f"❌ RIP deshabilitado en {self.name}")
        return True
    
    def add_rip_network(self, network: str) -> bool:
        """Agrega una red al protocolo RIP (solo para routers)."""
        if self.type != "router" or not self.rip_protocol:
            print(f"❌ Solo los routers pueden usar RIP. {self.name} es un {self.type}")
            return False
        
        self.rip_protocol.add_network(network)
        print(f"✅ Red {network} agregada a RIP en {self.name}")
        return True
    
    def enable_rip_interface(self, interface_name: str, send_version: int = 2, receive_version: int = 2) -> bool:
        """Habilita RIP en una interfaz específica (solo para routers)."""
        if self.type != "router" or not self.rip_protocol:
            print(f"❌ Solo los routers pueden usar RIP. {self.name} es un {self.type}")
            return False
        
        self.rip_protocol.enable_interface(interface_name, send_version, receive_version)
        print(f"✅ RIP habilitado en interfaz {interface_name} de {self.name}")
        return True
    
    def show_rip_database(self) -> str:
        """Muestra la base de datos RIP (solo para routers)."""
        if self.type != "router" or not self.rip_protocol:
            return f"❌ Solo los routers tienen RIP. {self.name} es un {self.type}"
        
        return self.rip_protocol.show_rip_database()
    
    def show_rip_interfaces(self) -> str:
        """Muestra la configuración de interfaces RIP (solo para routers)."""
        if self.type != "router" or not self.rip_protocol:
            return f"❌ Solo los routers tienen RIP. {self.name} es un {self.type}"
        
        return self.rip_protocol.show_rip_interfaces()
    
    def show_rip_neighbors(self) -> str:
        """Muestra los vecinos RIP (solo para routers)."""
        if self.type != "router" or not self.rip_protocol:
            return f"❌ Solo los routers tienen RIP. {self.name} es un {self.type}"
        
        return self.rip_protocol.show_rip_neighbors()
    
    def _get_interfaces_by_status_count(self) -> Dict[str, int]:
        """Retorna conteo de interfaces por estado."""
        status_count = {}
        for interface in self.interfaces:
            status = interface.status
            status_count[status] = status_count.get(status, 0) + 1
        return status_count
    
    # === MÉTODOS DE SERIALIZACIÓN (MÓDULO 6 - Configuration Persistence) ===
    
    def to_dict(self) -> dict:
        """
        Serializa el dispositivo a un diccionario para guardado JSON con validaciones.
        
        Returns:
            dict: Representación serializable del dispositivo con metadatos completos
        """
        device_dict = {
            "metadata": {
                "serialization_version": "1.0",
                "creation_time": self._creation_time,
                "last_activity": self._last_activity_time
            },
            "device_info": {
                "name": self.name,
                "type": self.type,
                "status": self.status,
                "total_packets_processed": self._total_packets_processed
            },
            "interfaces": [],
            "statistics": {
                "interface_count": len(self.interfaces),
                "active_interfaces": len(self.getActiveInterfaces()),
                "connected_interfaces": len(self.getConnectedInterfaces())
            }
        }
        
        # === SERIALIZAR INTERFACES ===
        for interface in self.interfaces:
            try:
                device_dict["interfaces"].append(interface.to_dict())
            except Exception as e:
                # Manejar errores de serialización de interfaces individuales
                self._log_device_event("error", f"Error serializing interface {interface.name}: {str(e)}")
        
        # === SERIALIZAR HISTORIAL DE PAQUETES (LIMITADO) ===
        history_items = []
        if not self.receivedPacketsHistory.is_empty():
            # Limitar historial para evitar archivos JSON muy grandes
            recent_packets = self.receivedPacketsHistory.getAll()[:50]
            for item in recent_packets:
                try:
                    if isinstance(item, dict):
                        # Serializar metadatos completos
                        history_items.append({
                            "packet": str(item.get("packet", "")),
                            "timestamp": item.get("timestamp", ""),
                            "source_interface": item.get("source_interface", "")
                        })
                    else:
                        # Compatibilidad hacia atrás
                        history_items.append({"packet": str(item), "timestamp": "", "source_interface": ""})
                except Exception:
                    # Si falla la serialización de un paquete, continuar con los demás
                    history_items.append({"packet": "Serialization Error", "timestamp": "", "source_interface": ""})
        
        device_dict["received_packets_history"] = history_items
        
        return device_dict
    
    @classmethod
    def from_dict(cls, device_dict: dict, interface_mapping: dict = None) -> 'Device':
        """
        Crea un dispositivo desde un diccionario deserializado con validaciones completas.
        
        Args:
            device_dict (dict): Diccionario con datos del dispositivo
            interface_mapping (dict): Mapeo de nombres de interfaces para conexiones
            
        Returns:
            Device: Nueva instancia del dispositivo completamente configurada
            
        Raises:
            ValidationError: Si los datos del diccionario no son válidos
            KeyError: Si faltan campos requeridos
        """
        # === VALIDAR ESTRUCTURA DEL DICCIONARIO ===
        if not isinstance(device_dict, dict):
            raise ValidationError("device_dict debe ser un diccionario", "device_dict", type(device_dict))
        
        # Verificar campos requeridos
        required_fields = ["device_info"]
        for field in required_fields:
            if field not in device_dict:
                raise KeyError(f"Campo requerido '{field}' no encontrado en device_dict")
        
        device_info = device_dict["device_info"]
        if "name" not in device_info or "type" not in device_info:
            raise KeyError("Campos 'name' y 'type' son requeridos en device_info")
        
        # === CREAR DISPOSITIVO ===
        device = cls(device_info["name"], device_info["type"])
        
        # === RESTAURAR ESTADO ===
        if "status" in device_info:
            device.setStatus(device_info["status"])
        
        # === RESTAURAR ESTADÍSTICAS ===
        if "total_packets_processed" in device_info:
            device._total_packets_processed = device_info["total_packets_processed"]
        
        if "metadata" in device_dict:
            metadata = device_dict["metadata"]
            if "creation_time" in metadata:
                device._creation_time = metadata["creation_time"]
            if "last_activity" in metadata:
                device._last_activity_time = metadata["last_activity"]
        
        # === RECREAR INTERFACES ===
        if "interfaces" in device_dict:
            for interface_data in device_dict["interfaces"]:
                try:
                    interface = Interface.from_dict(interface_data)
                    device.interfaces.append(interface)
                    
                    # Registrar interfaz en mapeo global si se proporciona
                    if interface_mapping is not None:
                        interface_key = f"{device.name}:{interface.name}"
                        interface_mapping[interface_key] = interface
                        
                except Exception as e:
                    # Log error pero continuar con otras interfaces
                    device._log_device_event("error", f"Error deserializing interface: {str(e)}")
        
        # === RESTAURAR HISTORIAL DE PAQUETES ===
        if "received_packets_history" in device_dict:
            for packet_data in device_dict["received_packets_history"]:
                try:
                    if isinstance(packet_data, dict):
                        # Entrada con metadatos
                        device.receivePacket(
                            packet_data.get("packet", ""),
                            packet_data.get("source_interface", "")
                        )
                    else:
                        # Compatibilidad hacia atrás
                        device.receivePacket(str(packet_data))
                except Exception:
                    # Continuar con otros paquetes si uno falla
                    continue
        
        return device
    
    def get_config_summary(self) -> str:
        """
        Retorna un resumen de configuración del dispositivo en formato legible.
        
        Returns:
            str: Resumen detallado de la configuración del dispositivo
        """
        summary = []
        summary.append(f"Device: {self.name} ({self.type}) - {self.status}")
        summary.append(f"  Created: {self._format_timestamp(self._creation_time)}")
        summary.append(f"  Last Activity: {self._format_timestamp(self._last_activity_time)}")
        summary.append(f"  Interfaces: {len(self.interfaces)} total, {len(self.getActiveInterfaces())} active")
        summary.append(f"  Packets Processed: {self._total_packets_processed}")
        
        # Detalles de interfaces
        for interface in self.interfaces:
            ip_info = f" [{interface.ipAddress}]" if interface.ipAddress else ""
            status_indicator = "🟢" if interface.isUp() else "🔴"
            connection_info = ""
            
            if interface.isConnected():
                # Buscar dispositivo padre de la interfaz conectada (información limitada)
                connected_device = "Unknown"
                connection_info = f" <-> {connected_device}:{interface.connectedTo.name if interface.connectedTo else 'None'}"
            
            summary.append(f"    {status_indicator} {interface.name}{ip_info} ({interface.status}){connection_info}")
        
        return "\n".join(summary)
    
    # === MÉTODOS AUXILIARES Y UTILIDADES ===
    
    def _update_last_activity(self) -> None:
        """Actualiza el timestamp de última actividad."""
        self._last_activity_time = self._get_current_time()
    
    def _get_current_time(self) -> float:
        """Retorna el timestamp actual."""
        import time
        return time.time()
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Formatea un timestamp para display legible."""
        try:
            import datetime
            return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return str(timestamp)
    
    def _log_device_event(self, event_type: str, message: str) -> None:
        """
        Registra eventos del dispositivo (placeholder para sistema de logging).
        
        Args:
            event_type (str): Tipo de evento (info, warning, error, etc.)
            message (str): Mensaje descriptivo del evento
        """
        # En una implementación completa, esto se conectaría a un sistema de logging
        # Por ahora, opcionalmente imprimir en debug mode
        pass
    
    # === MÉTODOS ESPECIALES (DUNDER METHODS) ===
    
    def __str__(self) -> str:
        """
        Representación en string del dispositivo para debugging y display.
        
        Returns:
            str: Representación legible del dispositivo
        """
        status_indicator = "🟢" if self.isOnline() else "🔴"
        return f"{status_indicator} {self.name} ({self.type}) - {len(self.interfaces)} interfaces"
    
    def __repr__(self) -> str:
        """
        Representación oficial del dispositivo para debugging avanzado.
        
        Returns:
            str: Representación que permite recrear el objeto
        """
        return f"Device(name='{self.name}', deviceType='{self.type}')"
    
    def __eq__(self, other) -> bool:
        """
        Permite comparar dos dispositivos por igualdad basada en nombre y tipo.
        
        Args:
            other: Otro dispositivo para comparar
            
        Returns:
            bool: True si ambos dispositivos tienen el mismo nombre y tipo
        """
        if not isinstance(other, Device):
            return False
        return self.name == other.name and self.type == other.type
    
    def __hash__(self) -> int:
        """
        Permite usar dispositivos como claves en diccionarios y sets.
        
        Returns:
            int: Hash basado en nombre y tipo del dispositivo
        """
        return hash((self.name, self.type))
    
    def __len__(self) -> int:
        """
        Permite usar len() para obtener el número de interfaces.
        
        Returns:
            int: Número de interfaces del dispositivo
        """
        return len(self.interfaces) 

class RoutingTable:
    def __init__(self):
        self.routes = {}
    
    def add_route(self, destination, next_hop, interface, metric=1):
        self.routes[destination] = {
            'next_hop': next_hop,
            'interface': interface,
            'metric': metric
        }
    
    def lookup_route(self, destination):
        return self.routes.get(destination)