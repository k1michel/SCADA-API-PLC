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
    refresh = pyqtSignal(list)
    ip_api= 'http://localhost:8000/'
    list_all_envios: list
    respuesta_server:bool

    def run(self):
        
        while True:
            
            try:
                all_envios = requests.get(f'{self.ip_api}envios',timeout=4)
                self.respuesta_server= True
                print(f'Server {self.ip_api} ACTIVO')
            except (requests.exceptions.ConnectTimeout,requests.exceptions.ReadTimeout):
                self.respuesta_server=False
                print(f'Server {self.ip_api} INACTIVO')
                sleep(1)
                
        
            if self.respuesta_server==True:
                json_all_envios = all_envios.json()
                list_all_envios = [dict(id_item) for id_item in json_all_envios]
                self.refresh.emit(list_all_envios)
            else:
                info_server = 'server_inactivo'
                list_all_envios.append(info_server)
                self.refresh.emit(list_all_envios)
                print(list_all_envios)
                list_all_envios= []
                print(list_all_envios)

            
            
            
            
            


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

    ## FECHA ACTUAL ##
    def fecha_actual(self):
        ahora = datetime.now()
        formato = "%Y-%m-%d_%H:%M:%S"
        fecha_hora_actual = ahora.strftime(formato)
        return fecha_hora_actual
        
    ## ENVIAR A TABLA ##
    def visualizar_tabla(self,list_all_envios):
        if list_all_envios[0]=='server_inactivo':
            self.estado_server.setText('INACTIVO')
            self.estado_server.setStyleSheet("color: red")
        else:    
            self.estado_server.setText('ACTIVO')
            self.estado_server.setStyleSheet("color: green")
            print(f'BdD Envios: {list_all_envios}')
            inv_codigo =  []
            inv_piezas = []
            inv_cajas = []
            inv_pales = []
                
            for i in range(0,len(list_all_envios)):
                dict_json_all_envio = list_all_envios[i]
                valor_codigo = dict_json_all_envio['codigo']
                valor_piezas = dict_json_all_envio['piezas']
                valor_cajas = dict_json_all_envio['cajas']
                valor_pales = dict_json_all_envio['pales']

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
            list_id = []
            for i in range(0,len(list_all_envios)):
                dict_json_all_envios_id = list_all_envios[i]
                n_id = dict_json_all_envios_id['id']
                list_id.append(n_id)
            n_id_max = max(list_id)
            for i in range(0,len(list_all_envios)):
                dict_json_all_envios_id_max = list_all_envios[i]
                if dict_json_all_envios_id_max['id']==n_id_max:
                    n_piezas_id_max = dict_json_all_envios_id_max['piezas']
                    n_cajas_id_max = dict_json_all_envios_id_max['cajas']
                    n_pales_id_max = dict_json_all_envios_id_max['pales']
                    estado_marcha = dict_json_all_envios_id_max['marcha']
            
            self.n_piezas_total = (n_piezas_id_max) + (4 * (n_pales_id_max-1))
            self.n_cajas_total = (n_cajas_id_max) + (4 * (n_pales_id_max-1))
            self.n_pales_total = n_pales_id_max - 1
            self.in_n_piezas.setText(str(self.n_piezas_total))
            self.in_n_cajas.setText(str(self.n_cajas_total))
            self.in_n_pales.setText(str(self.n_pales_total))
            if estado_marcha==1:
                self.estado_maquina.setText('MARCHA')
                self.estado_maquina.setStyleSheet("color: green")
            else:
                self.estado_maquina.setText('PARO')
                self.estado_maquina.setStyleSheet("color: orange")
        

        


def run_gui():
    app = QApplication(sys.argv)
    GUI = gui_api_scada()
    GUI.show()
    sys.exit(app.exec_()) 

if __name__ == '__main__':
    run_gui()
    