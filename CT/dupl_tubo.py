# -*- coding: cp1252 -*-
# Módulo de Equações para Trocadores de Calor Duplo-Tubo
# Última Alteração 11:15 19/09/2016

from math import *

# Fluido1 arbitrado como o tubo interno
fluido1={'Vazao':0,'T_entr':0,'T_said':0,'cp':0,'k':0,'Pr':0,'Viscos':0,
         'Densidade':0,'Diam_ext':0,'Diam_int':0,'Annulus':0,'Liquido':0,'Viscos_tw':0}

# Fluido2 arbitrado como a região anular
fluido2={'Vazao':0,'T_entr':0,'T_said':0,'cp':0,'k':0,'Pr':0,'Viscos':0,
         'Densidade':0,'Diam_ext':0,'Diam_int':0,'Annulus':0,'Liquido':0,'Viscos_tw':0}
material={'K':0,'L':1, 'Fouling factor':0,'Calor_cnste':0,'Multi_tube':0,'Num_tubs':1,
          'Tw':(fluido1['T_entr']+fluido2['T_said']+fluido2['T_entr']+fluido2['T_said'])/4}


def Pressure_drop_serth(fluido,material,diam_h=0):
    # s --> gravidade específica, s=(densidade do fluido)/(densidade da água) ## coisa do Serth --;
    # r --> Return bends, n --> nozzle losses; Serth pg. 154
    s=fluido['Densidade']/1000;G=fluido['Vazao']/fluido['Area_h']
    if fluido['Re']<4000:
        f=16/fluido['Re'] #Kakaç e Liu pg. 132
        material[u'\u0394Pn']=(1.5*10**-3)*(material['Num_gramp'])*(G**2)/s
        if fluido['Annulus']==1:
            f*=1.5 #Serth pg 113
            #material[u'\u0394Pr2']=(6*10**-4)*(material['Num_gramp']*2-1)*G**2/s
            material[u'\u0394Pr2']=(7.5*10**-4)*(material['Num_gramp']*2-1)*(G**2)/s
        else:
            material[u'\u0394Pr1']=(7.5*10**-4)*(material['Num_gramp']*2-1)*(G**2)/s
    else:
        f=0.00140+0.125*fluido['Re']**-0.32
        material[u'\u0394Pn']=(7.5*10**-4)*(material['Num_gramp'])*G**2/s
        if fluido['Annulus']==1:
            material[u'\u0394Pr2']=(6*10**-4)*(material['Num_gramp']*2-1)*G**2/s
        else:
            #material[u'\u0394Pr1']=(7.5*10**-4)*(material['Num_gramp']*2-1)*(G**2)
            material[u'\u0394Pr1']=(6*10**-4)*(material['Num_gramp']*2-1)*G**2/s
    if fluido['Annulus']==0:
        fluido[u'\u0394P']=(4*f*2*material['L']*material['Num_gramp']*fluido['Densidade']*fluido['Vel_m']**2)/(2*fluido['Diam_int'])
        fluido[u'\u0394Ptotal']=fluido[u'\u0394P']+ material[u'\u0394Pr1']
    else:
        fluido[u'\u0394P']=(8*f*material['L']*material['Num_gramp']*fluido['Densidade']*fluido['Vel_m']**2)/(2*diam_h)
        fluido[u'\u0394Ptotal']=fluido[u'\u0394P']+ material[u'\u0394Pr2']+material[u'\u0394Pn']
    return fluido, material


def desvio(dados):
	"Retira os dados que se afastam muito da média do conjunto"
	desvio={};med=sum(dados.values())/len(dados);M=max(dados.values())
	if abs(med-M)/med>0.4:
		for d in dados.keys():
			if dados[d]==M: del dados[d]
	med=sum(dados.values())/len(dados)
	for p in dados.keys():desvio[p]=abs(med-dados[p])/med
	for p in desvio.keys():
		if desvio[p]>0.3: del dados[p]
	return dados

