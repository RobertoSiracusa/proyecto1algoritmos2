"""
Módulo DataEstructures
======================

Contiene las implementaciones de estructuras de datos fundamentales para el proyecto de simulación de red.

Clases incluidas:
- LinkedList: Lista enlazada para almacenar vecinos de interfaces
- Queue: Cola FIFO para gestionar paquetes entrantes y salientes  
- Stack: Pila LIFO para historial de mensajes recibidos
"""

from .stack import Stack
from .queue import Queue
from .linked_list import LinkedList

__all__ = ['Stack', 'Queue', 'LinkedList'] 