#!/usr/bin/env python3
"""
Demo Completo - Simulador de Red con Todas las Funcionalidades
============================================================

Este script demuestra todas las funcionalidades implementadas:
- Sistema de Firewall con ACLs
- Sistema de VLANs
- Protocolo RIP
- Routing avanzado
- Ping y Traceroute
- Configuración de dispositivos

Autor: Simulador de Red
Fecha: 2024
"""

import sys
import os
import time
import json

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.Devices_Network.network import Network
from src.PacketCommunication.communication_manager import CommunicationManager
from src.CLI.cli_parser import CLIParser

def print_banner():
    """Muestra el banner del demo"""
    print("=" * 80)
    print("🚀 DEMO COMPLETO - SIMULADOR DE RED CON TODAS LAS FUNCIONALIDADES")
    print("=" * 80)
    print("🔥 Firewall con ACLs | 🏷️ VLANs | 📡 RIP | 🛣️ Routing | 📊 Estadísticas")
    print("=" * 80)

def setup_network():
    """Configura la red de demo"""
    print("\n📋 Configurando red de demo...")
    
    # Crear red
    network = Network("Demo Completo")
    
    # Crear dispositivos
    router1 = network.addDevice("Router1", "router")
    router2 = network.addDevice("Router2", "router")
    switch1 = network.addDevice("Switch1", "switch")
    firewall1 = network.addDevice("Firewall1", "firewall")
    host1 = network.addDevice("Host1", "host")
    host2 = network.addDevice("Host2", "host")
    host3 = network.addDevice("Host3", "host")
    
    # Configurar interfaces
    router1.addInterface("eth0", "192.168.1.1", "255.255.255.0")
    router1.addInterface("eth1", "10.0.0.1", "255.255.255.0")
    
    router2.addInterface("eth0", "10.0.0.2", "255.255.255.0")
    router2.addInterface("eth1", "192.168.2.1", "255.255.255.0")
    
    switch1.addInterface("eth0")
    switch1.addInterface("eth1")
    switch1.addInterface("eth2")
    switch1.addInterface("eth3")
    
    firewall1.addInterface("eth0", "192.168.2.10", "255.255.255.0")
    firewall1.addInterface("eth1", "192.168.3.1", "255.255.255.0")
    
    host1.addInterface("eth0", "192.168.1.100", "255.255.255.0")
    host2.addInterface("eth0", "192.168.2.100", "255.255.255.0")
    host3.addInterface("eth0", "192.168.3.100", "255.255.255.0")
    
    # Conectar dispositivos
    network.connectDevices("Router1", "eth0", "Switch1", "eth3")
    network.connectDevices("Router1", "eth1", "Router2", "eth0")
    network.connectDevices("Router2", "eth1", "Firewall1", "eth0")
    network.connectDevices("Switch1", "eth0", "Host1", "eth0")
    network.connectDevices("Firewall1", "eth1", "Host3", "eth0")
    
    print("✅ Red configurada exitosamente")
    return network

def configure_firewall(firewall):
    """Configura el firewall con ACLs"""
    print("\n🔥 Configurando Firewall...")
    
    # Crear ACLs
    firewall.create_acl("INBOUND", "extended")
    firewall.create_acl("OUTBOUND", "extended")
    
    # Agregar reglas
    firewall.add_firewall_rule("INBOUND", "permit", "ip", "192.168.1.0", "any", 
                              "0.0.0.255", "0.0.0.0", "Permitir tráfico interno")
    firewall.add_firewall_rule("INBOUND", "deny", "tcp", "any", "192.168.3.0", 
                              "0.0.0.0", "0.0.0.255", "Bloquear acceso a red interna")
    
    firewall.add_firewall_rule("OUTBOUND", "permit", "ip", "192.168.3.0", "any", 
                              "0.0.0.255", "0.0.0.0", "Permitir salida a internet")
    
    # Activar ACLs
    firewall.activate_acl("INBOUND")
    firewall.activate_acl("OUTBOUND")
    
    print("✅ Firewall configurado")