def calor_vazao(fluido1,fluido2):
    '''Calor Cedido igual o calor recebido pelos fluidos'''
    cp1=fluido1['cp'];cp2=fluido2['cp']
    if fluido1['Vazao']==0:
        fluido1['Vazao']=(float(fluido2['Vazao'])*cp2*abs(fluido2['T_entr']-fluido2['T_said']))/(cp1*abs(fluido1['T_entr']-fluido1['T_said']))
    elif fluido2['Vazao']==0:
        fluido2['Vazao']=(float(fluido1['Vazao'])*cp1*abs(fluido1['T_entr']-fluido1['T_said']))/(cp2*abs(fluido2['T_entr']-fluido2['T_said']))
    elif fluido1['T_said']==0:
        fluido1['T_said']=fluido1['T_entr']+(float(fluido2['Vazao'])*cp2*abs(fluido2['T_entr']-fluido2['T_said']))/(fluido1['Vazao']*cp1)
    elif fluido2['T_said']==0:
        fluido2['T_said']=fluido2['T_entr']+(float(fluido1['Vazao'])*cp1*abs(fluido1['T_entr']-fluido1['T_said']))/(fluido2['Vazao']*cp2)
    elif fluido1['T_entr']==0:
        fluido1['T_entr']=fluido1['T_said']-((float(fluido2['Vazao'])*cp2*abs(fluido2['T_said']-fluido2['T_entr']))/(fluido1['Vazao']*cp1))
    elif fluido2['T_entr']==0:
        fluido2['T_entr']=fluido2['T_said']-((float(fluido1['Vazao'])*cp1*abs(fluido1['T_said']-fluido1['T_entr']))/(fluido2['Vazao']*cp2))
    return None  

def reynolds_tube(fluido1,fluido2,material):
    n=material['Num_tubs'] if material['Multi_tube']==True else 1
    fluido2['Area_h']=(pi/4)*(pow(fluido2['Diam_int'],2)-n*pow(fluido1['Diam_ext'],2)) 
    fluido1['Area_h']=pi*(fluido1['Diam_int']**2)/4
    diam_h=(pow(fluido2['Diam_int'],2)-n*pow(fluido1['Diam_ext'],2))/(fluido2['Diam_int']+n*fluido2['Diam_ext'])
    # Causa1 ==> obs.: Kern usa o diâmetro equivalente
    #KAKAÇ E LIU, PG. 87, DESCRIÇÃO DO MOTIVO DE DIAMETRO HIDRÁULICO
    fluido2['Vel_m']=fluido2['Vazao']/(fluido2['Densidade']*fluido2['Area_h'])
    fluido1['Vel_m']=fluido1['Vazao']/(fluido1['Densidade']*pi*fluido1['Diam_int']**2/4)
    fluido2['Re']=fluido2['Densidade']*fluido2['Vel_m']*diam_h/fluido2['Viscos']
    fluido1['Re']=4*fluido1['Vazao']/(pi*fluido1['Viscos']*fluido1['Diam_int'])
    return fluido1['Re'],fluido2['Re']
    
