from ..command_base import Command
from typing import List

class CreateVLANCommand(Command):
    """Comando para crear una VLAN"""
    
    def __init__(self):
        super().__init__(
            name="vlan",
            description="Crear una VLAN",
            usage="vlan <vlan_id> <name> [description]",
            examples=[
                "vlan 10 ADMIN",
                "vlan 20 SALES 'Departamento de Ventas'"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 2:
            return "❌ Uso: vlan <vlan_id> <name> [description]"
        
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
            usage="no vlan <vlan_id>",
            examples=[
                "no vlan 10",
                "no vlan 20"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 1:
            return "❌ Uso: no vlan <vlan_id>"
        
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
            usage="switchport access vlan <interface> <vlan_id>",
            examples=[
                "switchport access vlan eth0 10",
                "switchport access vlan eth1 20"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 2:
            return "❌ Uso: switchport access vlan <interface> <vlan_id>"
        
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
            usage="switchport trunk <interface> <allowed_vlans> [native_vlan]",
            examples=[
                "switchport trunk eth0 1-10,20",
                "switchport trunk eth1 1-50 1"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 2:
            return "❌ Uso: switchport trunk <interface> <allowed_vlans> [native_vlan]"
        
        try:
            interface_name = args[0]
            allowed_vlans_str = args[1]
            native_vlan = int(args[2]) if len(args) > 2 else 1
            
            # Parsear VLANs permitidas
            allowed_vlans = []
            for vlan_range in allowed_vlans_str.split(','):
                if '-' in vlan_range:
                    start, end = map(int, vlan_range.split('-'))
                    allowed_vlans.extend(range(start, end + 1))
                else:
                    allowed_vlans.append(int(vlan_range))
            
            if current_device.configure_interface_trunk(interface_name, allowed_vlans, native_vlan):
                return f"✅ Interfaz {interface_name} configurada en modo trunk"
            else:
                return f"❌ Error al configurar interfaz {interface_name}"
        except ValueError:
            return "❌ Parámetros de VLAN deben ser números"

class ShowVLANsCommand(Command):
    """Comando para mostrar VLANs"""
    
    def __init__(self):
        super().__init__(
            name="show vlan",
            description="Mostrar VLANs configuradas",
            usage="show vlan [vlan_id]",
            examples=[
                "show vlan",
                "show vlan 10"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if args:
            try:
                vlan_id = int(args[0])
                return current_device.show_vlan_detail(vlan_id)
            except ValueError:
                return "❌ VLAN ID debe ser un número"
        else:
            return current_device.show_vlans()

class ShowVLANInterfacesCommand(Command):
    """Comando para mostrar configuración de VLAN en interfaces"""
    
    def __init__(self):
        super().__init__(
            name="show vlan interfaces",
            description="Mostrar configuración de VLAN en interfaces",
            usage="show vlan interfaces",
            examples=[
                "show vlan interfaces"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        return current_device.show_vlan_interfaces() 