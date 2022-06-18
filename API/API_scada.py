
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
    
    valor_app_piezas = str
    valor_app_cajas = str
    if valores_mensaje[5] ==0:
        valor_app_piezas= ' '
    elif valores_mensaje[5] ==1:
        valor_app_piezas= 'Piston'
    elif valores_mensaje[5] ==2:
        valor_app_piezas= 'Biela'
    elif valores_mensaje[5] ==3:
        valor_app_piezas= 'Culata'
    elif valores_mensaje[5] ==4:
        valor_app_piezas= 'Cilindro' 
    

    if valores_mensaje[7] ==0:
        valor_app_cajas= ' '
    elif valores_mensaje[7] ==1:
        valor_app_cajas= 'Segmentos'
    elif valores_mensaje[7] ==2:
        valor_app_cajas= 'Rodamientos'
    elif valores_mensaje[7] ==3:
        valor_app_cajas= 'Tornillos'
    elif valores_mensaje[7] ==4:
        valor_app_cajas= 'Juntas'
    
    if len(mensaje_separado)==22: 
        mensaje_plc = dict(
            plc_run = valores_mensaje[0],
            emergencias = valores_mensaje[1],
            paro = valores_mensaje[2],
            marcha = valores_mensaje[3],
            piezas = valores_mensaje[4],
            app_piezas = valor_app_piezas,
            cajas = valores_mensaje[6],
            contenido_cajas = valor_app_cajas,
            pales = valores_mensaje[8],
            codigo = str(valores_mensaje[9])+str(valores_mensaje[10])+str(valores_mensaje[11])+str(valores_mensaje[12]),
            cond_reposo = valores_mensaje[13],
            pick_reposo = valores_mensaje[14],
            ftc_piezas = valores_mensaje[15],
            ftc_cajas = valores_mensaje[16],
            ftc_pales = valores_mensaje[17],
            cinta_piezas = valores_mensaje[18],
            cinta_cajas = valores_mensaje[19],
            cinta_pales = valores_mensaje[20],
            contaje = int(valores_mensaje[21]),
            fecha = fecha_actual()
        )


    print(f'Datos enviados del PLC a la BdD Envios: {mensaje_plc}')
    conexion.insertar_envios(mensaje_plc)
    seleccionar_envios(mensaje_plc)
    return 'Datos recibidos OK'

@api_scada.delete("/envios")
def delete_envios():
    conexion.eliminar_envios()
    return 'Eliminado completo Envios OK'

## ESTADOS ##
@api_scada.get("/estados")
def get_estados():
    list_estados = conexion.mostrar_estados()
    return list_estados
@api_scada.delete("/estados")
def delete_estados():
    conexion.eliminar_estados()
    return 'Eliminado completo Estados OK'

## MAQUINA ##
@api_scada.get("/maquina")
def get_maquina():
    list_maquina = conexion.mostrar_maquina()
    return list_maquina
@api_scada.delete("/maquina")
def delete_maquina():
    conexion.eliminar_maquina()
    return 'Eliminado completo Maquina OK'

## DATOS ##
@api_scada.get("/datos")
def get_datos():
    list_datos = conexion.mostrar_datos()
    return list_datos
@api_scada.delete("/datos")
def delete_datos():
    conexion.eliminar_datos()
    return 'Eliminado completo Datos OK'

## FUNCIONES ##

def bytes_to_str(bytes1):
    return bytes1.decode('utf-8')

## FECHA ACTUAL ##
def fecha_actual():
    ahora = datetime.now()
    formato = "%Y-%m-%d_%H:%M:%S"
    fecha_hora_actual = ahora.strftime(formato)
    return fecha_hora_actual

def seleccionar_envios(mensaje_plc):
    mensaje_estados = dict(
        estado_server = 1,
        estado_plc = mensaje_plc['plc_run'],
        fecha = fecha_actual(),
    )
    conexion.insertar_estados(mensaje_estados)
    list_id = []
    list_all_envios = conexion.mostrar_envios()
    for i in range(0,len(list_all_envios)):
        dict_all_envios_id = list_all_envios[i]
        n_id = dict_all_envios_id['id']
        list_id.append(n_id)
    n_id_max = max(list_id)
    for i in range(0,len(list_all_envios)):
        dict_all_envios_id_max = list_all_envios[i]
        if dict_all_envios_id_max['id']==n_id_max:
            if dict_all_envios_id_max['plc_run']==1:
                mensaje_maquina = dict(
                    plc_run = dict_all_envios_id_max['plc_run'],
                    emergencias = dict_all_envios_id_max['emergencias'],
                    paro = dict_all_envios_id_max['paro'],
                    marcha = dict_all_envios_id_max['marcha'],
                    cond_reposo = dict_all_envios_id_max['cond_reposo'],
                    pick_reposo = dict_all_envios_id_max['pick_reposo'],
                    ftc_piezas = dict_all_envios_id_max['ftc_piezas'],
                    ftc_cajas = dict_all_envios_id_max['ftc_cajas'],
                    ftc_pales = dict_all_envios_id_max['ftc_pales'],
                    cinta_piezas = dict_all_envios_id_max['cinta_piezas'],
                    cinta_cajas = dict_all_envios_id_max['cinta_piezas'],
                    cinta_pales = dict_all_envios_id_max['cinta_pales'],
                    contaje = dict_all_envios_id_max['contaje'],
                    fecha = dict_all_envios_id_max['fecha'],
                )
                conexion.insertar_maquina(mensaje_maquina)
                seleccionar_maquina(mensaje_maquina,mensaje_plc)

def seleccionar_maquina(mensaje_maquina,mensaje_plc):
    
    if mensaje_maquina['contaje']==1:
        mensaje_datos = dict(
            piezas = mensaje_plc['piezas'],
            app_piezas = mensaje_plc['app_piezas'],
            cajas = mensaje_plc['cajas'],
            contenido_cajas = mensaje_plc['contenido_cajas'],
            pales = mensaje_plc['pales'],
            codigo = mensaje_plc['codigo'],
            contaje = mensaje_plc['contaje'],
            fecha = mensaje_plc['fecha'],
        )
        conexion.insertar_datos(mensaje_datos)                 
                            
    
if __name__ == '__main__':
    uvicorn.run(api_scada, host="0.0.0.0", port=8000)
    
    

     
