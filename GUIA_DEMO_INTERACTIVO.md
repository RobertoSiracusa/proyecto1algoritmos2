# 🤖 GUÍA - DEMOSTRACIÓN INTERACTIVA AUTOMÁTICA

## 🎯 ¿Qué hace este script?

**`demo_interactivo.py`** ejecuta directamente `python main.py` y simula automáticamente toda la interacción del usuario, como si fueras tú escribiendo comandos en la terminal.

## 🚀 Uso Simple

```bash
python demo_interactivo.py
```

## 📋 Opciones Disponibles

### **1. 🎬 Demostración Completa Automática**
- Ejecuta **TODOS** los comandos automáticamente
- Duración: **10-15 minutos**
- No requiere intervención

### **2. 👣 Demostración Paso a Paso**
- Ejecuta comando por comando
- **Presiona ENTER** para avanzar
- Perfecto para **explicar durante la presentación**

### **3. ⚡ Demostración Rápida**
- Solo comandos **esenciales**
- Duración: **3-5 minutos**
- Ideal para **presentaciones cortas**

### **4. 📋 Ver Secuencia de Comandos**
- Muestra **todos los comandos** que se ejecutarán
- Útil para **planificar la presentación**

## 🎭 ¿Qué Comandos Simula?

### **Secuencia Completa (16 pasos):**

1. **Inicialización**: Selecciona opción 1 (red de prueba)
2. **Ayuda**: `help`
3. **Dispositivos**: `show devices`
4. **Interfaces**: `show interfaces`
5. **Envío**: `send 192.168.1.10 192.168.1.1 "Prueba de conectividad"`
6. **Procesamiento**: `tick`
7. **Segundo tick**: `tick`
8. **Estadísticas**: `show statistics`
9. **Historial**: `show history Test-Router`
10. **Modo privilegiado**: `enable`
11. **Configuración**: `configure terminal`
12. **Cambiar hostname**: `hostname Demo-Router`
13. **Salir config**: `end`
14. **Guardar**: `save running-config demo_presentacion.json`
15. **Ver configs**: `show configs`
16. **Salir**: `exit`

## 🎯 Perfecto para Presentaciones

### **Ventajas:**
- ✅ **Ejecuta `main.py` real** - No simula, usa tu programa
- ✅ **Automatiza TODO** - Sin errores de tipeo
- ✅ **Control total** - Pausas cuando quieras
- ✅ **Tiempo perfecto** - Adaptas a tu presentación
- ✅ **Muestra TODO** - Todas las funcionalidades

### **Durante la Presentación:**
1. **Ejecuta**: `python demo_interactivo.py`
2. **Selecciona** opción 2 (paso a paso)
3. **Presiona ENTER** para cada comando
4. **Explica** mientras se ejecuta cada paso
5. **Destaca funcionalidades** que aparecen

## 💡 Consejos de Uso

### **Para Presentación al Profesor:**
- Usa **opción 2** (paso a paso)
- **Explica conceptos** entre comandos
- **Destaca aspectos técnicos**
- **Menciona decisiones de diseño**

### **Para Demo Rápida:**
- Usa **opción 3** (demostración rápida)
- Ideal para **tiempo limitado**
- Muestra **funcionalidades esenciales**

### **Para Planificación:**
- Usa **opción 4** (ver comandos)
- **Revisa la secuencia** antes de presentar
- **Calcula tiempo** necesario

## 🔧 Características Técnicas

- **No modifica** tu proyecto
- **Ejecuta main.py** como usuario normal
- **Simula entrada** de teclado
- **Muestra salida** en tiempo real
- **Maneja errores** gracefully
- **Limpia archivos** temporales

## ⚡ Ejemplo de Uso Rápido

```bash
# 1. Ejecutar script
python demo_interactivo.py

# 2. Seleccionar opción
👉 Selecciona una opción (1-5): 2

# 3. Presionar ENTER en cada paso
⏸️  Ejecutar paso 1

# 4. Ver resultado automático
💻 Comando a ejecutar: '1'
📤 SALIDA:
🌐 Creando red de prueba rápida...
...
```

---

**🌟 ¡Tu presentación será perfecta con este script automático! 🌟** 