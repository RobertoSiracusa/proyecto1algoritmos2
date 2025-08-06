import sys
import os
from datetime import datetime, timedelta
import time
import threading

# Agregar el directorio padre al path para importar DataEstructures
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DataEstructures import LinkedList


class RIPRoute:
    """Ruta aprendida por RIP"""
    
    def __init__(self, destination, next_hop, interface, metric, source_router, last_update, timeout, garbage_collection, is_valid=True):
        self.destination = destination
        self.next_hop = next_hop
        self.interface = interface
        self.metric = metric
        self.source_router = source_router
        self.last_update = last_update
        self.timeout = timeout
        self.garbage_collection = garbage_collection
        self.is_valid = is_valid
    
    def is_expired(self):
        """Verifica si la ruta ha expirado"""
        return datetime.now() > self.timeout
    
    def is_garbage(self):
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
    
    def __init__(self, interface_name):
        self.interface_name = interface_name
        self.is_enabled = False
        self.send_version = 2
        self.receive_version = 2
        self.authentication = None
        self.passive = False
        self.split_horizon = True
        self.poison_reverse = False
    
    def enable(self, send_version=2, receive_version=2):
        """Habilita RIP en la interfaz"""
        self.is_enabled = True
        self.send_version = send_version
        self.receive_version = receive_version
    
    def disable(self):
        """Deshabilita RIP en la interfaz"""
        self.is_enabled = False

