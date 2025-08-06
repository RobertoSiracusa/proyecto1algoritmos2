"""
Módulo CLI (Command Line Interface) - Módulo 4
==============================================

Implementa una interfaz de línea de comandos completa para el simulador de red.
Incluye manejo de múltiples modos CLI y patrón Command para extensibilidad.

Componentes:
- CLIParser: Gestor principal de la interfaz CLI
- Command Pattern: Implementación del patrón Command para comandos
- CLI Modes: Diferentes modos de operación (User, Privileged, Config, Interface)
- Commands: Comandos específicos para cada funcionalidad
"""

from .cli_parser import CLIParser
from .command_base import Command
from .cli_modes import CLIMode
from .commands import *

__all__ = [
    'CLIParser', 
    'Command', 
    'CLIMode',
    'EnableCommand',
    'ConfigureTerminalCommand', 
    'SendPacketCommand',
    'ShowHistoryCommand',
    'ShowInterfacesCommand',
    'ShowQueueCommand',
    'TickCommand',
    'ExitCommand',
    'EndCommand',
    'InterfaceCommand',
    'HostnameCommand',
    'IpAddressCommand',
    'ShutdownCommand',
    'NoShutdownCommand'
] 