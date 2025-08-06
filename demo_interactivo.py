#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 DEMOSTRACIÓN INTERACTIVA AUTOMÁTICA
====================================

Script que ejecuta main.py y simula automáticamente toda la interacción
del usuario, escribiendo comandos como si fueras tú mismo usando el programa.

Este script:
1. Ejecuta "python main.py"
2. Simula selecciones de menú
3. Escribe comandos CLI automáticamente
4. Muestra todo el proceso en tiempo real

Usage: python demo_interactivo.py
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def mostrar_banner():
    """Muestra banner inicial del demo"""
    print("\n" + "=" * 70)
    print("🤖 DEMOSTRACIÓN INTERACTIVA AUTOMÁTICA")
    print("=" * 70)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🎯 Ejecutando main.py con comandos automáticos")
    print("⏸️  Presiona ENTER para continuar en cada paso...")
    print("=" * 70)

def esperar_enter(mensaje="Presiona ENTER para continuar..."):
    """Pausa hasta que el usuario presione ENTER"""
    input(f"\n⏸️  {mensaje}")

def mostrar_paso(paso, descripcion):
    """Muestra información del paso actual"""
    print(f"\n🔹 PASO {paso}: {descripcion}")
    print("-" * 50)

class DemoInteractivo:
    """
    Automatiza la interacción completa con main.py simulando un usuario real.
    Ejecuta comandos paso a paso mostrando todo el proceso.
    """
    
    def __init__(self):
        self.comandos_demo = []
        self.preparar_comandos()
    
    def preparar_comandos(self):
        """Prepara la secuencia de comandos a ejecutar"""
        self.comandos_demo = [
            # Secuencia 1: Inicio con red de prueba
            {
                "paso": 1,
                "descripcion": "Iniciar simulador y seleccionar red de prueba",
                "entrada": "1\n",  # Seleccionar opción 1 (red de prueba rápida)
                "delay": 2
            },
            
            # Secuencia 2: Comandos básicos de consulta
            {
                "paso": 2,
                "descripcion": "Ejecutar comando 'help' para ver ayuda",
                "entrada": "help\n",
                "delay": 3
            },
            {
                "paso": 3,
                "descripcion": "Mostrar dispositivos con 'show devices'",
                "entrada": "show devices\n",
                "delay": 3
            },
            {
                "paso": 4,
                "descripcion": "Ver interfaces con 'show interfaces'",
                "entrada": "show interfaces\n",
                "delay": 3
            },
            
            # Secuencia 3: Comunicación de paquetes
            {
                "paso": 5,
                "descripcion": "Enviar paquete de prueba",
                "entrada": "send 192.168.1.10 192.168.1.1 \"Prueba de conectividad\"\n",
                "delay": 2
            },
            {
                "paso": 6,
                "descripcion": "Procesar paquetes con 'tick'",
                "entrada": "tick\n",
                "delay": 2
            },
            {
                "paso": 7,
                "descripcion": "Segundo tick para completar procesamiento",
                "entrada": "tick\n",
                "delay": 2
            },
            
            # Secuencia 4: Estadísticas y reportes
            {
                "paso": 8,
                "descripcion": "Ver estadísticas de red",
                "entrada": "show statistics\n",
                "delay": 3
            },
            {
                "paso": 9,
                "descripcion": "Ver historial de un dispositivo",
                "entrada": "show history Test-Router\n",
                "delay": 2
            },
            
            # Secuencia 5: Configuración CLI
            {
                "paso": 10,
                "descripcion": "Entrar al modo privilegiado",
                "entrada": "enable\n",
                "delay": 2
            },
            {
                "paso": 11,
                "descripcion": "Entrar al modo configuración",
                "entrada": "configure terminal\n",
                "delay": 2
            },
            {
                "paso": 12,
                "descripcion": "Cambiar hostname del dispositivo",
                "entrada": "hostname Demo-Router\n",
                "delay": 2
            },
            {
                "paso": 13,
                "descripcion": "Salir al modo privilegiado",
                "entrada": "end\n",
                "delay": 2
            },
            
            # Secuencia 6: Persistencia
            {
                "paso": 14,
                "descripcion": "Guardar configuración",
                "entrada": "save running-config demo_presentacion.json\n",
                "delay": 3
            },
            {
                "paso": 15,
                "descripcion": "Ver configuraciones guardadas",
                "entrada": "show configs\n",
                "delay": 2
            },
            
            # Secuencia 7: Finalizar
            {
                "paso": 16,
                "descripcion": "Salir del simulador",
                "entrada": "exit\n",
                "delay": 1
            }
        ]
    
    def ejecutar_con_entrada_automatica(self):
        """Ejecuta main.py con entrada automática completa"""
        print("🚀 Preparando demostración automática completa...")
        
        # Crear archivo con todas las entradas
        entradas_completas = ""
        for cmd in self.comandos_demo:
            entradas_completas += cmd["entrada"]
        
        # Guardar en archivo temporal
        with open("demo_input.txt", "w") as f:
            f.write(entradas_completas)
        
        print("📝 Archivo de comandos creado")
        print("🎬 Ejecutando demostración completa...")
        print("\n" + "=" * 50)
        
        try:
            # Ejecutar main.py con entrada desde archivo
            result = subprocess.run(
                ["python", "main.py"],
                input=entradas_completas,
                text=True,
                capture_output=False,  # Mostrar salida en tiempo real
                timeout=300  # 5 minutos máximo
            )
            
            print("\n" + "=" * 50)
            if result.returncode == 0:
                print("✅ Demostración completada exitosamente")
            else:
                print(f"⚠️ Demostración terminó con código: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Demostración terminada por timeout")
        except KeyboardInterrupt:
            print("\n⏹️ Demostración interrumpida por el usuario")
        except Exception as e:
            print(f"❌ Error durante la demostración: {e}")
        finally:
            # Limpiar archivo temporal
            if os.path.exists("demo_input.txt"):
                os.remove("demo_input.txt")
    
    def ejecutar_paso_a_paso(self):
        """Ejecuta la demostración paso a paso con pausas"""
        print("🎭 Ejecutando demostración paso a paso...")
        print("📝 Cada comando se ejecutará individualmente")
        
        for cmd in self.comandos_demo:
            mostrar_paso(cmd["paso"], cmd["descripcion"])
            print(f"💻 Comando a ejecutar: {repr(cmd['entrada'].strip())}")
            
            esperar_enter(f"Ejecutar paso {cmd['paso']}")
            
            try:
                # Ejecutar main.py con este comando específico
                process = subprocess.Popen(
                    ["python", "main.py"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Enviar comando y obtener resultado
                stdout, stderr = process.communicate(input=cmd["entrada"], timeout=30)
                
                print("📤 SALIDA:")
                print(stdout)
                
                if stderr:
                    print("⚠️ ERRORES:")
                    print(stderr)
                
                time.sleep(cmd["delay"])
                
            except subprocess.TimeoutExpired:
                print("⏰ Comando terminado por timeout")
                process.kill()
            except Exception as e:
                print(f"❌ Error ejecutando comando: {e}")
    
    def mostrar_secuencia_comandos(self):
        """Muestra la secuencia completa de comandos que se ejecutarán"""
        print("📋 SECUENCIA COMPLETA DE COMANDOS:")
        print("=" * 60)
        
        for i, cmd in enumerate(self.comandos_demo, 1):
            comando_limpio = cmd["entrada"].strip().replace('\n', '')
            print(f"{i:2d}. {cmd['descripcion']}")
            print(f"    💻 Comando: {comando_limpio}")
            print()
        
        print("⏱️ DURACIÓN ESTIMADA: 10-15 minutos")
        print("🎯 TOTAL COMANDOS: " + str(len(self.comandos_demo)))
    
    def ejecutar_demo_rapido(self):
        """Ejecuta una demostración rápida con comandos esenciales"""
        comandos_rapidos = [
            "1\n",  # Seleccionar red de prueba
            "show devices\n",
            "send 192.168.1.10 192.168.1.1 \"Ping de prueba\"\n",
            "tick\n",
            "show statistics\n",
            "enable\n",
            "save running-config demo.json\n",
            "exit\n"
        ]
        
        entrada_rapida = "".join(comandos_rapidos)
        
        print("⚡ Ejecutando demostración rápida...")
        print("🕐 Duración estimada: 3-5 minutos")
        
        try:
            result = subprocess.run(
                ["python", "main.py"],
                input=entrada_rapida,
                text=True,
                capture_output=False,
                timeout=180
            )
            
            if result.returncode == 0:
                print("\n✅ Demostración rápida completada")
            else:
                print(f"\n⚠️ Terminó con código: {result.returncode}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def menu_principal(self):
        """Muestra menú de opciones para la demostración"""
        while True:
            print("\n" + "=" * 60)
            print("🎭 MENÚ DE DEMOSTRACIÓN INTERACTIVA")
            print("=" * 60)
            print("1. 🎬 Demostración completa automática")
            print("2. 👣 Demostración paso a paso (con pausas)")
            print("3. ⚡ Demostración rápida (solo esenciales)")
            print("4. 📋 Ver secuencia de comandos")
            print("5. 🚪 Salir")
            print("=" * 60)
            
            try:
                opcion = input("👉 Selecciona una opción (1-5): ").strip()
                
                if opcion == "1":
                    self.ejecutar_con_entrada_automatica()
                elif opcion == "2":
                    self.ejecutar_paso_a_paso()
                elif opcion == "3":
                    self.ejecutar_demo_rapido()
                elif opcion == "4":
                    self.mostrar_secuencia_comandos()
                elif opcion == "5":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción no válida. Intenta de nuevo.")
                    
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Función principal"""
    mostrar_banner()
    
    # Verificar que main.py existe
    if not os.path.exists("main.py"):
        print("❌ Error: No se encontró main.py en el directorio actual")
        print("💡 Asegúrate de ejecutar este script desde el directorio del proyecto")
        return
    
    esperar_enter("Iniciar demostración interactiva")
    
    demo = DemoInteractivo()
    demo.menu_principal()

if __name__ == "__main__":
    main() 