"""
Módulo DataEstructures
======================

Contiene las implementaciones de estructuras de datos fundamentales para el proyecto de simulación de red.

Clases incluidas:
- Node: Nodo básico para estructuras de datos enlazadas
- LinkedList: Lista enlazada para almacenar vecinos de interfaces
- Queue: Cola FIFO para gestionar paquetes entrantes y salientes  
- Stack: Pila LIFO para historial de mensajes recibidos
"""

from .node import Node
from .stack import Stack
from .queue import Queue
from .linked_list import LinkedList

__all__ = ['Node', 'Stack', 'Queue', 'LinkedList'] 