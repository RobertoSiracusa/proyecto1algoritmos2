from typing import List
from ..command_base import Command, CommandResult
from ..cli_modes import CLIMode


class HelpCommand(Command):
    """Comando para mostrar ayuda"""
    
    def __init__(self):
        super().__init__(
            name="help",
            description="Muestra ayuda sobre comandos disponibles",
            syntax="help [comando]"
        )
        self.add_alias("?")
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not args:
            # Mostrar ayuda general
            from ..cli_modes import CLIModeManager
            help_text = CLIModeManager.get_help_for_mode(context.current_mode)
            return CommandResult(True, help_text)
        else:
            # Mostrar ayuda de comando específico
            command_name = args[0]
            # Aquí podríamos buscar en el registry de comandos
            return CommandResult(True, f"Ayuda para comando '{command_name}' no implementada aún")


class ExitCommand(Command):
    """Comando para salir del modo actual o del CLI"""
    
    def __init__(self):
        super().__init__(
            name="exit",
            description="Sale del modo actual o termina el CLI",
            syntax="exit"
        )
        self.add_alias("quit")
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode == CLIMode.USER:
            # En modo usuario, salir del CLI completamente
            return CommandResult(True, "CLI_EXIT", {"exit": True})
        else:
            # En otros modos, regresar al modo anterior
            if context.pop_mode():
                return CommandResult(True, f"Regresando a modo {context.current_mode.value}")
            else:
                return CommandResult(False, "No se puede regresar a modo anterior")


class EnableCommand(Command):
    """Comando para entrar al modo privilegiado"""
    
    def __init__(self):
        super().__init__(
            name="enable",
            description="Entra al modo privilegiado",
            syntax="enable"
        )
        self.add_alias("en")
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.USER:
            return CommandResult(False, "El comando 'enable' solo está disponible en modo usuario")
        
        if context.change_mode(CLIMode.PRIVILEGED):
            return CommandResult(True, "Entrando al modo privilegiado")
        else:
            return CommandResult(False, "No se pudo cambiar al modo privilegiado")


class DisableCommand(Command):
    """Comando para regresar al modo usuario"""
    
    def __init__(self):
        super().__init__(
            name="disable",
            description="Regresa al modo usuario",
            syntax="disable"
        )
        self.add_alias("dis")
    
    def execute(self, args: List[str], context) -> CommandResult:
        if context.current_mode != CLIMode.PRIVILEGED:
            return CommandResult(False, "El comando 'disable' solo está disponible en modo privilegiado")
        
        # Regresar al modo usuario
        context.current_mode = CLIMode.USER
        context.mode_stack = [CLIMode.USER]
        return CommandResult(True, "Regresando al modo usuario")


class SelectDeviceCommand(Command):
    """Comando para seleccionar un dispositivo específico"""
    
    def __init__(self):
        super().__init__(
            name="select",
            description="Selecciona un dispositivo específico para trabajar",
            syntax="select device <nombre_dispositivo>"
        )
        self.add_alias("sel")
    
    def execute(self, args: List[str], context) -> CommandResult:
        # Validar argumentos
        if not self.validate_args(args, min_args=2, max_args=2):
            return CommandResult(False, "Sintaxis: select device <nombre_dispositivo>")
        
        if args[0].lower() != "device":
            return CommandResult(False, "Sintaxis: select device <nombre_dispositivo>")
        
        device_name = args[1]
        
        # Verificar que hay una red disponible
        network = getattr(context, 'network', None)
        if not network:
            return CommandResult(False, "No hay red disponible")
        
        # Buscar el dispositivo en la red
        target_device = network.getDevice(device_name)
        if not target_device:
            # Mostrar dispositivos disponibles
            available_devices = network.getAllDeviceNames()
            available_list = ', '.join(available_devices)
            return CommandResult(False, f"Dispositivo '{device_name}' no encontrado. Disponibles: {available_list}")
        
        # Establecer el dispositivo como actual
        context.current_device = target_device
        
        return CommandResult(True, f"Dispositivo '{device_name}' seleccionado. Ahora puedes usar comandos sin especificar el dispositivo.")


class ShowCurrentDeviceCommand(Command):
    """Comando para mostrar el dispositivo actualmente seleccionado"""
    
    def __init__(self):
        super().__init__(
            name="current",
            description="Muestra el dispositivo actualmente seleccionado",
            syntax="current"
        )
        self.add_alias("cur")
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado. Use 'select device <nombre>' para seleccionar uno.")
        
        device = context.current_device
        info = f"Dispositivo actual: {device.name} ({device.type}) - Estado: {device.status}"
        
        # Agregar información de interfaces
        if device.interfaces.size > 0:
            info += f"\nInterfaces: {device.interfaces.size} total"
            active_count = 0
            connected_count = 0
            
            current = device.interfaces.head
            while current:
                interface = current.data
                if interface.isUp():
                    active_count += 1
                if interface.isConnected():
                    connected_count += 1
                current = current.next
            
            info += f", {active_count} activas, {connected_count} conectadas"
        
        return CommandResult(True, info) 