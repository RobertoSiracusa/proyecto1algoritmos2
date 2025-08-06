from enum import Enum


class CLIMode(Enum):
    """
    Enumeración de los diferentes modos CLI disponibles
    """
    USER = "user"                    # Device>
    PRIVILEGED = "privileged"        # Device#
    GLOBAL_CONFIG = "global_config"  # Device(config)#
    INTERFACE_CONFIG = "interface_config"  # Device(config-if)#
    
    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, mode_str: str):
        """Convierte string a CLIMode"""
        for mode in cls:
            if mode.value == mode_str.lower():
                return mode
        raise ValueError(f"Modo CLI inválido: {mode_str}")


class CLIModeManager:
    """
    Gestor de modos CLI que maneja transiciones y validaciones
    """
    
    # Definir transiciones válidas entre modos
    VALID_TRANSITIONS = {
        CLIMode.USER: [CLIMode.PRIVILEGED],
        CLIMode.PRIVILEGED: [CLIMode.USER, CLIMode.GLOBAL_CONFIG],
        CLIMode.GLOBAL_CONFIG: [CLIMode.PRIVILEGED, CLIMode.INTERFACE_CONFIG],
        CLIMode.INTERFACE_CONFIG: [CLIMode.GLOBAL_CONFIG, CLIMode.PRIVILEGED]
    }
    
    # Comandos disponibles por modo
    AVAILABLE_COMMANDS = {
        CLIMode.USER: [
            'show', 'help', 'enable', 'exit', 'select', 'current'
        ],
        CLIMode.PRIVILEGED: [
            'show', 'help', 'configure', 'send', 'tick', 'process', 
            'exit', 'disable', 'select', 'current'
        ],
        CLIMode.GLOBAL_CONFIG: [
            'hostname', 'interface', 'exit', 'end', 'help', 'select', 'current'
        ],
        CLIMode.INTERFACE_CONFIG: [
            'ip', 'shutdown', 'no', 'exit', 'end', 'help', 'select', 'current'
        ]
    }
    
    @classmethod
    def can_transition(cls, from_mode: CLIMode, to_mode: CLIMode) -> bool:
        """
        Verifica si es posible hacer transición entre modos
        
        Args:
            from_mode: Modo actual
            to_mode: Modo destino
            
        Returns:
            bool: True si la transición es válida
        """
        return to_mode in cls.VALID_TRANSITIONS.get(from_mode, [])
    
    @classmethod
    def get_available_commands(cls, mode: CLIMode) -> list:
        """
        Obtiene comandos disponibles para un modo específico
        
        Args:
            mode: Modo CLI
            
        Returns:
            list: Lista de comandos disponibles
        """
        return cls.AVAILABLE_COMMANDS.get(mode, [])
    
    @classmethod
    def get_prompt_symbol(cls, mode: CLIMode, device_name: str = "Device", 
                         interface_name: str = None) -> str:
        """
        Genera el símbolo de prompt apropiado para el modo
        
        Args:
            mode: Modo CLI actual
            device_name: Nombre del dispositivo
            interface_name: Nombre de la interfaz (para interface config mode)
            
        Returns:
            str: Prompt string apropiado
        """
        if mode == CLIMode.USER:
            return f"{device_name}>"
        elif mode == CLIMode.PRIVILEGED:
            return f"{device_name}#"
        elif mode == CLIMode.GLOBAL_CONFIG:
            return f"{device_name}(config)#"
        elif mode == CLIMode.INTERFACE_CONFIG:
            if interface_name:
                return f"{device_name}(config-if-{interface_name})#"
            else:
                return f"{device_name}(config-if)#"
        else:
            return f"{device_name}>"
    
    @classmethod
    def get_mode_description(cls, mode: CLIMode) -> str:
        """
        Obtiene descripción del modo CLI
        
        Args:
            mode: Modo CLI
            
        Returns:
            str: Descripción del modo
        """
        descriptions = {
            CLIMode.USER: "Modo Usuario - Comandos básicos de consulta",
            CLIMode.PRIVILEGED: "Modo Privilegiado - Acceso completo a comandos",
            CLIMode.GLOBAL_CONFIG: "Modo Configuración Global - Configuración del dispositivo",
            CLIMode.INTERFACE_CONFIG: "Modo Configuración de Interfaz - Configuración específica de interfaz"
        }
        return descriptions.get(mode, "Modo desconocido")
    
    @classmethod
    def get_help_for_mode(cls, mode: CLIMode) -> str:
        """
        Obtiene ayuda específica para un modo
        
        Args:
            mode: Modo CLI
            
        Returns:
            str: Texto de ayuda para el modo
        """
        help_texts = {
            CLIMode.USER: """
Comandos disponibles en Modo Usuario:
  show          - Mostrar información del sistema
  select        - Seleccionar dispositivo específico
  current       - Mostrar dispositivo actual
  help          - Mostrar esta ayuda
  enable        - Entrar al modo privilegiado
  exit          - Salir del CLI
            """,
            CLIMode.PRIVILEGED: """
Comandos disponibles en Modo Privilegiado:
  show          - Mostrar información del sistema
  select        - Seleccionar dispositivo específico
  current       - Mostrar dispositivo actual
  configure     - Entrar al modo de configuración
  send          - Enviar paquete de red
  tick          - Procesar un tick del simulador
  process       - Procesar colas de red
  help          - Mostrar esta ayuda
  disable       - Volver al modo usuario
  exit          - Salir del CLI
            """,
            CLIMode.GLOBAL_CONFIG: """
Comandos disponibles en Modo Configuración Global:
  hostname      - Configurar nombre del dispositivo
  interface     - Entrar a configuración de interfaz
  select        - Seleccionar dispositivo específico
  current       - Mostrar dispositivo actual
  help          - Mostrar esta ayuda
  exit          - Volver al modo anterior
  end           - Volver al modo privilegiado
            """,
            CLIMode.INTERFACE_CONFIG: """
Comandos disponibles en Modo Configuración de Interfaz:
  ip address    - Configurar dirección IP
  shutdown      - Apagar interfaz
  no shutdown   - Encender interfaz
  select        - Seleccionar dispositivo específico
  current       - Mostrar dispositivo actual
  help          - Mostrar esta ayuda
  exit          - Volver al modo anterior
  end           - Volver al modo privilegiado
            """
        }
        return help_texts.get(mode, "Ayuda no disponible para este modo")


