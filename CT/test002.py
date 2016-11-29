# -*- coding: cp1252 -*-
# Módulo de Propriedades físicas, Teste 002

# Estimar valores através do Banco de Dados

# Adicionar caminho em sys.path

import sqlite3

def temp_media(fluido):
    T1=fluido['T_entr'];T2=fluido['T_said']
    return float(T1+T2)/2

def temp_wall(fluido1,fluido2):
    t1=fluido1['T_entr'];t2=fluido1['T_said']
    t3=fluido2['T_entr'];t4=fluido2['T_said']
    return float(t1+t2+t3+t4)/4


def propried_get(temp_m,temp_w,table,fluido):
    con=sqlite3.connect('propriedades01.db')
    cur=con.cursor()
    def inter_temp(temp,table,prop):
        sql2='SELECT %s,temp FROM %s '\
              'WHERE temp >= %.5f LIMIT 1;'
        sql1='SELECT %s,temp FROM %s '\
              'WHERE temp <= %.5f '\
              'ORDER BY temp DESC LIMIT 1;'
        y1=float(cur.execute(sql1%(prop,table,temp,)).fetchall()[0][0])
        y2=float(cur.execute(sql2%(prop,table,temp,)).fetchall()[0][0])
        temp1=float(cur.execute(sql1%(prop,table,temp,)).fetchall()[0][1])
        temp2=float(cur.execute(sql2%(prop,table,temp,)).fetchall()[0][1])
        if y2>y1:
            prop=(y2-y1)*(temp-temp1)/(temp2-temp1) + y1
        else:
            prop=-(y1-y2)*(temp-temp1)/(temp2-temp1) + y1
        return prop
    # Final da função de interpolação
    sql_stmnt='SELECT %s FROM %s WHERE temp == %s;'
    if temp_m in cur.execute('SELECT * FROM %s;'%table).fetchall():
        fluido['Densidade']=float(cur.execute(sql_stmnt%('densidade',table,temp_m)).fetchone()[0])
        fluido['Viscos']=float(cur.execute(sql_stmnt%('Viscos',table,temp_m)).fetchone()[0])
        fluido['cp']=float(cur.execute(sql_stmnt%('cp',table,temp_m)).fetchone()[0])
        fluido['Viscos_tw']=float(cur.execute(sql_stmnt%('Viscos',table,temp_m)).fetchone()[0])
        fluido['k']=float(cur.execute(sql_stmnt%('k',table,temp_w)).fetchone()[0])
        fluido['Pr']=fluido['cp']*fluido['Viscos']/fluido['k']
    else:
        fluido['Densidade']=inter_temp(temp_m,table,'densidade')
        fluido['Viscos']=inter_temp(temp_m,table,'Viscos')
        fluido['cp']=inter_temp(temp_m,table,'cp')
        fluido['Viscos_tw']=inter_temp(temp_w,table,'Viscos')
        fluido['k']=inter_temp(temp_m,table,'k')
        fluido['Pr']=fluido['cp']*fluido['Viscos']/fluido['k']
    return fluido















