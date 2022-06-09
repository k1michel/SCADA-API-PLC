import dataset

class Conexion:
    fichero_sqlite: str = 'base_datos.db' 
    inventario = None
    envios = None
    

    def __init__(self):

        self.db = dataset.connect(
            f'sqlite:///{Conexion.fichero_sqlite}?check_same_thread=False')  
        self.envios = self.db['envios']
        self.inventario = self.db['inventario']
    
    

    ### PEDIDO MARCHANDO ###

    def insertar_envios(self,dict_datos):
        return self.envios.insert(dict_datos)

    def mostrar_envios(self):
        return [dict(datos) for datos in self.envios.all()]
    
    def eliminar_envios(self):
        self.envios.delete()
        return
