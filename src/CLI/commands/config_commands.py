from typing import List
from ..command_base import Command, CommandResult
from ..cli_modes import CLIMode
import re
import os


class HostnameCommand(Command):
    """Comando para configurar el nombre del dispositivo"""
    
    def __init__(self):
        super().__init__(
            name="hostname",
            description="Configura el nombre del dispositivo",
            syntax="hostname <nombre>"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.GLOBAL_CONFIG:
            return CommandResult(False, "El comando 'hostname' solo está disponible en modo de configuración global")
        
        if not self.validate_args(args, min_args=1, max_args=1):
            return CommandResult(False, "Sintaxis: hostname <nombre>")
        
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        new_hostname = args[0]
        
        # Validar formato del hostname
        if not re.match(r'^[a-zA-Z0-9-_]+$', new_hostname):
            return CommandResult(False, "El hostname solo puede contener letras, números, guiones y guiones bajos")
        
        if len(new_hostname) > 50:
            return CommandResult(False, "El hostname no puede exceder 50 caracteres")
        
        try:
            # Usar el método setHostname del dispositivo
            context.current_device.setHostname(new_hostname)
            return CommandResult(True, f"Hostname cambiado a '{new_hostname}'")
        except Exception as e:
            return CommandResult(False, f"Error al cambiar hostname: {str(e)}")


class IpAddressCommand(Command):
    """Comando para configurar dirección IP de interfaz"""
    
    def __init__(self):
        super().__init__(
            name="ip",
            description="Configura parámetros IP de la interfaz",
            syntax="ip address <direccion_ip> [mask]"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.INTERFACE_CONFIG:
            return CommandResult(False, "El comando 'ip' solo está disponible en modo de configuración de interfaz")
        
        if not args:
            return CommandResult(False, "Sintaxis: ip address <direccion_ip> [mask]")
        
        if args[0].lower() != "address":
            return CommandResult(False, "Subcomando no soportado. Use: ip address")
        
        if not self.validate_args(args[1:], min_args=1, max_args=2):
            return CommandResult(False, "Sintaxis: ip address <direccion_ip> [mask]")
        
        if not context.current_interface:
            return CommandResult(False, "No hay interfaz seleccionada")
        
        ip_address = args[1]
        mask = args[2] if len(args) > 2 else "255.255.255.0"
        
        # Validar formato de IP
        if not self._validate_ip(ip_address):
            return CommandResult(False, f"Dirección IP inválida: {ip_address}")
        
        if not self._validate_ip(mask):
            return CommandResult(False, f"Máscara de subred inválida: {mask}")
        
        try:
            # Usar el método assignIpAddress de la interfaz
            context.current_interface.assignIpAddress(ip_address)
            return CommandResult(True, f"Dirección IP {ip_address} asignada a interfaz {context.current_interface.name}")
        except Exception as e:
            return CommandResult(False, f"Error al asignar IP: {str(e)}")
    
    def _validate_ip(self, ip: str) -> bool:
        """Valida formato de dirección IP"""
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(pattern, ip)
        if not match:
            return False
        
        # Verificar que cada octeto esté en rango 0-255
        for octet in match.groups():
            if not (0 <= int(octet) <= 255):
                return False
        
        return True


class ShutdownCommand(Command):
    """Comando para apagar interfaz"""
    
    def __init__(self):
        super().__init__(
            name="shutdown",
            description="Apaga la interfaz actual",
            syntax="shutdown"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.INTERFACE_CONFIG:
            return CommandResult(False, "El comando 'shutdown' solo está disponible en modo de configuración de interfaz")
        
        if not context.current_interface:
            return CommandResult(False, "No hay interfaz seleccionada")
        
        try:
            # Usar el método setStatus de la interfaz
            context.current_interface.setStatus("shutdown")
            return CommandResult(True, f"Interfaz {context.current_interface.name} apagada")
        except Exception as e:
            return CommandResult(False, f"Error al apagar interfaz: {str(e)}")


class NoShutdownCommand(Command):
    """Comando para encender interfaz"""
    
    def __init__(self):
        super().__init__(
            name="no",
            description="Niega un comando (ej: no shutdown para encender interfaz)",
            syntax="no shutdown"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.INTERFACE_CONFIG:
            return CommandResult(False, "El comando 'no' solo está disponible en modo de configuración de interfaz")
        
        if not args:
            return CommandResult(False, "Sintaxis: no <comando>")
        
        if args[0].lower() == "shutdown":
            if not context.current_interface:
                return CommandResult(False, "No hay interfaz seleccionada")
            
            try:
                # Usar el método setStatus de la interfaz
                context.current_interface.setStatus("no shutdown")
                return CommandResult(True, f"Interfaz {context.current_interface.name} encendida")
            except Exception as e:
                return CommandResult(False, f"Error al encender interfaz: {str(e)}")
        else:
            return CommandResult(False, f"Comando 'no {args[0]}' no soportado")


# ===== NUEVO: Módulo 6 Configuration Persistence - Comandos de persistencia =====

class SaveRunningConfigCommand(Command):
    """Comando para guardar la configuración actual"""
    
    def __init__(self):
        super().__init__(
            name="save",
            description="Guarda la configuración actual en un archivo JSON",
            syntax="save running-config [filename]"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.PRIVILEGED:
            return CommandResult(False, "El comando 'save' solo está disponible en modo privilegiado")
        
        # Verificar argumentos
        if not args or args[0].lower() != "running-config":
            return CommandResult(False, "Sintaxis: save running-config [filename]")
        
        # Obtener red
        network = getattr(context, 'network', None)
        if not network:
            return CommandResult(False, "No hay red disponible para guardar")
        
        # Determinar nombre de archivo
        filename = None
        if len(args) > 1:
            filename = args[1]
            # Validar nombre de archivo
            if not self._validate_filename(filename):
                return CommandResult(False, "Nombre de archivo inválido. Use solo letras, números, guiones y puntos")
        
        try:
            # Guardar configuración
            filepath = network.save_running_config(filename)
            
            # Mostrar resumen
            summary = f"""
Configuración guardada exitosamente:
  Archivo: {filepath}
  Red: {network.name}
  Dispositivos: {len(network.devices)}
  Conexiones: {len(network.connections)}
  Estadísticas preservadas: Sí
            """
            
            return CommandResult(True, summary.strip())
            
        except Exception as e:
            return CommandResult(False, f"Error guardando configuración: {str(e)}")
    
    def _validate_filename(self, filename: str) -> bool:
        """Valida el nombre del archivo"""
        # Permitir letras, números, guiones, puntos y guiones bajos
        pattern = r'^[a-zA-Z0-9._-]+$'
        if not re.match(pattern, filename):
            return False
        
        # Verificar longitud
        if len(filename) > 100:
            return False
        
        return True


class LoadConfigCommand(Command):
    """Comando para cargar configuración desde archivo"""
    
    def __init__(self):
        super().__init__(
            name="load",
            description="Carga configuración desde un archivo JSON",
            syntax="load config <filename>"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.PRIVILEGED:
            return CommandResult(False, "El comando 'load' solo está disponible en modo privilegiado")
        
        # Verificar argumentos
        if len(args) < 2 or args[0].lower() != "config":
            return CommandResult(False, "Sintaxis: load config <filename>")
        
        filename = args[1]
        
        # Obtener red
        network = getattr(context, 'network', None)
        if not network:
            return CommandResult(False, "No hay red disponible")
        
        try:
            # Mostrar warning sobre pérdida de configuración actual
            if len(network.devices) > 0:
                warning = f"""
⚠️  ADVERTENCIA: Esta operación reemplazará la configuración actual
   Dispositivos actuales: {len(network.devices)}
   Conexiones actuales: {len(network.connections)}
   
¿Continuar? (Esta operación no se puede deshacer)
"""
                print(warning)
                
            # Cargar configuración
            success = network.load_config(filename)
            
            if success:
                # Mostrar resumen de configuración cargada
                summary = f"""
Configuración cargada exitosamente:
  Archivo: {filename}
  Red: {network.name}
  Dispositivos: {len(network.devices)}
  Conexiones: {len(network.connections)}
  
Dispositivos cargados:
"""
                for device_name, device in network.devices.items():
                    summary += f"  - {device_name} ({device.type}) - {device.status}\n"
                
                return CommandResult(True, summary.strip())
            else:
                return CommandResult(False, f"Error cargando configuración desde {filename}")
                
        except Exception as e:
            return CommandResult(False, f"Error cargando configuración: {str(e)}")


class ShowConfigsCommand(Command):
    """Comando para listar configuraciones guardadas"""
    
    def __init__(self):
        super().__init__(
            name="configs",
            description="Muestra archivos de configuración disponibles",
            syntax="show configs"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        # Obtener red
        network = getattr(context, 'network', None)
        if not network:
            return CommandResult(False, "No hay red disponible")
        
        try:
            # Listar configuraciones
            config_files = network.list_saved_configs()
            
            if not config_files:
                return CommandResult(True, "No hay archivos de configuración guardados")
            
            output = f"\n=== Archivos de Configuración Disponibles ===\n"
            output += f"{'Archivo':<30} {'Red':<20} {'Dispositivos':<12} {'Creado':<20}\n"
            output += "-" * 85 + "\n"
            
            for config_file in config_files:
                info = network.get_config_info(config_file)
                if info:
                    output += f"{info['filename']:<30} {info['network_name'][:19]:<20} "
                    output += f"{info['devices_count']:<12} {info['created'][:19]:<20}\n"
                else:
                    output += f"{config_file:<30} {'ERROR':<20} {'?':<12} {'?':<20}\n"
            
            output += f"\nTotal: {len(config_files)} archivos de configuración"
            
            return CommandResult(True, output)
            
        except Exception as e:
            return CommandResult(False, f"Error listando configuraciones: {str(e)}")


class ConfigInfoCommand(Command):
    """Comando para mostrar información detallada de una configuración"""
    
    def __init__(self):
        super().__init__(
            name="config-info",
            description="Muestra información detallada de un archivo de configuración",
            syntax="show config-info <filename>"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not self.validate_args(args, min_args=1, max_args=1):
            return CommandResult(False, "Sintaxis: show config-info <filename>")
        
        filename = args[0]
        
        # Obtener red
        network = getattr(context, 'network', None)
        if not network:
            return CommandResult(False, "No hay red disponible")
        
        try:
            info = network.get_config_info(filename)
            
            if not info:
                return CommandResult(False, f"No se pudo obtener información del archivo: {filename}")
            
            output = f"""
=== Información de Configuración ===
Archivo: {info['filename']}
Red: {info['network_name']}
Dispositivos: {info['devices_count']}
Conexiones: {info['connections_count']}
Creado: {info['created']}
Versión: {info['version']}

Para cargar esta configuración use:
  load config {info['filename']}
"""
            
            return CommandResult(True, output.strip())
            
        except Exception as e:
            return CommandResult(False, f"Error obteniendo información: {str(e)}") 