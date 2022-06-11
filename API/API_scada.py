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

class Envio_PLC(BaseModel):         
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

def bytes_to_str(bytes1):
    return bytes1.decode('utf-8')

@api_scada.post("/envios")
async def post_envios(requests: Request):
    mensaje_bytes = await requests.body()
    print(f'Mensaje PLC original: {mensaje_bytes}, tipo:{type(mensaje_bytes)}')
    mensaje_str = bytes_to_str(mensaje_bytes)
    mensaje_separado = list(mensaje_str)
    n_piezas = int.from_bytes(mensaje_separado[0].encode('ascii'), byteorder='little')
    n_cajas = int.from_bytes(mensaje_separado[1].encode('ascii'), byteorder='little')
    n_pales = int.from_bytes(mensaje_separado[2].encode('ascii'), byteorder='little')
    n_marcha = int.from_bytes(mensaje_separado[3].encode('ascii'), byteorder='little')
    mensaje_plc = dict(
        piezas = n_piezas,
        cajas = n_cajas,
        pales = n_pales,
        marcha = n_marcha,
    )
    print(f'Datos enviados del PLC a la BdD Envios: {mensaje_plc}')
    conexion.insertar_envios(mensaje_plc)
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
    

     
