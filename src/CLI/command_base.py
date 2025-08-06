from abc import ABC, abstractmethod
import sys
import os

# Agregar el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataEstructures import LinkedList


class CommandResult:
    """
    Resultado de la ejecución de un comando
    """
    
    def __init__(self, success, message="", data=None):
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
    
    def __init__(self, name, description, syntax=""):
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
        self.aliases = LinkedList()  # Lista de alias usando LinkedList
        
    @abstractmethod
    def execute(self, args, context):
        """
        Ejecuta el comando con los argumentos dados
        
        Args:
            args: Lista de argumentos del comando
            context: Contexto actual del CLI
            
        Returns:
            CommandResult: Resultado de la ejecución
        """
        pass
    
    def validate_args(self, args, min_args=0, max_args=None):
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
    
    def get_help(self):
        """
        Obtiene texto de ayuda para el comando
        
        Returns:
            str: Texto de ayuda
        """
        help_text = f"Comando: {self.name}\n"
        help_text += f"Descripción: {self.description}\n"
        if self.syntax:
            help_text += f"Sintaxis: {self.syntax}\n"
        if not self.aliases.is_empty():
            # Convertir LinkedList a lista para join
            alias_list = []
            current = self.aliases.head
            while current is not None:
                alias_list.append(current.data)
                current = current.next
            help_text += f"Alias: {', '.join(alias_list)}\n"
        return help_text
    
    def add_alias(self, alias):
        """Agrega un alias al comando"""
        # Verificar si el alias ya existe
        current = self.aliases.head
        while current is not None:
            if current.data == alias:
                return  # Ya existe
            current = current.next
        self.aliases.add_node(alias)
    
    def matches(self, command_name):
        """
        Verifica si el comando coincide con el nombre o algún alias
        
        Args:
            command_name: Nombre del comando a verificar
            
        Returns:
            bool: True si coincide
        """
        if command_name.lower() == self.name.lower():
            return True
        
        # Verificar en aliases
        current = self.aliases.head
        while current is not None:
            if command_name.lower() == current.data.lower():
                return True
            current = current.next
        return False


class CompositeCommand(Command):
    """
    Comando compuesto que puede contener subcomandos
    """
    
    def __init__(self, name, description, syntax=""):
        super().__init__(name, description, syntax)
        self.subcommands = LinkedList()  # Lista de subcomandos usando LinkedList
        
    def _find_subcommand_by_name(self, name):
        """Busca un subcomando por nombre"""
        current = self.subcommands.head
        while current is not None:
            if current.data.name.lower() == name.lower():
                return current.data
            current = current.next
        return None
        
    def add_subcommand(self, subcommand):
        """Agrega un subcomando"""
        self.subcommands.add_node(subcommand)
        
    def get_subcommand(self, name):
        """Obtiene un subcomando por nombre"""
        return self._find_subcommand_by_name(name)
        
    def execute(self, args, context):
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
            # Obtener nombres de subcomandos disponibles
            available_names = []
            current = self.subcommands.head
            while current is not None:
                available_names.append(current.data.name)
                current = current.next
            available = ', '.join(available_names)
            return CommandResult(False, f"Subcomando '{subcommand_name}' no reconocido. Disponibles: {available}")
    
    def get_help(self):
        """Obtiene ayuda incluyendo subcomandos"""
        help_text = super().get_help()
        if not self.subcommands.is_empty():
            help_text += "\nSubcomandos disponibles:\n"
            current = self.subcommands.head
            while current is not None:
                cmd = current.data
                help_text += f"  {cmd.name:15} - {cmd.description}\n"
                current = current.next
        return help_text


class CommandRegistry:
    """
    Registro de comandos disponibles
    """
    
    def __init__(self):
        self.commands = LinkedList()  # Lista de comandos usando LinkedList
        
    def _find_command_by_name(self, name):
        """Busca un comando por nombre"""
        current = self.commands.head
        while current is not None:
            if current.data.name.lower() == name.lower():
                return current.data
            current = current.next
        return None
        
    def register(self, command):
        """
        Registra un comando
        
        Args:
            command: Comando a registrar
        """
        self.commands.add_node(command)
        
        # Registrar también los alias
        current = command.aliases.head
        while current is not None:
            # Crear una entrada adicional para el alias
            self.commands.add_node(command)
            current = current.next
            
    def get_command(self, name):
        """
        Obtiene un comando por nombre
        
        Args:
            name: Nombre del comando
            
        Returns:
            Command: Comando encontrado o None
        """
        return self._find_command_by_name(name)
        
    def get_all_commands(self):
        """Obtiene todos los comandos registrados"""
        # Retornar solo los comandos principales (no alias)
        main_commands = {}
        current = self.commands.head
        while current is not None:
            cmd = current.data
            if cmd.name.lower() not in main_commands:
                main_commands[cmd.name.lower()] = cmd
            current = current.next
        return main_commands
        
    def get_commands_for_mode(self, mode):
        """
        Obtiene comandos disponibles para un modo específico
        
        Args:
            mode: Modo CLI
            
        Returns:
            Dict: Comandos disponibles
        """
        from .cli_modes import CLIModeManager
        available_command_names = CLIModeManager.get_available_commands(mode)
        
        available_commands = {}
        for cmd_name in available_command_names:
            command = self.get_command(cmd_name)
            if command:
                available_commands[cmd_name] = command
                
        return available_commands 