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
    respuesta_server: bool

    def run(self):
        
        while True:
            
            try:
                all_datos = requests.get(f'{self.ip_api}datos',timeout=4)
            except (requests.exceptions.ConnectionError):
                print('Server INACTIVO...Conectando')
                self.respuesta_server=False
                list_all_datos=[]
                server = False
                self.refresh.emit(list_all_datos,server)
                continue
            if all_datos.status_code == 200:  
                self.respuesta_server = True
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
                list_all_datos= []
                
   


class gui_api_scada(QMainWindow):
    ip_api= 'http://localhost:8000/'
    
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
        self.table.setColumnCount(6)
        self.table.setRowCount(50)
        self.table.setHorizontalHeaderLabels(['Codigo','Piezas','Funcion','Cajas','Contenido','Pales'])
        self.table.horizontalHeader().setSectionResizeMode(80)
        
        ## BOTON BORRAR BdD ##
        self.boton_borrar_base_datos.clicked.connect(self.Borrar_base_datos)


        ## VARIABLES AUXILIARES ##
        
        self.n_piezas_total = int
        self.n_cajas_total = int
        self.n_pales_total = int
        self.estado_marcha = int
        self.contaje_aux = bool
        self.long_list_envios = 0

    ## BORAR BASE DE DATOS ##
    def Borrar_base_datos(self):
        try:
            borar_base_envios = requests.delete(f'{self.ip_api}envios',timeout=4)
            borar_base_estados = requests.delete(f'{self.ip_api}estados',timeout=4)
            borrar_base_maquina = requests.delete(f'{self.ip_api}maquina',timeout=4)
            borrar_base_datos = requests.delete(f'{self.ip_api}datos',timeout=4)
            inv_codigo =  [' ']
            inv_piezas = [' ']
            inv_cajas = [' ']
            inv_pales = [' ']
            inv_app_piezas = [' ']
            inv_contenido_cajas = [' ']
                
            inv_datos = dict(
                Inv_Codigo = inv_codigo,
                Inv_Piezas = inv_piezas,
                Inv_app_piezas = inv_app_piezas,
                Inv_Cajas = inv_cajas,
                Inv_contenido_cajas = inv_contenido_cajas,
                Inv_Pales = inv_pales,
            )
            #print(f'Datos para mostrar: {inv_datos}')
            self.table.clear()
            self.table.setHorizontalHeaderLabels(['Codigo','Piezas','Funcion','Cajas','Contenido','Pales'])
            for n, key in enumerate(inv_datos.keys()):
                for m, item in enumerate(inv_datos[key]):
                    self.table.setItem(m,n,QTableWidgetItem(str(item)))
            self.table.verticalHeader().setDefaultSectionSize(80)
        except(requests.exceptions.ConnectionError):
            print('Server INACTIVO ...')
            server = False
            self.estado_server.setText('INACTIVO')
            self.estado_server.setStyleSheet("color: red")
            self.estado_plc.setText('SIN CONEXION')
            self.estado_plc.setStyleSheet("color: white")
            self.estado_maquina.setText('SIN CONEXION')
            self.estado_maquina.setStyleSheet("color: white")
        

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
            self.estado_plc.setText('SIN CONEXION')
            self.estado_maquina.setText('SIN CONEXION')
        else:    
            self.estado_server.setText('ACTIVO')
            self.estado_server.setStyleSheet("color: green")
            #print(f'BdD Envios: {list_all_datos}')      
            

            dict_all_datos_id_max = {}
            if len(list_all_datos)>0:
                
                list_id = []
                for i in range(0,len(list_all_datos)):
                    dict_all_datos_id = list_all_datos[i]
                    n_id = dict_all_datos_id['id']
                    list_id.append(n_id)
                n_id_max = max(list_id)
                for i in range(0,len(list_all_datos)):
                    dict_all_datos_id_max = list_all_datos[i]
                    if dict_all_datos_id_max['id']==n_id_max:
                            
                            
                            if dict_all_datos_id_max['paro']==1:
                                self.estado_maquina.setText('PARO')
                                self.estado_maquina.setStyleSheet("color: red")
                            
                            elif dict_all_datos_id_max['emergencias']==1:
                                self.estado_maquina.setText('EMERGENCIA')
                                self.estado_maquina.setStyleSheet("color: red")
                            
                            elif dict_all_datos_id_max['marcha']==1:
                                self.estado_maquina.setText('MARCHA')
                                self.estado_maquina.setStyleSheet("color: green")
                            
                            n_piezas_id_max = dict_all_datos_id_max['piezas']
                            n_cajas_id_max = dict_all_datos_id_max['cajas']
                            n_pales_id_max = dict_all_datos_id_max['pales']
                            self.n_piezas_total = (n_piezas_id_max) + (4 * (n_pales_id_max-1))
                            self.n_cajas_total = (n_cajas_id_max) + (4 * (n_pales_id_max-1))
                            if dict_all_datos_id_max['paro']==0:
                                self.n_pales_total = n_pales_id_max -1
                                self.out_n_pales.setText(str(self.n_pales_total))
                            elif dict_all_datos_id_max['paro']==1 and dict_all_datos_id_max['cinta_pales']==1:
                                self.n_pales_total = n_pales_id_max
                                self.out_n_pales.setText(str(self.n_pales_total))
                            self.out_n_piezas.setText(str(self.n_piezas_total))
                            self.out_n_cajas.setText(str(self.n_cajas_total))

                            if dict_all_datos_id_max['cond_reposo']==1:
                                self.out_cond_reposo.setText('Activas')
                            else:
                                self.out_cond_reposo.setText('Inactivas')
                            
                            if dict_all_datos_id_max['pick_reposo']==1:
                                self.out_pick_reposo.setText('En reposo')
                            else:
                                self.out_pick_reposo.setText('Operando...')
                
                
                inv_codigo =  []
                inv_piezas = []
                inv_cajas = []
                inv_pales = []
                inv_app_piezas = []
                inv_contenido_cajas = []

                for v in range(0,len(list_all_datos)):
                    dict_all_datos = list_all_datos[v]
                    valor_codigo = dict_all_datos['codigo']
                    valor_piezas = dict_all_datos['piezas']
                    valor_app_piezas = dict_all_datos['app_piezas']
                    valor_cajas = dict_all_datos['cajas']
                    valor_contenido_cajas = dict_all_datos['contenido_cajas']
                    valor_pales = dict_all_datos['pales']

                    inv_codigo.append(valor_codigo)
                    inv_piezas.append(valor_piezas)
                    inv_app_piezas.append(valor_app_piezas)
                    inv_cajas.append(valor_cajas)
                    inv_contenido_cajas.append(valor_contenido_cajas)
                    inv_pales.append(valor_pales)
                
                inv_datos = dict(
                    Inv_Codigo = inv_codigo,
                    Inv_Piezas = inv_piezas,
                    Inv_app_piezas = inv_app_piezas,
                    Inv_Cajas = inv_cajas,
                    Inv_contenido_cajas = inv_contenido_cajas,
                    Inv_Pales = inv_pales,
                )
                #print(f'Datos para mostrar: {inv_datos}')
                self.table.clear()
                self.table.setHorizontalHeaderLabels(['Codigo','Piezas','Funcion','Cajas','Contenido','Pales'])
                for n, key in enumerate(inv_datos.keys()):
                    for m, item in enumerate(inv_datos[key]):
                        self.table.setItem(m,n,QTableWidgetItem(str(item)))
                self.table.verticalHeader().setDefaultSectionSize(80)

            else:
                try:
                    all_envios = requests.get(f'{self.ip_api}envios',timeout=4)
                except(requests.exceptions.ConnectionError):
                    print('Server INACTIVO ...')
                    server = False
                    self.estado_server.setText('INACTIVO')
                    self.estado_server.setStyleSheet("color: red")
                    self.estado_plc.setText('SIN CONEXION')
                    self.estado_plc.setStyleSheet("color: white")
                    self.estado_maquina.setText('SIN CONEXION')
                    self.estado_maquina.setStyleSheet("color: white")
                
                    
                
                if server == True:
                    json_all_envios = all_envios.json()
                    list_all_envios = [dict(id_item) for id_item in json_all_envios]
                    list_id_envios = []
                    if len(list_all_envios)>1:
                        for i in range(0,len(list_all_envios)):
                            dict_all_envios_id = list_all_envios[i]
                            n_id_envios = dict_all_envios_id['id']
                            list_id_envios.append(n_id_envios)
                        n_id_max_envios = max(list_id_envios)
                        print(f'Longitud Lista Envios: {len(list_id_envios)}')
                        for i in range(0,len(list_all_envios)):
                            dict_all_envios=list_all_envios[i]

                            if dict_all_envios['id']==n_id_max_envios:  
                                
                                if ((len(list_all_envios)) > (self.long_list_envios)) and self.long_list_envios != 0:   
                                    if dict_all_envios['emergencias']==1:
                                        self.estado_maquina.setText('EMERGENCIA')
                                        self.estado_maquina.setStyleSheet("color: red")
                                    elif dict_all_envios['emergencias']==0 and dict_all_envios['marcha']==0 and dict_all_envios['paro']==0:
                                        self.estado_maquina.setText('OPERATIVA STANDBY')
                                        self.estado_maquina.setStyleSheet("color: green")
                                    elif dict_all_envios['paro']==1:
                                        self.estado_maquina.setText('PARO')
                                        self.estado_maquina.setStyleSheet("color: red")
                                    
                                    elif dict_all_envios['marcha']==1:
                                        self.estado_maquina.setText('MARCHA')
                                        self.estado_maquina.setStyleSheet("color: green")
                                
                                    if dict_all_envios['cond_reposo']==1:
                                        self.out_cond_reposo.setText('Activas')
                                    else:
                                        self.out_cond_reposo.setText('Inactivas')
                                            
                                    if dict_all_envios['pick_reposo']==1:
                                        self.out_pick_reposo.setText('En reposo')
                                    else:
                                        self.out_pick_reposo.setText('Operando...')

                        if ((len(list_all_envios)) > (self.long_list_envios)) and self.long_list_envios != 0:
                                self.estado_plc.setText('RUN')
                                self.estado_plc.setStyleSheet("color: green")

                        else:
                                self.estado_plc.setText('STOP')
                                self.estado_plc.setStyleSheet("color: red")
                                self.estado_maquina.setText('-----')
                                self.estado_maquina.setStyleSheet("color: white")
                                self.out_cond_reposo.setText('-----')
                                self.out_pick_reposo.setText('-----')
                                
                        print(f'Longitud de lista Envios guardada para saber RUN: {self.long_list_envios}')
                        self.long_list_envios = len(list_all_envios)
                        
                    else:
                        self.estado_plc.setText('STOP')
                        self.estado_plc.setStyleSheet("color: red")
                        self.estado_maquina.setText('-----')
                        self.estado_maquina.setStyleSheet("color: white")
                    

                               
                            


            
                
                
                        

            
        

        


def run_gui():
    app = QApplication(sys.argv)
    GUI = gui_api_scada()
    GUI.show()
    sys.exit(app.exec_()) 

if __name__ == '__main__':
    run_gui()
    