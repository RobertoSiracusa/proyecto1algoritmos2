import sys
import os
from datetime import datetime

# Agregar el directorio padre al path para importar DataEstructures
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DataEstructures import LinkedList


class RouteEntry:
    """Entrada en la tabla de rutas"""
    
    def __init__(self, destination, next_hop, interface, metric, protocol, timestamp, is_active=True):
        self.destination = destination
        self.next_hop = next_hop
        self.interface = interface
        self.metric = metric
        self.protocol = protocol
        self.timestamp = timestamp
        self.is_active = is_active


class RoutingTable:
    """
    Tabla de rutas para dispositivos de red.
    
    Implementa funcionalidades básicas de routing incluyendo:
    - Agregar/eliminar rutas
    - Búsqueda de rutas
    - Métricas y protocolos de routing
    - Rutas estáticas y dinámicas
    """
    
    def __init__(self):
        """Inicializa una tabla de rutas vacía."""
        self.routes = LinkedList()  # Lista de rutas (simulando diccionario)
        self.default_route = None
        self._route_counter = 0
    
    def _find_route_by_destination(self, destination):
        """Busca una ruta por destino en la lista enlazada"""
        current = self.routes.head
        while current is not None:
            if current.data.destination == destination:
                return current.data
            current = current.next
        return None
    
    def add_route(self, destination, next_hop, interface, metric=1, protocol="static"):
        """
        Agrega una ruta a la tabla.
        
        Args:
            destination: Red de destino (ej: "192.168.1.0/24")
            next_hop: Próximo salto (ej: "192.168.0.1")
            interface: Interfaz de salida
            metric: Métrica de la ruta (menor = mejor)
            protocol: Protocolo de routing (static, rip, ospf, etc.)
            
        Returns:
            bool: True si la ruta fue agregada exitosamente
        """
        try:
            # Validar parámetros
            if not destination or not next_hop or not interface:
                return False
            
            # Verificar si ya existe una ruta para este destino
            if self._find_route_by_destination(destination):
                return False
            
            # Crear entrada de ruta
            route_entry = RouteEntry(
                destination=destination,
                next_hop=next_hop,
                interface=interface,
                metric=metric,
                protocol=protocol,
                timestamp=datetime.now()
            )
            
            # Agregar a la tabla
            self.routes.add_node(route_entry)
            self._route_counter += 1
            
            return True
            
        except Exception:
            return False
    
    def remove_route(self, destination):
        """
        Elimina una ruta de la tabla.
        
        Args:
            destination: Red de destino a eliminar
            
        Returns:
            bool: True si la ruta fue eliminada exitosamente
        """
        route = self._find_route_by_destination(destination)
        if route:
            self.routes.remove_node(route)
            return True
        return False
    
    def lookup_route(self, destination_ip):
        """
        Busca la mejor ruta para un destino IP.
        
        Args:
            destination_ip: IP de destino
            
        Returns:
            RouteEntry: Mejor ruta encontrada o None
        """
        # Buscar ruta exacta primero
        route = self._find_route_by_destination(destination_ip)
        if route:
            return route
        
        # Buscar ruta de red (subnet matching)
        best_route = None
        best_metric = float('inf')
        
        current = self.routes.head
        while current is not None:
            route = current.data
            if self._is_in_network(destination_ip, route.destination):
                if route.metric < best_metric and route.is_active:
                    best_route = route
                    best_metric = route.metric
            current = current.next
        
        # Si no se encuentra ruta específica, usar ruta por defecto
        if not best_route and self.default_route:
            return self.default_route
        
        return best_route
    
    def set_default_route(self, next_hop, interface):
        """
        Establece la ruta por defecto.
        
        Args:
            next_hop: Próximo salto para la ruta por defecto
            interface: Interfaz de salida
            
        Returns:
            bool: True si se estableció exitosamente
        """
        try:
            self.default_route = RouteEntry(
                destination="0.0.0.0/0",
                next_hop=next_hop,
                interface=interface,
                metric=1,
                protocol="static",
                timestamp=datetime.now()
            )
            return True
        except Exception:
            return False
    
    def get_routes_by_protocol(self, protocol):
        """
        Obtiene todas las rutas de un protocolo específico.
        
        Args:
            protocol: Protocolo de routing
            
        Returns:
            Lista de rutas del protocolo
        """
        routes = []
        current = self.routes.head
        while current is not None:
            if current.data.protocol == protocol:
                routes.append(current.data)
            current = current.next
        return routes
    
    def get_active_routes(self):
        """
        Obtiene todas las rutas activas.
        
        Returns:
            Lista de rutas activas
        """
        routes = []
        current = self.routes.head
        while current is not None:
            if current.data.is_active:
                routes.append(current.data)
            current = current.next
        return routes
    
    def clear_routes(self, protocol=None):
        """
        Limpia rutas de la tabla.
        
        Args:
            protocol: Si se especifica, solo limpia rutas de ese protocolo
            
        Returns:
            int: Número de rutas eliminadas
        """
        routes_to_remove = []
        
        # Encontrar rutas a eliminar
        current = self.routes.head
        while current is not None:
            if protocol is None or current.data.protocol == protocol:
                routes_to_remove.append(current.data)
            current = current.next
        
        # Eliminar las rutas encontradas
        for route in routes_to_remove:
            self.routes.remove_node(route)
        
        return len(routes_to_remove)
    
    def show_routing_table(self):
        """
        Genera una representación en texto de la tabla de rutas.
        
        Returns:
            str: Tabla de rutas formateada
        """
        if self.routes.is_empty() and not self.default_route:
            return "Tabla de rutas vacía"
        
        output = []
        output.append("Códigos: C - conectado, S - estático, R - RIP, O - OSPF")
        output.append("")
        output.append("Red de Destino        Próximo Salto    Interfaz    Métrica  Protocolo")
        output.append("-" * 70)
        
        # Obtener todas las rutas y ordenarlas por destino
        routes_list = self.routes.traverse()
        routes_sorted = sorted(routes_list, key=lambda r: r.destination)
        
        # Mostrar rutas normales
        for route in routes_sorted:
            if route.is_active:
                protocol_code = route.protocol[0].upper()
                output.append(f"{route.destination:<20} {route.next_hop:<16} {route.interface:<11} "
                            f"{route.metric:<8} {protocol_code}")
        
        # Mostrar ruta por defecto
        if self.default_route:
            output.append(f"{'0.0.0.0/0':<20} {self.default_route.next_hop:<16} "
                        f"{self.default_route.interface:<11} {self.default_route.metric:<8} S")
        
        return "\n".join(output)
    
    def get_statistics(self):
        """
        Obtiene estadísticas de la tabla de rutas.
        
        Returns:
            Dict[str, Any]: Estadísticas de la tabla
        """
        total_routes = self.routes.get_size()
        active_routes = len(self.get_active_routes())
        
        protocol_counts = {}
        current = self.routes.head
        while current is not None:
            protocol = current.data.protocol
            protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
            current = current.next
        
        return {
            "total_routes": total_routes,
            "active_routes": active_routes,
            "protocol_counts": protocol_counts,
            "has_default_route": self.default_route is not None
        }
    
    def _is_in_network(self, ip, network):
        """
        Verifica si una IP está en una red específica.
        
        Args:
            ip: IP a verificar
            network: Red en formato CIDR
            
        Returns:
            bool: True si la IP está en la red
        """
        try:
            # Implementación simplificada para simulación
            # En una implementación real, usaría ipaddress module
            if "/" not in network:
                return ip == network
            
            network_addr, prefix = network.split("/")
            prefix = int(prefix)
            
            # Para simulación, comparación simple
            if prefix == 24:  # /24
                return ip.startswith(network_addr.rsplit(".", 1)[0] + ".")
            elif prefix == 16:  # /16
                return ip.startswith(network_addr.rsplit(".", 2)[0] + ".")
            elif prefix == 8:  # /8
                return ip.startswith(network_addr.rsplit(".", 3)[0] + ".")
            else:
                return ip == network_addr
                
        except Exception:
            return False
    
    def __len__(self):
        """Retorna el número de rutas en la tabla."""
        return self.routes.get_size()
    
    def __str__(self):
        """Representación en string de la tabla de rutas."""
        return self.show_routing_table() 