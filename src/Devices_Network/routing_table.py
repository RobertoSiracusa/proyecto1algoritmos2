from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RouteEntry:
    """Entrada en la tabla de rutas"""
    destination: str
    next_hop: str
    interface: str
    metric: int
    protocol: str
    timestamp: datetime
    is_active: bool = True


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
        self.routes: Dict[str, RouteEntry] = {}
        self.default_route: Optional[RouteEntry] = None
        self._route_counter = 0
    
    def add_route(self, destination: str, next_hop: str, interface: str, 
                  metric: int = 1, protocol: str = "static") -> bool:
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
            self.routes[destination] = route_entry
            self._route_counter += 1
            
            return True
            
        except Exception:
            return False
    
    def remove_route(self, destination: str) -> bool:
        """
        Elimina una ruta de la tabla.
        
        Args:
            destination: Red de destino a eliminar
            
        Returns:
            bool: True si la ruta fue eliminada exitosamente
        """
        if destination in self.routes:
            del self.routes[destination]
            return True
        return False
    
    def lookup_route(self, destination_ip: str) -> Optional[RouteEntry]:
        """
        Busca la mejor ruta para un destino IP.
        
        Args:
            destination_ip: IP de destino
            
        Returns:
            RouteEntry: Mejor ruta encontrada o None
        """
        # Buscar ruta exacta primero
        if destination_ip in self.routes:
            return self.routes[destination_ip]
        
        # Buscar ruta de red (subnet matching)
        best_route = None
        best_metric = float('inf')
        
        for dest, route in self.routes.items():
            if self._is_in_network(destination_ip, dest):
                if route.metric < best_metric and route.is_active:
                    best_route = route
                    best_metric = route.metric
        
        # Si no se encuentra ruta específica, usar ruta por defecto
        if not best_route and self.default_route:
            return self.default_route
        
        return best_route
    
    def set_default_route(self, next_hop: str, interface: str) -> bool:
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
    
    def get_routes_by_protocol(self, protocol: str) -> List[RouteEntry]:
        """
        Obtiene todas las rutas de un protocolo específico.
        
        Args:
            protocol: Protocolo de routing
            
        Returns:
            List[RouteEntry]: Lista de rutas del protocolo
        """
        return [route for route in self.routes.values() if route.protocol == protocol]
    
    def get_active_routes(self) -> List[RouteEntry]:
        """
        Obtiene todas las rutas activas.
        
        Returns:
            List[RouteEntry]: Lista de rutas activas
        """
        return [route for route in self.routes.values() if route.is_active]
    
    def clear_routes(self, protocol: Optional[str] = None) -> int:
        """
        Limpia rutas de la tabla.
        
        Args:
            protocol: Si se especifica, solo limpia rutas de ese protocolo
            
        Returns:
            int: Número de rutas eliminadas
        """
        if protocol:
            routes_to_remove = [dest for dest, route in self.routes.items() 
                              if route.protocol == protocol]
        else:
            routes_to_remove = list(self.routes.keys())
        
        for dest in routes_to_remove:
            del self.routes[dest]
        
        return len(routes_to_remove)
    
    def show_routing_table(self) -> str:
        """
        Genera una representación en texto de la tabla de rutas.
        
        Returns:
            str: Tabla de rutas formateada
        """
        if not self.routes and not self.default_route:
            return "Tabla de rutas vacía"
        
        output = []
        output.append("Códigos: C - conectado, S - estático, R - RIP, O - OSPF")
        output.append("")
        output.append("Red de Destino        Próximo Salto    Interfaz    Métrica  Protocolo")
        output.append("-" * 70)
        
        # Mostrar rutas normales
        for dest, route in sorted(self.routes.items()):
            if route.is_active:
                protocol_code = route.protocol[0].upper()
                output.append(f"{dest:<20} {route.next_hop:<16} {route.interface:<11} "
                            f"{route.metric:<8} {protocol_code}")
        
        # Mostrar ruta por defecto
        if self.default_route:
            output.append(f"{'0.0.0.0/0':<20} {self.default_route.next_hop:<16} "
                        f"{self.default_route.interface:<11} {self.default_route.metric:<8} S")
        
        return "\n".join(output)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la tabla de rutas.
        
        Returns:
            Dict[str, Any]: Estadísticas de la tabla
        """
        total_routes = len(self.routes)
        active_routes = len(self.get_active_routes())
        
        protocol_counts = {}
        for route in self.routes.values():
            protocol_counts[route.protocol] = protocol_counts.get(route.protocol, 0) + 1
        
        return {
            "total_routes": total_routes,
            "active_routes": active_routes,
            "protocol_counts": protocol_counts,
            "has_default_route": self.default_route is not None
        }
    
    def _is_in_network(self, ip: str, network: str) -> bool:
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
    
    def __len__(self) -> int:
        """Retorna el número de rutas en la tabla."""
        return len(self.routes)
    
    def __str__(self) -> str:
        """Representación en string de la tabla de rutas."""
        return self.show_routing_table() 