def nusselt_tube(fluido1,fluido2,material):
    Pr=fluido1['Pr'];Re=fluido1['Re'];diam=fluido1['Diam_int'];L=material['L'];
    fl=fluido1['Liquido'];vis_tm=fluido1['Viscos'];vis_tw=fluido1['Viscos_tw']
    calor_cnste=material['Calor_cnste'];annulus=fluido1['Annulus']
    Pe=Re*Pr
    if annulus==True: do=fluido2['Diam_int'];D_i=fluido1['Diam_int']
    #Equação 3.8
    #Equação utilizada para escoamento de fluidos incompressíveis, em regime laminar,
    #em um duto circular com uma condição limite de temperatura constante na parede,
    #indicado pelo subscrito T, utilizada para 0.1<(Pe*diam/L)<10000"""
    if Re<=2100:
        nusselts={}
        if (Pe*diam/L)>1000 and (Pe*diam/L)<10000:
            Nu_T=(1.61)*((Pe*diam/L)**(1/3.))
            nusselts["Nu_T(Eq. 3.8)"]=Nu_T
        #Equação 3.9:
        #Correlação empírica desenvolvida por Hausen para as mesmas condições da equação 3.8, descrita a abaixo:
        #'Equação 3.8
        #Equação utilizada para escoamento de fluidos incompressíveis, em regime laminar,
        #em um duto circular com uma condição limite de temperatura constante na parede,
        #indicado pelo subscrito T, utilizada para 0.1<(Pe*diam/L)<10000
        if (Pe*diam/L)>0.1 and (Pe*diam/L)<10**4:
            Nu_T=3.66+(0.19*((Pe*diam/L)**0.8))/(1+0.117*((Pe*diam/L)**0.467))
            nusselts["Nu_T(Eq. 3.9)"]=Nu_T
        #Equação 3.11:
        #Equação utilizada considerando escoamento em regime laminar de fluidos
        #incompressíveis, com a condição limite de fluxo constante de calor pela parede, subscrito H,
        #geralmente realizados com as propriedades do fluido na temperatura média dos fluidos (KAKAÇ e LIU, 2002)"""
        if (Pe*diam/L)>100 and calor_cnste==True:
            Nu_H=1.953*(pow(Pe*diam/L,1/3.))
            nusselts["Nu_H(Eq. 3.11)"]=Nu_H
        #Equação 3.13 - Usada para escoamento em desenvolvimento simultâneo em tubos lisos
        if (Pr)>0.5 and (Pr)<500 and (Pe*diam/L)>1000:
            Nu_T=0.664*((Pe*diam/L)**0.5)*((Pe/Re)**(-1/6.))
            nusselts["Nu_T(Eq. 3.13)"]=Nu_T
        #Equação 3.24 - Utilizada para escoamento laminar de LÍQUIDOS'''
        if (((Pe*diam/L)**(1./3))*((vis_tm/vis_tw)**0.14))>=2 and (vis_tm/vis_tw)>4.4*10**-3 and (vis_tm/vis_tw)<9.75 and (vis_tm/vis_tw)>0.0044:
            Nu_T=1.86*(pow(Pe*diam/L,1/3.0))*(pow(vis_tm/vis_tw,0.14))
            nusselts["Nu_T(Eq. 3.24)"]=Nu_T
        if (Pe*diam/L)<100 and calor_cnste==True:
            Nu_H=4.36
            nusselts["Nu_H"]=Nu_H
        if annulus==True:
            d_ext=fluido2['Diam_ext']
            if calor_cnste==True:
                g=1+0.14*pow(d_ext/D_i,-1/2.);diam_h=(D_i**2-do**2)/do
                #Nu_H=(1.86*pow(Pe*diam/L,1./3)*pow(vis_tm/vis_tw,0.14))+((0.19*pow(Pe*diam_h/L,0.8))/(1+(0.117*pow(Pe*diam_h/L,0.467))))*g
                Nu_H=(3.66+1.2*pow(fluido1['Diam_ext']/fluido2['Diam_int']))+((0.19*pow(Pe*diam_h/L,0.8))/(1+(0.117*pow(Pe*diam_h/L,0.467))))*g
                nusselts['Nu_H (Eq. 3.20a)']=Nu_H
            if calor_cnste==False:
                g=1+0.14*pow(d_ext/D_i,0.1);diam_h=(D_i**2-do**2)/do
                Nu_H=(1.86*pow(Pe*diam/L,1./3)*pow(vis_tm/vis_tw,0.14))+((0.19*pow(Pe*diam_h/L,0.8))/(1+(0.117*pow(Pe*diam_h/L,0.467))))*g
                nusselts['Nu_H (Eq. 3.20b)']=Nu_H
        else:
            if (Pe*diam/L)>0.1 and (Pe*diam/L)<100:
                Nu_T=3.66
                nusselts["Nu_T(Eq. 3.7)"]=Nu_T
    # Para gases, não há correção do número de Nusselt, n = 0.
    if Re>=10000:
        nusselts={}
        if fl==True: # Se for Liquido
            if Pr>0.1 and Pr<10000:
                m=0.88-0.24/(4+Pr)
                n=1/3.+0.5*pow(e,-0.6*Pr)
                Nu=5+0.015*pow(Re,m)*pow(Pr,n)
                nusselts['Nu (Eq. 3.30)']=Nu
        if fl==False:
            if Pr>0.5 and Pr<1:
                Nu=0.022*pow(Re,0.8)*(Pr,0.5)
                nusselts['Nu (Caso 7 - Tabela 3.3)']=Nu
    if Re>2100 and Re<10000:
        nusselts={}
        if  Pr>0.5 and Pr<2000:
            f=pow((1.58*log(Re,e)-3.28),-2)
            Nu=((f/2)*(Re-1000)*Pr)/(1+12.7*pow(f/2,1./2)*(pow(Pr,2/3.)-1))
            nusselts["Nu (Eq. 3.31)"]=Nu
    desvio(nusselts)
    Nu=max(nusselts.values());fluido1['Nu']=Nu
    return fluido1


