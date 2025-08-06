class Node:
    """Nodo para la lista enlazada"""
    
    def __init__(self, data):
        self.data = data
        self.next = None
    
    def __str__(self):
        return str(self.data)


class LinkedList:
    """
    Implementación de lista enlazada para almacenar vecinos de cada interfaz.
    Utilizada para mantener conexiones y relaciones entre interfaces.
    """
    
    def __init__(self):
        self.head = None
        self.size = 0
    
    def add_node(self, data):
        """
        Agrega un nuevo nodo al inicio de la lista enlazada
        
        Args:
            data: Datos a almacenar en el nodo (puede ser interfaz, dispositivo, etc.)
        
        Returns:
            bool: True si se agregó exitosamente
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
        return True
    
    def remove_node(self, data):
        """
        Remueve el primer nodo que contenga los datos especificados
        
        Args:
            data: Datos del nodo a remover
        
        Returns:
            bool: True si se removió exitosamente, False si no se encontró
        """
        if self.head is None:
            return False
        
        # Si el nodo a remover es el primero
        if self.head.data == data:
            self.head = self.head.next
            self.size -= 1
            return True
        
        # Buscar el nodo en el resto de la lista
        current = self.head
        while current.next is not None:
            if current.next.data == data:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        
        return False
    
    def traverse(self):
        """
        Recorre la lista enlazada y retorna todos los elementos
        
        Returns:
            list: Lista con todos los datos almacenados en orden
        """
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result
    
    def find(self, data):
        """
        Busca un elemento en la lista enlazada
        
        Args:
            data: Dato a buscar
        
        Returns:
            bool: True si se encuentra el elemento, False en caso contrario
        """
        current = self.head
        while current is not None:
            if current.data == data:
                return True
            current = current.next
        return False
    
    def is_empty(self):
        """
        Verifica si la lista enlazada está vacía
        
        Returns:
            bool: True si está vacía, False en caso contrario
        """
        return self.head is None
    
    def get_size(self):
        """
        Obtiene el tamaño actual de la lista enlazada
        
        Returns:
            int: Número de elementos en la lista
        """
        return self.size
    
    def clear(self):
        """
        Limpia todos los elementos de la lista enlazada
        """
        self.head = None
        self.size = 0
    
    def get_first(self):
        """
        Obtiene el primer elemento sin removerlo
        
        Returns:
            El dato del primer nodo o None si está vacía
        """
        if self.head is None:
            return None
        return self.head.data
    
    def get_last(self):
        """
        Obtiene el último elemento sin removerlo
        
        Returns:
            El dato del último nodo o None si está vacía
        """
        if self.head is None:
            return None
        
        current = self.head
        while current.next is not None:
            current = current.next
        return current.data
    
    def __str__(self):
        """Representación en string de la lista enlazada"""
        if self.is_empty():
            return "LinkedList(vacía)"
        
        elements = self.traverse()
        return f"LinkedList({self.size} elementos): {' -> '.join(map(str, elements))}"
    
    def __len__(self):
        """Permite usar len() en la lista enlazada"""
        return self.size
    
    def __iter__(self):
        """Permite iterar sobre la lista enlazada"""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next 