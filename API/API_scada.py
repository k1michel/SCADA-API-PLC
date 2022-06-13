
import requests
import json
from time import sleep
from datetime import datetime
from typing import Optional   
from fastapi import FastAPI, Request
from pydantic import BaseModel  
from datetime import datetime
from threading import Thread
import uvicorn
from API_gestor_datos import Conexion
import asyncio
import codecs

## CLASE PARA RECIBIR DATOS PLC ##
class Envio_PLC(BaseModel):         
    envio: bytes
## CLASE CREACION GUI (INTERFAZ GRAFICA EN PYQT5) ##



    
## CREACION API ##
api_scada = FastAPI() 

## HEREDAR CLASE DE LA BASE DE DATOS (BdD) ##
conexion = Conexion()

## VARIABLES ##
mensaje_plc = dict
codigo_inicial = 56489712    
## ENVIOS ##
@api_scada.get("/envios")
def get_envios():
    list_envio = conexion.mostrar_envios()
    return list_envio

@api_scada.post("/envios")
async def post_envios(requests: Request):
    mensaje_bytes = await requests.body()
    print(f'Mensaje PLC original: {mensaje_bytes}, tipo:{type(mensaje_bytes)}')
    mensaje_str = bytes_to_str(mensaje_bytes)
    mensaje_separado = list(mensaje_str)
    print(mensaje_separado)
    valores_mensaje = []
    for i in range(0,len(mensaje_separado)):
        if mensaje_separado[i] != 'p':
            valores_mensaje.append(int.from_bytes(mensaje_separado[i].encode('ascii'), byteorder='little'))
        else:
            valores_mensaje.append(0)    
    
    if len(mensaje_separado)==4: 
        mensaje_plc = dict(
            codigo = codigo_inicial,
            piezas = valores_mensaje[0],
            cajas = valores_mensaje[1],
            pales = valores_mensaje[2],
            marcha = valores_mensaje[3],
        )


    print(f'Datos enviados del PLC a la BdD Envios: {mensaje_plc}')
    conexion.insertar_envios(mensaje_plc)
    return 'Datos recibidos OK'

@api_scada.delete("/envios")
def delete_envios():
    conexion.eliminar_envios()
    return 'Eliminado completo Envios OK'


## FUNCIONES ##

def bytes_to_str(bytes1):
    return bytes1.decode('utf-8')

## FECHA ACTUAL ##
def fecha_actual():
    ahora = datetime.now()
    formato = "%Y-%m-%d_%H:%M:%S"
    fecha_hora_actual = ahora.strftime(formato)
    return fecha_hora_actual


    
if __name__ == '__main__':
    uvicorn.run(api_scada, host="0.0.0.0", port=8000)
    
    

     
