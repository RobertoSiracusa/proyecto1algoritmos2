#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulador de Red - Punto de Entrada Principal
============================================

Este es el archivo principal del Simulador de Red desarrollado como proyecto
de Algoritmos y Estructuras de Datos 2. Proporciona una interfaz de línea
de comandos completa para crear, configurar y gestionar redes simuladas.

Funcionalidades principales:
- Creación y gestión de dispositivos de red (routers, switches, hosts, firewalls)
- Simulación de comunicación de paquetes
- Interfaz CLI profesional con múltiples modos
- Persistencia de configuraciones
- Estadísticas y reportes de red
- Datos de prueba predefinidos

Uso:
    python main.py [opciones]

Opciones:
    --interactive, -i    : Modo CLI interactivo (por defecto)
    --demo              : Ejecutar demostración rápida
    --load <archivo>    : Cargar configuración desde archivo
    --help, -h          : Mostrar esta ayuda

Author: Network Simulator Project
Version: 1.0
Date: 2025
"""

import sys
import os
import argparse

# Agregar el directorio src al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importaciones principales del proyecto
try:
    from Devices_Network.network import Network
    from Devices_Network.device import Device
    from PacketCommunication.communication_manager import CommunicationManager
    from CLI.cli_parser import CLIParser
    from core.default_data import load_default_network, get_quick_test_network
    from core.validators import ValidationError
except ImportError as e:
    print(f"❌ Error importando módulos del proyecto: {e}")
    print("💡 Asegúrate de que todos los módulos estén en el directorio 'src'")
    sys.exit(1)


class NetworkSimulatorApp:
    """
    Aplicación principal del Simulador de Red.
    
    Gestiona la inicialización, configuración y ejecución del simulador,
    proporcionando diferentes modos de operación según las necesidades del usuario.
    """
    
    def __init__(self):
        """Inicializa la aplicación del simulador."""
        self.network = None
        self.communication_manager = None
        self.cli_parser = None
        self.app_name = "Simulador de Red"
        self.version = "1.0"
    
    def show_banner(self):
        """Muestra el banner de bienvenida de la aplicación."""
        print("\n" + "=" * 70)
        print(f"🌐 {self.app_name.upper()} v{self.version}")
        print("=" * 70)
        print("📚 Proyecto: Algoritmos y Estructuras de Datos 2")
        print("🎯 Simulador completo de redes con CLI interactivo")
        print("🛠️  Funcionalidades: Dispositivos, Paquetes, CLI, Persistencia")
        print("=" * 70)
    
    def show_help(self):
        """Muestra ayuda detallada sobre el uso de la aplicación."""
        self.show_banner()
        print("\n📖 GUÍA DE USO:")
        print("-" * 50)
        print("🚀 MODOS DE EJECUCIÓN:")
        print("  python main.py                    # Modo interactivo (recomendado)")
        print("  python main.py -i                 # Modo interactivo explícito")
        print("  python main.py --demo             # Demostración rápida")
        print("  python main.py --load config.json # Cargar configuración")
        print("  python main.py --help             # Mostrar esta ayuda")
        
        print("\n🎮 COMANDOS CLI PRINCIPALES:")
        print("  enable                             # Modo privilegiado")
        print("  configure terminal                 # Modo configuración global")
        print("  show devices                       # Listar dispositivos")
        print("  send <src_ip> <dst_ip> <mensaje>   # Enviar paquete")
        print("  tick                               # Procesar paquetes")
        print("  show statistics                    # Ver estadísticas")
        print("  save running-config [archivo]      # Guardar configuración")
        print("  load config <archivo>              # Cargar configuración")
        print("  exit                               # Salir")
        
        print("\n📁 CONFIGURACIONES PREDEFINIDAS:")
        print("  simple_home                        # Red doméstica básica")
        print("  small_office                       # Red de oficina pequeña")
        print("  data_center                        # Centro de datos")
        
        print("\n💡 EJEMPLOS DE USO:")
        print("  1. Crear red simple: 'load default simple_home'")
        print("  2. Enviar ping: 'send 192.168.1.10 192.168.1.1 ping'")
        print("  3. Procesar: 'tick'")
        print("  4. Ver resultado: 'show history Home-Router'")
        
        print("=" * 70)
    
    def create_quick_demo_network(self) -> Network:
        """
        Crea una red de demostración rápida para mostrar las funcionalidades.
        
        Returns:
            Network: Red de demostración configurada
        """
        print("🏗️  Creando red de demostración...")
        
        # Crear red simple
        network = Network("Red de Demostración")
        
        # Crear dispositivos
        router = Device("Demo-Router", "router")
        router.setStatus("online")
        host1 = Device("PC-1", "host")
        host1.setStatus("online")
        host2 = Device("PC-2", "host")
        host2.setStatus("online")
        
        # Agregar dispositivos a la red
        network.addDevice(router)
        network.addDevice(host1)
        network.addDevice(host2)
        
        # Configurar interfaces
        router_lan = router.addInterface("lan0", autoActivate=True)
        router_lan.assignIpAddress("192.168.1.1")
        router_lan.setMacAddress("aa:bb:cc:dd:ee:01")
        
        router_lan2 = router.addInterface("lan1", autoActivate=True)
        router_lan2.assignIpAddress("192.168.1.2")
        router_lan2.setMacAddress("aa:bb:cc:dd:ee:03")
        
        pc1_eth = host1.addInterface("eth0", autoActivate=True)
        pc1_eth.assignIpAddress("192.168.1.10")
        pc1_eth.setMacAddress("bb:cc:dd:ee:ff:01")
        
        pc2_eth = host2.addInterface("eth0", autoActivate=True)
        pc2_eth.assignIpAddress("192.168.1.20")
        pc2_eth.setMacAddress("bb:cc:dd:ee:ff:02")
        
        # Establecer conexiones
        network.establishConnection("Demo-Router", "lan0", "PC-1", "eth0")
        # PC-2 necesita una interfaz diferente
        pc2_eth1 = host2.addInterface("eth1", autoActivate=True)
        pc2_eth1.assignIpAddress("192.168.1.21")
        pc2_eth1.setMacAddress("bb:cc:dd:ee:ff:04")
        network.establishConnection("Demo-Router", "lan1", "PC-2", "eth1")
        
        # Agregar algunas estadísticas de ejemplo
        network.total_packets_sent = 25
        network.delivered_packets = 23
        network.dropped_packets_ttl = 2
        network.total_hops = 58
        network.device_activity = {
            "Demo-Router": 15,
            "PC-1": 8,
            "PC-2": 5
        }
        
        print("✅ Red de demostración creada:")
        print(f"   📊 {len(network.devices)} dispositivos")
        print(f"   🔗 {len(network.connections)} conexiones")
        print(f"   📦 {network.total_packets_sent} paquetes de ejemplo")
        
        return network
    
    def run_quick_demo(self):
        """Ejecuta una demostración rápida del simulador."""
        self.show_banner()
        print("\n🎬 EJECUTANDO DEMOSTRACIÓN RÁPIDA")
        print("=" * 50)
        
        try:
            # Crear red de demo
            self.network = self.create_quick_demo_network()
            self.communication_manager = CommunicationManager(self.network)
            
            print("\n1️⃣ ESTADO INICIAL DE LA RED:")
            self.network.listDevices()
            
            print("\n2️⃣ ENVIANDO PAQUETE DE PRUEBA:")
            packet = self.communication_manager.send(
                "192.168.1.10", 
                "192.168.1.1", 
                "Ping desde PC-1 a Router"
            )
            if packet:
                print(f"   ✅ Paquete enviado: ID {packet.id}")
                print(f"   📤 Origen: {packet.sourceIp}")
                print(f"   📥 Destino: {packet.destinationIp}")
                print(f"   💬 Contenido: {packet.content}")
            
            print("\n3️⃣ PROCESANDO PAQUETES:")
            tick_result = self.communication_manager.tick()
            print(f"   ⚙️  Dispositivos procesados: {tick_result.get('devicesProcessed', 'N/A')}")
            print(f"   📦 Paquetes procesados: {tick_result.get('packetsProcessed', 'N/A')}")
            if 'packetsDelivered' in tick_result:
                print(f"   ✅ Paquetes entregados: {tick_result['packetsDelivered']}")
            if 'packetsForwarded' in tick_result:
                print(f"   📨 Paquetes reenviados: {tick_result['packetsForwarded']}")
            if 'packetsDropped' in tick_result:
                print(f"   ❌ Paquetes descartados: {tick_result['packetsDropped']}")
            
            print("\n4️⃣ ESTADÍSTICAS DE RED:")
            self.network.showStatistics()
            
            print("\n5️⃣ HISTORIAL DEL ROUTER:")
            router = self.network.getDevice("Demo-Router")
            if router:
                router.showHistory(max_entries=5)
            
            print("\n✨ DEMOSTRACIÓN COMPLETADA")
            print("💡 Para explorar más funcionalidades, ejecuta:")
            print("   python main.py --interactive")
            
        except Exception as e:
            print(f"❌ Error durante la demostración: {e}")
            return False
        
        return True
    
    def load_configuration(self, config_file: str) -> bool:
        """
        Carga una configuración de red desde un archivo.
        
        Args:
            config_file (str): Ruta al archivo de configuración
            
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            print(f"📂 Cargando configuración desde: {config_file}")
            
            # Verificar si es una configuración predefinida
            if config_file in ["simple_home", "small_office", "data_center"]:
                print(f"🏗️  Cargando plantilla predefinida: {config_file}")
                self.network = load_default_network(config_file)
                print(f"✅ Plantilla '{config_file}' cargada exitosamente")
            else:
                # Intentar cargar desde archivo
                if not os.path.exists(config_file):
                    print(f"❌ Archivo no encontrado: {config_file}")
                    return False
                
                self.network = Network("Red Cargada")
                self.network.load_config(config_file)
                print(f"✅ Configuración cargada desde {config_file}")
            
            # Inicializar communication manager
            if self.network:
                self.communication_manager = CommunicationManager(self.network)
                
                print(f"📊 Red cargada:")
                print(f"   📱 Dispositivos: {len(self.network.devices)}")
                print(f"   🔗 Conexiones: {len(self.network.connections)}")
                
                return True
                
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return False
        
        return False
    
    def initialize_network(self, network_type: str = "quick") -> bool:
        """
        Inicializa una red según el tipo especificado.
        
        Args:
            network_type (str): Tipo de red a crear ("quick", "simple_home", etc.)
            
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            if network_type == "quick":
                print("🚀 Inicializando red de prueba rápida...")
                self.network = get_quick_test_network()
            else:
                print(f"🏗️  Inicializando red predefinida: {network_type}")
                self.network = load_default_network(network_type)
            
            if self.network:
                self.communication_manager = CommunicationManager(self.network)
                print(f"✅ Red inicializada: {self.network.name}")
                return True
            else:
                print("❌ Error inicializando la red")
                return False
                
        except Exception as e:
            print(f"❌ Error durante inicialización: {e}")
            return False
    
    def run_interactive_mode(self):
        """Ejecuta el modo CLI interactivo."""
        self.show_banner()
        print("\n🎮 MODO INTERACTIVO INICIADO")
        print("=" * 50)
        
        # Si no hay red cargada, crear una rápida
        if not self.network:
            print("📝 No hay red cargada. Opciones disponibles:")
            print("  1. Crear red de prueba rápida")
            print("  2. Cargar plantilla predefinida")
            print("  3. Comenzar con red vacía")
            
            while True:
                try:
                    choice = input("\n👉 Selecciona una opción (1-3): ").strip()
                    
                    if choice == "1":
                        if self.initialize_network("quick"):
                            break
                    elif choice == "2":
                        print("\n📋 Plantillas disponibles:")
                        print("  • simple_home   - Red doméstica básica")
                        print("  • small_office  - Red de oficina pequeña")
                        print("  • data_center   - Centro de datos")
                        
                        template = input("\n👉 Nombre de la plantilla: ").strip()
                        if template in ["simple_home", "small_office", "data_center"]:
                            if self.initialize_network(template):
                                break
                        else:
                            print("❌ Plantilla no válida")
                    elif choice == "3":
                        self.network = Network("Mi Red")
                        self.communication_manager = CommunicationManager(self.network)
                        print("✅ Red vacía creada")
                        break
                    else:
                        print("❌ Opción no válida")
                        
                except KeyboardInterrupt:
                    print("\n👋 Saliendo...")
                    return
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        # Inicializar CLI
        try:
            self.cli_parser = CLIParser(self.network, self.communication_manager)
            
            print(f"\n🌐 Red activa: {self.network.name}")
            print(f"📊 Dispositivos: {len(self.network.devices)}")
            print(f"🔗 Conexiones: {len(self.network.connections)}")
            
            print("\n💡 COMANDOS ÚTILES PARA EMPEZAR:")
            print("  help                    # Ver ayuda completa")
            print("  show devices            # Listar dispositivos")
            print("  show interfaces         # Ver todas las interfaces")
            print("  enable                  # Modo privilegiado")
            print("  configure terminal      # Modo configuración")
            print("  exit                    # Salir")
            
            print("\n" + "=" * 50)
            print("🎯 CLI LISTO - Escribe 'help' para ver comandos disponibles")
            print("=" * 50)
            
            # Ejecutar CLI interactivo
            self.cli_parser.run_interactive()
            
        except KeyboardInterrupt:
            print("\n👋 Saliendo del modo interactivo...")
        except Exception as e:
            print(f"❌ Error en modo interactivo: {e}")
    
    def run(self, args):
        """
        Método principal que ejecuta la aplicación según los argumentos.
        
        Args:
            args: Argumentos de línea de comandos parseados
        """
        try:
            if args.detailed_help:
                self.show_help()
            elif args.demo:
                self.run_quick_demo()
            elif args.load:
                if self.load_configuration(args.load):
                    if args.interactive:
                        self.run_interactive_mode()
                    else:
                        print("✅ Configuración cargada exitosamente")
                        print("💡 Usa --interactive para entrar al modo CLI")
                else:
                    print("❌ No se pudo cargar la configuración")
                    sys.exit(1)
            else:
                # Modo interactivo por defecto
                self.run_interactive_mode()
                
        except KeyboardInterrupt:
            print("\n👋 Aplicación interrumpida por el usuario")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            sys.exit(1)


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description="Simulador de Red - Proyecto Algoritmos y Estructuras de Datos 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                           # Modo interactivo
  python main.py --demo                    # Demostración rápida
  python main.py --load simple_home       # Cargar plantilla
  python main.py --load configs/mi_red.json  # Cargar archivo
        """
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Ejecutar en modo CLI interactivo (por defecto)"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true", 
        help="Ejecutar demostración rápida del simulador"
    )
    
    parser.add_argument(
        "--load",
        type=str,
        metavar="ARCHIVO",
        help="Cargar configuración desde archivo o plantilla (simple_home, small_office, data_center)"
    )
    
    parser.add_argument(
        "--detailed-help",
        action="store_true",
        help="Mostrar ayuda detallada con ejemplos"
    )
    
    return parser.parse_args()


def main():
    """Función principal de la aplicación."""
    # Verificar Python version
    if sys.version_info < (3, 6):
        print("❌ Este proyecto requiere Python 3.6 o superior")
        sys.exit(1)
    
    # Parsear argumentos
    args = parse_arguments()
    
    # Crear y ejecutar aplicación
    app = NetworkSimulatorApp()
    app.run(args)


if __name__ == "__main__":
    main() 