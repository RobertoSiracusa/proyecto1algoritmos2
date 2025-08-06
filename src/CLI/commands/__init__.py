"""
Módulo de comandos específicos del CLI
====================================

Contiene todas las implementaciones concretas de comandos CLI.
Cada comando implementa el patrón Command y puede ser usado
por el CLIParser.
"""

from .basic_commands import (
    HelpCommand,
    ExitCommand, 
    EnableCommand,
    DisableCommand
)

from .navigation_commands import (
    ConfigureTerminalCommand,
    InterfaceCommand,
    EndCommand
)

from .show_commands import (
    ShowCommand,
    ShowHistoryCommand,
    ShowInterfacesCommand,
    ShowQueueCommand,
    ShowStatisticsCommand,
    ShowDevicesCommand,
    ShowTopologyCommand,
    ShowConfigsCommand,
    ConfigInfoCommand,
    ShowIpRouteCommand,
    ShowIpInterfaceBriefCommand
)

from .network_commands import (
    SendPacketCommand,
    TickCommand,
    ProcessCommand,
    PingCommand,
    TracerouteCommand
)

from .config_commands import (
    HostnameCommand,
    IpAddressCommand,
    ShutdownCommand,
    NoShutdownCommand,
    SaveRunningConfigCommand,
    LoadConfigCommand
)

from .routing_commands import (
    AddRouteCommand,
    RemoveRouteCommand,
    DefaultRouteCommand,
    ClearRoutesCommand,
    ShowRoutingTableCommand
)

__all__ = [
    # Basic commands
    'HelpCommand',
    'ExitCommand',
    'EnableCommand', 
    'DisableCommand',
    
    # Navigation commands
    'ConfigureTerminalCommand',
    'InterfaceCommand',
    'EndCommand',
    
    # Show commands
    'ShowCommand',
    'ShowHistoryCommand',
    'ShowInterfacesCommand', 
    'ShowQueueCommand',
    'ShowStatisticsCommand',
    'ShowDevicesCommand',
    'ShowTopologyCommand',
    'ShowConfigsCommand',
    'ConfigInfoCommand',
    'ShowIpRouteCommand',
    'ShowIpInterfaceBriefCommand',
    
    # Network commands
    'SendPacketCommand',
    'TickCommand',
    'ProcessCommand',
    'PingCommand',
    'TracerouteCommand',
    
    # Configuration commands
    'HostnameCommand',
    'IpAddressCommand',
    'ShutdownCommand',
    'NoShutdownCommand',
    'SaveRunningConfigCommand',
    'LoadConfigCommand',
    
    # Routing commands
    'AddRouteCommand',
    'RemoveRouteCommand',
    'DefaultRouteCommand',
    'ClearRoutesCommand',
    'ShowRoutingTableCommand'
] 