from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import time
import threading

@dataclass
class RIPRoute:
    """Ruta aprendida por RIP"""
    destination: str
    next_hop: str
    interface: str
    metric: int
    source_router: str
    last_update: datetime
    timeout: datetime
    garbage_collection: datetime
    is_valid: bool = True
    
    def is_expired(self) -> bool:
        """Verifica si la ruta ha expirado"""
        return datetime.now() > self.timeout
    
    def is_garbage(self) -> bool:
        """Verifica si la ruta está en garbage collection"""
        return datetime.now() > self.garbage_collection
    
    def update_timers(self):
        """Actualiza los timers de la ruta"""
        now = datetime.now()
        self.last_update = now
        self.timeout = now + timedelta(seconds=180)  # 3 minutos
        self.garbage_collection = now + timedelta(seconds=240)  # 4 minutos

class RIPInterface:
    """Configuración de RIP para una interfaz"""
    
    def __init__(self, interface_name: str):
        self.interface_name = interface_name
        self.is_enabled = False
        self.send_version = 2
        self.receive_version = 2
        self.authentication = None
        self.passive = False
        self.split_horizon = True
        self.poison_reverse = False
    
    def enable(self, send_version: int = 2, receive_version: int = 2):
        """Habilita RIP en la interfaz"""
        self.is_enabled = True
        self.send_version = send_version
        self.receive_version = receive_version
    
    def disable(self):
        """Deshabilita RIP en la interfaz"""
        self.is_enabled = False

