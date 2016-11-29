# -*- coding: cp1252 -*-
import sys
from PyQt4 import QtCore, QtGui, uic
from casc_tubo_cal import *
import sqlite3
from test002 import *

testfqt = "casc_tub.ui"

# Necessário definir termo para temperature_cross
# Fluido1 é o fluido que escoa pelo lado do casco, shell
# Fluido2 é o fluido que escoa pelos tubos.

fluido1={'Vazao':0,'T_entr':0,'T_said':0,'cp':0,'k':0,'Pr':0,'Viscos':0,
         'Densidade':0,'Diam_ext':0,'Diam_int':0,'Liquido':0,'Viscos_tw':0}
fluido2={'Vazao':0,'T_entr':0,'T_said':0,'cp':0,'k':0,'Pr':0,'Viscos':0,
         'Densidade':0,'Diam_ext':0,'Diam_int':0,'Annulus':0,'Liquido':0,'Viscos_tw':0}
material={'K':0,'L':1, 'R_fi':0,'R_fo':0,'Calor_cnste':0,'Contracorrente':0,'Angulo_tubos':0,
          'Bfl_spac':0,'Bfl_prct':0,'Num_pass_tb':0,'Pt':0, 'Num_passes_casco':1}

Ui_MainWindow, QtBaseClass = uic.loadUiType(testfqt)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    # LEMBRAR DE FAZER ITENS ABAIXO:
    # CORRIGIR BANCO DE DADOS DOS FLUIDOS DIFERENTES
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.material=material
        self.fluido1=fluido1
        self.fluido2=fluido2
        #self.resultados2.setReadOnly(True)
        self.confir1.clicked.connect(self.toFluid1)
        self.confir1.clicked.connect(self.alter1)
        self.confir2.clicked.connect(self.toFluid2)
        self.confir2.clicked.connect(self.alter2)
        self.confir3.clicked.connect(self.tomaterial)
        self.confir3.clicked.connect(self.alter3)
        self.calcular_fim.clicked.connect(self.resultados)
        # Banco de dados dos tubos nominais
        con=sqlite3.connect('tub_num.db')
        cur=con.cursor()
        sql_state="SELECT nm_tubo FROM tb_nom;"
        for p in cur.execute(sql_state).fetchall():
            self.nom_diam1.addItem(p[0])
            self.nom_diam2.addItem(p[0])
        self.nom_diam1.addItem(u'Manual')
        self.nom_diam2.addItem(u'Manual')
        self.nom_diam1.currentIndexChanged.connect(self.setDiam1)
        self.nom_diam2.currentIndexChanged.connect(self.setDiam2)
        # Adição dos Compostos do Banco de Dados
        con=sqlite3.connect('propriedades01.db')
        cur=con.cursor()
        sql_state="SELECT name FROM sqlite_master where type='table';"
        for p in cur.execute(sql_state):
            self.fluidos.addItem(p[0])
            self.fluidos2.addItem(p[0])
        self.fluidos.addItem(u'Manual')
        self.fluidos2.addItem(u'Manual')
        # Fim do banco de dados!
        # Parte responsável pela adição de propriedades termofísicas
        #### Para o Tubo Interno
        self.T_entr1.textChanged.connect(self.toFluid1)
        self.T_said1.textChanged.connect(self.toFluid1)
        self.T_entr1.textChanged.connect(self.setProp1)
        self.T_said1.textChanged.connect(self.setProp1)
        self.T_said1.textChanged.connect(self.altern1)
        self.T_entr1.textChanged.connect(self.altern1)
        self.Vazao1.textChanged.connect(self.altern1)
        self.diam_int1.textChanged.connect(self.altern1)
        self.diam_ext1.textChanged.connect(self.altern1)
        self.fluidos.currentIndexChanged.connect(self.setProp1)
        #### Fim do Tubo Interno
        #### Região Anular
        self.T_entr2.textChanged.connect(self.toFluid2)
        self.T_said2.textChanged.connect(self.toFluid2)
        self.T_entr2.textChanged.connect(self.setProp2)
        self.T_said2.textChanged.connect(self.setProp2)
        self.T_said2.textChanged.connect(self.altern2)
        self.T_entr2.textChanged.connect(self.altern2)
        self.Vazao2.textChanged.connect(self.altern2)
        self.diam_int2.textChanged.connect(self.altern2)
        self.diam_ext2.textChanged.connect(self.altern2)
        self.fluidos2.currentIndexChanged.connect(self.setProp2)
        #### Fim do Interno Região Anular
        # Lembrar de fazer os butões de confirmar funcionarem apenas para
        # adicionar os dados dos fluidos à memoria.
        self.L_material.textChanged.connect(self.altern3)
        self.K_material.textChanged.connect(self.altern3)
        self.efic_bomb1.textChanged.connect(self.altern3)
        self.efic_bomb2.textChanged.connect(self.altern3)
        self.R_fi.textChanged.connect(self.altern3)
        self.R_fo.textChanged.connect(self.altern3)
        self.Calor_cnste.pressed.connect(self.altern3)
        self.Contracorrente.pressed.connect(self.altern3)

    def setDiam1(self):
        text=self.nom_diam1.currentIndex()
        d=sqlite3.connect('tub_num.db').cursor().execute("SELECT diam_int,diam_ext FROM tb_nom WHERE id=%d;"%int(text+1)).fetchall()
        self.diam_int1.setText(str(d[0][0]))
        self.diam_ext1.setText(str(d[0][1]))

    def setDiam2(self):
        text=self.nom_diam2.currentIndex()
        d=sqlite3.connect('tub_num.db').cursor().execute("SELECT diam_int,diam_ext FROM tb_nom WHERE id=%d;"%int(text+1)).fetchall()
        self.diam_int2.setText(str(d[0][0]))
        self.diam_ext2.setText(str(d[0][1]))

    def setProp1(self):
        fluido_test1=self.fluido1
        fluido_test2=self.fluido2
        table=self.fluidos.itemText(self.fluidos.currentIndex())
        temp_m=temp_media(fluido_test1)
        temp_w=temp_wall(fluido_test1,fluido_test2)
        propried_get(temp_m,temp_w,table,fluido_test1)
        self.k1.setText(str(fluido_test1['k']))
        self.cp1.setText(str(fluido_test1['cp']))
        self.Pr1.setText(str(fluido_test1['Pr']))
        self.Viscos1.setText(str(fluido_test1['Viscos']))
        self.Densidade1.setText(str(fluido_test1['Densidade']))
        
    def toFluid1(self):
        fluido1['Vazao']=float(self.Vazao1.text().replace(',','.'))
        fluido1['T_entr']=float(self.T_entr1.text().replace(',','.'))
        fluido1['T_said']=float(self.T_said1.text().replace(',','.'))
        fluido1['Diam_int']=float(self.diam_int1.text().replace(',','.'))/1000
        fluido1['Diam_ext']=float(self.diam_ext1.text().replace(',','.'))/1000
        fluido1['k']=float(self.k1.text().replace(',','.'))
        fluido1['cp']=float(self.cp1.text().replace(',','.'))
        fluido1['Pr']=float(self.Pr1.text().replace(',','.'))
        fluido1['Viscos']=float(self.Viscos1.text().replace(',','.'))
        fluido1['Densidade']=float(self.Densidade1.text().replace(',','.'))
        fluido1['Liquido']=1

    def setProp2(self):
        fluido_test1=self.fluido1
        fluido_test2=self.fluido2
        table=self.fluidos2.itemText(self.fluidos2.currentIndex())
        temp_m=temp_media(fluido_test2)
        temp_w=temp_wall(fluido_test2,fluido_test1)
        propried_get(temp_m,temp_w,table,fluido_test2)
        self.k2.setText(str(fluido_test2['k']))
        self.cp2.setText(str(fluido_test2['cp']))
        self.Pr2.setText(str(fluido_test2['Pr']))
        self.Viscos2.setText(str(fluido_test2['Viscos']))
        self.Densidade2.setText(str(fluido_test2['Densidade']))

    def toFluid2(self):
        fluido2['Vazao']=float(self.Vazao2.text().replace(',','.'))
        fluido2['T_entr']=float(self.T_entr2.text().replace(',','.'))
        fluido2['T_said']=float(self.T_said2.text().replace(',','.'))
        fluido2['k']=float(self.k2.text().replace(',','.'))
        fluido2['cp']=float(self.cp2.text().replace(',','.'))
        fluido2['Pr']=float(self.Pr2.text().replace(',','.'))
        fluido2['Diam_int']=float(self.diam_int2.text().replace(',','.'))/1000
        fluido2['Diam_ext']=float(self.diam_ext2.text().replace(',','.'))/1000
        fluido2['Viscos']=float(self.Viscos2.text().replace(',','.'))
        fluido2['Densidade']=float(self.Densidade2.text().replace(',','.'))
        fluido2['Annulus']=1
        fluido2['Liquido']=1

    def tomaterial(self):
        material['K']=float(self.K_material.text().replace(',','.'))
        material['L']=float(self.L_material.text().replace(',','.'))
        material['R_fi']=float(self.R_fi.text().replace(',','.'))
        material['R_fo']=float(self.R_fo.text().replace(',','.'))
        material['Calor_cnste']=float(self.Calor_cnste.isChecked())
        material['Efic_bomb1']=float(self.efic_bomb1.text().replace(',','.'))/100.0
        material['Efic_bomb2']=float(self.efic_bomb2.text().replace(',','.'))/100.0
        material['Contracorrente']=float(self.Contracorrente.isChecked())
        material['Angulo_tubos']=float(self.Angulo_tubos.itemText(self.Angulo_tubos.currentIndex())[:-1])
        material['Bfl_spac']=float(self.Bfl_spac.text().replace(',','.'))/1000.0
        material['Bfl_prct']=float(self.Bfl_prct.text().replace(',','.'))/100.0
        material['Num_pass_tb']=float(self.Num_pass_tb.itemText(self.Num_passes_casco.currentIndex()))
        material['Pt']=float(self.Pt.text().replace(',','.'))/1000.0
        material['Num_passes_casco']=float(self.Num_passes_casco.itemText(self.Num_passes_casco.currentIndex()))

        

    def resultados(self):
        result_fl,result_press,result_geral=heat_friction_shell(fluido1,fluido2,material)
        self.resultados1.setRowCount(len(result_fl))
        self.resultados1.setColumnCount(len(result_fl.values()[0]))
        self.resultados2.setRowCount(len(result_press))
        self.resultados2.setColumnCount(2)
        self.resultados3.setRowCount(len(result_geral))
        self.resultados3.setColumnCount(1)
        item = QtGui.QTableWidgetItem()
        self.resultados1.setHorizontalHeaderItem(0, item)
        self.resultados1.horizontalHeaderItem(0)
        item.setText(u'Casco')
        item = QtGui.QTableWidgetItem()
        self.resultados1.setHorizontalHeaderItem(1, item)
        self.resultados1.horizontalHeaderItem(1)
        item.setText(u'Tubos Internos')
        item = QtGui.QTableWidgetItem()
        self.resultados2.setHorizontalHeaderItem(0, item)
        self.resultados2.horizontalHeaderItem(0)
        item.setText(u'Casco')
        item = QtGui.QTableWidgetItem()
        self.resultados2.setHorizontalHeaderItem(1, item)
        self.resultados2.horizontalHeaderItem(1)
        item.setText(u'Tubos Internos')
        item = QtGui.QTableWidgetItem()
        self.resultados3.setHorizontalHeaderItem(0, item)
        self.resultados3.horizontalHeaderItem(0)
        item.setText(u'Definições')
        ### Resultados 1
        for line,p in enumerate(sorted(result_fl.keys(),reverse=True)):
            item = QtGui.QTableWidgetItem()
            self.resultados1.setVerticalHeaderItem(line, item)
            self.resultados1.verticalHeaderItem(line)
            item.setText(p)
            for column,v in enumerate(result_fl[p]):
                item = QtGui.QTableWidgetItem()
                self.resultados1.setItem(line, column,item)
                item.setText(v)
        del p, line, column
        for line,p in enumerate(sorted(result_press.keys(),reverse=True)):
            item = QtGui.QTableWidgetItem()
            self.resultados2.setVerticalHeaderItem(line, item)
            self.resultados2.verticalHeaderItem(line)
            item.setText(p)
            for column,v in enumerate(result_press[p]):
                item = QtGui.QTableWidgetItem()
                self.resultados2.setItem(line, column,item)
                item.setText(v)
        del p, line, column
        for line,p in enumerate(sorted(result_geral.keys())):
            item = QtGui.QTableWidgetItem()
            self.resultados3.setVerticalHeaderItem(line, item)
            self.resultados3.verticalHeaderItem(line)
            item.setText(p)
            #for column,v in enumerate(result_geral[p]):
            item = QtGui.QTableWidgetItem()
            self.resultados3.setItem(line, 0,item)
            item.setText(result_geral[p])
        del p, line
        self.resultados1.resizeColumnsToContents()
        self.resultados1.resizeRowsToContents()
        self.resultados2.resizeColumnsToContents()
        self.resultados2.resizeRowsToContents()
        self.resultados3.resizeColumnsToContents()
        self.resultados3.resizeRowsToContents()
        
        

    def alter1(self):
        self.label_4.setText(str('Alterações Salvas!'))

    def alter2(self):
        self.label_5.setText(str('Alterações Salvas!'))

    def alter3(self):
        self.label_23.setText(str('Alterações Salvas!'))

    def altern1(self):
        self.label_4.setText(str('As alterações não foram salvas!'))

    def altern2(self):
        self.label_5.setText(str('As alterações não foram salvas!'))

    def altern3(self):
        self.label_23.setText(str('As alterações não foram salvas!'))

        

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())










