from typing import List
from ..command_base import Command, CommandResult


class AddRouteCommand(Command):
    """Comando para agregar rutas a la tabla de routing"""
    
    def __init__(self):
        super().__init__(
            name="ip route",
            description="Agrega una ruta a la tabla de routing",
            syntax="ip route <destination> <next_hop> <interface> [metric] [protocol]"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not self.validate_args(args, min_args=3, max_args=5):
            return CommandResult(False, "Sintaxis: ip route <destination> <next_hop> <interface> [metric] [protocol]")
        
        # Verificar que hay un dispositivo seleccionado
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Verificar que es un router
        if context.current_device.type != "router":
            return CommandResult(False, f"Comando solo disponible para routers. {context.current_device.name} es un {context.current_device.type}")
        
        # Verificar que el dispositivo está online
        if not context.current_device.isOnline():
            return CommandResult(False, f"Router {context.current_device.name} está offline")
        
        destination = args[0]
        next_hop = args[1]
        interface = args[2]
        metric = int(args[3]) if len(args) > 3 else 1
        protocol = args[4] if len(args) > 4 else "static"
        
        # Verificar que la interfaz existe
        if not context.current_device.getInterface(interface):
            available_interfaces = [i.name for i in context.current_device.interfaces]
            return CommandResult(False, f"Interfaz '{interface}' no existe. Disponibles: {', '.join(available_interfaces)}")
        
        try:
            # Agregar ruta
            success = context.current_device.add_route(destination, next_hop, interface, metric, protocol)
            
            if success:
                return CommandResult(True, f"✅ Ruta agregada exitosamente:\n   Destino: {destination}\n   Próximo salto: {next_hop}\n   Interfaz: {interface}\n   Métrica: {metric}\n   Protocolo: {protocol}")
            else:
                return CommandResult(False, "❌ Error al agregar ruta")
                
        except Exception as e:
            return CommandResult(False, f"Error al agregar ruta: {str(e)}")


class RemoveRouteCommand(Command):
    """Comando para eliminar rutas de la tabla de routing"""
    
    def __init__(self):
        super().__init__(
            name="no ip route",
            description="Elimina una ruta de la tabla de routing",
            syntax="no ip route <destination>"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not self.validate_args(args, min_args=1, max_args=1):
            return CommandResult(False, "Sintaxis: no ip route <destination>")
        
        # Verificar que hay un dispositivo seleccionado
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Verificar que es un router
        if context.current_device.type != "router":
            return CommandResult(False, f"Comando solo disponible para routers. {context.current_device.name} es un {context.current_device.type}")
        
        # Verificar que el dispositivo está online
        if not context.current_device.isOnline():
            return CommandResult(False, f"Router {context.current_device.name} está offline")
        
        destination = args[0]
        
        try:
            # Eliminar ruta
            success = context.current_device.remove_route(destination)
            
            if success:
                return CommandResult(True, f"✅ Ruta eliminada exitosamente: {destination}")
            else:
                return CommandResult(False, f"❌ Ruta '{destination}' no encontrada")
                
        except Exception as e:
            return CommandResult(False, f"Error al eliminar ruta: {str(e)}")


class DefaultRouteCommand(Command):
    """Comando para configurar ruta por defecto"""
    
    def __init__(self):
        super().__init__(
            name="ip route default",
            description="Configura la ruta por defecto",
            syntax="ip route default <next_hop> <interface>"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not self.validate_args(args, min_args=2, max_args=2):
            return CommandResult(False, "Sintaxis: ip route default <next_hop> <interface>")
        
        # Verificar que hay un dispositivo seleccionado
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Verificar que es un router
        if context.current_device.type != "router":
            return CommandResult(False, f"Comando solo disponible para routers. {context.current_device.name} es un {context.current_device.type}")
        
        # Verificar que el dispositivo está online
        if not context.current_device.isOnline():
            return CommandResult(False, f"Router {context.current_device.name} está offline")
        
        next_hop = args[0]
        interface = args[1]
        
        # Verificar que la interfaz existe
        if not context.current_device.getInterface(interface):
            available_interfaces = [i.name for i in context.current_device.interfaces]
            return CommandResult(False, f"Interfaz '{interface}' no existe. Disponibles: {', '.join(available_interfaces)}")
        
        try:
            # Configurar ruta por defecto
            success = context.current_device.set_default_route(next_hop, interface)
            
            if success:
                return CommandResult(True, f"✅ Ruta por defecto configurada exitosamente:\n   Próximo salto: {next_hop}\n   Interfaz: {interface}")
            else:
                return CommandResult(False, "❌ Error al configurar ruta por defecto")
                
        except Exception as e:
            return CommandResult(False, f"Error al configurar ruta por defecto: {str(e)}")


class ClearRoutesCommand(Command):
    """Comando para limpiar rutas de la tabla de routing"""
    
    def __init__(self):
        super().__init__(
            name="clear ip route",
            description="Limpia rutas de la tabla de routing",
            syntax="clear ip route [protocol]"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not self.validate_args(args, min_args=0, max_args=1):
            return CommandResult(False, "Sintaxis: clear ip route [protocol]")
        
        # Verificar que hay un dispositivo seleccionado
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Verificar que es un router
        if context.current_device.type != "router":
            return CommandResult(False, f"Comando solo disponible para routers. {context.current_device.name} es un {context.current_device.type}")
        
        # Verificar que el dispositivo está online
        if not context.current_device.isOnline():
            return CommandResult(False, f"Router {context.current_device.name} está offline")
        
        protocol = args[0] if args else None
        
        try:
            # Limpiar rutas
            removed_count = context.current_device.clear_routes(protocol)
            
            if protocol:
                return CommandResult(True, f"✅ {removed_count} rutas del protocolo '{protocol}' eliminadas")
            else:
                return CommandResult(True, f"✅ {removed_count} rutas eliminadas de la tabla de routing")
                
        except Exception as e:
            return CommandResult(False, f"Error al limpiar rutas: {str(e)}")


class ShowRoutingTableCommand(Command):
    """Comando para mostrar tabla de rutas"""
    
    def __init__(self):
        super().__init__(
            name="show routing",
            description="Muestra la tabla de rutas del router",
            syntax="show routing"
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