def check_dtm(fluido1,fluido2,material):
    if material['Contracorrente']==1:
        if fluido1['T_entr']>=fluido2['T_entr']:
            Th1,Th2,Tc1,Tc2=fluido1['T_entr'],fluido1['T_said'],fluido2['T_entr'],fluido2['T_said']
            try:
                dTm=(((Th1-Tc2)-(Th2-Tc1))/log((Th1-Tc2)/(Th2-Tc1)))
            except:
                dTm=(Th1-Tc2)
        else:
            Th1,Th2,Tc1,Tc2=fluido2['T_entr'],fluido2['T_said'],fluido1['T_entr'],fluido1['T_said']
            dT1=float(Th1-Tc2);dT2=float(Th2-Tc1)
            try:
                dTm=((dT1-dT2)/log(dT1/dT2))
            except:
                dTm=(Th1-Tc2)
    else:
        if fluido1['T_entr']>=fluido2['T_entr']:
            Th1,Th2,Tc1,Tc2=fluido1['T_entr'],fluido1['T_said'],fluido2['T_entr'],fluido2['T_said']
            dT1=float(Th1-Tc1);dT2=float(Th2-Tc2)
            try:
                dTm=((dT1-dT2)/log(dT1/dT2))
            except:
                dTm=(dT1+dT2)/2
        else:
            Th1,Th2,Tc1,Tc2=fluido2['T_entr'],fluido2['T_said'],fluido1['T_entr'],fluido1['T_said']
            dT1=float(Th1-Tc1);dT2=float(Th2-Tc2)
            try:
                dTm=((dT1-dT2)/log(dT1/dT2))
            except:
                dTm=(dT1+dT2)/2
    return dTm

