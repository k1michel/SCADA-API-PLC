import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidget, QTableWidgetItem,QHeaderView
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QThread , pyqtSignal, QDateTime , QObject
import requests
import json
from time import sleep
from datetime import datetime
import subprocess
from threading import Thread

class BackendThread(QObject):
    refresh = pyqtSignal(list,bool)
    ip_api= 'http://localhost:8000/'
    list_all_envios: list
    respuesta_server:bool

    def run(self):
        
        while True:
            
            
            all_datos = requests.get(f'{self.ip_api}datos',timeout=4)
            if all_datos.status_code==200:  
                self.respuesta_server= True
                print(f'Server {self.ip_api} ACTIVO')
                sleep(1)
            else:
                self.respuesta_server=False
                print(f'Server {self.ip_api} INACTIVO')
                sleep(1)
                
        
            if self.respuesta_server==True:
                server = True
                json_all_datos = all_datos.json()
                list_all_datos = [dict(id_item) for id_item in json_all_datos]
                self.refresh.emit(list_all_datos,server)
                self.respuesta_server=False
            else:
                info_server = 'server_inactivo'
                server = False
                list_all_datos.append(info_server)
                self.refresh.emit(list_all_datos,server)
                print(list_all_datos)
                list_all_datos= []
                print(list_all_datos)

            
            
            
            
            


class gui_api_scada(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi("API_GUI.ui",self)
        ## LOGO ##
        pixmap = QPixmap('Logo_scada_api_plc.png')
        self.logo.setPixmap(pixmap)
        ## FONDO ##
        pixmap = QPixmap('Fondo_API_scada.png')
        self.img_fondo.setPixmap(pixmap)
        
        
        ## THREAD ## 
        self.backend = BackendThread() 
        self.backend.refresh.connect(self.visualizar_tabla)
        self.thread = QThread()
        self.backend.moveToThread(self.thread)
        self.thread.started.connect(self.backend.run)
        self.thread.start()
        

        ## TABLA ##    
        self.table.setColumnCount(4)
        self.table.setRowCount(50)
        self.table.setHorizontalHeaderLabels(['Codigo','Piezas','Cajas','Pales'])
        self.table.horizontalHeader().setSectionResizeMode(80)
        

        ## VARIABLES AUXILIARES ##
        
        self.n_piezas_total = int
        self.n_cajas_total = int
        self.n_pales_total = int
        self.estado_marcha = int
        self.contaje_aux = bool
        

    ## FECHA ACTUAL ##
    def fecha_actual(self):
        ahora = datetime.now()
        formato = "%d-%m-%Y_%H:%M"
        fecha_hora_actual = ahora.strftime(formato)
        return fecha_hora_actual
        
    ## ENVIAR A TABLA ##
    def visualizar_tabla(self,list_all_datos,server):
        fecha_recibida = self.fecha_actual()
        self.out_fecha.setText(fecha_recibida)
        
        if ((len(list_all_datos)==0) or (list_all_datos==None))and server==False:
            self.estado_server.setText('INACTIVO')
            self.estado_server.setStyleSheet("color: red")
            self.estado_plc.setText('STOP')
            self.estado_maquina.setText('PLC INACTIVO')
        else:    
            self.estado_server.setText('ACTIVO')
            self.estado_server.setStyleSheet("color: green")
            print(f'BdD Envios: {list_all_datos}')
            
            
            inv_codigo =  []
            inv_piezas = []
            inv_cajas = []
            inv_pales = []
                
            for i in range(0,len(list_all_datos)):
                dict_json_all_datos = list_all_datos[i]

                valor_codigo = dict_json_all_datos['codigo']
                valor_piezas = dict_json_all_datos['piezas']
                valor_cajas = dict_json_all_datos['cajas']
                valor_pales = dict_json_all_datos['pales']

                inv_codigo.append(valor_codigo)
                inv_piezas.append(valor_piezas)
                inv_cajas.append(valor_cajas)
                inv_pales.append(valor_pales)

            inventario = dict(
                Inv_Codigo = inv_codigo,
                Inv_Piezas = inv_piezas,
                Inv_Cajas = inv_cajas,
                Inv_Pales = inv_pales,
            )
            print(f'Inventario para mostrar: {inventario}')
            self.table.clear()
            self.table.setHorizontalHeaderLabels(['Codigo','Piezas','Cajas','Pales'])
            for n, key in enumerate(inventario.keys()):
                for m, item in enumerate(inventario[key]):
                    self.table.setItem(m,n,QTableWidgetItem(str(item)))
            self.table.verticalHeader().setDefaultSectionSize(80)
            

            dict_all_datos_id_max = {}
            if len(list_all_datos)>0:
                self.estado_plc.setText('RUN')
                self.estado_plc.setStyleSheet("color: green")
                list_id = []
                for i in range(0,len(list_all_datos)):
                    dict_all_datos_id = list_all_datos[i]
                    n_id = dict_all_datos_id['id']
                    list_id.append(n_id)
                n_id_max = max(list_id)
                for i in range(0,len(list_all_datos)):
                    dict_all_datos_id_max = list_all_datos[i]
                    if dict_all_datos_id_max['id']==n_id_max:
                            
                            if dict_all_datos_id_max['emergencias']==1:
                                self.estado_maquina.setText('EMERGENCIA')
                                self.estado_maquina.setStyleSheet("color: red")
                            elif dict_all_datos_id_max['paro']==1:
                                self.estado_maquina.setText('PARO')
                                self.estado_maquina.setStyleSheet("color: red")
                            
                            elif dict_all_datos_id_max['marcha']==1:
                                self.estado_maquina.setText('MARCHA')
                                self.estado_maquina.setStyleSheet("color: green")
                                if dict_all_datos_id_max['contaje']==1:
                                    n_piezas_id_max = dict_all_datos_id_max['piezas']
                                    n_cajas_id_max = dict_all_datos_id_max['cajas']
                                    n_pales_id_max = dict_all_datos_id_max['pales']
                                    self.n_piezas_total = (n_piezas_id_max) + (4 * (n_pales_id_max-1))
                                    self.n_cajas_total = (n_cajas_id_max) + (4 * (n_pales_id_max-1))
                                    self.n_pales_total = n_pales_id_max -1
                                    self.out_n_piezas.setText(str(self.n_piezas_total))
                                    self.out_n_cajas.setText(str(self.n_cajas_total))
                                    self.out_n_pales.setText(str(self.n_pales_total))
                            
                            if dict_all_datos_id_max['cond_reposo']==1:
                                self.out_cond_reposo.setText('Maquina en reposo')
                            else:
                                self.out_cond_reposo.setText('Maquina funcionando')
                            
                            if dict_all_datos_id_max['pick_reposo']==1:
                                self.out_pick_reposo.setText('Pick en reposo')
                            else:
                                self.out_pick_reposo.setText('Pick funcionando')


            
                
                
                        

            
        

        


def run_gui():
    app = QApplication(sys.argv)
    GUI = gui_api_scada()
    GUI.show()
    sys.exit(app.exec_()) 

if __name__ == '__main__':
    run_gui()
    