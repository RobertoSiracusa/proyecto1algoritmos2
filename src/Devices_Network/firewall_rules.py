import sys
import os
from datetime import datetime
import re

# Agregar el directorio padre al path para importar DataEstructures
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DataEstructures import LinkedList


class FirewallRule:
    """Regla de firewall individual"""
    
    def __init__(self, id, action, protocol, source_ip, source_wildcard, destination_ip, destination_wildcard, source_port=None, destination_port=None, description="", timestamp=None, is_active=True):
        self.id = id
        self.action = action  # "permit" o "deny"
        self.protocol = protocol  # "ip", "tcp", "udp", "icmp"
        self.source_ip = source_ip
        self.source_wildcard = source_wildcard
        self.destination_ip = destination_ip
        self.destination_wildcard = destination_wildcard
        self.source_port = source_port
        self.destination_port = destination_port
        self.description = description
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.is_active = is_active
    
    def matches_packet(self, packet):
        """Verifica si un paquete coincide con esta regla"""
        try:
            # Extraer información del paquete
            src_ip = getattr(packet, 'sourceIp', '')
            dst_ip = getattr(packet, 'destinationIp', '')
            
            # Verificar IPs
            if not self._ip_matches(src_ip, self.source_ip, self.source_wildcard):
                return False
            if not self._ip_matches(dst_ip, self.destination_ip, self.destination_wildcard):
                return False
            
            # Verificar protocolo (simplificado)
            if self.protocol != "ip" and hasattr(packet, 'protocol'):
                if packet.protocol != self.protocol:
                    return False
            
            return True
        except:
            return False
    
    def _ip_matches(self, packet_ip, rule_ip, wildcard):
        """Verifica si una IP coincide con la regla usando wildcard"""
        if rule_ip == "any" or wildcard == "0.0.0.0":
            return True
        
        try:
            # Convertir IPs a números para comparación
            packet_parts = [int(x) for x in packet_ip.split('.')]
            rule_parts = [int(x) for x in rule_ip.split('.')]
            wildcard_parts = [int(x) for x in wildcard.split('.')]
            
            for i in range(4):
                if (packet_parts[i] & ~wildcard_parts[i]) != (rule_parts[i] & ~wildcard_parts[i]):
                    return False
            return True
        except:
            return False

class FirewallACL:
    """Access Control List para firewall"""
    
    def __init__(self, name, acl_type="extended"):
        self.name = name
        self.acl_type = acl_type  # "standard" o "extended"
        self.rules = LinkedList()  # Lista de reglas (simulando lista)
        self._rule_counter = 1
        self.is_active = True
    
    def add_rule(self, action, protocol, source_ip, 
                 destination_ip, source_wildcard="0.0.0.0",
                 destination_wildcard="0.0.0.0",
                 source_port=None, destination_port=None,
                 description=""):
        """Agrega una regla a la ACL"""
        try:
            rule = FirewallRule(
                id=self._rule_counter,
                action=action.lower(),
                protocol=protocol.lower(),
                source_ip=source_ip,
                source_wildcard=source_wildcard,
                destination_ip=destination_ip,
                destination_wildcard=destination_wildcard,
                source_port=source_port,
                destination_port=destination_port,
                description=description
            )
            
            self.rules.add_node(rule)
            self._rule_counter += 1
            return True
        except Exception as e:
            print(f"Error agregando regla: {e}")
            return False
    
    def remove_rule(self, rule_id):
        """Elimina una regla por ID"""
        current = self.rules.head
        while current is not None:
            if current.data.id == rule_id:
                self.rules.remove_node(current.data)
                return True
            current = current.next
        return False
    
    def clear_rules(self):
        """Limpia todas las reglas"""
        count = self.rules.get_size()
        self.rules.clear()
        return count
    
    def evaluate_packet(self, packet):
        """Evalúa un paquete contra todas las reglas"""
        if not self.is_active:
            return True, None
        
        current = self.rules.head
        while current is not None:
            rule = current.data
            if rule.is_active and rule.matches_packet(packet):
                return rule.action == "permit", rule
            current = current.next
        
        # Regla por defecto: deny
        return False, None
    
    def show_rules(self):
        """Muestra las reglas de la ACL"""
        if self.rules.is_empty():
            return f"ACL {self.name} está vacía"
        
        output = [f"Access Control List {self.name} ({self.acl_type})"]
        output.append("-" * 60)
        
        current = self.rules.head
        while current is not None:
            rule = current.data
            status = "ACTIVE" if rule.is_active else "INACTIVE"
            output.append(f"{rule.id:3} {rule.action.upper():6} {rule.protocol:4} "
                         f"{rule.source_ip:15} {rule.source_wildcard:15} -> "
                         f"{rule.destination_ip:15} {rule.destination_wildcard:15} "
                         f"[{status}]")
            if rule.description:
                output.append(f"     {rule.description}")
            current = current.next
        
        return "\n".join(output)
    
    def get_statistics(self):
        """Obtiene estadísticas de la ACL"""
        total_rules = self.rules.get_size()
        active_rules = 0
        permit_rules = 0
        deny_rules = 0
        
        current = self.rules.head
        while current is not None:
            rule = current.data
            if rule.is_active:
                active_rules += 1
            if rule.action == "permit":
                permit_rules += 1
            elif rule.action == "deny":
                deny_rules += 1
            current = current.next
        
        return {
            "name": self.name,
            "type": self.acl_type,
            "total_rules": total_rules,
            "active_rules": active_rules,
            "permit_rules": permit_rules,
            "deny_rules": deny_rules,
            "is_active": self.is_active
        }

