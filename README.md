# 🌐 Simulador de Red

**Proyecto de Algoritmos y Estructuras de Datos 2**

Un simulador completo de redes de computadoras implementado en Python, que proporciona una interfaz de línea de comandos (CLI) profesional para crear, configurar y gestionar redes simuladas.

## 🚀 Características Principales

- ✅ **Dispositivos de Red**: Routers, switches, hosts y firewalls
- ✅ **Interfaz CLI Profesional**: Múltiples modos (User, Privileged, Configuration)
- ✅ **Simulación de Paquetes**: Envío, procesamiento y routing de paquetes
- ✅ **Persistencia de Configuración**: Guardar/cargar redes en formato JSON
- ✅ **Estadísticas Avanzadas**: Reportes detallados de actividad de red
- ✅ **Estructuras de Datos**: Stack, Queue y LinkedList implementadas desde cero
- ✅ **Validaciones Robustas**: Sistema completo de validación de datos
- ✅ **Arquitectura Modular**: Diseño orientado a objetos con separación clara de responsabilidades

## 📋 Requisitos

- **Python 3.6 o superior**
- Sistema operativo: Windows, macOS o Linux

## 🎯 Instalación y Uso Rápido

### 1. Clonar o descargar el proyecto
```bash
# Si tienes git
git clone <url-del-repositorio>
cd proyecto1algoritmos2

# O simplemente descargar y extraer el ZIP
```

### 2. Ejecutar el simulador

#### **Modo Interactivo (Recomendado)**
```bash
python main.py
```

#### **Demostración Rápida**
```bash
python main.py --demo
```

#### **Cargar Red Predefinida**
```bash
python main.py --load simple_home
```

#### **Ver Ayuda Completa**
```bash
python main.py --help
```

## 🎮 Guía de Uso

### **Primeros Pasos**

1. **Iniciar el Simulador**:
   ```bash
   python main.py
   ```

2. **Seleccionar una red**:
   - Opción 1: Red de prueba rápida
   - Opción 2: Plantilla predefinida (`simple_home`, `small_office`, `data_center`)
   - Opción 3: Red vacía

3. **Comandos básicos**:
   ```
   help                    # Ver ayuda completa
   show devices            # Listar dispositivos
   enable                  # Modo privilegiado
   configure terminal      # Modo configuración
   exit                    # Salir
   ```

### **Comandos CLI Principales**

#### **Navegación entre Modos**
```bash
Router>                           # Modo Usuario
Router> enable                    # Cambiar a modo privilegiado
Router# configure terminal        # Cambiar a modo configuración global
Router(config)# interface eth0    # Cambiar a modo configuración de interfaz
Router(config-if)# end            # Volver a modo privilegiado
```

#### **Gestión de Dispositivos**
```bash
show devices                      # Listar todos los dispositivos
show interfaces                   # Ver todas las interfaces
show history <dispositivo>        # Ver historial de paquetes
show queue <dispositivo>          # Ver colas de paquetes
show statistics                   # Ver estadísticas de red
```

#### **Comunicación de Paquetes**
```bash
send 192.168.1.10 192.168.1.1 "Hola Router"    # Enviar paquete
tick                                            # Procesar paquetes en cola
process                                         # Alias para tick
```

#### **Configuración de Dispositivos**
```bash
Router# configure terminal
Router(config)# hostname MiRouter               # Cambiar nombre
Router(config)# interface eth0                  # Configurar interfaz
Router(config-if)# ip address 192.168.1.1      # Asignar IP
Router(config-if)# no shutdown                  # Activar interfaz
Router(config-if)# shutdown                     # Desactivar interfaz
```

#### **Persistencia de Configuración**
```bash
save running-config                             # Guardar con nombre automático
save running-config mi_red.json                # Guardar con nombre específico
load config mi_red.json                        # Cargar configuración
show configs                                    # Listar configuraciones guardadas
show config-info mi_red.json                   # Ver información de configuración
```

#### **Comandos de Routing (Solo para Routers)**
```bash
show ip route                                   # Mostrar tabla de rutas
show ip interface brief                         # Resumen de interfaces IP
ip route 192.168.1.0/24 192.168.1.254 eth0     # Agregar ruta estática
ip route default 192.168.1.254 eth0            # Configurar ruta por defecto
no ip route 192.168.1.0/24                     # Eliminar ruta
clear ip route                                  # Limpiar todas las rutas
show routing                                    # Mostrar tabla de rutas (alias)
```

#### **Comandos de Red**
```bash
ping 192.168.1.1                               # Hacer ping a un destino
ping 192.168.1.1 10                            # Ping con número específico de paquetes
traceroute 192.168.1.1                         # Trazar ruta a un destino
```

## 🏗️ Arquitectura del Proyecto

