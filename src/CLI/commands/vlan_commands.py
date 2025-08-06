from ..command_base import Command

class CreateVLANCommand(Command):
    """Comando para crear una VLAN"""
    
    def __init__(self):
        super().__init__(
            name="vlan",
            description="Crear una VLAN",
            syntax="vlan <vlan_id> <name> [description]"
        )
    
    def execute(self, args, context):
        if len(args) < 2:
            return "❌ Uso: vlan <vlan_id> <name> [description]"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        try:
            vlan_id = int(args[0])
            vlan_name = args[1]
            description = " ".join(args[2:]) if len(args) > 2 else ""
            
            if not 1 <= vlan_id <= 4094:
                return "❌ VLAN ID debe estar entre 1 y 4094"
            
            if current_device.create_vlan(vlan_id, vlan_name, description):
                return f"✅ VLAN {vlan_id} '{vlan_name}' creada exitosamente"
            else:
                return f"❌ Error al crear VLAN {vlan_id}"
        except ValueError:
            return "❌ VLAN ID debe ser un número"

class DeleteVLANCommand(Command):
    """Comando para eliminar una VLAN"""
    
    def __init__(self):
        super().__init__(
            name="no vlan",
            description="Eliminar una VLAN",
            syntax="no vlan <vlan_id>"
        )
    
    def execute(self, args, context):
        if len(args) < 1:
            return "❌ Uso: no vlan <vlan_id>"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        try:
            vlan_id = int(args[0])
            
            if current_device.delete_vlan(vlan_id):
                return f"✅ VLAN {vlan_id} eliminada exitosamente"
            else:
                return f"❌ Error al eliminar VLAN {vlan_id}"
        except ValueError:
            return "❌ VLAN ID debe ser un número"

class ConfigureInterfaceAccessCommand(Command):
    """Comando para configurar interfaz en modo access"""
    
    def __init__(self):
        super().__init__(
            name="switchport access vlan",
            description="Configurar interfaz en modo access",
            syntax="switchport access vlan <interface> <vlan_id>"
        )
    
    def execute(self, args, context):
        if len(args) < 2:
            return "❌ Uso: switchport access vlan <interface> <vlan_id>"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        try:
            interface_name = args[0]
            vlan_id = int(args[1])
            
            if current_device.configure_interface_access(interface_name, vlan_id):
                return f"✅ Interfaz {interface_name} configurada en modo access VLAN {vlan_id}"
            else:
                return f"❌ Error al configurar interfaz {interface_name}"
        except ValueError:
            return "❌ VLAN ID debe ser un número"

class ConfigureInterfaceTrunkCommand(Command):
    """Comando para configurar interfaz en modo trunk"""
    
    def __init__(self):
        super().__init__(
            name="switchport trunk",
            description="Configurar interfaz en modo trunk",
            syntax="switchport trunk <interface> <allowed_vlans> [native_vlan]"
        )
    
    def execute(self, args, context):
        if len(args) < 2:
            return "❌ Uso: switchport trunk <interface> <allowed_vlans> [native_vlan]"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        try:
            interface_name = args[0]
            allowed_vlans = args[1]
            native_vlan = int(args[2]) if len(args) > 2 else None
            
            if current_device.configure_interface_trunk(interface_name, allowed_vlans, native_vlan):
                return f"✅ Interfaz {interface_name} configurada en modo trunk"
            else:
                return f"❌ Error al configurar interfaz {interface_name}"
        except ValueError:
            return "❌ Native VLAN debe ser un número"

class ShowVLANsCommand(Command):
    """Comando para mostrar VLANs"""
    
    def __init__(self):
        super().__init__(
            name="show vlan",
            description="Mostrar VLANs",
            syntax="show vlan [vlan_id]"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        vlan_id = int(args[0]) if args else None
        return current_device.show_vlans(vlan_id)

class ShowVLANInterfacesCommand(Command):
    """Comando para mostrar interfaces de VLAN"""
    
    def __init__(self):
        super().__init__(
            name="show vlan interfaces",
            description="Mostrar interfaces de VLAN",
            syntax="show vlan interfaces"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        return current_device.show_vlan_interfaces() 