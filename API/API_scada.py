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
from fastapi import FastAPI, Request
from pydantic import BaseModel  
from datetime import datetime
from threading import Thread
from time import sleep
import uvicorn
from API_gestor_datos import Conexion
import asyncio
import codecs

class Datos(BaseModel):         
    envio: bytes






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
async def post_envios(requests: Request):
    mensaje_bytes = await requests.body()
    print(type(mensaje_bytes))
    mensaje = codecs.decode(mensaje_bytes, encoding='utf-8', errors='strict')
    dict_datos = dict(
        envio = mensaje,
    )
    print(dict_datos)
    conexion.insertar_envios(dict_datos)
    return 'Datos recibidos OK'
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
    

     
