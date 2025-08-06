from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class VLAN:
    """Representa una VLAN individual"""
    id: int
    name: str
    description: str = ""
    status: str = "active"  # active, shutdown
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def __str__(self):
        return f"VLAN {self.id} - {self.name} ({self.status})"

class VLANInterface:
    """Configuración de VLAN para una interfaz"""
    
    def __init__(self, interface_name: str):
        self.interface_name = interface_name
        self.mode = "access"  # access, trunk
        self.access_vlan = 1  # VLAN por defecto
        self.trunk_vlans: Set[int] = set()  # VLANs permitidas en trunk
        self.native_vlan = 1  # VLAN nativa para trunk
        self.is_active = True
    
    def set_access_mode(self, vlan_id: int) -> bool:
        """Configura la interfaz en modo access"""
        if not 1 <= vlan_id <= 4094:
            return False
        
        self.mode = "access"
        self.access_vlan = vlan_id
        self.trunk_vlans.clear()
        return True
    
    def set_trunk_mode(self, allowed_vlans: List[int] = None, native_vlan: int = 1) -> bool:
        """Configura la interfaz en modo trunk"""
        if not 1 <= native_vlan <= 4094:
            return False
        
        self.mode = "trunk"
        self.native_vlan = native_vlan
        
        if allowed_vlans:
            self.trunk_vlans = set(v for v in allowed_vlans if 1 <= v <= 4094)
        else:
            # Permitir todas las VLANs por defecto
            self.trunk_vlans = set(range(1, 4095))
        
        return True
    
    def add_trunk_vlan(self, vlan_id: int) -> bool:
        """Agrega una VLAN al trunk"""
        if self.mode != "trunk":
            return False
        
        if 1 <= vlan_id <= 4094:
            self.trunk_vlans.add(vlan_id)
            return True
        return False
    
    def remove_trunk_vlan(self, vlan_id: int) -> bool:
        """Remueve una VLAN del trunk"""
        if self.mode != "trunk":
            return False
        
        self.trunk_vlans.discard(vlan_id)
        return True
    
    def is_vlan_allowed(self, vlan_id: int) -> bool:
        """Verifica si una VLAN está permitida en esta interfaz"""
        if self.mode == "access":
            return vlan_id == self.access_vlan
        elif self.mode == "trunk":
            return vlan_id in self.trunk_vlans
        return False
    
    def get_config_summary(self) -> str:
        """Obtiene un resumen de la configuración"""
        if self.mode == "access":
            return f"{self.interface_name}: access vlan {self.access_vlan}"
        elif self.mode == "trunk":
            vlan_list = ",".join(map(str, sorted(self.trunk_vlans)))
            return f"{self.interface_name}: trunk allowed vlans {vlan_list}, native vlan {self.native_vlan}"
        return f"{self.interface_name}: no vlan config"

class VLANManager:
    """Gestor principal de VLANs"""
    
    def __init__(self):
        self.vlans: Dict[int, VLAN] = {}
        self.vlan_interfaces: Dict[str, VLANInterface] = {}
        self._vlan_counter = 1
    
    def create_vlan(self, vlan_id: int, name: str, description: str = "") -> bool:
        """Crea una nueva VLAN"""
        if not 1 <= vlan_id <= 4094:
            return False
        
        if vlan_id in self.vlans:
            return False
        
        self.vlans[vlan_id] = VLAN(vlan_id, name, description)
        return True
    
    def delete_vlan(self, vlan_id: int) -> bool:
        """Elimina una VLAN"""
        if vlan_id in self.vlans:
            # Verificar que no esté en uso
            for interface in self.vlan_interfaces.values():
                if interface.is_vlan_allowed(vlan_id):
                    return False
            
            del self.vlans[vlan_id]
            return True
        return False
    
    def get_vlan(self, vlan_id: int) -> Optional[VLAN]:
        """Obtiene una VLAN por ID"""
        return self.vlans.get(vlan_id)
    
    def configure_interface_access(self, interface_name: str, vlan_id: int) -> bool:
        """Configura una interfaz en modo access"""
        if vlan_id not in self.vlans:
            return False
        
        if interface_name not in self.vlan_interfaces:
            self.vlan_interfaces[interface_name] = VLANInterface(interface_name)
        
        return self.vlan_interfaces[interface_name].set_access_mode(vlan_id)
    
    def configure_interface_trunk(self, interface_name: str, allowed_vlans: List[int] = None, 
                                 native_vlan: int = 1) -> bool:
        """Configura una interfaz en modo trunk"""
        if native_vlan not in self.vlans:
            return False
        
        if interface_name not in self.vlan_interfaces:
            self.vlan_interfaces[interface_name] = VLANInterface(interface_name)
        
        return self.vlan_interfaces[interface_name].set_trunk_mode(allowed_vlans, native_vlan)
    
    def get_interface_config(self, interface_name: str) -> Optional[VLANInterface]:
        """Obtiene la configuración de VLAN de una interfaz"""
        return self.vlan_interfaces.get(interface_name)
    
    def show_vlans(self) -> str:
        """Muestra todas las VLANs"""
        if not self.vlans:
            return "No hay VLANs configuradas"
        
        output = ["VLAN Database"]
        output.append("-" * 50)
        output.append("VLAN ID  Name                    Status")
        output.append("-" * 50)
        
        for vlan_id in sorted(self.vlans.keys()):
            vlan = self.vlans[vlan_id]
            output.append(f"{vlan_id:7}  {vlan.name:20}  {vlan.status:6}")
        
        return "\n".join(output)
    
    def show_vlan_interfaces(self) -> str:
        """Muestra la configuración de VLAN de todas las interfaces"""
        if not self.vlan_interfaces:
            return "No hay interfaces con configuración de VLAN"
        
        output = ["VLAN Interface Configuration"]
        output.append("-" * 60)
        
        for interface_name in sorted(self.vlan_interfaces.keys()):
            interface = self.vlan_interfaces[interface_name]
            output.append(interface.get_config_summary())
        
        return "\n".join(output)
    
    def show_vlan_detail(self, vlan_id: int) -> str:
        """Muestra detalles de una VLAN específica"""
        vlan = self.get_vlan(vlan_id)
        if not vlan:
            return f"VLAN {vlan_id} no encontrada"
        
        output = [f"VLAN {vlan_id} - {vlan.name}"]
        output.append("-" * 40)
        output.append(f"Description: {vlan.description}")
        output.append(f"Status: {vlan.status}")
        output.append(f"Created: {vlan.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        output.append("Interfaces:")
        
        # Encontrar interfaces que usan esta VLAN
        interfaces_using_vlan = []
        for interface_name, interface in self.vlan_interfaces.items():
            if interface.is_vlan_allowed(vlan_id):
                interfaces_using_vlan.append(interface_name)
        
        if interfaces_using_vlan:
            for interface_name in sorted(interfaces_using_vlan):
                interface = self.vlan_interfaces[interface_name]
                output.append(f"  {interface.get_config_summary()}")
        else:
            output.append("  No hay interfaces configuradas para esta VLAN")
        
        return "\n".join(output)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de VLANs"""
        total_interfaces = len(self.vlan_interfaces)
        access_interfaces = len([i for i in self.vlan_interfaces.values() if i.mode == "access"])
        trunk_interfaces = len([i for i in self.vlan_interfaces.values() if i.mode == "trunk"])
        
        return {
            "total_vlans": len(self.vlans),
            "total_interfaces": total_interfaces,
            "access_interfaces": access_interfaces,
            "trunk_interfaces": trunk_interfaces,
            "active_vlans": len([v for v in self.vlans.values() if v.status == "active"])
        } 