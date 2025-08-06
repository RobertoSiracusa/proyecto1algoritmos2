#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Datos por Defecto
===========================

Proporciona configuraciones y datos predefinidos para pruebas, demostraciones
y inicialización rápida del simulador de red. Incluye redes de ejemplo,
dispositivos preconfigurados y escenarios de prueba estándar.

Este módulo facilita la creación rápida de entornos de prueba y permite
a los usuarios explorar las funcionalidades del simulador sin necesidad
de configuración manual extensa.

Author: Network Simulator Project  
Version: 1.0
"""

import sys
import os

# Agregar path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Devices_Network.network import Network
from Devices_Network.device import Device
from Devices_Network.interface import Interface


class DefaultNetworkTemplates:
    """
    Plantillas de redes predefinidas para diferentes escenarios de uso.
    Cada plantilla representa una topología de red típica con configuraciones
    realistas y funcionales.
    """
    
    @staticmethod
    def create_simple_home_network():
        """
        Crea una red doméstica simple con router, switch y algunos dispositivos.
        
        Topología:
        Internet --- Router --- Switch --- [PC1, PC2, Printer]
        
        Returns:
            Network: Red doméstica configurada
        """
        # Crear la red
        network = Network("Red Doméstica Simple")
        
        # === CREAR DISPOSITIVOS ===
        
        # Router principal (gateway)
        router = Device("Home-Router", "router")
        router.setStatus("online")
        
        # Switch de acceso
        switch = Device("Home-Switch", "switch")
        switch.setStatus("online")
        
        # Dispositivos finales
        pc1 = Device("PC-Sala", "host")
        pc1.setStatus("online")
        
        pc2 = Device("PC-Dormitorio", "host")
        pc2.setStatus("online")
        
        printer = Device("Printer-HP", "host")
        printer.setStatus("online")
        
        # Agregar dispositivos a la red
        for device in [router, switch, pc1, pc2, printer]:
            network.addDevice(device)
        
        # === CONFIGURAR INTERFACES ===
        
        # Router - Interfaz WAN
        wan_iface = router.addInterface("wan0")
        wan_iface.assignIpAddress("192.168.0.1")
        wan_iface.setMacAddress("00:1A:2B:3C:4D:01")
        wan_iface.setStatus("up")
        
        # Router - Interfaz LAN
        lan_iface = router.addInterface("lan0")
        lan_iface.assignIpAddress("192.168.1.1")
        lan_iface.setMacAddress("00:1A:2B:3C:4D:02")
        lan_iface.setStatus("up")
        
        # Switch - Puerto uplink
        sw_uplink = switch.addInterface("gi0/1")
        sw_uplink.setStatus("up")
        
        # Switch - Puertos de acceso
        sw_port1 = switch.addInterface("fa0/1")
        sw_port1.setStatus("up")
        
        sw_port2 = switch.addInterface("fa0/2")
        sw_port2.setStatus("up")
        
        sw_port3 = switch.addInterface("fa0/3")
        sw_port3.setStatus("up")
        
        # Dispositivos finales - Interfaces ethernet
        pc1_eth = pc1.addInterface("eth0")
        pc1_eth.assignIpAddress("192.168.1.10")
        pc1_eth.setMacAddress("AA:BB:CC:DD:EE:01")
        pc1_eth.setStatus("up")
        
        pc2_eth = pc2.addInterface("eth0")
        pc2_eth.assignIpAddress("192.168.1.20")
        pc2_eth.setMacAddress("AA:BB:CC:DD:EE:02")
        pc2_eth.setStatus("up")
        
        printer_eth = printer.addInterface("eth0")
        printer_eth.assignIpAddress("192.168.1.100")
        printer_eth.setMacAddress("AA:BB:CC:DD:EE:03")
        printer_eth.setStatus("up")
        
        # === ESTABLECER CONEXIONES ===
        
        connections = [
            ("Home-Router", "lan0", "Home-Switch", "gi0/1"),
            ("Home-Switch", "fa0/1", "PC-Sala", "eth0"),
            ("Home-Switch", "fa0/2", "PC-Dormitorio", "eth0"),
            ("Home-Switch", "fa0/3", "Printer-HP", "eth0")
        ]
        
        for dev1, iface1, dev2, iface2 in connections:
            network.establishConnection(dev1, iface1, dev2, iface2)
        
        # === CONFIGURAR ESTADÍSTICAS INICIALES ===
        network.total_packets_sent = 45
        network.delivered_packets = 42
        network.dropped_packets_ttl = 1
        network.total_hops = 128
        network.device_activity = {
            "Home-Router": 15,
            "Home-Switch": 12,
            "PC-Sala": 8,
            "PC-Dormitorio": 6,
            "Printer-HP": 4
        }
        
        return network
    
    @staticmethod
    def create_small_office_network():
        """
        Crea una red de oficina pequeña con múltiples segmentos.
        
        Topología:
        Internet --- Firewall --- Core-Switch --- [Access-Switch1, Access-Switch2]
                                     |
                                  Server
        
        Returns:
            Network: Red de oficina configurada
        """
        # Crear la red
        network = Network("Red Oficina Pequeña")
        
        # === CREAR DISPOSITIVOS ===
        
        # Dispositivos de infraestructura
        firewall = Device("Office-Firewall", "firewall")
        firewall.setStatus("online")
        
        core_switch = Device("Core-Switch", "switch")
        core_switch.setStatus("online")
        
        access_sw1 = Device("Access-Switch-Piso1", "switch")
        access_sw1.setStatus("online")
        
        access_sw2 = Device("Access-Switch-Piso2", "switch")
        access_sw2.setStatus("online")
        
        # Servidor
        file_server = Device("File-Server", "host")
        file_server.setStatus("online")
        
        web_server = Device("Web-Server", "host")
        web_server.setStatus("online")
        
        # Estaciones de trabajo
        admin_pc = Device("Admin-Workstation", "host")
        admin_pc.setStatus("online")
        
        dev_pc = Device("Dev-Workstation", "host")
        dev_pc.setStatus("online")
        
        sales_pc = Device("Sales-PC", "host")
        sales_pc.setStatus("online")
        
        # Agregar todos los dispositivos
        devices = [firewall, core_switch, access_sw1, access_sw2, 
                  file_server, web_server, admin_pc, dev_pc, sales_pc]
        
        for device in devices:
            network.addDevice(device)
        
        # === CONFIGURAR INTERFACES ===
        
        # Firewall
        fw_outside = firewall.addInterface("outside")
        fw_outside.assignIpAddress("203.0.113.1")
        fw_outside.setMacAddress("00:50:56:12:34:01")
        fw_outside.setStatus("up")
        
        fw_inside = firewall.addInterface("inside")
        fw_inside.assignIpAddress("10.0.0.1")
        fw_inside.setMacAddress("00:50:56:12:34:02")
        fw_inside.setStatus("up")
        
        fw_dmz = firewall.addInterface("dmz")
        fw_dmz.assignIpAddress("172.16.1.1")
        fw_dmz.setMacAddress("00:50:56:12:34:03")
        fw_dmz.setStatus("up")
        
        # Core Switch
        core_fw = core_switch.addInterface("gi0/1")
        core_fw.setStatus("up")
        
        core_srv = core_switch.addInterface("gi0/2")
        core_srv.setStatus("up")
        
        core_acc1 = core_switch.addInterface("gi0/3")
        core_acc1.setStatus("up")
        
        core_acc2 = core_switch.addInterface("gi0/4")
        core_acc2.setStatus("up")
        
        core_dmz = core_switch.addInterface("gi0/5")
        core_dmz.setStatus("up")
        
        # Access Switches
        acc1_uplink = access_sw1.addInterface("gi0/1")
        acc1_uplink.setStatus("up")
        
        acc1_admin = access_sw1.addInterface("fa0/1")
        acc1_admin.setStatus("up")
        
        acc1_dev = access_sw1.addInterface("fa0/2")
        acc1_dev.setStatus("up")
        
        acc2_uplink = access_sw2.addInterface("gi0/1")
        acc2_uplink.setStatus("up")
        
        acc2_sales = access_sw2.addInterface("fa0/1")
        acc2_sales.setStatus("up")
        
        # Servidores
        file_srv_eth = file_server.addInterface("eth0")
        file_srv_eth.assignIpAddress("10.0.1.10")
        file_srv_eth.setMacAddress("00:15:5D:FF:FF:01")
        file_srv_eth.setStatus("up")
        
        web_srv_eth = web_server.addInterface("eth0")
        web_srv_eth.assignIpAddress("172.16.1.10")
        web_srv_eth.setMacAddress("00:15:5D:FF:FF:02")
        web_srv_eth.setStatus("up")
        
        # Estaciones de trabajo
        admin_eth = admin_pc.addInterface("eth0")
        admin_eth.assignIpAddress("10.0.2.10")
        admin_eth.setMacAddress("00:15:5D:AA:BB:01")
        admin_eth.setStatus("up")
        
        dev_eth = dev_pc.addInterface("eth0")
        dev_eth.assignIpAddress("10.0.2.20")
        dev_eth.setMacAddress("00:15:5D:AA:BB:02")
        dev_eth.setStatus("up")
        
        sales_eth = sales_pc.addInterface("eth0")
        sales_eth.assignIpAddress("10.0.3.10")
        sales_eth.setMacAddress("00:15:5D:AA:BB:03")
        sales_eth.setStatus("up")
        
        # === ESTABLECER CONEXIONES ===
        
        connections = [
            # Firewall al core
            ("Office-Firewall", "inside", "Core-Switch", "gi0/1"),
            ("Office-Firewall", "dmz", "Core-Switch", "gi0/5"),
            
            # Core a access switches
            ("Core-Switch", "gi0/3", "Access-Switch-Piso1", "gi0/1"),
            ("Core-Switch", "gi0/4", "Access-Switch-Piso2", "gi0/1"),
            
            # Servidores
            ("Core-Switch", "gi0/2", "File-Server", "eth0"),
            ("Web-Server", "eth0", "Core-Switch", "gi0/5"),  # En DMZ
            
            # Estaciones de trabajo
            ("Access-Switch-Piso1", "fa0/1", "Admin-Workstation", "eth0"),
            ("Access-Switch-Piso1", "fa0/2", "Dev-Workstation", "eth0"),
            ("Access-Switch-Piso2", "fa0/1", "Sales-PC", "eth0")
        ]
        
        for dev1, iface1, dev2, iface2 in connections:
            network.establishConnection(dev1, iface1, dev2, iface2)
        
        # === ESTADÍSTICAS INICIALES ===
        network.total_packets_sent = 234
        network.delivered_packets = 218
        network.dropped_packets_ttl = 8
        network.blocked_by_firewall = 12
        network.total_hops = 892
        network.device_activity = {
            "Office-Firewall": 45,
            "Core-Switch": 38,
            "File-Server": 32,
            "Web-Server": 28,
            "Access-Switch-Piso1": 25,
            "Access-Switch-Piso2": 15,
            "Admin-Workstation": 18,
            "Dev-Workstation": 22,
            "Sales-PC": 11
        }
        
        return network
    
    @staticmethod
    def create_data_center_network():
        """
        Crea una red de centro de datos con redundancia y múltiples servicios.
        
        Topología más compleja con múltiples routers, switches y servidores.
        
        Returns:
            Network: Red de centro de datos configurada
        """
        # Crear la red
        network = Network("Centro de Datos Corporativo")
        
        # === DISPOSITIVOS DE CORE ===
        
        # Routers de borde
        border_router1 = Device("Border-Router-1", "router")
        border_router1.setStatus("online")
        
        border_router2 = Device("Border-Router-2", "router")
        border_router2.setStatus("online")
        
        # Switches de core con redundancia
        core_switch1 = Device("Core-Switch-1", "switch")
        core_switch1.setStatus("online")
        
        core_switch2 = Device("Core-Switch-2", "switch")
        core_switch2.setStatus("online")
        
        # Switches de distribución
        dist_switch1 = Device("Distribution-Switch-1", "switch")
        dist_switch1.setStatus("online")
        
        dist_switch2 = Device("Distribution-Switch-2", "switch")
        dist_switch2.setStatus("online")
        
        # Switches de acceso para diferentes racks
        access_switch_web = Device("Access-Switch-Web", "switch")
        access_switch_web.setStatus("online")
        
        access_switch_db = Device("Access-Switch-Database", "switch")
        access_switch_db.setStatus("online")
        
        access_switch_storage = Device("Access-Switch-Storage", "switch")
        access_switch_storage.setStatus("online")
        
        # === SERVIDORES ===
        
        # Servidores Web (cluster)
        web_server1 = Device("Web-Server-1", "host")
        web_server1.setStatus("online")
        
        web_server2 = Device("Web-Server-2", "host")
        web_server2.setStatus("online")
        
        load_balancer = Device("Load-Balancer", "host")
        load_balancer.setStatus("online")
        
        # Servidores de Base de Datos
        db_primary = Device("DB-Server-Primary", "host")
        db_primary.setStatus("online")
        
        db_secondary = Device("DB-Server-Secondary", "host")
        db_secondary.setStatus("online")
        
        # Almacenamiento
        storage_server1 = Device("Storage-Server-1", "host")
        storage_server1.setStatus("online")
        
        storage_server2 = Device("Storage-Server-2", "host")
        storage_server2.setStatus("online")
        
        # Servicios de infraestructura
        dns_server = Device("DNS-Server", "host")
        dns_server.setStatus("online")
        
        monitoring_server = Device("Monitoring-Server", "host")
        monitoring_server.setStatus("online")
        
        backup_server = Device("Backup-Server", "host")
        backup_server.setStatus("online")
        
        # Agregar todos los dispositivos
        all_devices = [
            border_router1, border_router2, core_switch1, core_switch2,
            dist_switch1, dist_switch2, access_switch_web, access_switch_db,
            access_switch_storage, web_server1, web_server2, load_balancer,
            db_primary, db_secondary, storage_server1, storage_server2,
            dns_server, monitoring_server, backup_server
        ]
        
        for device in all_devices:
            network.addDevice(device)
        
        # === CONFIGURAR INTERFACES (Selección representativa) ===
        
        # Border Routers
        br1_wan = border_router1.addInterface("wan0")
        br1_wan.assignIpAddress("203.0.113.1")
        br1_wan.setStatus("up")
        
        br1_lan = border_router1.addInterface("lan0")
        br1_lan.assignIpAddress("10.0.0.1")
        br1_lan.setStatus("up")
        
        br2_wan = border_router2.addInterface("wan0")
        br2_wan.assignIpAddress("203.0.113.2")
        br2_wan.setStatus("up")
        
        br2_lan = border_router2.addInterface("lan0")
        br2_lan.assignIpAddress("10.0.0.2")
        br2_lan.setStatus("up")
        
        # Core Switches - Uplinks
        cs1_br1 = core_switch1.addInterface("gi0/1")
        cs1_br1.setStatus("up")
        
        cs1_br2 = core_switch1.addInterface("gi0/2")
        cs1_br2.setStatus("up")
        
        cs2_br1 = core_switch2.addInterface("gi0/1")
        cs2_br1.setStatus("up")
        
        cs2_br2 = core_switch2.addInterface("gi0/2")
        cs2_br2.setStatus("up")
        
        # Distribution uplinks
        cs1_dist1 = core_switch1.addInterface("gi0/3")
        cs1_dist1.setStatus("up")
        
        cs1_dist2 = core_switch1.addInterface("gi0/4")
        cs1_dist2.setStatus("up")
        
        # Servidores representativos
        web1_eth = web_server1.addInterface("eth0")
        web1_eth.assignIpAddress("10.1.1.10")
        web1_eth.setMacAddress("00:50:56:AA:BB:01")
        web1_eth.setStatus("up")
        
        db_pri_eth = db_primary.addInterface("eth0")
        db_pri_eth.assignIpAddress("10.2.1.10")
        db_pri_eth.setMacAddress("00:50:56:CC:DD:01")
        db_pri_eth.setStatus("up")
        
        # === CONEXIONES PRINCIPALES ===
        
        # Solo establecer algunas conexiones representativas debido a la complejidad
        key_connections = [
            ("Border-Router-1", "lan0", "Core-Switch-1", "gi0/1"),
            ("Border-Router-2", "lan0", "Core-Switch-2", "gi0/1"),
            ("Core-Switch-1", "gi0/3", "Distribution-Switch-1", "gi0/1"),
            ("Web-Server-1", "eth0", "Access-Switch-Web", "fa0/1"),
            ("DB-Server-Primary", "eth0", "Access-Switch-Database", "fa0/1")
        ]
        
        for dev1, iface1, dev2, iface2 in key_connections:
            # Verificar que las interfaces existen antes de conectar
            device1 = network.getDevice(dev1)
            device2 = network.getDevice(dev2)
            
            if (device1 and device2 and 
                device1.getInterface(iface1) and device2.getInterface(iface2)):
                network.establishConnection(dev1, iface1, dev2, iface2)
        
        # === ESTADÍSTICAS DE CENTRO DE DATOS ===
        network.total_packets_sent = 15847
        network.delivered_packets = 14502
        network.dropped_packets_ttl = 89
        network.blocked_by_firewall = 156
        network.total_hops = 47234
        network.device_activity = {
            "Border-Router-1": 1205,
            "Border-Router-2": 1034,
            "Core-Switch-1": 1456,
            "Core-Switch-2": 1289,
            "Web-Server-1": 856,
            "Web-Server-2": 734,
            "Load-Balancer": 1523,
            "DB-Server-Primary": 945,
            "DB-Server-Secondary": 567,
            "DNS-Server": 234,
            "Monitoring-Server": 445,
            "Backup-Server": 189
        }
        
        return network


class DefaultDeviceConfigurations:
    """
    Configuraciones predefinidas para diferentes tipos de dispositivos.
    """
    
    # === CONFIGURACIONES DE ROUTER ===
    
    @staticmethod
    def get_home_router_config():
        """Configuración típica de router doméstico."""
        return {
            "name": "Home-Router",
            "type": "router",
            "status": "online",
            "interfaces": [
                {
                    "name": "wan0",
                    "ip": "192.168.0.1",
                    "mac": "00:1A:2B:3C:4D:01",
                    "status": "up"
                },
                {
                    "name": "lan0", 
                    "ip": "192.168.1.1",
                    "mac": "00:1A:2B:3C:4D:02",
                    "status": "up"
                }
            ]
        }
    
    @staticmethod
    def get_enterprise_router_config():
        """Configuración típica de router empresarial."""
        return {
            "name": "Enterprise-Router",
            "type": "router", 
            "status": "online",
            "interfaces": [
                {
                    "name": "wan0",
                    "ip": "203.0.113.1",
                    "mac": "00:50:56:12:34:01",
                    "status": "up"
                },
                {
                    "name": "lan0",
                    "ip": "10.0.0.1", 
                    "mac": "00:50:56:12:34:02",
                    "status": "up"
                },
                {
                    "name": "dmz0",
                    "ip": "172.16.1.1",
                    "mac": "00:50:56:12:34:03", 
                    "status": "up"
                }
            ]
        }
    
    # === CONFIGURACIONES DE SWITCH ===
    
    @staticmethod
    def get_access_switch_config():
        """Configuración típica de switch de acceso."""
        return {
            "name": "Access-Switch",
            "type": "switch",
            "status": "online", 
            "interfaces": [
                {
                    "name": "gi0/1",
                    "ip": "",
                    "mac": "",
                    "status": "up"
                },
                {
                    "name": "fa0/1",
                    "ip": "",
                    "mac": "",
                    "status": "up"
                },
                {
                    "name": "fa0/2", 
                    "ip": "",
                    "mac": "",
                    "status": "up"
                }
            ]
        }
    
    # === CONFIGURACIONES DE HOST ===
    
    @staticmethod
    def get_workstation_config():
        """Configuración típica de estación de trabajo."""
        return {
            "name": "Workstation",
            "type": "host",
            "status": "online",
            "interfaces": [
                {
                    "name": "eth0",
                    "ip": "192.168.1.100",
                    "mac": "AA:BB:CC:DD:EE:01",
                    "status": "up"
                }
            ]
        }
    
    @staticmethod
    def get_server_config():
        """Configuración típica de servidor."""
        return {
            "name": "File-Server",
            "type": "host", 
            "status": "online",
            "interfaces": [
                {
                    "name": "eth0",
                    "ip": "10.0.1.10",
                    "mac": "00:15:5D:FF:FF:01",
                    "status": "up"
                },
                {
                    "name": "eth1",
                    "ip": "10.0.1.11", 
                    "mac": "00:15:5D:FF:FF:02",
                    "status": "up"
                }
            ]
        }


class DefaultTestData:
    """
    Datos de prueba predefinidos para validación y testing.
    """
    
    # === IP ADDRESSES DE PRUEBA ===
    
    VALID_IPS = [
        "192.168.1.1",
        "10.0.0.1", 
        "172.16.1.1",
        "203.0.113.1",
        "8.8.8.8",
        "127.0.0.1"
    ]
    
    INVALID_IPS = [
        "256.1.1.1",
        "192.168.1",
        "192.168.1.1.1",
        "abc.def.ghi.jkl",
        "",
        "192.168.01.1"
    ]
    
    # === MAC ADDRESSES DE PRUEBA ===
    
    VALID_MACS = [
        "00:1A:2B:3C:4D:5E",
        "AA:BB:CC:DD:EE:FF", 
        "00:50:56:12:34:56",
        "00:15:5D:FF:FF:01"
    ]
    
    INVALID_MACS = [
        "00:1A:2B:3C:4D",
        "00:1A:2B:3C:4D:5E:6F",
        "GG:HH:II:JJ:KK:LL",
        "00-1A-2B-3C-4D-5E",
        ""
    ]
    
    # === NOMBRES DE DISPOSITIVOS DE PRUEBA ===
    
    VALID_DEVICE_NAMES = [
        "Router-1",
        "Core-Switch",
        "Access_Switch_Floor1", 
        "Web-Server",
        "DB_Primary",
        "Firewall01"
    ]
    
    INVALID_DEVICE_NAMES = [
        "",
        "1Router",  # Empieza con número
        "-Router",  # Empieza con guión
        "Router@Home",  # Caracteres no válidos
        "A" * 51,  # Muy largo
        "Router Space"  # Espacios
    ]
    
    # === CONTENIDO DE PAQUETES DE PRUEBA ===
    
    SAMPLE_PACKET_CONTENTS = [
        "Ping request from 192.168.1.10",
        "HTTP GET /index.html",
        "SSH connection established",
        "File transfer: document.pdf",
        "Database query: SELECT * FROM users",
        "Email notification sent",
        "System heartbeat signal",
        "DNS query for example.com"
    ]
    
    # === CONFIGURACIONES DE PRUEBA COMPLEJAS ===
    
    @staticmethod
    def get_test_packet_scenarios():
        """Escenarios de prueba para paquetes."""
        return [
            {
                "name": "Ping básico",
                "source_ip": "192.168.1.10",
                "dest_ip": "192.168.1.1", 
                "content": "ICMP Echo Request",
                "ttl": 64
            },
            {
                "name": "Transferencia HTTP",
                "source_ip": "10.0.1.100",
                "dest_ip": "172.16.1.10",
                "content": "HTTP GET /api/data",
                "ttl": 32
            },
            {
                "name": "Consulta DNS",
                "source_ip": "192.168.1.50",
                "dest_ip": "8.8.8.8",
                "content": "DNS query: www.example.com",
                "ttl": 128
            },
            {
                "name": "TTL bajo",
                "source_ip": "10.0.0.1",
                "dest_ip": "203.0.113.50",
                "content": "Test packet low TTL",
                "ttl": 2
            }
        ]
    
    @staticmethod
    def get_test_network_statistics():
        """Estadísticas de red de prueba."""
        return {
            "total_packets_sent": 1250,
            "delivered_packets": 1180,
            "dropped_packets_ttl": 25,
            "blocked_by_firewall": 15,
            "total_hops": 3840,
            "device_activity": {
                "Router-1": 245,
                "Core-Switch": 189,
                "Access-Switch": 156,
                "Web-Server": 134,
                "DB-Server": 98,
                "Workstation-1": 67,
                "Workstation-2": 54
            }
        }


# === FUNCIONES DE CONVENIENCIA ===

def load_default_network(template_name="simple_home"):
    """
    Carga una red predefinida por nombre de plantilla.
    
    Args:
        template_name: Nombre de la plantilla a cargar
                      ("simple_home", "small_office", "data_center")
    
    Returns:
        Network: Red configurada según la plantilla
        
    Raises:
        ValueError: Si el nombre de plantilla no es válido
    """
    templates = {
        "simple_home": DefaultNetworkTemplates.create_simple_home_network,
        "small_office": DefaultNetworkTemplates.create_small_office_network,
        "data_center": DefaultNetworkTemplates.create_data_center_network
    }
    
    if template_name not in templates:
        raise ValueError(f"Plantilla '{template_name}' no válida. Disponibles: {list(templates.keys())}")
    
    return templates[template_name]()


def get_quick_test_network():
    """
    Retorna una red simple y rápida para pruebas básicas.
    
    Returns:
        Network: Red mínima funcional para testing
    """
    network = Network("Test Network")
    
    # Crear dispositivos mínimos
    router = Device("Test-Router", "router")
    router.setStatus("online")
    
    host = Device("Test-Host", "host")
    host.setStatus("online")
    
    network.addDevice(router)
    network.addDevice(host)
    
    # Configurar interfaces básicas
    router_iface = router.addInterface("eth0")
    router_iface.assignIpAddress("192.168.1.1")
    router_iface.setStatus("up")
    
    host_iface = host.addInterface("eth0")
    host_iface.assignIpAddress("192.168.1.10")
    host_iface.setStatus("up")
    
    # Conectar
    network.establishConnection("Test-Router", "eth0", "Test-Host", "eth0")
    
    return network


def populate_test_statistics(network):
    """
    Llena una red con estadísticas de prueba realistas.
    
    Args:
        network: Red a llenar con estadísticas
    """
    test_stats = DefaultTestData.get_test_network_statistics()
    
    network.total_packets_sent = test_stats["total_packets_sent"]
    network.delivered_packets = test_stats["delivered_packets"] 
    network.dropped_packets_ttl = test_stats["dropped_packets_ttl"]
    network.blocked_by_firewall = test_stats["blocked_by_firewall"]
    network.total_hops = test_stats["total_hops"]
    
    # Asignar actividad solo a dispositivos que existen
    for device_name in network.getAllDeviceNames():
        if device_name in test_stats["device_activity"]:
            network.device_activity[device_name] = test_stats["device_activity"][device_name]
        else:
            # Asignar actividad aleatoria baja para dispositivos no listados
            network.device_activity[device_name] = 15


if __name__ == "__main__":
    """Demostración rápida de datos por defecto."""
    print("🏗️  Demostración de Datos por Defecto")
    print("="*50)
    
    # Crear red simple
    print("\n1. Red Doméstica Simple:")
    home_net = load_default_network("simple_home")
    print(f"   Dispositivos: {len(home_net.devices)}")
    print(f"   Conexiones: {len(home_net.connections)}")
    
    # Crear red de oficina
    print("\n2. Red de Oficina:")
    office_net = load_default_network("small_office")
    print(f"   Dispositivos: {len(office_net.devices)}")
    print(f"   Conexiones: {len(office_net.connections)}")
    
    # Red de prueba rápida
    print("\n3. Red de Prueba Rápida:")
    test_net = get_quick_test_network()
    print(f"   Dispositivos: {len(test_net.devices)}")
    print(f"   Conexiones: {len(test_net.connections)}")
    
    print("\n✅ Datos por defecto listos para usar") 