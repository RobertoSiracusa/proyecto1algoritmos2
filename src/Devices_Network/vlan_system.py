import sys
import os
from datetime import datetime

# Agregar el directorio padre al path para importar DataEstructures
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DataEstructures import LinkedList


class VLAN:
    """Representa una VLAN individual"""
    
    def __init__(self, vlan_id, name, description="", status="active"):
        self.id = vlan_id
        self.name = name
        self.description = description
        self.status = status  # active, shutdown
        self.created_at = datetime.now()
    
    def __str__(self):
        return f"VLAN {self.id} - {self.name} ({self.status})"

class VLANInterface:
    """Configuración de VLAN para una interfaz"""
    
    def __init__(self, interface_name):
        self.interface_name = interface_name
        self.mode = "access"  # access, trunk
        self.access_vlan = 1  # VLAN por defecto
        self.trunk_vlans = LinkedList()  # VLANs permitidas en trunk (simulando set)
        self.native_vlan = 1  # VLAN nativa para trunk
        self.is_active = True
    
    def set_access_mode(self, vlan_id):
        """Configura la interfaz en modo access"""
        if not 1 <= vlan_id <= 4094:
            return False
        
        self.mode = "access"
        self.access_vlan = vlan_id
        self.trunk_vlans.clear()
        return True
    
    def set_trunk_mode(self, allowed_vlans=None, native_vlan=1):
        """Configura la interfaz en modo trunk"""
        if not 1 <= native_vlan <= 4094:
            return False
        
        self.mode = "trunk"
        self.native_vlan = native_vlan
        
        # Limpiar la lista enlazada
        self.trunk_vlans.clear()
        
        if allowed_vlans:
            # Agregar VLANs válidas a la lista enlazada
            for v in allowed_vlans:
                if 1 <= v <= 4094:
                    self.trunk_vlans.add_node(v)
        else:
            # Permitir todas las VLANs por defecto (solo las primeras 100 para eficiencia)
            for v in range(1, 101):
                self.trunk_vlans.add_node(v)
        
        return True
    
    def add_trunk_vlan(self, vlan_id):
        """Agrega una VLAN al trunk"""
        if self.mode != "trunk":
            return False
        
        if 1 <= vlan_id <= 4094:
            # Verificar si ya existe para evitar duplicados
            if not self.trunk_vlans.find(vlan_id):
                self.trunk_vlans.add_node(vlan_id)
            return True
        return False
    
    def remove_trunk_vlan(self, vlan_id):
        """Remueve una VLAN del trunk"""
        if self.mode != "trunk":
            return False
        
        self.trunk_vlans.remove_node(vlan_id)
        return True
    
    def is_vlan_allowed(self, vlan_id):
        """Verifica si una VLAN está permitida en esta interfaz"""
        if self.mode == "access":
            return vlan_id == self.access_vlan
        elif self.mode == "trunk":
            return self.trunk_vlans.find(vlan_id)
        return False
    
    def get_config_summary(self):
        """Obtiene un resumen de la configuración"""
        if self.mode == "access":
            return f"{self.interface_name}: access vlan {self.access_vlan}"
        elif self.mode == "trunk":
            vlan_elements = self.trunk_vlans.traverse()
            vlan_list = ",".join(map(str, sorted(vlan_elements)))
            return f"{self.interface_name}: trunk allowed vlans {vlan_list}, native vlan {self.native_vlan}"
        return f"{self.interface_name}: no vlan config"

