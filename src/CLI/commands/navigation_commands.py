from typing import List
from ..command_base import Command, CommandResult
from ..cli_modes import CLIMode


class ConfigureTerminalCommand(Command):
    """Comando para entrar al modo de configuración global"""
    
    def __init__(self):
        super().__init__(
            name="configure",
            description="Entra al modo de configuración global",
            syntax="configure terminal"
        )
        self.add_alias("conf")
        self.add_alias("config")
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.PRIVILEGED:
            return CommandResult(False, "El comando 'configure' solo está disponible en modo privilegiado")
        
        # Validar argumentos
        if not args or args[0].lower() not in ["terminal", "t"]:
            return CommandResult(False, "Sintaxis: configure terminal")
        
        if context.change_mode(CLIMode.GLOBAL_CONFIG):
            return CommandResult(True, "Entrando al modo de configuración global")
        else:
            return CommandResult(False, "No se pudo cambiar al modo de configuración")


class InterfaceCommand(Command):
    """Comando para entrar al modo de configuración de interfaz"""
    
    def __init__(self):
        super().__init__(
            name="interface",
            description="Entra al modo de configuración de interfaz específica",
            syntax="interface <nombre_interfaz>"
        )
        self.add_alias("int")
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.GLOBAL_CONFIG:
            return CommandResult(False, "El comando 'interface' solo está disponible en modo de configuración global")
        
        if not self.validate_args(args, min_args=1, max_args=1):
            return CommandResult(False, "Sintaxis: interface <nombre_interfaz>")
        
        interface_name = args[0]
        
        # Validar que el dispositivo tenga la interfaz
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Buscar la interfaz en el dispositivo
        target_interface = None
        for interface in context.current_device.interfaces:
            if interface.name.lower() == interface_name.lower():
                target_interface = interface
                break
        
        if not target_interface:
            available_interfaces = [iface.name for iface in context.current_device.interfaces]
            return CommandResult(
                False, 
                f"Interfaz '{interface_name}' no encontrada. Disponibles: {', '.join(available_interfaces)}"
            )
        
        # Cambiar al modo de configuración de interfaz
        context.current_interface = target_interface
        if context.change_mode(CLIMode.INTERFACE_CONFIG):
            return CommandResult(True, f"Entrando al modo de configuración de interfaz {interface_name}")
        else:
            return CommandResult(False, "No se pudo cambiar al modo de configuración de interfaz")


class EndCommand(Command):
    """Comando para regresar directamente al modo privilegiado"""
    
    def __init__(self):
        super().__init__(
            name="end",
            description="Regresa directamente al modo privilegiado desde cualquier modo de configuración",
            syntax="end"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode in [CLIMode.USER, CLIMode.PRIVILEGED]:
            return CommandResult(False, "El comando 'end' solo está disponible en modos de configuración")
        
        # Limpiar contexto de interfaz si estamos en config de interfaz
        if context.current_mode == CLIMode.INTERFACE_CONFIG:
            context.current_interface = None
        
        # Regresar directamente al modo privilegiado
        context.reset_to_privileged()
        return CommandResult(True, "Regresando al modo privilegiado") 