#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Validaciones Centralizadas
===================================

Contiene todas las validaciones de datos y entrada de usuario utilizadas 
a lo largo del simulador de red. Proporciona funciones de validación 
reutilizables y robustas para asegurar la integridad de los datos.

Author: Network Simulator Project
Version: 1.0
"""

import re
import ipaddress
from typing import Any, List, Optional, Union, Dict
from enum import Enum


class DeviceType(Enum):
    """Tipos de dispositivos válidos en la red"""
    ROUTER = "router"
    SWITCH = "switch" 
    HOST = "host"
    FIREWALL = "firewall"


class InterfaceStatus(Enum):
    """Estados válidos para interfaces de red"""
    UP = "up"
    DOWN = "down"
    SHUTDOWN = "shutdown"
    NO_SHUTDOWN = "no shutdown"


class DeviceStatus(Enum):
    """Estados válidos para dispositivos de red"""
    ONLINE = "online"
    OFFLINE = "offline"


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class DataValidator:
    """
    Clase principal de validaciones con métodos estáticos para validar
    diferentes tipos de datos utilizados en el simulador de red.
    """
    
    # === VALIDACIONES DE NOMBRES Y IDENTIFICADORES ===
    
    @staticmethod
    def validate_device_name(name: str) -> bool:
        """
        Valida el nombre de un dispositivo de red.
        
        Reglas:
        - Debe ser string no vacío
        - Longitud entre 1 y 50 caracteres
        - Solo letras, números, guiones y guiones bajos
        - No puede empezar con número o guión
        
        Args:
            name: Nombre del dispositivo a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el nombre no es válido
        """
        if not isinstance(name, str):
            raise ValidationError("El nombre del dispositivo debe ser un string", "name", name)
        
        if not name or name.strip() == "":
            raise ValidationError("El nombre del dispositivo no puede estar vacío", "name", name)
        
        if len(name) > 50:
            raise ValidationError("El nombre del dispositivo no puede exceder 50 caracteres", "name", name)
        
        if len(name) < 1:
            raise ValidationError("El nombre del dispositivo debe tener al menos 1 caracter", "name", name)
        
        # Patrón: debe empezar con letra, seguido de letras, números, guiones o guiones bajos
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
            raise ValidationError(
                "El nombre del dispositivo debe empezar con letra y contener solo letras, números, guiones y guiones bajos", 
                "name", name
            )
        
        return True
    
    @staticmethod
    def validate_interface_name(name: str) -> bool:
        """
        Valida el nombre de una interfaz de red.
        
        Reglas:
        - Debe ser string no vacío
        - Longitud entre 1 y 20 caracteres
        - Formatos válidos: eth0, gi0/0, fa0/1, wan0, lan0, etc.
        
        Args:
            name: Nombre de la interfaz a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el nombre no es válido
        """
        if not isinstance(name, str):
            raise ValidationError("El nombre de la interfaz debe ser un string", "interface_name", name)
        
        if not name or name.strip() == "":
            raise ValidationError("El nombre de la interfaz no puede estar vacío", "interface_name", name)
        
        if len(name) > 20:
            raise ValidationError("El nombre de la interfaz no puede exceder 20 caracteres", "interface_name", name)
        
        # Patrones válidos para nombres de interfaces
        valid_patterns = [
            r'^eth\d+$',           # eth0, eth1, etc.
            r'^gi\d+/\d+$',        # gi0/0, gi1/1, etc.
            r'^fa\d+/\d+$',        # fa0/1, fa1/2, etc.
            r'^[a-zA-Z]+\d*$',     # wan0, lan0, dmz, inside, outside, etc.
            r'^[a-zA-Z0-9_-]+$'    # nombres personalizados
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, name):
                return True
        
        raise ValidationError(
            f"Nombre de interfaz '{name}' no sigue un formato válido (ej: eth0, gi0/0, fa0/1, wan0)", 
            "interface_name", name
        )
    
    # === VALIDACIONES DE DIRECCIONES DE RED ===
    
    @staticmethod
    def validate_ip_address(ip: str, allow_empty: bool = False) -> bool:
        """
        Valida una dirección IP v4.
        
        Args:
            ip: Dirección IP a validar
            allow_empty: Si se permite IP vacía
            
        Returns:
            bool: True si es válida
            
        Raises:
            ValidationError: Si la IP no es válida
        """
        if allow_empty and (not ip or ip.strip() == ""):
            return True
        
        if not isinstance(ip, str):
            raise ValidationError("La dirección IP debe ser un string", "ip_address", ip)
        
        if not ip or ip.strip() == "":
            raise ValidationError("La dirección IP no puede estar vacía", "ip_address", ip)
        
        try:
            # Usar el módulo ipaddress para validación robusta
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            raise ValidationError(f"'{ip}' no es una dirección IP v4 válida", "ip_address", ip)
    
    @staticmethod
    def validate_mac_address(mac: str, allow_empty: bool = False) -> bool:
        """
        Valida una dirección MAC.
        
        Args:
            mac: Dirección MAC a validar
            allow_empty: Si se permite MAC vacía
            
        Returns:
            bool: True si es válida
            
        Raises:
            ValidationError: Si la MAC no es válida
        """
        if allow_empty and (not mac or mac.strip() == ""):
            return True
        
        if not isinstance(mac, str):
            raise ValidationError("La dirección MAC debe ser un string", "mac_address", mac)
        
        if not mac or mac.strip() == "":
            raise ValidationError("La dirección MAC no puede estar vacía", "mac_address", mac)
        
        # Patrón MAC: XX:XX:XX:XX:XX:XX donde X es hexadecimal
        mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        
        if not re.match(mac_pattern, mac):
            raise ValidationError(
                f"'{mac}' no es una dirección MAC válida. Formato esperado: XX:XX:XX:XX:XX:XX", 
                "mac_address", mac
            )
        
        return True
    
    # === VALIDACIONES DE ESTADOS Y TIPOS ===
    
    @staticmethod
    def validate_device_type(device_type: str) -> bool:
        """
        Valida el tipo de dispositivo.
        
        Args:
            device_type: Tipo de dispositivo a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el tipo no es válido
        """
        if not isinstance(device_type, str):
            raise ValidationError("El tipo de dispositivo debe ser un string", "device_type", device_type)
        
        valid_types = [dt.value for dt in DeviceType]
        
        if device_type not in valid_types:
            raise ValidationError(
                f"Tipo de dispositivo '{device_type}' no válido. Tipos válidos: {valid_types}", 
                "device_type", device_type
            )
        
        return True
    
    @staticmethod
    def validate_device_status(status: str) -> bool:
        """
        Valida el estado de un dispositivo.
        
        Args:
            status: Estado del dispositivo a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el estado no es válido
        """
        if not isinstance(status, str):
            raise ValidationError("El estado del dispositivo debe ser un string", "device_status", status)
        
        valid_statuses = [ds.value for ds in DeviceStatus]
        
        if status not in valid_statuses:
            raise ValidationError(
                f"Estado de dispositivo '{status}' no válido. Estados válidos: {valid_statuses}", 
                "device_status", status
            )
        
        return True
    
    @staticmethod
    def validate_interface_status(status: str) -> bool:
        """
        Valida el estado de una interfaz.
        
        Args:
            status: Estado de la interfaz a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el estado no es válido
        """
        if not isinstance(status, str):
            raise ValidationError("El estado de la interfaz debe ser un string", "interface_status", status)
        
        valid_statuses = [is_.value for is_ in InterfaceStatus]
        
        if status not in valid_statuses:
            raise ValidationError(
                f"Estado de interfaz '{status}' no válido. Estados válidos: {valid_statuses}", 
                "interface_status", status
            )
        
        return True
    
    # === VALIDACIONES DE PAQUETES Y COMUNICACIÓN ===
    
    @staticmethod
    def validate_ttl(ttl: int) -> bool:
        """
        Valida el valor TTL (Time To Live) de un paquete.
        
        Args:
            ttl: Valor TTL a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el TTL no es válido
        """
        if not isinstance(ttl, int):
            raise ValidationError("El TTL debe ser un número entero", "ttl", ttl)
        
        if ttl < 0:
            raise ValidationError("El TTL no puede ser negativo", "ttl", ttl)
        
        if ttl > 255:
            raise ValidationError("El TTL no puede ser mayor a 255", "ttl", ttl)
        
        return True
    
    @staticmethod
    def validate_packet_content(content: str) -> bool:
        """
        Valida el contenido de un paquete.
        
        Args:
            content: Contenido del paquete a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el contenido no es válido
        """
        if not isinstance(content, str):
            raise ValidationError("El contenido del paquete debe ser un string", "packet_content", content)
        
        if len(content) > 1500:  # MTU típico de Ethernet
            raise ValidationError("El contenido del paquete no puede exceder 1500 caracteres", "packet_content", content)
        
        return True
    
    # === VALIDACIONES DE CONFIGURACIÓN Y ARCHIVOS ===
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Valida un nombre de archivo de configuración.
        
        Args:
            filename: Nombre del archivo a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el nombre no es válido
        """
        if not isinstance(filename, str):
            raise ValidationError("El nombre del archivo debe ser un string", "filename", filename)
        
        if not filename or filename.strip() == "":
            raise ValidationError("El nombre del archivo no puede estar vacío", "filename", filename)
        
        if len(filename) > 100:
            raise ValidationError("El nombre del archivo no puede exceder 100 caracteres", "filename", filename)
        
        # Caracteres no permitidos en nombres de archivo
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, filename):
            raise ValidationError(
                "El nombre del archivo contiene caracteres no válidos: < > : \" / \\ | ? *", 
                "filename", filename
            )
        
        # No debe empezar o terminar con punto o espacio
        if filename.startswith('.') or filename.endswith('.') or filename.startswith(' ') or filename.endswith(' '):
            raise ValidationError("El nombre del archivo no puede empezar o terminar con punto o espacio", "filename", filename)
        
        return True
    
    # === VALIDACIONES DE DATOS CARGADOS ===
    
    @staticmethod
    def validate_config_data(config_data: Dict) -> bool:
        """
        Valida la estructura de datos de configuración cargada desde JSON.
        
        Args:
            config_data: Diccionario con datos de configuración
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        if not isinstance(config_data, dict):
            raise ValidationError("Los datos de configuración deben ser un diccionario", "config_data", type(config_data))
        
        # Verificar secciones requeridas
        required_sections = ['metadata', 'network', 'devices', 'connections']
        for section in required_sections:
            if section not in config_data:
                raise ValidationError(f"Sección requerida '{section}' no encontrada en configuración", "config_data", config_data.keys())
        
        # Validar metadata
        metadata = config_data['metadata']
        if not isinstance(metadata, dict):
            raise ValidationError("La sección 'metadata' debe ser un diccionario", "metadata", type(metadata))
        
        # Validar network
        network_data = config_data['network']
        if not isinstance(network_data, dict):
            raise ValidationError("La sección 'network' debe ser un diccionario", "network", type(network_data))
        
        if 'name' not in network_data:
            raise ValidationError("El nombre de la red es requerido", "network_name", network_data)
        
        # Validar devices
        devices = config_data['devices']
        if not isinstance(devices, list):
            raise ValidationError("La sección 'devices' debe ser una lista", "devices", type(devices))
        
        # Validar connections
        connections = config_data['connections']
        if not isinstance(connections, list):
            raise ValidationError("La sección 'connections' debe ser una lista", "connections", type(connections))
        
        return True
    
    # === VALIDACIONES NUMÉRICAS ===
    
    @staticmethod
    def validate_positive_integer(value: Any, field_name: str, max_value: Optional[int] = None) -> bool:
        """
        Valida que un valor sea un entero positivo.
        
        Args:
            value: Valor a validar
            field_name: Nombre del campo para errores
            max_value: Valor máximo permitido (opcional)
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el valor no es válido
        """
        if not isinstance(value, int):
            raise ValidationError(f"El {field_name} debe ser un número entero", field_name, value)
        
        if value < 0:
            raise ValidationError(f"El {field_name} no puede ser negativo", field_name, value)
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"El {field_name} no puede ser mayor a {max_value}", field_name, value)
        
        return True
    
    @staticmethod
    def validate_non_empty_string(value: Any, field_name: str, max_length: Optional[int] = None) -> bool:
        """
        Valida que un valor sea un string no vacío.
        
        Args:
            value: Valor a validar
            field_name: Nombre del campo para errores
            max_length: Longitud máxima permitida (opcional)
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el valor no es válido
        """
        if not isinstance(value, str):
            raise ValidationError(f"El {field_name} debe ser un string", field_name, value)
        
        if not value or value.strip() == "":
            raise ValidationError(f"El {field_name} no puede estar vacío", field_name, value)
        
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"El {field_name} no puede exceder {max_length} caracteres", field_name, value)
        
        return True


class InputValidator:
    """
    Clase específica para validar entrada de usuario desde CLI o interfaces.
    """
    
    @staticmethod
    def validate_cli_command(command: str) -> bool:
        """
        Valida un comando CLI.
        
        Args:
            command: Comando a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el comando no es válido
        """
        if not isinstance(command, str):
            raise ValidationError("El comando debe ser un string", "command", command)
        
        if not command or command.strip() == "":
            raise ValidationError("El comando no puede estar vacío", "command", command)
        
        if len(command) > 500:
            raise ValidationError("El comando no puede exceder 500 caracteres", "command", command)
        
        # Verificar caracteres peligrosos (básico)
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '{', '}']
        for char in dangerous_chars:
            if char in command:
                raise ValidationError(f"El comando contiene caracteres no permitidos: {char}", "command", command)
        
        return True
    
    @staticmethod
    def validate_cli_arguments(args: List[str], max_args: Optional[int] = None) -> bool:
        """
        Valida argumentos de comando CLI.
        
        Args:
            args: Lista de argumentos
            max_args: Número máximo de argumentos (opcional)
            
        Returns:
            bool: True si son válidos
            
        Raises:
            ValidationError: Si los argumentos no son válidos
        """
        if not isinstance(args, list):
            raise ValidationError("Los argumentos deben ser una lista", "args", type(args))
        
        if max_args is not None and len(args) > max_args:
            raise ValidationError(f"Demasiados argumentos. Máximo: {max_args}", "args", len(args))
        
        for i, arg in enumerate(args):
            if not isinstance(arg, str):
                raise ValidationError(f"El argumento {i+1} debe ser un string", f"arg_{i+1}", type(arg))
            
            if len(arg) > 100:
                raise ValidationError(f"El argumento {i+1} no puede exceder 100 caracteres", f"arg_{i+1}", len(arg))
        
        return True


# === FUNCIONES DE CONVENIENCIA ===

def safe_validate(validator_func, *args, **kwargs) -> bool:
    """
    Ejecuta una función de validación de forma segura, retornando False en lugar de lanzar excepción.
    
    Args:
        validator_func: Función de validación a ejecutar
        *args: Argumentos posicionales para la función
        **kwargs: Argumentos con nombre para la función
        
    Returns:
        bool: True si la validación pasa, False si falla
    """
    try:
        return validator_func(*args, **kwargs)
    except ValidationError:
        return False


def get_validation_error_message(validator_func, *args, **kwargs) -> Optional[str]:
    """
    Ejecuta una función de validación y retorna el mensaje de error si falla.
    
    Args:
        validator_func: Función de validación a ejecutar
        *args: Argumentos posicionales para la función
        **kwargs: Argumentos con nombre para la función
        
    Returns:
        Optional[str]: Mensaje de error si la validación falla, None si pasa
    """
    try:
        validator_func(*args, **kwargs)
        return None
    except ValidationError as e:
        return e.message 