class CLIModeContext:
    """
    Contexto que mantiene el estado actual del CLI
    """
    
    def __init__(self, initial_mode: CLIMode = CLIMode.USER):
        self.current_mode = initial_mode
        self.mode_stack = [initial_mode]  # Para manejar navegación entre modos
        self.current_device = None
        self.current_interface = None
        self.variables = {}  # Variables de sesión
        
    def change_mode(self, new_mode: CLIMode, push_to_stack: bool = True) -> bool:
        """
        Cambia el modo CLI actual
        
        Args:
            new_mode: Nuevo modo
            push_to_stack: Si agregar al stack de modos
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        if CLIModeManager.can_transition(self.current_mode, new_mode):
            if push_to_stack:
                self.mode_stack.append(new_mode)
            self.current_mode = new_mode
            return True
        return False
    
    def pop_mode(self) -> bool:
        """
        Regresa al modo anterior en el stack
        
        Returns:
            bool: True si se pudo regresar
        """
        if len(self.mode_stack) > 1:
            self.mode_stack.pop()
            self.current_mode = self.mode_stack[-1]
            return True
        return False
    
    def reset_to_privileged(self):
        """Resetea directamente al modo privilegiado"""
        self.current_mode = CLIMode.PRIVILEGED
        self.mode_stack = [CLIMode.PRIVILEGED]
        self.current_interface = None
    
    def get_prompt(self) -> str:
        """
        Obtiene el prompt actual
        
        Returns:
            str: String del prompt
        """
        device_name = self.current_device.name if self.current_device else "Device"
        interface_name = self.current_interface.name if self.current_interface else None
        
        return CLIModeManager.get_prompt_symbol(
            self.current_mode, 
            device_name, 
            interface_name
        ) 