def configure_vlans(switch):
    """Configura VLANs en el switch"""
    print("\n🏷️ Configurando VLANs...")
    
    # Crear VLANs
    switch.create_vlan(10, "ADMIN", "VLAN para administración")
    switch.create_vlan(20, "SALES", "VLAN para ventas")
    switch.create_vlan(30, "ENGINEERING", "VLAN para ingeniería")
    
    # Configurar interfaces
    switch.configure_interface_access("eth0", 10)
    switch.configure_interface_access("eth1", 20)
    switch.configure_interface_access("eth2", 30)
    switch.configure_interface_trunk("eth3", [10, 20, 30], 1)
    
    print("✅ VLANs configuradas")

def configure_routing(router1, router2):
    """Configura routing en los routers"""
    print("\n🛣️ Configurando Routing...")
    
    # Rutas estáticas
    router1.add_route("192.168.2.0", "10.0.0.2", "eth1", 1, "static")
    router1.set_default_route("10.0.0.2", "eth1")
    
    router2.add_route("192.168.1.0", "10.0.0.1", "eth0", 1, "static")
    router2.set_default_route("10.0.0.1", "eth0")
    
    # Habilitar RIP
    router1.enable_rip(2)
    router1.add_rip_network("192.168.1.0")
    router1.add_rip_network("10.0.0.0")
    router1.enable_rip_interface("eth0", 2, 2)
    router1.enable_rip_interface("eth1", 2, 2)
    
    router2.enable_rip(2)
    router2.add_rip_network("192.168.2.0")
    router2.add_rip_network("10.0.0.0")
    router2.enable_rip_interface("eth0", 2, 2)
    router2.enable_rip_interface("eth1", 2, 2)
    
    print("✅ Routing configurado")

def run_demo_commands(cli_parser):
    """Ejecuta comandos de demostración"""
    print("\n🎯 Ejecutando comandos de demostración...")
    
    commands = [
        # Comandos básicos
        "show devices",
        "show topology",
        
        # Comandos de firewall
        "connect Firewall1",
        "show access-list",
        "show security-log",
        
        # Comandos de VLAN
        "connect Switch1",
        "show vlan",
        "show vlan interfaces",
        "show vlan 10",
        
        # Comandos de routing
        "connect Router1",
        "show routing",
        "show ip route",
        "show rip database",
        "show rip interfaces",
        
        # Comandos de red
        "connect Host1",
        "ping 192.168.1.1",
        "connect Router1",
        "ping 192.168.2.100",
        "traceroute 192.168.3.100",
        
        # Comandos de estadísticas
        "show statistics",
        "show interfaces",
        "show queue"
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"\n[{i:2d}] Ejecutando: {command}")
        print("-" * 50)
        
        try:
            result = cli_parser.execute_script([command])
            if result:
                print(result[0].output)
            time.sleep(1)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)

def main():
    """Función principal del demo"""
    print_banner()
    
    try:
        # Configurar red
        network = setup_network()
        
        # Configurar funcionalidades avanzadas
        firewall1 = network.getDevice("Firewall1")
        switch1 = network.getDevice("Switch1")
        router1 = network.getDevice("Router1")
        router2 = network.getDevice("Router2")
        
        configure_firewall(firewall1)
        configure_vlans(switch1)
        configure_routing(router1, router2)
        
        # Crear CLI parser
        communication_manager = CommunicationManager(network)
        cli_parser = CLIParser(network, communication_manager)
        
        print("\n🎉 ¡Configuración completada! Iniciando demo...")
        time.sleep(2)
        
        # Ejecutar comandos de demo
        run_demo_commands(cli_parser)
        
        print("\n" + "=" * 80)
        print("🎊 ¡DEMO COMPLETADO EXITOSAMENTE!")
        print("=" * 80)
        print("✅ Todas las funcionalidades han sido demostradas:")
        print("   🔥 Firewall con ACLs y logging de seguridad")
        print("   🏷️ Sistema de VLANs con modos access y trunk")
        print("   📡 Protocolo RIP con base de datos y vecinos")
        print("   🛣️ Routing estático y dinámico")
        print("   📊 Ping, traceroute y estadísticas")
        print("   ⚙️ Configuración completa de dispositivos")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error en el demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 