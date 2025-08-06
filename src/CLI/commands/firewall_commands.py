from ..command_base import Command

class CreateACLCommand(Command):
    """Comando para crear una ACL"""
    
    def __init__(self):
        super().__init__(
            name="access-list",
            description="Crear una Access Control List",
            syntax="access-list <name> <type>"
        )
    
    def execute(self, args, context):
        if len(args) < 2:
            return "❌ Uso: access-list <name> <type>"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
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
            syntax="access-list-rule <acl_name> <action> <protocol> <source> <destination> [description]"
        )
    
    def execute(self, args, context):
        if len(args) < 5:
            return "❌ Uso: access-list-rule <acl_name> <action> <protocol> <source> <destination> [description]"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
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
            syntax="show access-list [acl_name]"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        acl_name = args[0] if args else None
        return current_device.show_acl(acl_name)

class ActivateACLCommand(Command):
    """Comando para activar una ACL"""
    
    def __init__(self):
        super().__init__(
            name="activate-acl",
            description="Activar una Access Control List",
            syntax="activate-acl <acl_name>"
        )
    
    def execute(self, args, context):
        if len(args) < 1:
            return "❌ Uso: activate-acl <acl_name>"
        
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
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
            syntax="show security-log [max_entries]"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        max_entries = int(args[0]) if args else 50
        return current_device.show_security_log(max_entries)

class ClearSecurityLogCommand(Command):
    """Comando para limpiar el log de seguridad"""
    
    def __init__(self):
        super().__init__(
            name="clear security-log",
            description="Limpiar log de seguridad del firewall",
            syntax="clear security-log"
        )
    
    def execute(self, args, context):
        current_device = context.current_device
        if not current_device:
            return "❌ No hay dispositivo seleccionado"
        
        count = current_device.clear_security_log()
        return f"✅ Log de seguridad limpiado. {count} entradas eliminadas." 