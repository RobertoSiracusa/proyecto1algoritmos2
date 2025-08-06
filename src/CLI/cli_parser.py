from typing import List, Optional, Dict, Any
import sys
import os
import shlex

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .cli_modes import CLIMode, CLIModeManager, CLIModeContext
from .command_base import Command, CommandResult, CommandRegistry
from .commands import *


class CLIParser:
    """
    Parser principal del CLI que maneja todos los modos, comandos y contexto.
    Implementa una interfaz de línea de comandos completa para el simulador de red.
    """
    
    def __init__(self, network=None, communication_manager=None):
        """
        Inicializa el parser CLI
        
        Args:
            network: Instancia de Network para operaciones de red
            communication_manager: Instancia de CommunicationManager para paquetes
        """
        self.context = CLIModeContext(CLIMode.USER)
        self.command_registry = CommandRegistry()
        self.history = []  # Historial de comandos
        self.running = False
        
        # Referencias a componentes del sistema
        self.network = network
        self.communication_manager = communication_manager
        
        # Configurar referencias en el contexto
        if communication_manager:
            self.context.communication_manager = communication_manager
        if network:
            self.context.network = network
        
        # Registrar todos los comandos
        self._register_commands()
        
        # Configuración del parser
        self.max_history = 100
        self.banner_shown = False
    
    def _register_commands(self):
        """Registra todos los comandos disponibles en el CLI"""
        # Comandos básicos
        self.command_registry.register(HelpCommand())
        self.command_registry.register(ExitCommand())
        self.command_registry.register(EnableCommand())
        self.command_registry.register(DisableCommand())
        
        # Comandos de navegación
        self.command_registry.register(ConfigureTerminalCommand())
        self.command_registry.register(InterfaceCommand())
        self.command_registry.register(EndCommand())
        
        # Comandos show
        self.command_registry.register(ShowCommand())
        
        # Comandos de red
        self.command_registry.register(SendPacketCommand())
        self.command_registry.register(TickCommand())
        self.command_registry.register(ProcessCommand())
        self.command_registry.register(PingCommand())
        self.command_registry.register(TracerouteCommand())
        
        # Registrar comandos de configuración
        self.command_registry.register(HostnameCommand())
        self.command_registry.register(IpAddressCommand())
        self.command_registry.register(ShutdownCommand())
        self.command_registry.register(NoShutdownCommand())
        
        # ===== NUEVO: Módulo 6 Configuration Persistence - Registrar comandos de persistencia =====
        self.command_registry.register(SaveRunningConfigCommand())
        self.command_registry.register(LoadConfigCommand())
        
        # ===== NUEVO: Comandos de routing =====
        self.command_registry.register(AddRouteCommand())
        self.command_registry.register(RemoveRouteCommand())
        self.command_registry.register(DefaultRouteCommand())
        self.command_registry.register(ClearRoutesCommand())
        self.command_registry.register(ShowRoutingTableCommand())
    
    def parse_command(self, command_string: str) -> tuple:
        """
        Parsea una línea de comando en comando y argumentos
        
        Args:
            command_string: String del comando completo
            
        Returns:
            tuple: (comando, lista_de_argumentos)
        """
        if not command_string or not command_string.strip():
            return None, []
        
        try:
            # Usar shlex para parsear respetando comillas
            tokens = shlex.split(command_string.strip())
            if not tokens:
                return None, []
            
            command = tokens[0]
            args = tokens[1:] if len(tokens) > 1 else []
            
            return command, args
            
        except ValueError as e:
            # Error de parseo (ej: comillas no cerradas)
            raise ValueError(f"Error en sintaxis del comando: {str(e)}")
    
    def execute_command(self, command: str, args: List[str]) -> CommandResult:
        """
        Ejecuta un comando con los argumentos dados
        
        Args:
            command: Nombre del comando
            args: Lista de argumentos
            
        Returns:
            CommandResult: Resultado de la ejecución
        """
        if not command:
            return CommandResult(False, "Comando vacío")
        
        # Buscar el comando en el registry
        cmd_obj = self.command_registry.get_command(command)
        
        if not cmd_obj:
            return CommandResult(False, f"Comando '{command}' no reconocido. Use 'help' para ver comandos disponibles.")
        
        # Verificar que el comando esté disponible en el modo actual
        available_commands = CLIModeManager.get_available_commands(self.context.current_mode)
        if command.lower() not in [cmd.lower() for cmd in available_commands]:
            return CommandResult(False, f"Comando '{command}' no disponible en modo {self.context.current_mode.value}")
        
        try:
            # Ejecutar el comando
            result = cmd_obj.execute(args, self.context)
            
            # Agregar al historial si fue exitoso
            if result.success:
                self._add_to_history(f"{command} {' '.join(args)}".strip())
            
            return result
            
        except Exception as e:
            return CommandResult(False, f"Error ejecutando comando: {str(e)}")
    
    def change_mode(self, new_mode: CLIMode) -> bool:
        """
        Cambia el modo CLI actual
        
        Args:
            new_mode: Nuevo modo CLI
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        return self.context.change_mode(new_mode)
    
    def display_prompt(self) -> str:
        """
        Muestra el prompt correcto para el modo actual
        
        Returns:
            str: String del prompt
        """
        return self.context.get_prompt()
    
    def set_current_device(self, device):
        """
        Establece el dispositivo actual para el contexto
        
        Args:
            device: Instancia de Device
        """
        self.context.current_device = device
    
    def get_current_device(self):
        """Obtiene el dispositivo actual"""
        return self.context.current_device
    
    def validate_input(self, command_string: str) -> tuple:
        """
        Valida la entrada del usuario y retorna errores si los hay
        
        Args:
            command_string: String del comando
            
        Returns:
            tuple: (es_válido, mensaje_error)
        """
        if not command_string:
            return True, ""
        
        # Validaciones básicas
        if len(command_string) > 1000:
            return False, "Comando demasiado largo"
        
        # Verificar caracteres peligrosos
        dangerous_chars = [';', '&', '|', '`', '$']
        for char in dangerous_chars:
            if char in command_string:
                return False, f"Carácter no permitido: {char}"
        
        return True, ""
    
    def _add_to_history(self, command: str):
        """Agrega un comando al historial"""
        self.history.append(command)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_command_history(self) -> List[str]:
        """Obtiene el historial de comandos"""
        return self.history.copy()
    
    def clear_history(self):
        """Limpia el historial de comandos"""
        self.history.clear()
    
    def get_available_commands(self) -> List[str]:
        """Obtiene comandos disponibles para el modo actual"""
        return CLIModeManager.get_available_commands(self.context.current_mode)
    
    def get_command_help(self, command_name: str) -> str:
        """
        Obtiene ayuda para un comando específico
        
        Args:
            command_name: Nombre del comando
            
        Returns:
            str: Texto de ayuda
        """
        cmd = self.command_registry.get_command(command_name)
        if cmd:
            return cmd.get_help()
        else:
            return f"Comando '{command_name}' no encontrado"
    
    def auto_complete(self, partial_command: str) -> List[str]:
        """
        Proporciona autocompletado para comandos
        
        Args:
            partial_command: Comando parcial
            
        Returns:
            List[str]: Lista de posibles comandos
        """
        available_commands = self.get_available_commands()
        matches = []
        
        for cmd in available_commands:
            if cmd.lower().startswith(partial_command.lower()):
                matches.append(cmd)
        
        return matches
    
    def show_banner(self):
        """Muestra el banner de bienvenida"""
        if not self.banner_shown:
            banner = """
