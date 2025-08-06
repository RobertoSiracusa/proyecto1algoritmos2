from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class FirewallRule:
    """Regla de firewall individual"""
    id: int
    action: str  # "permit" o "deny"
    protocol: str  # "ip", "tcp", "udp", "icmp"
    source_ip: str
    source_wildcard: str
    destination_ip: str
    destination_wildcard: str
    source_port: Optional[str] = None
    destination_port: Optional[str] = None
    description: str = ""
    timestamp: datetime = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def matches_packet(self, packet: Any) -> bool:
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
    
    def _ip_matches(self, packet_ip: str, rule_ip: str, wildcard: str) -> bool:
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
    
    def __init__(self, name: str, acl_type: str = "extended"):
        self.name = name
        self.acl_type = acl_type  # "standard" o "extended"
        self.rules: List[FirewallRule] = []
        self._rule_counter = 1
        self.is_active = True
    
    def add_rule(self, action: str, protocol: str, source_ip: str, 
                 destination_ip: str, source_wildcard: str = "0.0.0.0",
                 destination_wildcard: str = "0.0.0.0",
                 source_port: str = None, destination_port: str = None,
                 description: str = "") -> bool:
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
            
            self.rules.append(rule)
            self._rule_counter += 1
            return True
        except Exception as e:
            print(f"Error agregando regla: {e}")
            return False
    
    def remove_rule(self, rule_id: int) -> bool:
        """Elimina una regla por ID"""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                del self.rules[i]
                return True
        return False
    
    def clear_rules(self) -> int:
        """Limpia todas las reglas"""
        count = len(self.rules)
        self.rules.clear()
        return count
    
    def evaluate_packet(self, packet: Any) -> tuple[bool, Optional[FirewallRule]]:
        """Evalúa un paquete contra todas las reglas"""
        if not self.is_active:
            return True, None
        
        for rule in self.rules:
            if rule.is_active and rule.matches_packet(packet):
                return rule.action == "permit", rule
        
        # Regla por defecto: deny
        return False, None
    
    def show_rules(self) -> str:
        """Muestra las reglas de la ACL"""
        if not self.rules:
            return f"ACL {self.name} está vacía"
        
        output = [f"Access Control List {self.name} ({self.acl_type})"]
        output.append("-" * 60)
        
        for rule in self.rules:
            status = "ACTIVE" if rule.is_active else "INACTIVE"
            output.append(f"{rule.id:3} {rule.action.upper():6} {rule.protocol:4} "
                         f"{rule.source_ip:15} {rule.source_wildcard:15} -> "
                         f"{rule.destination_ip:15} {rule.destination_wildcard:15} "
                         f"[{status}]")
            if rule.description:
                output.append(f"     {rule.description}")
        
        return "\n".join(output)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la ACL"""
        return {
            "name": self.name,
            "type": self.acl_type,
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules if r.is_active]),
            "permit_rules": len([r for r in self.rules if r.action == "permit"]),
            "deny_rules": len([r for r in self.rules if r.action == "deny"]),
            "is_active": self.is_active
        }

class FirewallManager:
    """Gestor principal de firewall"""
    
    def __init__(self):
        self.acls: Dict[str, FirewallACL] = {}
        self.active_acls: List[str] = []
        self.security_log: List[Dict[str, Any]] = []
        self._log_counter = 1
    
    def create_acl(self, name: str, acl_type: str = "extended") -> bool:
        """Crea una nueva ACL"""
        if name in self.acls:
            return False
        
        self.acls[name] = FirewallACL(name, acl_type)
        return True
    
    def delete_acl(self, name: str) -> bool:
        """Elimina una ACL"""
        if name in self.acls:
            del self.acls[name]
            if name in self.active_acls:
                self.active_acls.remove(name)
            return True
        return False
    
    def get_acl(self, name: str) -> Optional[FirewallACL]:
        """Obtiene una ACL por nombre"""
        return self.acls.get(name)
    
    def activate_acl(self, name: str) -> bool:
        """Activa una ACL"""
        if name in self.acls and name not in self.active_acls:
            self.active_acls.append(name)
            return True
        return False
    
    def deactivate_acl(self, name: str) -> bool:
        """Desactiva una ACL"""
        if name in self.active_acls:
            self.active_acls.remove(name)
            return True
        return False
    
    def evaluate_packet(self, packet: Any) -> tuple[bool, Optional[FirewallRule], Optional[str]]:
        """Evalúa un paquete contra todas las ACLs activas"""
        for acl_name in self.active_acls:
            acl = self.acls.get(acl_name)
            if acl:
                permitted, matched_rule = acl.evaluate_packet(packet)
                if not permitted:
                    self._log_security_event(packet, "DENIED", acl_name, matched_rule)
                    return False, matched_rule, acl_name
        
        # Si pasa todas las ACLs, está permitido
        self._log_security_event(packet, "PERMITTED", None, None)
        return True, None, None
    
    def _log_security_event(self, packet: Any, action: str, acl_name: str = None, 
                           rule: FirewallRule = None):
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
            self.security_log.append(log_entry)
            self._log_counter += 1
        except:
            pass
    
    def show_security_log(self, max_entries: int = 50) -> str:
        """Muestra el log de seguridad"""
        if not self.security_log:
            return "No hay eventos de seguridad registrados"
        
        output = ["SECURITY LOG - Firewall Events"]
        output.append("-" * 80)
        
        # Mostrar los eventos más recientes
        recent_logs = self.security_log[-max_entries:]
        
        for log in recent_logs:
            timestamp = log["timestamp"].strftime("%H:%M:%S")
            output.append(f"{log['id']:4} [{timestamp}] {log['action']:8} "
                         f"{log['source_ip']:15} -> {log['destination_ip']:15} "
                         f"ACL: {log['acl_name'] or 'N/A'}")
        
        return "\n".join(output)
    
    def clear_security_log(self) -> int:
        """Limpia el log de seguridad"""
        count = len(self.security_log)
        self.security_log.clear()
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del firewall"""
        total_denied = len([log for log in self.security_log if log["action"] == "DENIED"])
        total_permitted = len([log for log in self.security_log if log["action"] == "PERMITTED"])
        
        return {
            "total_acls": len(self.acls),
            "active_acls": len(self.active_acls),
            "total_rules": sum(len(acl.rules) for acl in self.acls.values()),
            "security_events": len(self.security_log),
            "packets_denied": total_denied,
            "packets_permitted": total_permitted
        } 