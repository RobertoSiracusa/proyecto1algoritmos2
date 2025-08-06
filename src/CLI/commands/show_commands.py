from typing import List
from ..command_base import Command, CommandResult, CompositeCommand


class ShowHistoryCommand(Command):
    """Comando para mostrar historial de paquetes de un dispositivo específico"""
    
    def __init__(self):
        super().__init__(
            name="history",
            description="Muestra el historial de paquetes recibidos de un dispositivo",
            syntax="show history [device_name]"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        # ===== NUEVO: Módulo 5 StatsReports - Soporte para dispositivo específico =====
        if args:
            # Comando: show history <device>
            device_name = args[0]
            
            # Buscar dispositivo en la red
            network = getattr(context, 'network', None)
            if not network:
                return CommandResult(False, "No hay red disponible")
            
            target_device = network.getDevice(device_name)
            if not target_device:
                available_devices = ', '.join(network.getAllDeviceNames())
                return CommandResult(False, f"Dispositivo '{device_name}' no encontrado. Disponibles: {available_devices}")
            
            # Mostrar historial del dispositivo específico
            try:
                import io
                import sys
                
                old_stdout = sys.stdout
                sys.stdout = captured_output = io.StringIO()
                
                target_device.showHistory()
                
                sys.stdout = old_stdout
                output = captured_output.getvalue()
                
                return CommandResult(True, output if output else f"No hay historial disponible para {device_name}")
                
            except Exception as e:
                return CommandResult(False, f"Error al mostrar historial de {device_name}: {str(e)}")
        else:
            # Comando sin parámetros: usar dispositivo actual
            if not context.current_device:
                return CommandResult(False, "No hay dispositivo seleccionado. Use: show history <device_name>")
            
            try:
                import io
                import sys
                
                old_stdout = sys.stdout
                sys.stdout = captured_output = io.StringIO()
                
                context.current_device.showHistory()
                
                sys.stdout = old_stdout
                output = captured_output.getvalue()
                
                return CommandResult(True, output if output else "No hay historial disponible")
                
            except Exception as e:
                return CommandResult(False, f"Error al mostrar historial: {str(e)}")


class ShowQueueCommand(Command):
    """Comando para mostrar colas de un dispositivo específico"""
    
    def __init__(self):
        super().__init__(
            name="queue",
            description="Muestra las colas de paquetes de un dispositivo",
            syntax="show queue [device_name]"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        # ===== NUEVO: Módulo 5 StatsReports - Soporte para dispositivo específico =====
        if args:
            # Comando: show queue <device>
            device_name = args[0]
            
            # Buscar dispositivo en la red
            network = getattr(context, 'network', None)
            if not network:
                return CommandResult(False, "No hay red disponible")
            
            target_device = network.getDevice(device_name)
            if not target_device:
                available_devices = ', '.join(network.getAllDeviceNames())
                return CommandResult(False, f"Dispositivo '{device_name}' no encontrado. Disponibles: {available_devices}")
            
            # Mostrar colas del dispositivo específico
            try:
                import io
                import sys
                
                old_stdout = sys.stdout
                sys.stdout = captured_output = io.StringIO()
                
                target_device.showQueue()
                
                sys.stdout = old_stdout
                output = captured_output.getvalue()
                
                return CommandResult(True, output if output else f"No hay información de colas disponible para {device_name}")
                
            except Exception as e:
                return CommandResult(False, f"Error al mostrar colas de {device_name}: {str(e)}")
        else:
            # Comando sin parámetros: usar dispositivo actual
            if not context.current_device:
                return CommandResult(False, "No hay dispositivo seleccionado. Use: show queue <device_name>")
            
            try:
                import io
                import sys
                
                old_stdout = sys.stdout
                sys.stdout = captured_output = io.StringIO()
                
                context.current_device.showQueue()
                
                sys.stdout = old_stdout
                output = captured_output.getvalue()
                
                return CommandResult(True, output if output else "No hay información de colas disponible")
                
            except Exception as e:
                return CommandResult(False, f"Error al mostrar colas: {str(e)}")


class ShowInterfacesCommand(Command):
    """Comando para mostrar interfaces de un dispositivo específico"""
    
    def __init__(self):
        super().__init__(
            name="interfaces",
            description="Muestra información de las interfaces de un dispositivo",
            syntax="show interfaces [device_name]"
        )
        self.add_alias("int")
    
    def execute(self, args: List[str], context) -> CommandResult:
        # ===== NUEVO: Módulo 5 StatsReports - Soporte para dispositivo específico =====
        if args:
            # Comando: show interfaces <device>
            device_name = args[0]
            
            # Buscar dispositivo en la red
            network = getattr(context, 'network', None)
            if not network:
                return CommandResult(False, "No hay red disponible")
            
            target_device = network.getDevice(device_name)
            if not target_device:
                available_devices = ', '.join(network.getAllDeviceNames())
                return CommandResult(False, f"Dispositivo '{device_name}' no encontrado. Disponibles: {available_devices}")
            
            # Mostrar interfaces del dispositivo específico
            try:
                import io
                import sys
                
                old_stdout = sys.stdout
                sys.stdout = captured_output = io.StringIO()
                
                target_device.showInterfaces()
                
                sys.stdout = old_stdout
                output = captured_output.getvalue()
                
                return CommandResult(True, output if output else f"No hay interfaces disponibles para {device_name}")
                
            except Exception as e:
                return CommandResult(False, f"Error al mostrar interfaces de {device_name}: {str(e)}")
        else:
            # Comando sin parámetros: usar dispositivo actual
            if not context.current_device:
                return CommandResult(False, "No hay dispositivo seleccionado. Use: show interfaces <device_name>")
            
            try:
                import io
                import sys
                
                old_stdout = sys.stdout
                sys.stdout = captured_output = io.StringIO()
                
                context.current_device.showInterfaces()
                
                sys.stdout = old_stdout
                output = captured_output.getvalue()
                
                return CommandResult(True, output if output else "No hay interfaces disponibles")
                
            except Exception as e:
                return CommandResult(False, f"Error al mostrar interfaces: {str(e)}")


class ShowStatisticsCommand(Command):
    """Comando para mostrar estadísticas de red"""
    
    def __init__(self):
        super().__init__(
            name="statistics",
            description="Muestra estadísticas completas de la red",
            syntax="show statistics"
        )
        self.add_alias("stats")
    
    def execute(self, args: List[str], context) -> CommandResult:
        # ===== NUEVO: Módulo 5 StatsReports - Llamar a network.show_statistics() =====
        network = getattr(context, 'network', None)
        if not network:
            return CommandResult(False, "No hay red disponible")
        
        try:
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Llamar al método showStatistics de la red
            network.showStatistics()
            
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            
            return CommandResult(True, output if output else "No hay estadísticas disponibles")
            
        except Exception as e:
            return CommandResult(False, f"Error al mostrar estadísticas: {str(e)}")


class ShowDevicesCommand(Command):
    """Comando para listar todos los dispositivos de la red"""
    
    def __init__(self):
        super().__init__(
            name="devices",
            description="Muestra lista de dispositivos en la red",
            syntax="show devices"
        )
        self.add_alias("dev")
    
    def execute(self, args: List[str], context) -> CommandResult:
        network = getattr(context, 'network', None)
        if not network:
            return CommandResult(False, "No hay red disponible")
        
        try:
            devices = network.listDevices()
            
            if not devices:
                return CommandResult(True, "No hay dispositivos en la red")
            
            output = f"\n=== Dispositivos en la red '{network.name}' ===\n"
            output += f"{'Nombre':<20} {'Tipo':<10} {'Estado':<8} {'Interfaces':<10} {'Activas':<8} {'Conectadas':<10}\n"
            output += "-" * 75 + "\n"
            
            for device in devices:
                output += f"{device['name']:<20} {device['type']:<10} {device['status']:<8} "
                output += f"{device['interfaces']:<10} {device['active_interfaces']:<8} {device['connected_interfaces']:<10}\n"
            
            output += f"\nTotal: {len(devices)} dispositivos"
            
            return CommandResult(True, output)
            
        except Exception as e:
            return CommandResult(False, f"Error al listar dispositivos: {str(e)}")


class ShowTopologyCommand(Command):
    """Comando para mostrar la topología de la red"""
    
    def __init__(self):
        super().__init__(
            name="topology",
            description="Muestra la topología completa de la red",
            syntax="show topology"
        )
        self.add_alias("topo")
    
    def execute(self, args: List[str], context) -> CommandResult:
        network = getattr(context, 'network', None)
        if not network:
            return CommandResult(False, "No hay red disponible")
        
        try:
            topology = network.getNetworkTopology()
            
            output = f"\n=== Topología de Red: {topology['name']} ===\n"
            
            # Mostrar dispositivos
            output += "\nDispositivos:\n"
            for device_name, device_data in topology['devices'].items():
                output += f"  {device_name} ({device_data['type']}) - {device_data['status']}\n"
                
                for iface_name, iface_data in device_data['interfaces'].items():
                    status_symbol = "🟢" if iface_data['status'] in ['up', 'no shutdown'] else "🔴"
                    connected = f" <-> {iface_data['connectedTo']}" if iface_data['connectedTo'] else ""
                    ip_info = f" [{iface_data['ipAddress']}]" if iface_data['ipAddress'] else ""
                    output += f"    {status_symbol} {iface_name}{ip_info}{connected}\n"
            
            # Mostrar conexiones
            output += f"\nConexiones ({len(topology['connections'])}):\n"
            for connection in topology['connections']:
                device1, iface1, device2, iface2 = connection
                output += f"  {device1}:{iface1} <--> {device2}:{iface2}\n"
            
            return CommandResult(True, output)
            
        except Exception as e:
            return CommandResult(False, f"Error al mostrar topología: {str(e)}")


# ===== NUEVO: Módulo 6 Configuration Persistence - Comandos show para configuraciones =====

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
            output += f"\n\nPara cargar una configuración use: load config <filename>"
            
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


class ShowCommand(CompositeCommand):
    """Comando compuesto para todos los subcomandos show"""
    
    def __init__(self):
        super().__init__(
            name="show",
            description="Muestra información del sistema",
            syntax="show <subcomando> [parámetros]"
        )
        
        # Agregar subcomandos
        self.add_subcommand(ShowHistoryCommand())
        self.add_subcommand(ShowInterfacesCommand())
        self.add_subcommand(ShowQueueCommand())
        self.add_subcommand(ShowStatisticsCommand())
        self.add_subcommand(ShowDevicesCommand())
        self.add_subcommand(ShowTopologyCommand())
        self.add_subcommand(ShowConfigsCommand())
        self.add_subcommand(ConfigInfoCommand())
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not args:
            # Mostrar ayuda de subcomandos disponibles
            help_text = self.get_help()
            help_text += "\n\nEjemplos de uso:"
            help_text += "\n  show statistics              - Estadísticas completas de la red"
            help_text += "\n  show history Router-1        - Historial del dispositivo Router-1"
            help_text += "\n  show queue Switch-Core       - Colas del dispositivo Switch-Core"
            help_text += "\n  show interfaces              - Interfaces del dispositivo actual"
            help_text += "\n  show devices                 - Lista todos los dispositivos"
            help_text += "\n  show topology                - Topología completa de la red"
            help_text += "\n  show configs                 - Archivos de configuración guardados"
            help_text += "\n  show config-info <file>      - Información de configuración específica"
            
            return CommandResult(True, help_text)
        
        return super().execute(args, context) 

class ShowIpRouteCommand(Command):
    """Comando para mostrar tabla de rutas IP"""
    
    def __init__(self):
        super().__init__(
            name="ip route",
            description="Muestra la tabla de rutas IP",
            syntax="show ip route"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        # Verificar que hay un dispositivo seleccionado
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Verificar que es un router
        if context.current_device.type != "router":
            return CommandResult(False, f"Comando solo disponible para routers. {context.current_device.name} es un {context.current_device.type}")
        
        # Verificar que el dispositivo está online
        if not context.current_device.isOnline():
            return CommandResult(False, f"Router {context.current_device.name} está offline")
        
        try:
            # Mostrar tabla de rutas
            routing_table = context.current_device.show_routing_table()
            return CommandResult(True, routing_table)
            
        except Exception as e:
            return CommandResult(False, f"Error al mostrar tabla de rutas: {str(e)}")


class ShowIpInterfaceBriefCommand(Command):
    """Comando para mostrar resumen de interfaces IP"""
    
    def __init__(self):
        super().__init__(
            name="ip interface brief",
            description="Muestra un resumen de interfaces IP",
            syntax="show ip interface brief"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        # Verificar que hay un dispositivo seleccionado
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Verificar que el dispositivo está online
        if not context.current_device.isOnline():
            return CommandResult(False, f"Dispositivo {context.current_device.name} está offline")
        
        try:
            # Obtener interfaces activas
            active_interfaces = context.current_device.getActiveInterfaces()
            
            if not active_interfaces:
                return CommandResult(True, "No hay interfaces IP activas")
            
            # Formatear salida
            result = f"Resumen de interfaces IP - {context.current_device.name}:\n"
            result += "-" * 60 + "\n"
            result += f"{'Interfaz':<15} {'Estado':<10} {'IP':<15} {'MAC':<17} {'Conectado a'}\n"
            result += "-" * 60 + "\n"
            
            for interface in active_interfaces:
                status = "up" if interface.isUp() else "down"
                ip = interface.ipAddress if interface.ipAddress else "No configurada"
                mac = interface.macAddress if interface.macAddress else "No configurada"
                
                connected_to = ""
                if interface.isConnected():
                    connected_to = f"{interface.connectedTo.name} ({interface.connectedTo.type})"
                
                result += f"{interface.name:<15} {status:<10} {ip:<15} {mac:<17} {connected_to}\n"
            
            return CommandResult(True, result)
            
        except Exception as e:
            return CommandResult(False, f"Error al mostrar interfaces: {str(e)}")