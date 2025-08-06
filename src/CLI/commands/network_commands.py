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

class PingCommand(Command):
    """Comando para hacer ping a un destino"""
    
    def __init__(self):
        super().__init__(
            name="ping",
            description="Hace ping a un destino IP",
            syntax="ping <destination_ip> [count]"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not self.validate_args(args, min_args=1, max_args=2):
            return CommandResult(False, "Sintaxis: ping <destination_ip> [count]")
        
        destination_ip = args[0]
        count = int(args[1]) if len(args) > 1 else 4
        
        # Verificar que hay un dispositivo seleccionado
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Verificar que el dispositivo está online
        if not context.current_device.isOnline():
            return CommandResult(False, f"Dispositivo {context.current_device.name} está offline")
        
        # Simular ping usando el CommunicationManager
        comm_manager = getattr(context, 'communication_manager', None)
        if not comm_manager:
            return CommandResult(False, "No hay gestor de comunicaciones disponible")
        
        result = f"Ping a {destination_ip} desde {context.current_device.name} ({count} paquetes):\n"
        result += "-" * 60 + "\n"
        
        successful_pings = 0
        total_time = 0
        
        for i in range(count):
            try:
                # Simular envío de paquete ICMP
                import time
                start_time = time.time()
                
                # Crear paquete de ping
                packet = comm_manager.send(
                    source_ip=context.current_device.name,  # Usar nombre como IP temporal
                    destination_ip=destination_ip,
                    content=f"PING-{i+1}",
                    ttl=64
                )
                
                if packet:
                    # Simular procesamiento
                    time.sleep(0.1)  # Simular latencia
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convertir a ms
                    
                    result += f"Paquete {i+1}: Respuesta recibida en {response_time:.2f} ms\n"
                    successful_pings += 1
                    total_time += response_time
                else:
                    result += f"Paquete {i+1}: Timeout\n"
                    
            except Exception as e:
                result += f"Paquete {i+1}: Error - {str(e)}\n"
        
        # Estadísticas finales
        if successful_pings > 0:
            avg_time = total_time / successful_pings
            result += f"\nEstadísticas:\n"
            result += f"  Paquetes enviados: {count}\n"
            result += f"  Paquetes recibidos: {successful_pings}\n"
            result += f"  Tiempo promedio: {avg_time:.2f} ms\n"
            result += f"  Tasa de éxito: {(successful_pings/count)*100:.1f}%\n"
        else:
            result += f"\n❌ No se recibieron respuestas de {destination_ip}\n"
        
        return CommandResult(True, result)


class TracerouteCommand(Command):
    """Comando para hacer traceroute a un destino"""
    
    def __init__(self):
        super().__init__(
            name="traceroute",
            description="Hace traceroute a un destino IP",
            syntax="traceroute <destination_ip>"
        )
    
    def execute(self, args: List[str], context) -> CommandResult:
        if not self.validate_args(args, min_args=1, max_args=1):
            return CommandResult(False, "Sintaxis: traceroute <destination_ip>")
        
        destination_ip = args[0]
        
        # Verificar que hay un dispositivo seleccionado
        if not context.current_device:
            return CommandResult(False, "No hay dispositivo seleccionado")
        
        # Verificar que el dispositivo está online
        if not context.current_device.isOnline():
            return CommandResult(False, f"Dispositivo {context.current_device.name} está offline")
        
        result = f"Traceroute a {destination_ip} desde {context.current_device.name}:\n"
        result += "-" * 60 + "\n"
        
        # Simular traceroute con TTL incrementales
        max_hops = 15
        destination_reached = False
        
        for hop in range(1, max_hops + 1):
            try:
                # Simular envío con TTL específico
                import time
                start_time = time.time()
                
                # Crear paquete con TTL específico
                comm_manager = getattr(context, 'communication_manager', None)
                if comm_manager:
                    packet = comm_manager.send(
                        source_ip=context.current_device.name,
                        destination_ip=destination_ip,
                        content=f"TRACEROUTE-HOP-{hop}",
                        ttl=hop
                    )
                
                # Simular respuesta del hop
                time.sleep(0.05)  # Simular latencia
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                # Simular diferentes respuestas según el hop
                if hop == 1:
                    hop_name = "Router-1"
                    hop_ip = "192.168.1.1"
                elif hop == 2:
                    hop_name = "Switch-1"
                    hop_ip = "192.168.2.1"
                elif hop == 3:
                    hop_name = "Router-2"
                    hop_ip = "10.0.0.1"
                elif hop == 4:
                    hop_name = destination_ip
                    hop_ip = destination_ip
                    destination_reached = True
                else:
                    hop_name = f"Hop-{hop}"
                    hop_ip = f"192.168.{hop}.1"
                
                result += f"{hop:2}  {hop_name} ({hop_ip})  {response_time:.2f} ms\n"
                
                if destination_reached:
                    result += f"\n✅ Destino alcanzado en {hop} saltos\n"
                    break
                    
            except Exception as e:
                result += f"{hop:2}  * * *  Timeout\n"
        
        if not destination_reached:
            result += f"\n❌ No se pudo alcanzar el destino en {max_hops} saltos\n"
        
        return CommandResult(True, result)