class FirewallManager:
    """Gestor principal de firewall"""
    
    def __init__(self):
        self.acls = LinkedList()  # Lista de ACLs (simulando diccionario)
        self.active_acls = LinkedList()  # Lista de ACLs activas (simulando lista)
        self.security_log = LinkedList()  # Lista de eventos de seguridad (simulando lista)
        self._log_counter = 1
    
    def _find_acl_by_name(self, name):
        """Busca una ACL por nombre"""
        current = self.acls.head
        while current is not None:
            if current.data.name == name:
                return current.data
            current = current.next
        return None
    
    def create_acl(self, name, acl_type="extended"):
        """Crea una nueva ACL"""
        if self._find_acl_by_name(name):
            return False
        
        new_acl = FirewallACL(name, acl_type)
        self.acls.add_node(new_acl)
        return True
    
    def delete_acl(self, name):
        """Elimina una ACL"""
        acl = self._find_acl_by_name(name)
        if acl:
            self.acls.remove_node(acl)
            # Remover de ACLs activas si está ahí
            current = self.active_acls.head
            while current is not None:
                if current.data == name:
                    self.active_acls.remove_node(current.data)
                    break
                current = current.next
            return True
        return False
    
    def get_acl(self, name):
        """Obtiene una ACL por nombre"""
        return self._find_acl_by_name(name)
    
    def activate_acl(self, name):
        """Activa una ACL"""
        if self._find_acl_by_name(name):
            # Verificar si ya está activa
            current = self.active_acls.head
            while current is not None:
                if current.data == name:
                    return False  # Ya está activa
                current = current.next
            self.active_acls.add_node(name)
            return True
        return False
    
    def deactivate_acl(self, name):
        """Desactiva una ACL"""
        current = self.active_acls.head
        while current is not None:
            if current.data == name:
                self.active_acls.remove_node(current.data)
                return True
            current = current.next
        return False
    
    def evaluate_packet(self, packet):
        """Evalúa un paquete contra todas las ACLs activas"""
        current = self.active_acls.head
        while current is not None:
            acl_name = current.data
            acl = self._find_acl_by_name(acl_name)
            if acl:
                permitted, matched_rule = acl.evaluate_packet(packet)
                if not permitted:
                    self._log_security_event(packet, "DENIED", acl_name, matched_rule)
                    return False, matched_rule, acl_name
            current = current.next
        
        # Si pasa todas las ACLs, está permitido
        self._log_security_event(packet, "PERMITTED", None, None)
        return True, None, None
    
    def _log_security_event(self, packet, action, acl_name=None, 
                           rule=None):
        """Registra un evento de seguridad"""
        try:
            log_entry = {
                "id": self._log_counter,
                "timestamp": datetime.now(),
                "action": action,
                "source_ip": getattr(packet, 'sourceIp', 'unknown'),
                "destination_ip": getattr(packet, 'destinationIp', 'unknown'),
                "acl_name": acl_name,
                "rule_id": rule.id if rule else None,
                "packet_id": getattr(packet, 'id', 'unknown')
            }
            self.security_log.add_node(log_entry)
            self._log_counter += 1
        except:
            pass
    
    def show_security_log(self, max_entries=50):
        """Muestra el log de seguridad"""
        if self.security_log.is_empty():
            return "No hay eventos de seguridad registrados"
        
        output = ["SECURITY LOG - Firewall Events"]
        output.append("-" * 80)
        
        # Obtener todos los logs y mostrar los más recientes
        all_logs = self.security_log.traverse()
        recent_logs = all_logs[-max_entries:] if len(all_logs) > max_entries else all_logs
        
        for log in recent_logs:
            timestamp = log["timestamp"].strftime("%H:%M:%S")
            output.append(f"{log['id']:4} [{timestamp}] {log['action']:8} "
                         f"{log['source_ip']:15} -> {log['destination_ip']:15} "
                         f"ACL: {log['acl_name'] or 'N/A'}")
        
        return "\n".join(output)
    
    def clear_security_log(self):
        """Limpia el log de seguridad"""
        count = self.security_log.get_size()
        self.security_log.clear()
        return count
    
    def get_statistics(self):
        """Obtiene estadísticas del firewall"""
        total_denied = 0
        total_permitted = 0
        
        current = self.security_log.head
        while current is not None:
            log = current.data
            if log["action"] == "DENIED":
                total_denied += 1
            elif log["action"] == "PERMITTED":
                total_permitted += 1
            current = current.next
        
        total_rules = 0
        current = self.acls.head
        while current is not None:
            total_rules += current.data.rules.get_size()
            current = current.next
        
        return {
            "total_acls": self.acls.get_size(),
            "active_acls": self.active_acls.get_size(),
            "total_rules": total_rules,
            "security_events": self.security_log.get_size(),
            "packets_denied": total_denied,
            "packets_permitted": total_permitted
        } 