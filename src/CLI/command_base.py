from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import sys
import os

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CommandResult:
    """
    Resultado de la ejecución de un comando
    """
    
    def __init__(self, success: bool, message: str = "", data: Any = None):
        self.success = success
        self.message = message
        self.data = data
        
    def __str__(self):
        return self.message
    
    def __bool__(self):
        return self.success


class Command(ABC):
    """
    Clase abstracta base para implementar el patrón Command.
    Todos los comandos CLI deben heredar de esta clase.
    """
    
    def __init__(self, name: str, description: str, syntax: str = ""):
        """
        Inicializa el comando base
        
        Args:
            name: Nombre del comando
            description: Descripción del comando
            syntax: Sintaxis del comando
        """
        self.name = name
        self.description = description
        self.syntax = syntax
        self.aliases = []  # Lista de alias para el comando
        
    @abstractmethod
    def execute(self, args: List[str], context: 'CLIModeContext') -> CommandResult:
        """
        Ejecuta el comando con los argumentos dados
        
        Args:
            args: Lista de argumentos del comando
            context: Contexto actual del CLI
            
        Returns:
            CommandResult: Resultado de la ejecución
        """
        pass
    
    def validate_args(self, args: List[str], min_args: int = 0, max_args: int = None) -> bool:
        """
        Valida el número de argumentos
        
        Args:
            args: Lista de argumentos
            min_args: Número mínimo de argumentos
            max_args: Número máximo de argumentos (None = ilimitado)
            
        Returns:
            bool: True si la validación es exitosa
        """
        if len(args) < min_args:
            return False
        if max_args is not None and len(args) > max_args:
            return False
        return True
    
    def get_help(self) -> str:
        """
        Obtiene texto de ayuda para el comando
        
        Returns:
            str: Texto de ayuda
        """
        help_text = f"Comando: {self.name}\n"
        help_text += f"Descripción: {self.description}\n"
        if self.syntax:
            help_text += f"Sintaxis: {self.syntax}\n"
        if self.aliases:
            help_text += f"Alias: {', '.join(self.aliases)}\n"
        return help_text
    
    def add_alias(self, alias: str):
        """Agrega un alias al comando"""
        if alias not in self.aliases:
            self.aliases.append(alias)
    
    def matches(self, command_name: str) -> bool:
        """
        Verifica si el comando coincide con el nombre o algún alias
        
        Args:
            command_name: Nombre del comando a verificar
            
        Returns:
            bool: True si coincide
        """
        return (command_name.lower() == self.name.lower() or 
                command_name.lower() in [alias.lower() for alias in self.aliases])


class CompositeCommand(Command):
    """
    Comando compuesto que puede contener subcomandos
    """
    
    def __init__(self, name: str, description: str, syntax: str = ""):
        super().__init__(name, description, syntax)
        self.subcommands: Dict[str, Command] = {}
        
    def add_subcommand(self, subcommand: Command):
        """Agrega un subcomando"""
        self.subcommands[subcommand.name.lower()] = subcommand
        
    def get_subcommand(self, name: str) -> Optional[Command]:
        """Obtiene un subcomando por nombre"""
        return self.subcommands.get(name.lower())
        
    def execute(self, args: List[str], context: 'CLIModeContext') -> CommandResult:
        """
        Ejecuta el comando o subcomando apropiado
        """
        if not args:
            return CommandResult(False, f"Subcomando requerido para '{self.name}'. Use 'help {self.name}' para ver opciones.")
        
        subcommand_name = args[0]
        subcommand = self.get_subcommand(subcommand_name)
        
        if subcommand:
            return subcommand.execute(args[1:], context)
        else:
            available = ', '.join(self.subcommands.keys())
            return CommandResult(False, f"Subcomando '{subcommand_name}' no reconocido. Disponibles: {available}")
    
    def get_help(self) -> str:
        """Obtiene ayuda incluyendo subcomandos"""
        help_text = super().get_help()
        if self.subcommands:
            help_text += "\nSubcomandos disponibles:\n"
            for name, cmd in self.subcommands.items():
                help_text += f"  {name:15} - {cmd.description}\n"
        return help_text


class CommandRegistry:
    """
    Registro de comandos disponibles
    """
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        
    def register(self, command: Command):
        """
        Registra un comando
        
        Args:
            command: Comando a registrar
        """
        self.commands[command.name.lower()] = command
        
        # Registrar también los alias
        for alias in command.aliases:
            self.commands[alias.lower()] = command
            
    def get_command(self, name: str) -> Optional[Command]:
        """
        Obtiene un comando por nombre
        
        Args:
            name: Nombre del comando
            
        Returns:
            Command: Comando encontrado o None
        """
        return self.commands.get(name.lower())
        
    def get_all_commands(self) -> Dict[str, Command]:
        """Obtiene todos los comandos registrados"""
        # Retornar solo los comandos principales (no alias)
        main_commands = {}
        for name, cmd in self.commands.items():
            if name == cmd.name.lower():
                main_commands[name] = cmd
        return main_commands
        
    def get_commands_for_mode(self, mode: 'CLIMode') -> Dict[str, Command]:
        """
        Obtiene comandos disponibles para un modo específico
        
        Args:
            mode: Modo CLI
            
        Returns:
            Dict[str, Command]: Comandos disponibles
        """
        from .cli_modes import CLIModeManager
        available_command_names = CLIModeManager.get_available_commands(mode)
        
        available_commands = {}
        for cmd_name in available_command_names:
            command = self.get_command(cmd_name)
            if command:
                available_commands[cmd_name] = command
                
        return available_commands 