═══════════════════════════════════════════════════════════════
         CLI SIMULADOR DE RED - MÓDULO 4
         Implementación con Patrón Command
═══════════════════════════════════════════════════════════════

Bienvenido al simulador de red CLI.
Escriba 'help' para ver comandos disponibles.
Escriba 'enable' para entrar al modo privilegiado.

═══════════════════════════════════════════════════════════════
            """
            print(banner)
            self.banner_shown = True
    
    def run_interactive(self):
        """
        Ejecuta el CLI en modo interactivo
        """
        self.running = True
        self.show_banner()
        
        try:
            while self.running:
                try:
                    # Mostrar prompt y obtener entrada
                    prompt = self.display_prompt()
                    user_input = input(f"{prompt} ").strip()
                    
                    # Saltar líneas vacías
                    if not user_input:
                        continue
                    
                    # Parsear comando
                    try:
                        command, args = self.parse_command(user_input)
                        if not command:
                            continue
                    except ValueError as e:
                        print(f"Error: {e}")
                        continue
                    
                    # Validar entrada
                    is_valid, error_msg = self.validate_input(user_input)
                    if not is_valid:
                        print(f"Error: {error_msg}")
                        continue
                    
                    # Ejecutar comando
                    result = self.execute_command(command, args)
                    
                    # Mostrar resultado
                    if result.message:
                        print(result.message)
                    
                    # Manejar comandos especiales
                    if result.data and isinstance(result.data, dict):
                        if result.data.get("exit"):
                            print("Saliendo del CLI...")
                            self.running = False
                            break
                
                except KeyboardInterrupt:
                    print("\nUse 'exit' para salir del CLI")
                    continue
                except EOFError:
                    print("\nSaliendo del CLI...")
                    self.running = False
                    break
                    
        except Exception as e:
            print(f"Error crítico en CLI: {e}")
        finally:
            self.running = False
    
    def execute_script(self, commands: List[str]) -> List[CommandResult]:
        """
        Ejecuta una lista de comandos (modo script)
        
        Args:
            commands: Lista de strings de comandos
            
        Returns:
            List[CommandResult]: Resultados de cada comando
        """
        results = []
        
        for cmd_line in commands:
            if not cmd_line.strip() or cmd_line.strip().startswith('#'):
                continue  # Saltar líneas vacías y comentarios
            
            try:
                command, args = self.parse_command(cmd_line)
                if command:
                    result = self.execute_command(command, args)
                    results.append(result)
                    
                    # Si hay error, detener ejecución del script
                    if not result.success:
                        print(f"Error en script: {result.message}")
                        break
                        
            except Exception as e:
                error_result = CommandResult(False, f"Error parseando comando '{cmd_line}': {str(e)}")
                results.append(error_result)
                break
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del CLI
        
        Returns:
            Dict: Estado actual del CLI
        """
        return {
            'current_mode': self.context.current_mode.value,
            'current_device': self.context.current_device.name if self.context.current_device else None,
            'current_interface': self.context.current_interface.name if self.context.current_interface else None,
            'command_history_count': len(self.history),
            'available_commands': self.get_available_commands(),
            'running': self.running
        } 