class RIPProtocol:
    """Implementación del protocolo RIP (Routing Information Protocol)"""
    
    def __init__(self, router_name):
        self.router_name = router_name
        self.is_enabled = False
        self.version = 2
        self.networks = LinkedList()  # Lista de redes (simulando lista)
        self.interfaces = LinkedList()  # Lista de interfaces RIP (simulando diccionario)
        self.routes = LinkedList()  # Lista de rutas RIP (simulando diccionario)
        self.neighbors = LinkedList()  # Lista de vecinos (simulando diccionario)
        self.update_interval = 30  # segundos
        self.invalid_timer = 180   # segundos
        self.holddown_timer = 180  # segundos
        self.flush_timer = 240     # segundos
        self._update_thread = None
        self._running = False
    
    def _find_interface_by_name(self, interface_name):
        """Busca una interfaz RIP por nombre"""
        current = self.interfaces.head
        while current is not None:
            if current.data.interface_name == interface_name:
                return current.data
            current = current.next
        return None
    
    def _find_route_by_destination(self, destination):
        """Busca una ruta RIP por destino"""
        current = self.routes.head
        while current is not None:
            if current.data.destination == destination:
                return current.data
            current = current.next
        return None
    
    def _find_neighbor_by_name(self, neighbor_name):
        """Busca un vecino por nombre"""
        current = self.neighbors.head
        while current is not None:
            if current.data['name'] == neighbor_name:
                return current.data
            current = current.next
        return None
    
    def enable(self, version=2):
        """Habilita el protocolo RIP"""
        self.is_enabled = True
        self.version = version
        self._start_update_thread()
    
    def disable(self):
        """Deshabilita el protocolo RIP"""
        self.is_enabled = False
        self._stop_update_thread()
    
    def add_network(self, network):
        """Agrega una red al protocolo RIP"""
        if not self.networks.find(network):
            self.networks.add_node(network)
    
    def remove_network(self, network):
        """Remueve una red del protocolo RIP"""
        self.networks.remove_node(network)
    
    def enable_interface(self, interface_name, send_version=2, receive_version=2):
        """Habilita RIP en una interfaz específica"""
        interface = self._find_interface_by_name(interface_name)
        if not interface:
            new_interface = RIPInterface(interface_name)
            self.interfaces.add_node(new_interface)
            interface = new_interface
        
        interface.enable(send_version, receive_version)
    
    def disable_interface(self, interface_name):
        """Deshabilita RIP en una interfaz específica"""
        interface = self._find_interface_by_name(interface_name)
        if interface:
            interface.disable()
    
    def add_route(self, destination, next_hop, interface, metric, source_router):
        """Agrega o actualiza una ruta RIP"""
        now = datetime.now()
        
        existing_route = self._find_route_by_destination(destination)
        if existing_route:
            # Actualizar ruta existente
            if metric < existing_route.metric or source_router == existing_route.source_router:
                existing_route.next_hop = next_hop
                existing_route.interface = interface
                existing_route.metric = metric
                existing_route.source_router = source_router
                existing_route.update_timers()
                existing_route.is_valid = True
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
            self.routes.add_node(route)
    
    def remove_route(self, destination):
        """Remueve una ruta RIP"""
        route = self._find_route_by_destination(destination)
        if route:
            self.routes.remove_node(route)
    
    def get_routes(self):
        """Obtiene todas las rutas RIP válidas"""
        # Limpiar rutas expiradas
        self._cleanup_expired_routes()
        
        routes = []
        current = self.routes.head
        while current is not None:
            if current.data.is_valid:
                routes.append(current.data)
            current = current.next
        return routes
    
    def _cleanup_expired_routes(self):
        """Limpia rutas expiradas"""
        now = datetime.now()
        expired_routes = []
        
        current = self.routes.head
        while current is not None:
            route = current.data
            if route.is_garbage():
                expired_routes.append(route)
            elif route.is_expired():
                route.is_valid = False
            current = current.next
        
        # Eliminar rutas en garbage collection
        for route in expired_routes:
            self.routes.remove_node(route)
    
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
        current = self.interfaces.head
        while current is not None:
            interface = current.data
            if interface.is_enabled:
                print(f"📡 RIP: Enviando actualizaciones desde {self.router_name} por {interface.interface_name}")
                # En una implementación real, aquí se enviarían los paquetes RIP
            current = current.next
    
    def receive_update(self, source_router, routes):
        """Recibe una actualización RIP de otro router"""
        if not self.is_enabled:
            return
        
        print(f"📥 RIP: Recibiendo actualización de {source_router}")
        
        # Actualizar timestamp del vecino
        neighbor_data = {'name': source_router, 'last_update': datetime.now()}
        existing_neighbor = self._find_neighbor_by_name(source_router)
        if existing_neighbor:
            existing_neighbor['last_update'] = datetime.now()
        else:
            self.neighbors.add_node(neighbor_data)
        
        # Procesar rutas recibidas
        for destination, next_hop, interface, metric in routes:
            # Aplicar split horizon y poison reverse si está habilitado
            if self._should_advertise_route(destination, interface):
                # Incrementar métrica (RIP usa hop count)
                new_metric = min(metric + 1, 16)  # Máximo 16 hops
                
                if new_metric < 16:  # Evitar rutas inalcanzables
                    self.add_route(destination, next_hop, interface, new_metric, source_router)
    
    def _should_advertise_route(self, destination, interface):
        """Determina si una ruta debe ser anunciada por una interfaz"""
        # Implementar split horizon y poison reverse
        current = self.routes.head
        while current is not None:
            route = current.data
            if route.destination == destination and route.interface == interface:
                return False  # Split horizon: no anunciar ruta por la interfaz donde se aprendió
            current = current.next
        return True
    
    def show_rip_database(self):
        """Muestra la base de datos RIP"""
        if not self.is_enabled:
            return "RIP no está habilitado"
        
        self._cleanup_expired_routes()
        
        output = [f"RIP Database - {self.router_name}"]
        output.append("-" * 80)
        output.append("Destination        Next Hop          Interface    Metric  Source    Status")
        output.append("-" * 80)
        
        routes_list = self.routes.traverse()
        routes_sorted = sorted(routes_list, key=lambda x: x.destination)
        
        for route in routes_sorted:
            status = "VALID" if route.is_valid else "INVALID"
            output.append(f"{route.destination:16} {route.next_hop:16} {route.interface:12} "
                         f"{route.metric:6} {route.source_router:8} {status:6}")
        
        return "\n".join(output)
    
    def show_rip_interfaces(self):
        """Muestra la configuración de interfaces RIP"""
        if self.interfaces.is_empty():
            return "No hay interfaces configuradas para RIP"
        
        output = [f"RIP Interfaces - {self.router_name}"]
        output.append("-" * 60)
        output.append("Interface    Enabled  Send  Receive  Split Horizon")
        output.append("-" * 60)
        
        interfaces_list = self.interfaces.traverse()
        interfaces_sorted = sorted(interfaces_list, key=lambda x: x.interface_name)
        
        for interface in interfaces_sorted:
            enabled = "Yes" if interface.is_enabled else "No"
            split_horizon = "Yes" if interface.split_horizon else "No"
            output.append(f"{interface.interface_name:12} {enabled:7} {interface.send_version:4} "
                         f"{interface.receive_version:7} {split_horizon:13}")
        
        return "\n".join(output)
    
    def show_rip_neighbors(self):
        """Muestra los vecinos RIP"""
        if self.neighbors.is_empty():
            return "No hay vecinos RIP conocidos"
        
        output = [f"RIP Neighbors - {self.router_name}"]
        output.append("-" * 50)
        output.append("Neighbor         Last Update")
        output.append("-" * 50)
        
        now = datetime.now()
        neighbors_list = self.neighbors.traverse()
        neighbors_sorted = sorted(neighbors_list, key=lambda x: x['name'])
        
        for neighbor_data in neighbors_sorted:
            time_diff = now - neighbor_data['last_update']
            output.append(f"{neighbor_data['name']:15} {time_diff.total_seconds():.0f}s ago")
        
        return "\n".join(output)
    
    def get_statistics(self):
        """Obtiene estadísticas del protocolo RIP"""
        self._cleanup_expired_routes()
        
        valid_routes = 0
        invalid_routes = 0
        current = self.routes.head
        while current is not None:
            if current.data.is_valid:
                valid_routes += 1
            else:
                invalid_routes += 1
            current = current.next
        
        enabled_interfaces = 0
        current = self.interfaces.head
        while current is not None:
            if current.data.is_enabled:
                enabled_interfaces += 1
            current = current.next
        
        return {
            "enabled": self.is_enabled,
            "version": self.version,
            "networks": self.networks.get_size(),
            "interfaces": enabled_interfaces,
            "total_routes": self.routes.get_size(),
            "valid_routes": valid_routes,
            "invalid_routes": invalid_routes,
            "neighbors": self.neighbors.get_size(),
            "update_interval": self.update_interval
        } 