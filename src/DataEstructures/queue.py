from collections import deque
from typing import Optional


class Queue:
    """
    Implementación de una cola (Queue) FIFO para gestionar paquetes entrantes y salientes.
    Utilizada para manejar colas de paquetes en dispositivos e interfaces.
    Soporta capacidad máxima opcional para evitar desbordamientos.
    """
    
    def __init__(self, max_capacity: Optional[int] = None):
        """
        Inicializa una nueva cola vacía.
        
        Args:
            max_capacity (Optional[int]): Capacidad máxima de la cola.
                                        Si es None, la cola no tiene límite.
        """
        self._items = deque()
        self._max_capacity = max_capacity
    
    def enqueue(self, item):
        """
        Agrega un elemento al final de la cola
        
        Args:
            item: Elemento a agregar al final de la cola
            
        Raises:
            Exception: Si la cola ha alcanzado su capacidad máxima
        """
        if self._max_capacity is not None and len(self._items) >= self._max_capacity:
            raise Exception(f"La cola ha alcanzado su capacidad máxima de {self._max_capacity} elementos")
        
        self._items.append(item)
    
    def dequeue(self):
        """
        Remueve y retorna el primer elemento de la cola (FIFO)
        
        Returns:
            El primer elemento de la cola o None si está vacía
        """
        if self.is_empty():
            return None
        return self._items.popleft()
    
    def is_empty(self):
        """
        Verifica si la cola está vacía
        
        Returns:
            bool: True si la cola está vacía, False en caso contrario
        """
        return len(self._items) == 0
    
    def front(self):
        """
        Retorna el primer elemento de la cola sin removerlo
        
        Returns:
            El primer elemento de la cola o None si está vacía
        """
        if self.is_empty():
            return None
        return self._items[0]
    
    def size(self):
        """
        Retorna el tamaño actual de la cola
        
        Returns:
            int: Número de elementos en la cola
        """
        return len(self._items)
    
    def clear(self):
        """
        Limpia todos los elementos de la cola
        """
        self._items.clear()
    
    def getAll(self):
        """
        Retorna todos los elementos de la cola en orden FIFO
        
        Returns:
            list: Lista con todos los elementos en orden
        """
        return list(self._items)
    
    def get_capacity(self) -> Optional[int]:
        """
        Retorna la capacidad máxima configurada para la cola.
        
        Returns:
            Optional[int]: Capacidad máxima de la cola, o None si es ilimitada
        """
        return self._max_capacity
    
    def get_remaining_capacity(self) -> Optional[int]:
        """
        Retorna la cantidad de elementos que aún se pueden agregar a la cola.
        
        Returns:
            Optional[int]: Espacios disponibles, o None si la capacidad es ilimitada
        """
        if self._max_capacity is None:
            return None
        return self._max_capacity - len(self._items)
    
    def is_full(self) -> bool:
        """
        Verifica si la cola ha alcanzado su capacidad máxima.
        
        Returns:
            bool: True si la cola está llena, False en caso contrario.
                 Si no hay límite de capacidad, siempre retorna False.
        """
        if self._max_capacity is None:
            return False
        return len(self._items) >= self._max_capacity
    
    def get_statistics(self) -> dict:
        """
        Retorna estadísticas útiles sobre la cola.
        
        Returns:
            dict: Diccionario con estadísticas de la cola
        """
        return {
            "current_size": len(self._items),
            "max_capacity": self._max_capacity,
            "remaining_capacity": self.get_remaining_capacity(),
            "is_empty": self.is_empty(),
            "is_full": self.is_full(),
            "utilization_rate": (len(self._items) / self._max_capacity * 100) if self._max_capacity else None
        }
    
    def __str__(self):
        """Representación en string de la cola"""
        capacity_info = ""
        if self._max_capacity is not None:
            capacity_info = f", capacity={self._max_capacity}"
        return f"Queue(size={self.size()}{capacity_info})"
    
    def __len__(self):
        """Permite usar len() en la cola"""
        return self.size()
    
    def __iter__(self):
        """Permite iterar sobre la cola (del frente hacia atrás)"""
        for item in self._items:
            yield item 