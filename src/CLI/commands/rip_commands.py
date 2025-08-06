from ..command_base import Command
from typing import List

class EnableRIPCommand(Command):
    """Comando para habilitar RIP"""
    
    def __init__(self):
        super().__init__(
            name="router rip",
            description="Habilitar protocolo RIP",
            usage="router rip [version]",
            examples=[
                "router rip",
                "router rip 2"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        version = int(args[0]) if args else 2
        
        if version not in [1, 2]:
            return "❌ Versión de RIP debe ser 1 o 2"
        
        if current_device.enable_rip(version):
            return f"✅ RIP v{version} habilitado exitosamente"
        else:
            return "❌ Error al habilitar RIP"

class DisableRIPCommand(Command):
    """Comando para deshabilitar RIP"""
    
    def __init__(self):
        super().__init__(
            name="no router rip",
            description="Deshabilitar protocolo RIP",
            usage="no router rip",
            examples=[
                "no router rip"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if current_device.disable_rip():
            return "✅ RIP deshabilitado exitosamente"
        else:
            return "❌ Error al deshabilitar RIP"

class AddRIPNetworkCommand(Command):
    """Comando para agregar red a RIP"""
    
    def __init__(self):
        super().__init__(
            name="network rip",
            description="Agregar red al protocolo RIP",
            usage="network rip <network>",
            examples=[
                "network rip 192.168.1.0",
                "network rip 10.0.0.0"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 1:
            return "❌ Uso: network rip <network>"
        
        network_address = args[0]
        
        if current_device.add_rip_network(network_address):
            return f"✅ Red {network_address} agregada a RIP"
        else:
            return f"❌ Error al agregar red {network_address} a RIP"

class EnableRIPInterfaceCommand(Command):
    """Comando para habilitar RIP en una interfaz"""
    
    def __init__(self):
        super().__init__(
            name="rip interface",
            description="Habilitar RIP en una interfaz",
            usage="rip interface <interface> [send_version] [receive_version]",
            examples=[
                "rip interface eth0",
                "rip interface eth1 2 2"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 1:
            return "❌ Uso: rip interface <interface> [send_version] [receive_version]"
        
        interface_name = args[0]
        send_version = int(args[1]) if len(args) > 1 else 2
        receive_version = int(args[2]) if len(args) > 2 else 2
        
        if send_version not in [1, 2] or receive_version not in [1, 2]:
            return "❌ Versión de RIP debe ser 1 o 2"
        
        if current_device.enable_rip_interface(interface_name, send_version, receive_version):
            return f"✅ RIP habilitado en interfaz {interface_name}"
        else:
            return f"❌ Error al habilitar RIP en interfaz {interface_name}"

class ShowRIPDatabaseCommand(Command):
    """Comando para mostrar base de datos RIP"""
    
    def __init__(self):
        super().__init__(
            name="show rip database",
            description="Mostrar base de datos RIP",
            usage="show rip database",
            examples=[
                "show rip database"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        return current_device.show_rip_database()

class ShowRIPInterfacesCommand(Command):
    """Comando para mostrar interfaces RIP"""
    
    def __init__(self):
        super().__init__(
            name="show rip interfaces",
            description="Mostrar configuración de interfaces RIP",
            usage="show rip interfaces",
            examples=[
                "show rip interfaces"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        return current_device.show_rip_interfaces()

class ShowRIPNeighborsCommand(Command):
    """Comando para mostrar vecinos RIP"""
    
    def __init__(self):
        super().__init__(
            name="show rip neighbors",
            description="Mostrar vecinos RIP",
            usage="show rip neighbors",
            examples=[
                "show rip neighbors"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        return current_device.show_rip_neighbors() 