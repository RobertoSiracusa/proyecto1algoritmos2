from typing import List
from ..command_base import Command, CommandResult


class SendPacketCommand(Command):
    """Comando para enviar paquetes de red"""
    
    def __init__(self):
        super().__init__(
            name="send",
            description="Envía un paquete de red",
            syntax="send <source_ip> <destination_ip> <content> [ttl]"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not self.validate_args(args, min_args=3, max_args=4):
            return CommandResult(False, "Sintaxis: send <source_ip> <destination_ip> <content> [ttl]")
        
        source_ip = args[0]
        destination_ip = args[1]
        content = args[2]
        ttl = int(args[3]) if len(args) > 3 else 64
        
        # Necesitamos acceso al CommunicationManager
        # Por ahora, este comando requiere que el contexto tenga referencia al network y comm_manager
        comm_manager = getattr(context, 'communication_manager', None)
        if not comm_manager:
            return CommandResult(False, "No hay gestor de comunicaciones disponible")
        
        try:
            packet = comm_manager.send(source_ip, destination_ip, content, ttl)
            if packet:
                return CommandResult(True, f"Paquete {packet.id} enviado exitosamente")
            else:
                return CommandResult(False, "Error al enviar paquete")
        except Exception as e:
            return CommandResult(False, f"Error al enviar paquete: {str(e)}")


class TickCommand(Command):
    """Comando para procesar un tick del simulador"""
    
    def __init__(self):
        super().__init__(
            name="tick",
            description="Procesa un tick del simulador de red",
            syntax="tick"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        comm_manager = getattr(context, 'communication_manager', None)
        if not comm_manager:
            return CommandResult(False, "No hay gestor de comunicaciones disponible")
        
        try:
            # Capturar la salida del tick
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            stats = comm_manager.tick()
            
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            
            # Agregar resumen de estadísticas
            summary = f"""
Tick procesado exitosamente:
- Paquetes procesados: {stats['packetsProcessed']}
- Paquetes entregados: {stats['packetsDelivered']}
- Paquetes reenviados: {stats['packetsForwarded']}
- Paquetes descartados: {stats['packetsDropped']}
"""
            
            return CommandResult(True, output + summary)
            
        except Exception as e:
            return CommandResult(False, f"Error al procesar tick: {str(e)}")


class ProcessCommand(Command):
    """Comando para procesar colas de red"""
    
    def __init__(self):
        super().__init__(
            name="process",
            description="Procesa las colas de red del dispositivo actual",
            syntax="process"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        try:
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Procesar colas del dispositivo
            processed_packets = context.current_device.processOutgoingQueue()
            
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            
            result_text = f"Procesadas {len(processed_packets)} paquetes de las colas del dispositivo {context.current_device.name}"
            
            if output:
                result_text = output + "\n" + result_text
            
            return CommandResult(True, result_text)
            
        except Exception as e:
            return CommandResult(False, f"Error al procesar colas: {str(e)}") 