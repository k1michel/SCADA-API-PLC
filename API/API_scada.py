import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem,QHeaderView
from PyQt5.QtGui import QIcon, QPixmap
import requests
import json
from time import sleep
from datetime import datetime
from ObjectListView import ObjectListView, ColumnDefn
from typing import Optional   
from fastapi import FastAPI
from pydantic import BaseModel  
from datetime import datetime
from threading import Thread
from time import sleep
import uvicorn
from API_gestor_datos import Conexion

class Datos(BaseModel):         
    n_piezas: str                     
    n_cajas: str  
    






class gui_api_scada(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("API_GUI.ui",self)
        ## LOGO ##
        #pixmap = QPixmap('Letras_gestor_almacen_2.png')
        #self.img_letras_logo.setPixmap(pixmap)
        ## FONDO ##
        #pixmap = QPixmap('Fondo_gestor_almacen.png')
        #self.img_fondo.setPixmap(pixmap)

## CREACION API ##
api_scada = FastAPI() 
conexion = Conexion()


## ENVIOS ##
@api_scada.get("/envios")
def get_envios():
    list_envio = conexion.mostrar_envios()
    return list_envio

@api_scada.post("/envios")
def post_envios(datos : Datos):
    
    dic_datos= dict(
        n_piezas=datos.n_piezas,
        n_cajas=datos.n_cajas,
    )
    conexion.insertar_envios(dic_datos)
    return 'Datos recibidos en Envios OK'
@api_scada.delete("/envios")
def delete_envios():
    conexion.eliminar_envios()
    return 'Eliminado completo Envios OK'

def run_server():
    uvicorn.run(api_scada, host="0.0.0.0", port=8000)
def run_gui():
    app = QApplication(sys.argv)
    GUI = gui_api_scada()
    GUI.show()
    sys.exit(app.exec_()) 

if __name__ == '__main__':
    chequeo = Thread(target=run_server, daemon=True)
    chequeo.start()
    run_gui()
    

     
