class Node:
    """
    Nodo para estructuras de datos enlazadas.
    
    Esta clase representa un nodo básico que puede ser utilizado en listas enlazadas,
    árboles, grafos y otras estructuras de datos que requieren nodos con referencias.
    
    Attributes:
        data: Los datos almacenados en el nodo
        next: Referencia al siguiente nodo (None si es el último)
    """
    
    def __init__(self, data):
        """
        Inicializa un nuevo nodo con los datos especificados.
        
        Args:
            data: Los datos a almacenar en el nodo
        """
        self.data = data
        self.next = None
    
    def __str__(self):
        """
        Retorna una representación en string del nodo.
        
        Returns:
            str: Representación en string de los datos del nodo
        """
        return str(self.data)
    
    def __repr__(self):
        """
        Retorna una representación oficial del nodo para debugging.
        
        Returns:
            str: Representación que permite recrear el objeto
        """
        return f"Node(data={repr(self.data)})" 