class VLANManager:
    """Gestor principal de VLANs"""
    
    def __init__(self):
        # Usar listas enlazadas para simular diccionarios
        self.vlans = LinkedList()  # Lista de VLANs
        self.vlan_interfaces = LinkedList()  # Lista de interfaces VLAN
        self._vlan_counter = 1
    
    def _find_vlan_by_id(self, vlan_id):
        """Busca una VLAN por ID en la lista enlazada"""
        current = self.vlans.head
        while current is not None:
            if current.data.id == vlan_id:
                return current.data
            current = current.next
        return None
    
    def _find_interface_by_name(self, interface_name):
        """Busca una interfaz por nombre en la lista enlazada"""
        current = self.vlan_interfaces.head
        while current is not None:
            if current.data.interface_name == interface_name:
                return current.data
            current = current.next
        return None
    
    def create_vlan(self, vlan_id, name, description=""):
        """Crea una nueva VLAN"""
        if not 1 <= vlan_id <= 4094:
            return False
        
        # Verificar si ya existe
        if self._find_vlan_by_id(vlan_id):
            return False
        
        new_vlan = VLAN(vlan_id, name, description)
        self.vlans.add_node(new_vlan)
        return True
    
    def delete_vlan(self, vlan_id):
        """Elimina una VLAN"""
        vlan = self._find_vlan_by_id(vlan_id)
        if vlan:
            # Verificar que no esté en uso
            current = self.vlan_interfaces.head
            while current is not None:
                if current.data.is_vlan_allowed(vlan_id):
                    return False
                current = current.next
            
            # Remover la VLAN
            self.vlans.remove_node(vlan)
            return True
        return False
    
    def get_vlan(self, vlan_id):
        """Obtiene una VLAN por ID"""
        return self._find_vlan_by_id(vlan_id)
    
    def configure_interface_access(self, interface_name, vlan_id):
        """Configura una interfaz en modo access"""
        if not self._find_vlan_by_id(vlan_id):
            return False
        
        interface = self._find_interface_by_name(interface_name)
        if not interface:
            new_interface = VLANInterface(interface_name)
            self.vlan_interfaces.add_node(new_interface)
            interface = new_interface
        
        return interface.set_access_mode(vlan_id)
    
    def configure_interface_trunk(self, interface_name, allowed_vlans=None, native_vlan=1):
        """Configura una interfaz en modo trunk"""
        if not self._find_vlan_by_id(native_vlan):
            return False
        
        interface = self._find_interface_by_name(interface_name)
        if not interface:
            new_interface = VLANInterface(interface_name)
            self.vlan_interfaces.add_node(new_interface)
            interface = new_interface
        
        return interface.set_trunk_mode(allowed_vlans, native_vlan)
    
    def get_interface_config(self, interface_name):
        """Obtiene la configuración de VLAN de una interfaz"""
        return self._find_interface_by_name(interface_name)
    
    def show_vlans(self):
        """Muestra todas las VLANs"""
        if self.vlans.is_empty():
            return "No hay VLANs configuradas"
        
        output = ["VLAN Database"]
        output.append("-" * 50)
        output.append("VLAN ID  Name                    Status")
        output.append("-" * 50)
        
        # Obtener todas las VLANs y ordenarlas por ID
        vlans_list = self.vlans.traverse()
        vlans_sorted = sorted(vlans_list, key=lambda v: v.id)
        
        for vlan in vlans_sorted:
            output.append(f"{vlan.id:7}  {vlan.name:20}  {vlan.status:6}")
        
        return "\n".join(output)
    
    def show_vlan_interfaces(self):
        """Muestra la configuración de VLAN de todas las interfaces"""
        if self.vlan_interfaces.is_empty():
            return "No hay interfaces con configuración de VLAN"
        
        output = ["VLAN Interface Configuration"]
        output.append("-" * 60)
        
        # Obtener todas las interfaces y ordenarlas por nombre
        interfaces_list = self.vlan_interfaces.traverse()
        interfaces_sorted = sorted(interfaces_list, key=lambda i: i.interface_name)
        
        for interface in interfaces_sorted:
            output.append(interface.get_config_summary())
        
        return "\n".join(output)
    
    def show_vlan_detail(self, vlan_id):
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
        current = self.vlan_interfaces.head
        while current is not None:
            if current.data.is_vlan_allowed(vlan_id):
                interfaces_using_vlan.append(current.data.interface_name)
            current = current.next
        
        if interfaces_using_vlan:
            for interface_name in sorted(interfaces_using_vlan):
                interface = self._find_interface_by_name(interface_name)
                output.append(f"  {interface.get_config_summary()}")
        else:
            output.append("  No hay interfaces configuradas para esta VLAN")
        
        return "\n".join(output)
    
    def get_statistics(self):
        """Obtiene estadísticas del sistema de VLANs"""
        total_interfaces = self.vlan_interfaces.get_size()
        
        # Contar interfaces por tipo
        access_interfaces = 0
        trunk_interfaces = 0
        current = self.vlan_interfaces.head
        while current is not None:
            if current.data.mode == "access":
                access_interfaces += 1
            elif current.data.mode == "trunk":
                trunk_interfaces += 1
            current = current.next
        
        # Contar VLANs activas
        active_vlans = 0
        current = self.vlans.head
        while current is not None:
            if current.data.status == "active":
                active_vlans += 1
            current = current.next
        
        return {
            "total_vlans": self.vlans.get_size(),
            "total_interfaces": total_interfaces,
            "access_interfaces": access_interfaces,
            "trunk_interfaces": trunk_interfaces,
            "active_vlans": active_vlans
        } 