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
    server: bool

    def run(self):
        
        while True:
            
            try:
                all_datos = requests.get(f'{self.ip_api}datos',timeout=4)
                server = True
            except (requests.exceptions.ConnectionError):
                print('Server INACTIVO...Conectando...')
                list_all_datos=[]
                server = False
                self.refresh.emit(list_all_datos,server)
                continue
                
            if server==True:
                server = True
                json_all_datos = all_datos.json()
                list_all_datos = [dict(id_item) for id_item in json_all_datos]
                self.refresh.emit(list_all_datos,server)
                self.respuesta_server=False
                sleep(1)
            else:
                info_server = ' '
                server = False
                list_all_datos.append(info_server)
                self.refresh.emit(list_all_datos,server)
                list_all_datos= []
                sleep(1)
                
   


class gui_api_scada(QMainWindow):
    ip_api= 'http://localhost:8000/'
    
    def __init__(self):
        super().__init__()
        uic.loadUi("API_GUI.ui",self)
        
        ## NOMBRE VENTANA ##
        self.setWindowTitle('SCADA PAPETIZADOR')
        
        ## LOGO ##
        pixmap1 = QPixmap('Letras_paletizador_motores.png')
        self.logo.setPixmap(pixmap1)
        ## FONDO ##
        pixmap2 = QPixmap('Fondo_API_scada.png')
        self.img_fondo.setPixmap(pixmap2)
        ## MAQUINA ##
        pixmap3 = QPixmap('Maquina_Paletizador_motores.png')
        self.img_maquina.setPixmap(pixmap3)
        
        ## THREAD ## 
        self.backend = BackendThread() 
        self.backend.refresh.connect(self.visualizar)
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
        self.long_list_maquina = 0
        self.primer_ciclo = False
        self.ver_envios = False
        self.ver_maquina = False
        self.paro_fin_ciclo = 0

    ## BORRAR BASES DE DATOS ##
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
    def visualizar(self,list_all_datos,server):
        fecha_recibida = self.fecha_actual()
        self.out_fecha.setText(fecha_recibida)
        if server == False:
            self.primer_ciclo = False
            self.ver_envios = False
            self.ver_maquina = False

        if self.primer_ciclo == True and self.ver_envios==True and self.ver_maquina==True and server==True:
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
                            n_piezas_id_max = dict_all_datos_id_max['piezas']
                            n_cajas_id_max = dict_all_datos_id_max['cajas']
                            n_pales_id_max = dict_all_datos_id_max['pales']
                            self.n_piezas_total = (n_piezas_id_max) + (4 * (n_pales_id_max-1))
                            self.n_cajas_total = (n_cajas_id_max) + (4 * (n_pales_id_max-1))
                            if self.paro_fin_ciclo==0:
                                self.n_pales_total = n_pales_id_max -1
                                self.out_n_pales.setText(str(self.n_pales_total))
                            elif self.paro_fin_ciclo==1 and estado_cinta_pales==1:
                                self.n_pales_total = n_pales_id_max
                                self.out_n_pales.setText(str(self.n_pales_total))
                            self.out_n_piezas.setText(str(self.n_piezas_total))
                            self.out_n_cajas.setText(str(self.n_cajas_total))
                    
                    # Producciones en media de unidades/tiempo
                    list_horas = []
                    list_minutos = []
                    list_segundos = []
                    media_piezas_segundos = 0.00
                    media_cajas_segundos = 0.00
                    media_pales_segundos = 0.00
                    for f in range(0,len(list_all_datos)):
                        dict_all_datos_fecha = list_all_datos[f]
                        recepcion_fecha = dict_all_datos_fecha['fecha']
                        separar_fecha = list(recepcion_fecha)
                        #['2', '0', '2', '2', '-', '0', '6', '-', '1', '8', '_', '1', '9', ':', '5', '3', ':', '2', '5']
                        str_hora = str(separar_fecha[11])+str(separar_fecha[12])
                        str_minutos = str(separar_fecha[14])+str(separar_fecha[15])
                        str_segundos = str(separar_fecha[17])+str(separar_fecha[18])
                        list_horas.append(int(str_hora))
                        list_minutos.append(int(str_minutos))
                        list_segundos.append(int(str_segundos))
                    print(f'Lista de horas {list_horas}')
                    print(f'Lista de minutos {list_minutos}')
                    print(f'Lista de segundos {list_segundos}')
                    
                    otro_dia= False
                    n_dias = 0
                    if len(list_horas)>4:
                        '''
                        for m in range(0,len(list_horas)):
                            if m > 0:
                                if list_horas[m-1]>list_horas[m]:
                                    otro_dia = True
                                    n_dias=n_dias + 1
                        '''
                        if otro_dia == False:
                            if self.n_piezas_total>0:
                                media_piezas_segundos = self.n_piezas_total/(((list_horas[len(list_horas)-1]*60*60)+(list_minutos[len(list_minutos)-1]*60)+(list_segundos[len(list_segundos)-1]))-((list_horas[0]*60*60)+(list_minutos[0]*60)+list_segundos[0]))
                            if self.n_cajas_total>0:
                                media_cajas_segundos = self.n_cajas_total/(((list_horas[len(list_horas)-1]*60*60)+(list_minutos[len(list_minutos)-1]*60)+(list_segundos[len(list_segundos)-1]))-((list_horas[0]*60*60)+(list_minutos[0]*60)+list_segundos[0]))
                            if self.n_pales_total>0:
                                media_pales_segundos = self.n_pales_total/(((list_horas[len(list_horas)-1]*60*60)+(list_minutos[len(list_minutos)-1]*60)+(list_segundos[len(list_segundos)-1]))-((list_horas[0]*60*60)+(list_minutos[0]*60)+list_segundos[0]))
                            if self.n_piezas_total>0:
                                media_piezas_segundos = self.n_piezas_total/(((list_horas[len(list_horas)-1]*60*60)+(list_minutos[len(list_minutos)-1]*60)+(list_segundos[len(list_segundos)-1]))-((list_horas[0]*60*60)+(list_minutos[0]*60)+list_segundos[0]))
                            if self.n_cajas_total>0:   
                                media_cajas_segundos = self.n_cajas_total/(((list_horas[len(list_horas)-1]*60*60)+(list_minutos[len(list_minutos)-1]*60)+(list_segundos[len(list_segundos)-1]))-((list_horas[0]*60*60)+(list_minutos[0]*60)+list_segundos[0]))
                            if self.n_pales_total>0:   
                                media_pales_segundos = self.n_pales_total/(((list_horas[len(list_horas)-1]*60*60)+(list_minutos[len(list_minutos)-1]*60)+(list_segundos[len(list_segundos)-1]))-((list_horas[0]*60*60)+(list_minutos[0]*60)+list_segundos[0]))
                    

                    media_piezas_minutos = 0.00
                    media_cajas_minutos = 0.00
                    media_pales_minutos = 0.00
                    redon_media_piezas = 0.00
                    redon_media_cajas = 0.00
                    redon_media_pales = 0.00
                    media_piezas_minutos = media_piezas_segundos*60 
                    media_cajas_minutos = media_cajas_segundos*60
                    media_pales_minutos = media_pales_minutos*60

                    if media_piezas_minutos>0.00:
                        redon_media_piezas = round(media_piezas_minutos,2)
                        self.out_media_piezas.setText(str(redon_media_piezas))
                    else:
                        self.out_media_piezas.setText(str(0.00))
                    if media_cajas_minutos>0.00:
                        redon_media_cajas = round(media_cajas_minutos,2)
                        self.out_media_cajas.setText(str(redon_media_cajas))
                    else:
                        self.out_media_cajas.setText(str(0.00))
                    if media_pales_minutos>0.00:
                        redon_media_pales = round(media_pales_minutos,2)
                        self.out_media_pales.setText(str(redon_media_pales))
                    else:
                        self.out_media_pales.setText(str(0.00))
                    
                    # Mostrar datos en tabla en tiempo real
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



        if self.primer_ciclo==True and self.ver_envios==True and server==True:    
            try:
                all_maquina = requests.get(f'{self.ip_api}maquina',timeout=4)
                server = True
            except(requests.exceptions.ConnectionError):
                print('Server INACTIVO ...')
                server = False
                self.primer_ciclo=False
                self.ver_envios=False
                self.ver_maquina=False
                self.ver_datos=False
                self.estado_server.setText('INACTIVO')
                self.estado_server.setStyleSheet("color: red")
                self.estado_plc.setText('SIN CONEXION')
                self.estado_plc.setStyleSheet("color: white")
                self.estado_maquina.setText('SIN CONEXION')
                self.estado_maquina.setStyleSheet("color: white")
                self.out_cond_reposo.setText('-----')
                self.out_pick_reposo.setText('-----')
                self.out_ftc_piezas.setStyleSheet("background-color: white")
                self.out_ftc_cajas.setStyleSheet("background-color: white")
                self.out_ftc_pales.setStyleSheet("background-color: white")
                self.out_cinta_piezas.setStyleSheet("background-color: white")
                self.out_cinta_cajas.setStyleSheet("background-color: white")
                self.out_cinta_pales.setStyleSheet("background-color: white")
            
            if server == True:
                
                json_all_maquina = all_maquina.json()
                list_all_maquina = [dict(id_item) for id_item in json_all_maquina]
                list_id_maquina = []
                if len(list_all_maquina)>1:
                    for i in range(0,len(list_all_maquina)):
                        dict_all_maquina_id = list_all_maquina[i]
                        n_id_maquina = dict_all_maquina_id['id']
                        list_id_maquina.append(n_id_maquina)
                    n_id_max_maquina = max(list_id_maquina)
                    for i in range(0,len(list_all_maquina)):
                        dict_all_maquina=list_all_maquina[i]
                        if dict_all_maquina['id']==n_id_max_maquina:
                            estado_mostrar = dict_all_maquina['plc_run']
                            if estado_mostrar == 1:
                                self.estado_plc.setText('RUN')
                                self.estado_plc.setStyleSheet("color: green")
                                estado_emergencias = dict_all_maquina['emergencias']
                                estado_paro = dict_all_maquina['paro']
                                self.paro_fin_ciclo = estado_paro
                                estado_marcha = dict_all_maquina['marcha']
                                estado_cond_reposo = dict_all_maquina['cond_reposo']
                                estado_pick_reposo = dict_all_maquina['pick_reposo']
                                estado_ftc_piezas = dict_all_maquina['ftc_piezas']
                                estado_ftc_cajas = dict_all_maquina['ftc_cajas']
                                estado_ftc_pales = dict_all_maquina['ftc_pales']
                                estado_cinta_piezas = dict_all_maquina['cinta_piezas']
                                estado_cinta_cajas = dict_all_maquina['cinta_cajas']
                                estado_cinta_pales = dict_all_maquina['cinta_pales']
                                
                                if estado_emergencias==1:
                                    self.estado_maquina.setText('EMERGENCIA')
                                    self.estado_maquina.setStyleSheet("color: red")
                                elif estado_emergencias==0 and estado_marcha==0 and estado_paro==0:
                                    self.estado_maquina.setText('PREPARADA')
                                    self.estado_maquina.setStyleSheet("color: green")
                                elif estado_paro==1:
                                    self.estado_maquina.setText('PARO')
                                    self.estado_maquina.setStyleSheet("color: red")          
                                elif estado_marcha==1:
                                    self.estado_maquina.setText('MARCHA')
                                    self.estado_maquina.setStyleSheet("color: green")
                                
                                if estado_cond_reposo==1:
                                    self.out_cond_reposo.setText('Activas')
                                else:
                                    self.out_cond_reposo.setText('Inactivas')               
                                if estado_pick_reposo==1:
                                    self.out_pick_reposo.setText('En reposo')
                                else:
                                    self.out_pick_reposo.setText('Operando...')
                                
                                if estado_ftc_piezas == 1:
                                    self.out_ftc_piezas.setStyleSheet("background-color: red")
                                else:
                                    self.out_ftc_piezas.setStyleSheet("background-color: green")
                                if estado_ftc_cajas == 1:
                                    self.out_ftc_cajas.setStyleSheet("background-color: red")
                                else:
                                    self.out_ftc_cajas.setStyleSheet("background-color: green")
                                if estado_ftc_pales == 1:
                                    self.out_ftc_pales.setStyleSheet("background-color: red")
                                else:
                                    self.out_ftc_pales.setStyleSheet("background-color: green")
                                if estado_cinta_piezas == 1:
                                    self.out_cinta_piezas.setStyleSheet("background-color: green")
                                else:
                                    self.out_cinta_piezas.setStyleSheet("background-color: red")
                                if estado_cinta_cajas == 1:
                                    self.out_cinta_cajas.setStyleSheet("background-color: green")
                                else:
                                    self.out_cinta_cajas.setStyleSheet("background-color: red")
                                if estado_cinta_pales == 1:
                                    self.out_cinta_pales.setStyleSheet("background-color: green")
                                else:
                                    self.out_cinta_pales.setStyleSheet("background-color: red")
                                
                    self.ver_maquina = True

                if ((len(list_all_maquina)) > (self.long_list_maquina)) and self.long_list_maquina != 0:
                    self.estado_plc.setText('RUN')
                    self.estado_plc.setStyleSheet("color: green")
                else:
                    self.estado_plc.setText('STOP')
                    self.estado_plc.setStyleSheet("color: red")
                    self.estado_maquina.setText('-----')
                    self.estado_maquina.setStyleSheet("color: white")
                    self.out_cond_reposo.setText('-----')
                    self.out_pick_reposo.setText('-----')
                    self.out_ftc_piezas.setStyleSheet("background-color: white")
                    self.out_ftc_cajas.setStyleSheet("background-color: white")
                    self.out_ftc_pales.setStyleSheet("background-color: white")
                    self.out_cinta_piezas.setStyleSheet("background-color: white")
                    self.out_cinta_cajas.setStyleSheet("background-color: white")
                    self.out_cinta_pales.setStyleSheet("background-color: white")
                
                self.long_list_maquina = len(list_all_maquina)

        if self.primer_ciclo==False and server == True and self.ver_maquina == False:    
            try:
                all_envios = requests.get(f'{self.ip_api}envios',timeout=4)
                server = True
            except(requests.exceptions.ConnectionError):
                print('Server INACTIVO ...')
                server = False
                self.primer_ciclo=False
                self.ver_envios=False
                self.ver_maquina=False
                self.ver_datos=False
                self.estado_server.setText('INACTIVO')
                self.estado_server.setStyleSheet("color: red")
                self.estado_plc.setText('SIN CONEXION')
                self.estado_plc.setStyleSheet("color: white")
                self.estado_maquina.setText('SIN CONEXION')
                self.estado_maquina.setStyleSheet("color: white")
                self.out_cond_reposo.setText('-----')
                self.out_pick_reposo.setText('-----') 
                self.out_ftc_piezas.setStyleSheet("background-color: white")
                self.out_ftc_cajas.setStyleSheet("background-color: white")
                self.out_ftc_pales.setStyleSheet("background-color: white")
                self.out_cinta_piezas.setStyleSheet("background-color: white")
                self.out_cinta_cajas.setStyleSheet("background-color: white")
                self.out_cinta_pales.setStyleSheet("background-color: white") 
                
            self.estado_server.setText('ACTIVO')
            self.estado_server.setStyleSheet("color: green")
            json_all_envios = all_envios.json()
            list_all_envios = [dict(id_item) for id_item in json_all_envios]  
            if ((len(list_all_envios)) > (self.long_list_envios)) and self.long_list_envios != 0:
                self.estado_plc.setText('RUN')
                self.estado_plc.setStyleSheet("color: green")
                self.primer_ciclo = True
                self.ver_envios = True
            else:
                self.estado_plc.setText('STOP')
                self.estado_plc.setStyleSheet("color: red")
                self.estado_maquina.setText('-----')
                self.estado_maquina.setStyleSheet("color: white")
                self.out_cond_reposo.setText('-----')
                self.out_pick_reposo.setText('-----')
                                
            self.long_list_envios = len(list_all_envios)
                
            
                   
        if server==False:
            self.estado_server.setText('INACTIVO')
            self.estado_server.setStyleSheet("color: red")
            self.estado_plc.setText('SIN CONEXION')
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
    