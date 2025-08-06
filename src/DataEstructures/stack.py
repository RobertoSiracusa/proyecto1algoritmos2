#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stack (Pila) - Estructura de Datos LIFO
=======================================

Implementación de una pila (Stack) que sigue el principio LIFO (Last-In, First-Out).
Esta estructura de datos es utilizada principalmente para almacenar el historial de 
paquetes recibidos en dispositivos de red, permitiendo acceso rápido a los elementos
más recientes.

Características principales:
- Operaciones principales: push, pop, peek
- Acceso solo al elemento superior (tope)
- Tamaño dinámico sin límite predefinido
- Iteración segura sin modificar la estructura
- Validaciones robustas de entrada
- Encapsulación completa de datos internos

Author: Network Simulator Project
Version: 1.0
Date: 2025
"""


class StackEmptyError(Exception):
    """
    Excepción personalizada lanzada cuando se intenta realizar operaciones
    en una pila vacía que requieren elementos.
    """
    def __init__(self, operation):
        self.operation = operation
        super().__init__(f"No se puede realizar '{operation}' en una pila vacía")


class StackFullError(Exception):
    """
    Excepción personalizada lanzada cuando se excede la capacidad máxima
    de la pila (si está configurada).
    """
    def __init__(self, max_capacity):
        self.max_capacity = max_capacity
        super().__init__(f"La pila ha alcanzado su capacidad máxima de {max_capacity} elementos")


class Stack:
    """
    Implementación robusta de una pila (Stack) LIFO para registrar el historial 
    de mensajes recibidos. Utilizada principalmente para el historial de paquetes 
    recibidos en dispositivos de red.
    
    La pila mantiene un orden LIFO estricto donde:
    - Los elementos se agregan al tope (push)
    - Los elementos se remueven del tope (pop)
    - Solo se puede acceder al elemento del tope (peek)
    
    Attributes:
        _items: Lista interna que almacena los elementos de la pila
        _max_capacity: Capacidad máxima de la pila (None = ilimitada)
        _creation_count: Contador de elementos agregados durante la vida de la pila
    """
    
    def __init__(self, max_capacity=None):
        """
        Inicializa una nueva pila vacía.
        
        Args:
            max_capacity: Capacidad máxima de elementos. 
                        Si es None, la pila no tiene límite.
                        Debe ser un entero positivo si se especifica.
        
        Raises:
            ValueError: Si max_capacity no es un entero positivo válido
        """
        # Validar capacidad máxima si se proporciona
        if max_capacity is not None:
            if not isinstance(max_capacity, int) or max_capacity <= 0:
                raise ValueError("max_capacity debe ser un entero positivo")
        
        # Atributos privados (encapsulación)
        self._items = []
        self._max_capacity = max_capacity
        self._creation_count = 0  # Estadística útil para debugging
    
    def push(self, item):
        """
        Agrega un elemento al tope de la pila.
        
        Args:
            item: Elemento a agregar al tope de la pila. Puede ser de cualquier tipo.
        
        Raises:
            StackFullError: Si la pila ha alcanzado su capacidad máxima
            
        Example:
            >>> stack = Stack()
            >>> stack.push("primer elemento")
            >>> stack.push(42)
            >>> print(stack.size())
            2
        """
        # Verificar capacidad máxima
        if self._max_capacity is not None and len(self._items) >= self._max_capacity:
            raise StackFullError(self._max_capacity)
        
        # Agregar elemento al final de la lista (tope de la pila)
        self._items.append(item)
        self._creation_count += 1
    
    def pop(self):
        """
        Remueve y retorna el elemento del tope de la pila.
        
        Returns:
            El elemento que estaba en el tope de la pila
        
        Raises:
            StackEmptyError: Si la pila está vacía
            
        Example:
            >>> stack = Stack()
            >>> stack.push("elemento")
            >>> item = stack.pop()
            >>> print(item)
            "elemento"
        """
        if self.is_empty():
            raise StackEmptyError("pop")
        
        # Remover y retornar el último elemento (tope)
        return self._items.pop()
    
    def peek(self):
        """
        Retorna el elemento del tope de la pila sin removerlo.
        
        Permite inspeccionar el próximo elemento a ser removido sin
        modificar el estado de la pila.
        
        Returns:
            El elemento del tope de la pila
        
        Raises:
            StackEmptyError: Si la pila está vacía
            
        Example:
            >>> stack = Stack()
            >>> stack.push("elemento")
            >>> top = stack.peek()  # No modifica la pila
            >>> print(top)
            "elemento"
            >>> print(stack.size())  # Sigue siendo 1
            1
        """
        if self.is_empty():
            raise StackEmptyError("peek")
        
        # Retornar el último elemento sin removerlo
        return self._items[-1]
    
    def is_empty(self):
        """
        Verifica si la pila está vacía.
        
        Returns:
            bool: True si la pila no contiene elementos, False en caso contrario
            
        Example:
            >>> stack = Stack()
            >>> print(stack.is_empty())
            True
            >>> stack.push("elemento")
            >>> print(stack.is_empty())
            False
        """
        return len(self._items) == 0
    
    def size(self):
        """
        Retorna el número actual de elementos en la pila.
        
        Returns:
            int: Cantidad de elementos en la pila (0 o más)
            
        Example:
            >>> stack = Stack()
            >>> print(stack.size())
            0
            >>> stack.push("a")
            >>> stack.push("b") 
            >>> print(stack.size())
            2
        """
        return len(self._items)
    
    def clear(self):
        """
        Remueve todos los elementos de la pila, dejándola vacía.
        
        Útil para reinicializar la pila sin crear una nueva instancia.
        Mantiene la configuración de capacidad máxima.
        
        Example:
            >>> stack = Stack()
            >>> stack.push("a")
            >>> stack.push("b")
            >>> stack.clear()
            >>> print(stack.is_empty())
            True
        """
        self._items.clear()
    
    def get_capacity(self):
        """
        Retorna la capacidad máxima configurada para la pila.
        
        Returns:
            Capacidad máxima de la pila, o None si es ilimitada
        """
        return self._max_capacity
    
    def get_remaining_capacity(self):
        """
        Retorna la cantidad de elementos que aún se pueden agregar a la pila.
        
        Returns:
            Espacios disponibles, o None si la capacidad es ilimitada
        """
        if self._max_capacity is None:
            return None
        return self._max_capacity - len(self._items)
    
    def is_full(self):
        """
        Verifica si la pila ha alcanzado su capacidad máxima.
        
        Returns:
            bool: True si la pila está llena, False en caso contrario.
                 Si no hay límite de capacidad, siempre retorna False.
        """
        if self._max_capacity is None:
            return False
        return len(self._items) >= self._max_capacity
    
    def getAll(self):
        """
        Retorna una copia de todos los elementos en la pila manteniendo el orden LIFO.
        
        El primer elemento de la lista es el tope de la pila (último agregado).
        Esta operación no modifica la pila original.
        
        Returns:
            Lista con copia de todos los elementos, tope primero
            
        Example:
            >>> stack = Stack()
            >>> stack.push("primero")
            >>> stack.push("segundo") 
            >>> items = stack.getAll()
            >>> print(items)
            ["segundo", "primero"]  # Tope primero
        """
        # Retornar copia en orden inverso (tope primero)
        return self._items[::-1]
    
    def search(self, item):
        """
        Busca un elemento en la pila y retorna su posición desde el tope.
        
        Args:
            item: Elemento a buscar en la pila
        
        Returns:
            int: Posición del elemento desde el tope (0 = tope), o -1 si no se encuentra
            
        Example:
            >>> stack = Stack()
            >>> stack.push("a")
            >>> stack.push("b")
            >>> stack.push("c")
            >>> print(stack.search("c"))  # Está en el tope
            0
            >>> print(stack.search("a"))  # Está en el fondo
            2
            >>> print(stack.search("x"))  # No existe
            -1
        """
        try:
            # Buscar desde el final (tope) hacia el inicio
            index = len(self._items) - 1 - self._items[::-1].index(item)
            # Convertir a posición desde el tope
            return len(self._items) - 1 - index
        except ValueError:
            return -1
    
    def get_creation_count(self):
        """
        Retorna el número total de elementos que han sido agregados a la pila
        durante su existencia (incluyendo los que han sido removidos).
        
        Returns:
            int: Número total de elementos agregados históricamente
        """
        return self._creation_count
    
    # === MÉTODOS ESPECIALES (DUNDER METHODS) ===
    
    def __len__(self):
        """
        Permite usar len() con la pila.
        
        Returns:
            int: Número de elementos en la pila
            
        Example:
            >>> stack = Stack()
            >>> stack.push("elemento")
            >>> print(len(stack))
            1
        """
        return len(self._items)
    
    def __iter__(self):
        """
        Permite iterar sobre la pila desde el tope hacia abajo.
        
        Yields:
            Elementos de la pila, comenzando por el tope
            
        Example:
            >>> stack = Stack()
            >>> stack.push("a")
            >>> stack.push("b")
            >>> for item in stack:
            ...     print(item)
            b  # Tope primero
            a
        """
        # Iterar desde el tope (final de la lista) hacia abajo
        for item in reversed(self._items):
            yield item
    
    def __contains__(self, item):
        """
        Permite usar el operador 'in' para verificar si un elemento está en la pila.
        
        Args:
            item: Elemento a buscar
            
        Returns:
            bool: True si el elemento está en la pila, False en caso contrario
            
        Example:
            >>> stack = Stack()
            >>> stack.push("elemento")
            >>> print("elemento" in stack)
            True
            >>> print("otro" in stack)
            False
        """
        return item in self._items
    
    def __str__(self):
        """
        Representación en string de la pila para debugging y logging.
        
        Returns:
            str: Representación legible de la pila
            
        Example:
            >>> stack = Stack()
            >>> stack.push("a")
            >>> stack.push("b")
            >>> print(str(stack))
            Stack(size=2, top='b')
        """
        if self.is_empty():
            return "Stack(empty)"
        
        top_item = str(self._items[-1])
        if len(top_item) > 20:  # Truncar elementos muy largos
            top_item = top_item[:17] + "..."
        
        capacity_info = ""
        if self._max_capacity is not None:
            capacity_info = f", capacity={self._max_capacity}"
        
        return f"Stack(size={len(self._items)}, top='{top_item}'{capacity_info})"
    
    def __repr__(self):
        """
        Representación oficial de la pila para debugging avanzado.
        
        Returns:
            str: Representación que permite recrear el objeto
        """
        return f"Stack(max_capacity={self._max_capacity})"
    
    def __eq__(self, other):
        """
        Permite comparar dos pilas por igualdad.
        
        Args:
            other: Otra pila para comparar
            
        Returns:
            bool: True si ambas pilas contienen los mismos elementos en el mismo orden
        """
        if not isinstance(other, Stack):
            return False
        return self._items == other._items
    
    # === MÉTODOS DE UTILIDAD AVANZADA ===
    
    def copy(self):
        """
        Crea una copia superficial de la pila.
        
        Returns:
            Stack: Nueva pila con los mismos elementos y configuración
        """
        new_stack = Stack(self._max_capacity)
        new_stack._items = self._items.copy()
        new_stack._creation_count = self._creation_count
        return new_stack
    
    def to_list(self):
        """
        Convierte la pila a una lista manteniendo el orden interno.
        
        Returns:
            Lista con los elementos en el mismo orden que la estructura interna
        """
        return self._items.copy()
    
    def extend_from_iterable(self, iterable):
        """
        Agrega múltiples elementos desde un iterable.
        
        Args:
            iterable: Cualquier objeto iterable con elementos para agregar
            
        Raises:
            StackFullError: Si se excede la capacidad durante la operación
        """
        for item in iterable:
            self.push(item)  # Utilizará las validaciones de push
    
    def get_statistics(self):
        """
        Retorna estadísticas útiles sobre la pila.
        
        Returns:
            dict: Diccionario con estadísticas de la pila
        """
        stats = {
            "current_size": len(self._items),
            "max_capacity": self._max_capacity,
            "remaining_capacity": self.get_remaining_capacity(),
            "is_empty": self.is_empty(),
            "is_full": self.is_full(),
            "total_items_created": self._creation_count
        }
        
        # Calcular tasa de utilización si hay capacidad máxima
        if self._max_capacity is not None:
            stats["utilization_rate"] = (len(self._items) / self._max_capacity * 100)
        else:
            stats["utilization_rate"] = None
            
        return stats 