#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo de Routing - Simulador de Red
==================================

Script de demostración que muestra las funcionalidades de routing
implementadas en el simulador de red.

Este script incluye:
- Configuración de routers con tabla de rutas
- Comandos de routing (ip route, show ip route, etc.)
- Comandos de red (ping, traceroute)
- Demostración de procesamiento de paquetes con routing

Author: Network Simulator Project
Version: 1.0
Date: 2025
"""

import sys
import os
import time

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.Devices_Network.network import Network
from src.PacketCommunication.communication_manager import CommunicationManager
from src.CLI.cli_parser import CLIParser


def setup_network_with_routing():
    """Configura una red de ejemplo con routers y tabla de rutas"""
    print("🔧 Configurando red con routing...")
    
    # Crear red
    network = Network()
    
    # Crear routers
    router1 = network.addDevice("Router-1", "router")
    router2 = network.addDevice("Router-2", "router")
    
    # Crear otros dispositivos
    switch1 = network.addDevice("Switch-1", "switch")
    pc1 = network.addDevice("PC-1", "host")
    pc2 = network.addDevice("PC-2", "host")
    
    # Configurar interfaces del Router-1
    router1.addInterface("eth0", autoActivate=True)
    router1.addInterface("eth1", autoActivate=True)
    
    # Configurar interfaces del Router-2
    router2.addInterface("eth0", autoActivate=True)
    router2.addInterface("eth1", autoActivate=True)
    
    # Configurar interfaces de otros dispositivos
    switch1.addInterface("fa0/1", autoActivate=True)
    switch1.addInterface("fa0/2", autoActivate=True)
    pc1.addInterface("eth0", autoActivate=True)
    pc2.addInterface("eth0", autoActivate=True)
    
    # Activar todos los dispositivos
    router1.setStatus("online")
    router2.setStatus("online")
    switch1.setStatus("online")
    pc1.setStatus("online")
    pc2.setStatus("online")
    
    # Configurar conexiones
    network.connectDevices("Router-1", "eth0", "Switch-1", "fa0/1")
    network.connectDevices("Switch-1", "fa0/2", "PC-1", "eth0")
    network.connectDevices("Router-1", "eth1", "Router-2", "eth0")
    network.connectDevices("Router-2", "eth1", "PC-2", "eth0")
    
    # Configurar tabla de rutas del Router-1
    router1.add_route("192.168.1.0/24", "192.168.1.1", "eth0", 1, "connected")
    router1.add_route("10.0.0.0/24", "10.0.0.1", "eth1", 1, "connected")
    router1.add_route("172.16.0.0/16", "10.0.0.2", "eth1", 2, "static")
    router1.set_default_route("10.0.0.254", "eth1")
    
    # Configurar tabla de rutas del Router-2
    router2.add_route("10.0.0.0/24", "10.0.0.2", "eth0", 1, "connected")
    router2.add_route("172.16.1.0/24", "172.16.1.1", "eth1", 1, "connected")
    router2.add_route("192.168.1.0/24", "10.0.0.1", "eth0", 2, "static")
    router2.set_default_route("172.16.1.254", "eth1")
    
    print("✅ Red configurada exitosamente")
    return network


def demo_routing_commands(cli_parser):
    """Demuestra los comandos de routing"""
    print("\n" + "="*60)
    print("🚀 DEMOSTRACIÓN DE COMANDOS DE ROUTING")
    print("="*60)
    
    # Seleccionar Router-1
    cli_parser.set_current_device(cli_parser.network.getDevice("Router-1"))
    print(f"\n📍 Dispositivo seleccionado: {cli_parser.get_current_device().name}")
    
    # Comandos de demostración
    demo_commands = [
        "show routing",
        "show ip route",
        "show ip interface brief",
        "ping 172.16.1.100",
        "traceroute 172.16.1.100",
        "ip route 192.168.2.0/24 192.168.1.254 eth0 2 static",
        "show routing",
        "no ip route 192.168.2.0/24",
        "show routing"
    ]
    
    for command in demo_commands:
        print(f"\n🔹 Ejecutando: {command}")
        print("-" * 40)
        
        result = cli_parser.execute_command(command, command.split()[1:])
        
        if result.success:
            print(result.message)
        else:
            print(f"❌ Error: {result.message}")
        
        time.sleep(1)  # Pausa para mejor visualización


def demo_network_commands(cli_parser):
    """Demuestra los comandos de red"""
    print("\n" + "="*60)
    print("🌐 DEMOSTRACIÓN DE COMANDOS DE RED")
    print("="*60)
    
    # Seleccionar PC-1
    cli_parser.set_current_device(cli_parser.network.getDevice("PC-1"))
    print(f"\n📍 Dispositivo seleccionado: {cli_parser.get_current_device().name}")
    
    # Comandos de red
    network_commands = [
        "ping 172.16.1.100",
        "traceroute 172.16.1.100",
        "send 192.168.1.100 172.16.1.100 'Hola desde PC-1'",
        "tick"
    ]
    
    for command in network_commands:
        print(f"\n🔹 Ejecutando: {command}")
        print("-" * 40)
        
        result = cli_parser.execute_command(command, command.split()[1:])
        
        if result.success:
            print(result.message)
        else:
            print(f"❌ Error: {result.message}")
        
        time.sleep(1)


def demo_packet_processing(cli_parser):
    """Demuestra el procesamiento de paquetes con routing"""
    print("\n" + "="*60)
    print("📦 DEMOSTRACIÓN DE PROCESAMIENTO DE PAQUETES")
    print("="*60)
    
    # Seleccionar Router-1
    cli_parser.set_current_device(cli_parser.network.getDevice("Router-1"))
    print(f"\n📍 Dispositivo seleccionado: {cli_parser.get_current_device().name}")
    
    # Enviar paquetes y procesar
    processing_commands = [
        "send 192.168.1.100 172.16.1.100 'Paquete 1'",
        "send 192.168.1.101 172.16.1.101 'Paquete 2'",
        "send 192.168.1.102 172.16.1.102 'Paquete 3'",
        "process",
        "show queue",
        "tick"
    ]
    
    for command in processing_commands:
        print(f"\n🔹 Ejecutando: {command}")
        print("-" * 40)
        
        result = cli_parser.execute_command(command, command.split()[1:])
        
        if result.success:
            print(result.message)
        else:
            print(f"❌ Error: {result.message}")
        
        time.sleep(1)


def main():
    """Función principal de la demostración"""
    print("🚀 INICIANDO DEMOSTRACIÓN DE ROUTING")
    print("="*60)
    
    try:
        # Configurar red
        network = setup_network_with_routing()
        
        # Crear CommunicationManager
        comm_manager = CommunicationManager(network)
        
        # Crear CLI Parser
        cli_parser = CLIParser(network, comm_manager)
        
        # Mostrar información de la red
        print("\n📊 INFORMACIÓN DE LA RED:")
        print("-" * 40)
        devices = network.getAllDevices()
        for device in devices:
            print(f"  • {device.name} ({device.type}) - {device.status}")
            if device.type == "router" and device.routing_table:
                stats = device.routing_table.get_statistics()
                print(f"    └─ Tabla de rutas: {stats['total_routes']} rutas")
        
        # Ejecutar demostraciones
        demo_routing_commands(cli_parser)
        demo_network_commands(cli_parser)
        demo_packet_processing(cli_parser)
        
        print("\n" + "="*60)
        print("✅ DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\n📋 RESUMEN DE FUNCIONALIDADES DEMOSTRADAS:")
        print("  • Tabla de rutas en routers")
        print("  • Comandos de routing (ip route, show ip route)")
        print("  • Comandos de red (ping, traceroute)")
        print("  • Procesamiento de paquetes con routing")
        print("  • Gestión de interfaces IP")
        print("  • Simulación de comunicación entre redes")
        
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 