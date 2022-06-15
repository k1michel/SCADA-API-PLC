import dataset

class Conexion:
    fichero_sqlite: str = 'base_datos.db' 
    inventario = None
    envios = None
    

    def __init__(self):

        self.db = dataset.connect(
            f'sqlite:///{Conexion.fichero_sqlite}?check_same_thread=False')  
        self.envios = self.db['envios']
        self.estados = self.db['estados']
        self.maquina = self.db['maquina']
        self.datos = self.db['datos']    
    

    ### ENVIOS ###

    def insertar_envios(self,mensaje_plc):
        return self.envios.insert(mensaje_plc)

    def mostrar_envios(self):
        return [dict(envios) for envios in self.envios.all()]
    
    def eliminar_envios(self):
        self.envios.delete()
        return

    ### ESTADOS ###
    def insertar_estados(self,mensaje_estados):
        return self.estados.insert(mensaje_estados)

    def mostrar_estados(self):
        return [dict(estados) for estados in self.estados.all()]
    
    def eliminar_estados(self):
        self.estados.delete()
        return


    ### MAQUINA ###
    def insertar_maquina(self,mensaje_maquina):
        return self.maquina.insert(mensaje_maquina)

    def mostrar_maquina(self):
        return [dict(maquina) for maquina in self.maquina.all()]
    
    def eliminar_maquina(self):
        self.maquina.delete()
        return

    ### DATOS ###
    def insertar_datos(self,mensaje_datos):
        return self.datos.insert(mensaje_datos)

    def mostrar_datos(self):
        return [dict(datos) for datos in self.datos.all()]
    
    def eliminar_datos(self):
        self.datos.delete()
        return