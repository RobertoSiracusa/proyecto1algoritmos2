from ..command_base import Command
from typing import List

class CreateACLCommand(Command):
    """Comando para crear una ACL"""
    
    def __init__(self):
        super().__init__(
            name="access-list",
            description="Crear una Access Control List",
            usage="access-list <name> <type>",
            examples=[
                "access-list INBOUND extended",
                "access-list OUTBOUND standard"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 2:
            return "❌ Uso: access-list <name> <type>"
        
        acl_name = args[0]
        acl_type = args[1].lower()
        
        if acl_type not in ["standard", "extended"]:
            return "❌ Tipo de ACL debe ser 'standard' o 'extended'"
        
        if current_device.create_acl(acl_name, acl_type):
            return f"✅ ACL '{acl_name}' ({acl_type}) creada exitosamente"
        else:
            return f"❌ Error al crear ACL '{acl_name}'"

class AddFirewallRuleCommand(Command):
    """Comando para agregar reglas de firewall"""
    
    def __init__(self):
        super().__init__(
            name="access-list-rule",
            description="Agregar regla a una ACL",
            usage="access-list-rule <acl_name> <action> <protocol> <source> <destination> [description]",
            examples=[
                "access-list-rule INBOUND permit ip 192.168.1.0 0.0.0.255 any",
                "access-list-rule OUTBOUND deny tcp any 10.0.0.1 0.0.0.0 'Block specific host'"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 5:
            return "❌ Uso: access-list-rule <acl_name> <action> <protocol> <source> <destination> [description]"
        
        acl_name = args[0]
        action = args[1].lower()
        protocol = args[2].lower()
        source_ip = args[3]
        destination_ip = args[4]
        description = " ".join(args[5:]) if len(args) > 5 else ""
        
        if action not in ["permit", "deny"]:
            return "❌ Acción debe ser 'permit' o 'deny'"
        
        if protocol not in ["ip", "tcp", "udp", "icmp"]:
            return "❌ Protocolo debe ser 'ip', 'tcp', 'udp' o 'icmp'"
        
        # Wildcards por defecto
        source_wildcard = "0.0.0.0"
        destination_wildcard = "0.0.0.0"
        
        if current_device.add_firewall_rule(acl_name, action, protocol, source_ip, destination_ip, 
                                           source_wildcard, destination_wildcard, description):
            return f"✅ Regla agregada a ACL '{acl_name}': {action} {protocol} {source_ip} -> {destination_ip}"
        else:
            return f"❌ Error al agregar regla a ACL '{acl_name}'"

class ShowACLCommand(Command):
    """Comando para mostrar ACLs"""
    
    def __init__(self):
        super().__init__(
            name="show access-list",
            description="Mostrar Access Control Lists",
            usage="show access-list [acl_name]",
            examples=[
                "show access-list",
                "show access-list INBOUND"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        acl_name = args[0] if args else None
        return current_device.show_acl(acl_name)

class ActivateACLCommand(Command):
    """Comando para activar una ACL"""
    
    def __init__(self):
        super().__init__(
            name="activate-acl",
            description="Activar una Access Control List",
            usage="activate-acl <acl_name>",
            examples=[
                "activate-acl INBOUND",
                "activate-acl OUTBOUND"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        if len(args) < 1:
            return "❌ Uso: activate-acl <acl_name>"
        
        acl_name = args[0]
        
        if current_device.activate_acl(acl_name):
            return f"✅ ACL '{acl_name}' activada exitosamente"
        else:
            return f"❌ Error al activar ACL '{acl_name}'"

class ShowSecurityLogCommand(Command):
    """Comando para mostrar el log de seguridad"""
    
    def __init__(self):
        super().__init__(
            name="show security-log",
            description="Mostrar log de seguridad del firewall",
            usage="show security-log [max_entries]",
            examples=[
                "show security-log",
                "show security-log 20"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        max_entries = int(args[0]) if args else 50
        return current_device.show_security_log(max_entries)

class ClearSecurityLogCommand(Command):
    """Comando para limpiar el log de seguridad"""
    
    def __init__(self):
        super().__init__(
            name="clear security-log",
            description="Limpiar log de seguridad del firewall",
            usage="clear security-log",
            examples=[
                "clear security-log"
            ]
        )
    
    def execute(self, args: List[str], current_device, network) -> str:
        count = current_device.clear_security_log()
        return f"✅ Log de seguridad limpiado. {count} entradas eliminadas." 