```
proyecto1algoritmos2/
├── main.py                          # Punto de entrada principal
├── README.md                        # Este archivo
├── configs/                         # Configuraciones guardadas (JSON)
└── src/                            # Código fuente
    ├── core/                       # Módulos centrales
    │   ├── validators.py           # Sistema de validaciones
    │   └── default_data.py         # Datos y plantillas por defecto
    ├── DataEstructures/            # Estructuras de datos
    │   ├── stack.py               # Pila LIFO
    │   ├── queue.py               # Cola FIFO
    │   └── linked_list.py         # Lista enlazada
    ├── Devices_Network/            # Dispositivos y red
    │   ├── device.py              # Clase Device (router, switch, host, firewall)
    │   ├── interface.py           # Clase Interface (puertos de red)
    │   └── network.py             # Clase Network (gestión de red)
    ├── PacketCommunication/        # Comunicación de paquetes
    │   ├── packet.py              # Clase Packet
    │   └── communication_manager.py # Gestor de comunicaciones
    └── CLI/                        # Interfaz de línea de comandos
        ├── cli_parser.py          # Parser principal CLI
        ├── cli_modes.py           # Gestión de modos CLI
        ├── command_base.py        # Patrón Command base
        └── commands/              # Comandos específicos
            ├── basic_commands.py
            ├── navigation_commands.py
            ├── show_commands.py
            ├── network_commands.py
            └── config_commands.py
```

## 🔧 Módulos y Funcionalidades

### **1. DataEstructures**
- **Stack**: Historial LIFO de paquetes recibidos
- **Queue**: Colas FIFO para paquetes entrantes/salientes
- **LinkedList**: Lista enlazada para vecinos de interfaces

### **2. Devices_Network**
- **Device**: Dispositivos de red (router, switch, host, firewall)
- **Interface**: Puertos de red con direcciones IP/MAC
- **Network**: Gestión completa de la topología de red

### **3. PacketCommunication**
- **Packet**: Paquetes de datos con TTL y trazas de ruta
- **CommunicationManager**: Envío y procesamiento de paquetes

### **4. CLI (Command Line Interface)**
- **Múltiples Modos**: User, Privileged, Global Config, Interface Config
- **Patrón Command**: Comandos extensibles y modulares
- **Autocompletado**: Sugerencias de comandos
- **Historial**: Navegación por comandos anteriores

### **5. Core**
- **Validators**: Sistema robusto de validación de datos
- **Default Data**: Plantillas de red y datos de prueba

### **6. Configuration Persistence**
- **Serialización JSON**: Guardado completo del estado de red
- **Metadatos**: Versionado y timestamps
- **Gestión de Archivos**: Lista, información y carga de configuraciones

## 🌟 Redes Predefinidas

### **simple_home** - Red Doméstica
```
Internet --- Router --- Switch --- [PC-Sala, PC-Dormitorio, Printer]
```
- 1 Router (192.168.1.1)
- 1 Switch
- 3 Dispositivos finales

### **small_office** - Oficina Pequeña
```
Internet --- Firewall --- Core-Switch --- [Access-Switch1, Access-Switch2]
                            |
                         Servers
```
- Firewall perimetral
- Switches core y de acceso
- Servidores y estaciones de trabajo
- Segmentación DMZ

### **data_center** - Centro de Datos
```
Múltiples routers de borde, switches core redundantes,
switches de distribución y acceso, múltiples servidores
```
- Arquitectura redundante
- Múltiples servicios
- Balanceadores de carga

## 💡 Ejemplos de Uso

### **Ejemplo 1: Ping Básico**
```bash
# 1. Iniciar simulador
python main.py --load simple_home

# 2. Enviar ping
send 192.168.1.10 192.168.1.1 "ping request"

# 3. Procesar
tick

# 4. Ver resultado
show history Home-Router
```

### **Ejemplo 2: Configurar Nuevo Dispositivo**
```bash
# 1. Modo interactivo
python main.py

# 2. Crear red vacía
# (Seleccionar opción 3)

# 3. Entrar en configuración
enable
configure terminal

# 4. Agregar dispositivo y configurar
# (Usar comandos CLI para crear dispositivos)
```

### **Ejemplo 3: Guardar Configuración**
```bash
# 1. Después de configurar la red
save running-config mi_configuracion.json

# 2. Ver configuraciones guardadas
show configs

# 3. Cargar en otra sesión
python main.py --load configs/mi_configuracion.json
```

## 🐛 Solución de Problemas

### **Error de Importación**
```
❌ Error importando módulos del proyecto
```
**Solución**: Verificar que todos los archivos estén en `src/` y que Python pueda encontrar los módulos.

### **Dispositivo No Responde**
```
❌ No se puede realizar 'receive packet' en dispositivo offline
```
**Solución**: Verificar que el dispositivo esté online con `show devices` y usar `configure terminal` → `no shutdown`.

### **Paquete No Llega**
```
ℹ️ Paquete procesado pero no llega al destino
```
**Solución**: Verificar conectividad con `show interfaces` y que las interfaces estén "up".

## 🏆 Características de Calidad

- ✅ **100% OOP**: Uso extensivo de clases, herencia y polimorfismo
- ✅ **Validaciones Robustas**: 15+ tipos de validación con manejo de errores
- ✅ **Documentación Completa**: 100% clases documentadas, 93% métodos
- ✅ **Datos por Defecto**: 3 redes + 5 configuraciones + datos de prueba
- ✅ **Arquitectura Modular**: 5 módulos independientes
- ✅ **Código Legible**: Naming consistente, formato uniforme

## 👥 Contribuciones

Este proyecto fue desarrollado como parte del curso Algoritmos y Estructuras de Datos 2.

## 📄 Licencia

Proyecto académico - Todos los derechos reservados.

---

**¡Disfruta explorando el mundo de las redes de computadoras! 🌐** 