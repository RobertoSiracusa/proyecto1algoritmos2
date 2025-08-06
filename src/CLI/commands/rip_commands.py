from ..command_base import Command

class EnableRIPCommand(Command):
    """Comando para habilitar RIP"""
    
    def __init__(self):
        super().__init__(
            name="router rip",
            description="Habilitar protocolo RIP",
            syntax="router rip [version]"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        version = int(args[0]) if args else 2
        
        if current_device.enable_rip(version):
            return f"✅ RIP versión {version} habilitado exitosamente"
        else:
            return f"❌ Error al habilitar RIP versión {version}"

class DisableRIPCommand(Command):
    """Comando para deshabilitar RIP"""
    
    def __init__(self):
        super().__init__(
            name="no router rip",
            description="Deshabilitar protocolo RIP",
            syntax="no router rip"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
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
            syntax="network rip <network>"
        )
    
    def execute(self, args, context):
        if len(args) < 1:
            return "❌ Uso: network rip <network>"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        network = args[0]
        
        if current_device.add_rip_network(network):
            return f"✅ Red {network} agregada a RIP exitosamente"
        else:
            return f"❌ Error al agregar red {network} a RIP"

class EnableRIPInterfaceCommand(Command):
    """Comando para habilitar RIP en interfaz"""
    
    def __init__(self):
        super().__init__(
            name="rip interface",
            description="Habilitar RIP en interfaz específica",
            syntax="rip interface <interface> [send_version] [receive_version]"
        )
    
    def execute(self, args, context):
        if len(args) < 1:
            return "❌ Uso: rip interface <interface> [send_version] [receive_version]"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        interface_name = args[0]
        send_version = int(args[1]) if len(args) > 1 else 2
        receive_version = int(args[2]) if len(args) > 2 else 2
        
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
            syntax="show rip database"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        return current_device.show_rip_database()

class ShowRIPInterfacesCommand(Command):
    """Comando para mostrar interfaces RIP"""
    
    def __init__(self):
        super().__init__(
            name="show rip interfaces",
            description="Mostrar interfaces configuradas para RIP",
            syntax="show rip interfaces"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        return current_device.show_rip_interfaces()

class ShowRIPNeighborsCommand(Command):
    """Comando para mostrar vecinos RIP"""
    
    def __init__(self):
        super().__init__(
            name="show rip neighbors",
            description="Mostrar vecinos RIP descubiertos",
            syntax="show rip neighbors"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        return current_device.show_rip_neighbors() 