class RIPProtocol:
    """Implementación del protocolo RIP (Routing Information Protocol)"""
    
    def __init__(self, router_name: str):
        self.router_name = router_name
        self.is_enabled = False
        self.version = 2
        self.networks: List[str] = []
        self.interfaces: Dict[str, RIPInterface] = {}
        self.routes: Dict[str, RIPRoute] = {}
        self.neighbors: Dict[str, datetime] = {}
        self.update_interval = 30  # segundos
        self.invalid_timer = 180   # segundos
        self.holddown_timer = 180  # segundos
        self.flush_timer = 240     # segundos
        self._update_thread = None
        self._running = False
    
    def enable(self, version: int = 2):
        """Habilita el protocolo RIP"""
        self.is_enabled = True
        self.version = version
        self._start_update_thread()
    
    def disable(self):
        """Deshabilita el protocolo RIP"""
        self.is_enabled = False
        self._stop_update_thread()
    
    def add_network(self, network: str):
        """Agrega una red al protocolo RIP"""
        if network not in self.networks:
            self.networks.append(network)
    
    def remove_network(self, network: str):
        """Remueve una red del protocolo RIP"""
        if network in self.networks:
            self.networks.remove(network)
    
    def enable_interface(self, interface_name: str, send_version: int = 2, receive_version: int = 2):
        """Habilita RIP en una interfaz específica"""
        if interface_name not in self.interfaces:
            self.interfaces[interface_name] = RIPInterface(interface_name)
        
        self.interfaces[interface_name].enable(send_version, receive_version)
    
    def disable_interface(self, interface_name: str):
        """Deshabilita RIP en una interfaz específica"""
        if interface_name in self.interfaces:
            self.interfaces[interface_name].disable()
    
    def add_route(self, destination: str, next_hop: str, interface: str, metric: int, source_router: str):
        """Agrega o actualiza una ruta RIP"""
        now = datetime.now()
        
        if destination in self.routes:
            # Actualizar ruta existente
            route = self.routes[destination]
            if metric < route.metric or source_router == route.source_router:
                route.next_hop = next_hop
                route.interface = interface
                route.metric = metric
                route.source_router = source_router
                route.update_timers()
                route.is_valid = True
        else:
            # Crear nueva ruta
            route = RIPRoute(
                destination=destination,
                next_hop=next_hop,
                interface=interface,
                metric=metric,
                source_router=source_router,
                last_update=now,
                timeout=now + timedelta(seconds=self.invalid_timer),
                garbage_collection=now + timedelta(seconds=self.flush_timer)
            )
            self.routes[destination] = route
    
    def remove_route(self, destination: str):
        """Remueve una ruta RIP"""
        if destination in self.routes:
            del self.routes[destination]
    
    def get_routes(self) -> List[RIPRoute]:
        """Obtiene todas las rutas RIP válidas"""
        # Limpiar rutas expiradas
        self._cleanup_expired_routes()
        
        return [route for route in self.routes.values() if route.is_valid]
    
    def _cleanup_expired_routes(self):
        """Limpia rutas expiradas"""
        now = datetime.now()
        expired_routes = []
        
        for destination, route in self.routes.items():
            if route.is_garbage():
                expired_routes.append(destination)
            elif route.is_expired():
                route.is_valid = False
        
        # Eliminar rutas en garbage collection
        for destination in expired_routes:
            del self.routes[destination]
    
    def _start_update_thread(self):
        """Inicia el hilo de actualizaciones periódicas"""
        if self._update_thread is None or not self._update_thread.is_alive():
            self._running = True
            self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self._update_thread.start()
    
    def _stop_update_thread(self):
        """Detiene el hilo de actualizaciones"""
        self._running = False
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=1)
    
    def _update_loop(self):
        """Bucle principal de actualizaciones RIP"""
        while self._running and self.is_enabled:
            try:
                self._send_updates()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error en actualización RIP: {e}")
                time.sleep(5)
    
    def _send_updates(self):
        """Envía actualizaciones RIP a todas las interfaces habilitadas"""
        if not self.is_enabled:
            return
        
        # Simular envío de actualizaciones
        for interface_name, interface in self.interfaces.items():
            if interface.is_enabled:
                print(f"📡 RIP: Enviando actualizaciones desde {self.router_name} por {interface_name}")
                # En una implementación real, aquí se enviarían los paquetes RIP
    
    def receive_update(self, source_router: str, routes: List[Tuple[str, str, str, int]]):
        """Recibe una actualización RIP de otro router"""
        if not self.is_enabled:
            return
        
        print(f"📥 RIP: Recibiendo actualización de {source_router}")
        
        # Actualizar timestamp del vecino
        self.neighbors[source_router] = datetime.now()
        
        # Procesar rutas recibidas
        for destination, next_hop, interface, metric in routes:
            # Aplicar split horizon y poison reverse si está habilitado
            if self._should_advertise_route(destination, interface):
                # Incrementar métrica (RIP usa hop count)
                new_metric = min(metric + 1, 16)  # Máximo 16 hops
                
                if new_metric < 16:  # Evitar rutas inalcanzables
                    self.add_route(destination, next_hop, interface, new_metric, source_router)
    
    def _should_advertise_route(self, destination: str, interface: str) -> bool:
        """Determina si una ruta debe ser anunciada por una interfaz"""
        # Implementar split horizon y poison reverse
        for route in self.routes.values():
            if route.destination == destination and route.interface == interface:
                return False  # Split horizon: no anunciar ruta por la interfaz donde se aprendió
        return True
    
    def show_rip_database(self) -> str:
        """Muestra la base de datos RIP"""
        if not self.is_enabled:
            return "RIP no está habilitado"
        
        self._cleanup_expired_routes()
        
        output = [f"RIP Database - {self.router_name}"]
        output.append("-" * 80)
        output.append("Destination        Next Hop          Interface    Metric  Source    Status")
        output.append("-" * 80)
        
        for route in sorted(self.routes.values(), key=lambda x: x.destination):
            status = "VALID" if route.is_valid else "INVALID"
            output.append(f"{route.destination:16} {route.next_hop:16} {route.interface:12} "
                         f"{route.metric:6} {route.source_router:8} {status:6}")
        
        return "\n".join(output)
    
    def show_rip_interfaces(self) -> str:
        """Muestra la configuración de interfaces RIP"""
        if not self.interfaces:
            return "No hay interfaces configuradas para RIP"
        
        output = [f"RIP Interfaces - {self.router_name}"]
        output.append("-" * 60)
        output.append("Interface    Enabled  Send  Receive  Split Horizon")
        output.append("-" * 60)
        
        for interface_name, interface in sorted(self.interfaces.items()):
            enabled = "Yes" if interface.is_enabled else "No"
            split_horizon = "Yes" if interface.split_horizon else "No"
            output.append(f"{interface_name:12} {enabled:7} {interface.send_version:4} "
                         f"{interface.receive_version:7} {split_horizon:13}")
        
        return "\n".join(output)
    
    def show_rip_neighbors(self) -> str:
        """Muestra los vecinos RIP"""
        if not self.neighbors:
            return "No hay vecinos RIP conocidos"
        
        output = [f"RIP Neighbors - {self.router_name}"]
        output.append("-" * 50)
        output.append("Neighbor         Last Update")
        output.append("-" * 50)
        
        now = datetime.now()
        for neighbor, last_update in sorted(self.neighbors.items()):
            time_diff = now - last_update
            output.append(f"{neighbor:15} {time_diff.total_seconds():.0f}s ago")
        
        return "\n".join(output)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del protocolo RIP"""
        self._cleanup_expired_routes()
        
        valid_routes = len([r for r in self.routes.values() if r.is_valid])
        invalid_routes = len([r for r in self.routes.values() if not r.is_valid])
        
        return {
            "enabled": self.is_enabled,
            "version": self.version,
            "networks": len(self.networks),
            "interfaces": len([i for i in self.interfaces.values() if i.is_enabled]),
            "total_routes": len(self.routes),
            "valid_routes": valid_routes,
            "invalid_routes": invalid_routes,
            "neighbors": len(self.neighbors),
            "update_interval": self.update_interval
        } 