def alets(fluido1,fluido2,material):
    Nt=material['Num_tubs'];L=material['L'];Nf=material['Alet_per_tube']
    Hf=material['Alet_alt'];k_a=material['Alet_K'];sigm=material['Alet_espes']
    diam_ext=fluido1['Diam_ext'];diam_int=fluido1['Diam_int'];Diam_int=fluido2['Diam_int']
    k=material['K'];Rfo=material['R_fo'];Rfi=material['R_fi']
    Ac=(pi/4)*(Diam_int**2-Nt*(diam_ext**2))-sigm*Hf*Nt*Nf
    Af=2*Nt*Nf*L*(2*Hf+sigm) # Finned area
    Au=2*Nt*(pi*diam_ext*L-Nf*L*sigm) # Unfinned area
    Ai=2*pi*diam_int*L
    At=Au+Af
    Pw=pi*(Diam_int+diam_ext*Nt)+2*Hf*Nf*Nt
    Ph=pi*diam_ext+2*Hf*Nf*Nt
    Dh=4*Ac/Pw # Diam Hidraúlico (Kakaç e Liu) para Queda de Pressão
    De=4*Ac/Ph # Diam Equivalent (Kakaç e Liu) para Transferência de Calor
    Rw=(log(diam_ext/diam_int))/(2*pi*(2*L)*k) # Verificar 2*L 
    # Primeiro Reynolds Para Tubos Aletados
    fluido2['Area_h']=Ac
    fluido2['Vel_m']=fluido2['Vazao']/(fluido2['Densidade']*Ac)
    fluido2['Re']=fluido2['Densidade']*fluido2['Vel_m']*Dh/fluido2['Viscos']
    # Segundo: Nusselts para Tubos Aletados
    Pe=fluido2['Re']*fluido2['Pr'];vis_tm=fluido2['Viscos'];vis_tw=fluido2['Viscos_tw']
    Pr=fluido2['Pr'];Re=fluido2['Re']
    if fluido2['Re']<2100:
        if (((Pe*Dh/L)**(1./3))*((vis_tm/vis_tw)**0.14))>=2 and (vis_tm/vis_tw)<9.75 and (vis_tm/vis_tw)>0.0044:
            fluido2['Nu']=1.86*(pow(Pe*Dh/L,1/3.0))*(pow(vis_tm/vis_tw,0.14))
        else:
            fluido2['Nu']= 1.61*pow(Pe*Dh/L,1/3.0) if Pe*Dh/L>10**3 else 3.66
    elif fluido2['Re']>=10000:
        m=0.88-0.24/(4+Pr); n=1/3.+0.5*pow(e,-0.6*Pr)
        fluido2['Nu']=5+0.015*pow(Re,m)*pow(Pr,n)
    else:
        f=pow((1.58*log(fluido2['Re'])-3.28),-2)
        fluido2['Nu']=((f/2)*(fluido2['Re']-1000)*fluido2['Pr'])/(1+12.7*pow(f/2,1./2)*(pow(fluido2['Pr'],2/3.)-1))
    h_i=fluido1['Nu']*fluido1['k']/fluido1['Diam_int']
    h_o=fluido2['Nu']*fluido2['k']/De
    if material['Alet_type']=='retangular': # Kakaç e Liu (2002)
        nif=tanh((sqrt(2*h_o/(sigm*k_a)))*Hf)/((sqrt(2*h_o/(sigm*k_a)))*Hf) 
    elif material['Alet_type']=='circular': 
        m=sqrt(2*h_o/(k_a*sigm))
        de=Hf*2.0+diam_ext
        r_ast=de/diam_ext
        Hfe=Hf+sigm/2.0
        a=pow(r_ast,-0.246)
        b=(0.9107+0.0893*r_ast) if r_ast<=2 else (0.9706+0.17125*log(r_ast))
        n=exp(0.13*m*Hfe-1.3863)
        THT=m*Hfe*pow(r_ast,n)
        nif=a*pow(m*Hfe,-b) if THT>(0.6+2.257*pow(r_ast,-0.445)) else ((tanh(THT))/(THT))
    elif material['Alet_type']=='studded':
        W=material['Stud_Len']
        m=sqrt((2*h_o/(k_a*sigm))*(1+sigm/W))
        Hfe=Hf+sigm/2.0
        nif=tanh(m*Hfe)/(m*Hfe)
    nio=(1-(1-nif)*Af/At)
    U_d=(At/(Ai*h_i)+At/Ai*Rfi+At*Rw+Rfo/nio+1/(nio*h_o))**-1.0
    U_c=(At/(Ai*h_i)+At*Rw+1/(nio*h_o))**-1.0
    return Dh, h_o, U_d,U_c,At


def correction_factor(fluido1,fluido2,material):
    # Factor de Correção baseado nas Equações descritas pelo Serth
    # Para trocadores de Calor Casco e Tubos
    # O FLUIDO1 É O CASCO, FLUIDO2 PELOS TUBOS
    R=(fluido1['T_entr']-fluido2['T_said'])/(fluido2['T_said']-fluido2['T_entr'])
    P=(fluido2['T_said']-fluido2['T_entr'])/(fluido1['T_entr']-fluido2['T_entr'])
    N=material['Num_passes_casco']
    if R!=1:
        alfa=pow((1-R*P)/(1-P),(float(1/N)))
        S=(alfa-1)/(alfa-R)
        F=(((R**2 + 1)**0.5)*log((1-S)/(1-R*S)))/((R-1)*log((2-S*(R+1-((R**2 + 1)**0.5)))/(2-S*(R+1+((R**2 + 1)**0.5)))))
    else:
         S=P/(N-(N-1)*P)
         F=(S*(2**0.5))/((1-S)*log((2-S*0.5857864376269049)/(2-S*3.414213562373095)))
    return F


def dupl_fact_ser_paral(material):
    # Método descrito por Serth para o cálculo de correntes
    ta=material['Par_T_in']
    tb=material['Par_T_out']
    Ta=material['Ser_T_in']
    Tb=material['Ser_T_out']
    P=(tb-ta)/(Ta-ta)
    R=(Ta-Tb)/(tb-ta)
    x=material['Num_ramos']
    if R!=1:
        F=((R-x)/(x*(R-1)))*(((log((1-P)/(1-P*R)))/(log(((R-x)/(R*pow(1-P*R,1.0/x)))+x/R))))
    else:
        F=(P*(1-x))/((x-x*P)*log((1-x)/pow(1-P,1.0/x)+x))
    return F


















    

