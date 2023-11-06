#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:52:01 2023

@author: robotica
"""

import tkinter  as tk
from dataclasses import dataclass
from tkinter import messagebox
import math 

#ESTA CLASE PERMITE QUE LA COMPARACIÓN (5,6)==(6,5) SE CUMPLA Y AÑADE EL SWAP
@dataclass
class Ficha:
    a:int
    b: int
    # Ordena siempre del mayor al menor 
    def __init__(self, val1, val2):
        self.a = val1
        self.b = val2

    #Permite hacer la comparacion (5,6) = (6,5)
    def maximo(self):
        val=max(self.a,self.b)
        return val
    def minimo(self):
        val=min(self.a, self.b)
        return val
    
    def __eq__(self, other):
        if (self.maximo() == other.maximo()) and (self.minimo() == other.minimo()):
            return True 
        else:
            return False
    
    def swap(self):
        self.a, self.b = self.b,self.a


#---------------------CONFIGURACIÓN VENTANA 1-----------------------------------
ventana = tk.Tk();
#Creamos la ventana 
ventana.geometry('600x200')
ventana.minsize(200,100)
ventana.resizable(height= True, width= True)

#Titulo del juego 
etiqueta = tk.Label(ventana, text = "Juega al domino conmigo!", bg= "green" )
etiqueta.pack(fill = tk.X)

etiqueta = tk.Label(ventana, text = "Por favor dime con que fichas juego (x,y): ")
etiqueta.pack(side= tk.LEFT)

mis_fichas= tk.Entry(ventana)
mis_fichas.pack(side= tk.LEFT)
#_-----------------------------------------------------------------------------


#Recibe las coordenadas del TextBox y convierte a enteros
def Transf_coord(): 
    tt= mis_fichas.get()
    a=int(tt[0])
    b=int(tt[2])
    return a,b 

#Crea las fichas del juego y remueve las que ingresé en la primera ventana
#fichas es una lista global que contiene las fichas que no tiene la compu  
fichas= []
def Remueve_fichas():
    global mano
    global fichas
    
    #CREA TODAS LAS FICHAS 
    for i in range(7):
      for j in range(7):
        if i<=j:
          d=Ficha(i,j)
          fichas.append(d)
    print(fichas)     
    #ELIMINA LAS FICHAS QUE INGRESÉ DE LAS TOTALES
    for i in range(len(mano)):
        if mano[i] in fichas:
            fichas.remove(mano[i])

    print(fichas)

#Variables globales
mesa=[]
mi_turno = True
movimiento_optimo = None
tira_primero=None
tomadas=0
n_rival=7
pozo=14


#---------------------------------------------VENTANA DE JUEGO ----------------
def Ventana_juego():
    global fichas
    global mano
    global txt
    global mi_turno
    global tira_primero
    
    
    Remueve_fichas()
    
    #----------------CONFIGURACIÓN DE LA VENTANA ------------------------------------
    ventana2 = tk.Tk();
    ventana2.geometry('600x400')
    ventana2.minsize(736,200)
    ventana2.resizable(height= True, width= False)
    tira_primero= messagebox.askquestion("","Yo (Si) o Rival (No)")
    #Titulo del juego 
    etiqueta1 = tk.Label(ventana2, text = "Hora de empezar el juego", bg= "green" )
    etiqueta1.pack(fill = tk.X)
    
    etiqueta2 = tk.Label(ventana2, text = "Mis fichas:")
    etiqueta2.place(x=80, y=100)
    etiqueta5 = tk.Label(ventana2, text = "Ingresa la ficha que vas a tirar: ")
    etiqueta5.place(x=80, y=150)
    ficgame= tk.Entry(ventana2)
    ficgame.place(x=250, y=150)
    txt= ficgame.get()
    ficha_r= tk.Entry(ventana2, state=tk.DISABLED)
    ficha_r.place(x=250, y=225)
    
    robar = tk.Label(ventana2, text = "Necesito tomar fichas",state=tk.DISABLED )
    robar.place(x=80, y=225)
    #--------------------------------------------------------------------------------
    
    #Dice cuantas fichas con el numero ingresado están en las desconocidas
    def cuenta_numeros(numero, lista):
        count=0
        for ficha in lista: 
            if ficha.a == numero or ficha.b == numero:
                count += 1
        return count 
    #Obtiene la probabilidad de que el rival tenga una ficha con "num"                
    def proba_numeros(num): 
        pb = cuenta_numeros(num, fichas) / 7
        return pb 
    #------------------------------------------------------------------------
    
    def poner_ficha(mesa, ficha, derecha = True): # Función para poner una ficha del lado derecho o de lado izquierdo
        
        if len(mesa) == 0:
            return [ficha]
        else:
            nueva_mesa = mesa.copy()
            if derecha:
                if (mesa[-1].b != ficha.a):
                    ficha.swap()
                nueva_mesa.append(ficha)
            else:
                if (mesa[0].a != ficha.b):
                    ficha.swap()
                nueva_mesa.insert(0, ficha)
            return nueva_mesa
        
    def actualizar_fichas(mesa, fichas_a_actualizar, fichas_restantes):
        fichas_actualizadas = fichas_a_actualizar.copy()
        for ficha in (mesa + fichas_restantes):
            if ficha in fichas_actualizadas:
                fichas_actualizadas.remove(ficha)
        return fichas_actualizadas
    
    
    def movimientos_disponibles(mesa, fichas_turno): # Función que regresa lista de piezas que puedes poner, y en donde
        movimientos = []
        if len(mesa)==0:
            for ficha in fichas_turno:
                movimientos.append([ficha, True])
        else:
            derecha = mesa[-1].b
            izquierda = mesa[0].a
            for p in fichas_turno:
                if derecha == p.a or derecha == p.b:
                    movimientos.append([p, True]) # La ficha se guarda en los movimientos disponibles para poner en la derecha
                if izquierda == p.a or izquierda == p.b:
                    movimientos.append([p, False]) # La ficha se guarda en los movimientos disponibles para poner a la izquierda
        return movimientos
    
    def proba_enemigo_robe(mesa, mis_fichas, fichas_sueltas, n_enem):
        
        derecha = mesa[-1].b
        izquierda = mesa[0].a
        
        cant_der = 0
        cant_izq = 0
        
        for ficha in fichas_sueltas:
            if ficha.a == derecha or ficha.b == derecha:
                cant_der += 1
            if ficha.a == izquierda or ficha.b == izquierda:
                cant_izq += 1
        
        proba_der_comp = 1
        proba_izq_comp = 1
        
        for i in range(round(n_enem)):
            proba_der_comp = proba_der_comp * (len(fichas_sueltas) - cant_der - i)/(len(fichas_sueltas) - i)
            proba_izq_comp = proba_izq_comp * (len(fichas_sueltas) - cant_izq - i)/(len(fichas_sueltas) - i)
        
        proba_der = 1 - proba_der_comp
        proba_izq = 1 - proba_izq_comp
        
        if Ficha(izquierda, derecha) in fichas_sueltas:
            proba_int_comp = 1
            for r in range(round(n_enem)):
                proba_int_comp = proba_int_comp * (len(fichas_sueltas) - 1 - r)/(len(fichas_sueltas) - r)
            proba_int = 1 - proba_int_comp
        else:
            proba_int = 0
        
        proba = 1 - (proba_der + proba_izq - proba_int)
        
        return proba
    
    def proba_no_robar(mesa, mis_fichas, fichas_sueltas, n_enem):
        
        izquierda = mesa[0].a
        derecha = mesa[-1].b
        
        numeros_que_no_tengo = [1,2,3,4,5,6,0]
        
        for ficha in mis_fichas:
            if ficha.a in numeros_que_no_tengo:
                numeros_que_no_tengo.remove(ficha.a)
            if ficha.b in numeros_que_no_tengo:
                numeros_que_no_tengo.remove(ficha.b)
        
        fichas_que_me_hacen_robar = []
        
        for i in numeros_que_no_tengo:
            ficha_1 =  Ficha(i,derecha)
            ficha_2 = Ficha(i,izquierda)
            if ficha_1 not in fichas_que_me_hacen_robar:
                fichas_que_me_hacen_robar.append(ficha_1)
            if ficha_2 not in fichas_que_me_hacen_robar:
                fichas_que_me_hacen_robar.append(ficha_2)
        
        proba = 1
        
        for r in range(round(n_enem)):
            proba = proba * (len(fichas_sueltas) - len(fichas_que_me_hacen_robar) - r)/(len(fichas_sueltas) - r)
        
        return proba
        
    
    def heuristica(mesa, mis_fichas, fichas_sueltas, n_enem):
        
        proba_que_robe = proba_enemigo_robe(mesa, mis_fichas, fichas_sueltas, n_enem)
        proba_no_robo = proba_no_robar(mesa, mis_fichas, fichas_sueltas, n_enem)
        
        if n_enem < len(mis_fichas):
            vh = 0.7 * proba_no_robo + 0.3 * proba_que_robe
        elif n_enem == len(mis_fichas):
            vh = 0.5 * proba_que_robe + 0.5 * proba_no_robo
        else:
            vh = 0.3 * proba_no_robo + 0.7 * proba_que_robe
        
        return vh
        

    
    def minimax(mesa, mis_fichas, fichas_restantes, mi_turno):
        global n_rival
        global movimiento_optimo
        minimax_r(mesa, mis_fichas, fichas_restantes, mi_turno, n_rival)
        return movimiento_optimo
        
    
    def minimax_r(mesa, mis_fichas, fichas_restantes, mi_turno, n_enem, profundidad = 7, profundidad_actual = 7):
        
        global movimiento_optimo
        
        if (profundidad_actual == 0):
            r = heuristica(mesa, mis_fichas, fichas_restantes, n_enem)
            return r
        
        if mi_turno:
            valor_optimo = -math.inf
            movimientos = movimientos_disponibles(mesa, mis_fichas)
            #MOVIMIENTOS YA NO PUEDE SER IGUAL A 0 INVERTÍ CONDICIONES
            if len(movimientos) == 0:
                return heuristica(mesa, mis_fichas, fichas_restantes, n_enem) 
            else: 
                for m in movimientos:
                    nueva_mesa = poner_ficha(mesa, m[0], m[1])
                    mis_nuevas_fichas = actualizar_fichas(nueva_mesa, mis_fichas, fichas_restantes)
                    valor = minimax_r(nueva_mesa, mis_nuevas_fichas, fichas_restantes, False, n_enem, profundidad, profundidad_actual-1)                   
                    if movimiento_optimo == None:
                        movimiento_optimo = m      
                    if (profundidad_actual == profundidad and valor_optimo <= valor):
                        movimiento_optimo = m
                        valor_optimo = valor
                    elif valor_optimo <= valor:
                        valor_optimo = valor
                        
                return valor_optimo
          #--------------------------------------------------------------------- 
        else: # Turno de contrincante
            valor_optimo = math.inf
            movimientos = movimientos_disponibles(mesa, fichas_restantes)
            if (len(movimientos) == 0):
                return heuristica(mesa, mis_fichas, fichas_restantes, n_enem)
            else:
                for m in movimientos:
                    nueva_mesa = poner_ficha(mesa, m[0], m[1])
                    nuevas_fichas_restantes = actualizar_fichas(nueva_mesa, fichas_restantes, mis_fichas)
                    n_enem_nuevo = n_enem - 1 
                    valor = minimax_r(nueva_mesa, mis_fichas, nuevas_fichas_restantes, True, n_enem_nuevo, profundidad,  profundidad_actual-1) 
                    if (valor_optimo >= valor):
                        valor_optimo = valor
                        
                return valor_optimo
          
    #------------------------FUNCIONES PARA QUE TIRE EL RIVAL Y COMPUTADORA--------------------------------------------
    def juega_rival(mesa1):
        global pozo
        global n_rival
        txt= ficgame.get()
        c=int(txt[0])
        d=int(txt[2])
        if pozo ==0:
            b_pasar.config(state=tk.NORMAL)
        if c <= 6 and d <= 6 :
          #Ficha ingresada
          pl= Ficha(c,d)   
          #Revisa que no sea parte de las fichas de la compu 
          if pl in fichas:
              if len(mesa1) != 0:
                respuesta= messagebox.askquestion("","Izquierda (Si) o Derecha (No)")
                m= [mesa1[0].a, mesa1[-1].b]
                if respuesta== "yes":
                    #REVISA QUE LA FICHA COINCIDA CON EL EXTREMO DE LADO IZQUIERDO 
                    #ORDENA LA FICHA PARA QUE COINCIDAN LOS EXTREMOS 
                    if m[0] == pl.b or m[0] == pl.a:
                        if m[0] != pl.b:
                            pl.swap()
                        mesa1.insert(0,pl)
                        ficgame.delete(0,tk.END)
                        n_rival=n_rival-1
                        resultados_juego(n_rival)
                     
                    else: 
                        messagebox.showwarning("ERROR", "No es posible tirar esa ficha")
                  
                else:                           
                    if m[1] == pl.a or m[1] == pl.b:
                        if m[1] != pl.a:
                            pl.swap()
                        mesa1.append(pl)
                        ficgame.delete(0,tk.END)
                        n_rival=n_rival-1
                        resultados_juego(n_rival)
                    else:
                        messagebox.showwarning("ERROR", "No es posible tirar esa ficha")
              else:
                mesa1.append(pl)
                ficgame.delete(0,tk.END)
          else:
            messagebox.showwarning("ERROR", "No es posible tirar esa ficha")
            ficgame.delete(0,tk.END)
        else:
          messagebox.showwarning("ERROR", "No existe esa ficha")
          ficgame.delete(0,tk.END)
          
        for i in range(len(mesa)):
            if mesa1[i] in fichas:
                fichas.remove(mesa1[i])
              
        for i in range(0,7):
            n= proba_numeros(i)
            print(f"Probabilidad de que el rival tenga una ficha con el numero {i} es: {n:.2f}")
        print("NUEVO TIRO")
       
    #DECIDE RESPECTO A QUIEN TIRA PRIMERO, SI ES LA COMPUTADORA ENTONCES
    #LE TOCA TIRAR LOS NÚMEROS PARES, EN CASO CONTRARIO LOS IMPARES
    def juega_minimax(mesa2):
        global mano
        global tira_primero
        global pozo
        if tira_primero == "yes":
            if len(mesa2) % 2 != 0:
                b3.config(state=tk.NORMAL)
            else: 
                b3.config(state=tk.DISABLED)
                lista_prueba = movimientos_disponibles(mesa2, mano)
                
                #Si no hay movimientos disponibles entonces habilito el ingreso de fichas
                #comidas del pozo, si ya no hay pozo "Paso"
                if len(lista_prueba) == 0:
                    if pozo > 0:
                        robar.config(state=tk.NORMAL)
                        ficha_r.config(state=tk.NORMAL)
                        b_robar.config(state=tk.NORMAL)
                        b3.config(state=tk.DISABLED)
                        ficgame.config(state=tk.DISABLED)
                        lista_prueba = movimientos_disponibles(mesa2, mano)
                        pozo=pozo-1
                    else:
                        messagebox.showwarning("Mensaje", "Paso")
                        b3.config(state=tk.NORMAL)
                else:
                    #Para cada tiro imprime las probabilidades de que el rival tenga una ficha con x numero 
                    #Imprime el numero de fichas del rival y las que quedan en el pozo 
                    ficha_r.delete(0,tk.END)
                    ficha_r.config(state=tk.DISABLED)
                    b_robar.config(state=tk.DISABLED)
                    ficgame.config(state=tk.NORMAL)
                    vo=minimax(mesa2, mano, fichas, True)
                    print(vo[0])
                    print(vo[1])
                    ficha = vo[0]
                    if vo[1] == True: 
                        if ficha.a != mesa2[-1].b:
                            ficha.swap()
                        mesa2.append(ficha)
                        b3.config(state=tk.NORMAL)
                        mano.remove(ficha)
                        print("El numero de fichas del rival")
                        print(n_rival)
                        resultados_juego(n_rival)
                        print(pozo)
                    else:
                        if ficha.b != mesa2[0].a:
                            ficha.swap()
                        mesa2.insert(0,ficha)
                        b3.config(state=tk.NORMAL)
                        mano.remove(ficha)
                        print("El numero de fichas del rival")
                        print(n_rival)
                        resultados_juego(n_rival)
                        print(pozo)
        else:
            if len(mesa2) % 2 == 0:
                b3.config(state=tk.NORMAL)
            else: 
                b3.config(state=tk.DISABLED)
                # Propuesta
                lista_prueba = movimientos_disponibles(mesa2, mano)
                if len(lista_prueba) == 0:
                    if pozo > 0:
                        robar.config(state=tk.NORMAL)
                        ficha_r.config(state=tk.NORMAL)
                        b_robar.config(state=tk.NORMAL)
                        b3.config(state=tk.DISABLED)
                        ficgame.config(state=tk.DISABLED)
                        lista_prueba = movimientos_disponibles(mesa2, mano)
                        pozo=pozo-1
                    else:
                        messagebox.showwarning("Mensaje", "Paso")
                        b3.config(state=tk.DISABLED)
                else:
                    ficha_r.delete(0,tk.END)
                    ficha_r.config(state=tk.DISABLED)
                    b_robar.config(state=tk.DISABLED)
                    ficgame.config(state=tk.NORMAL)
                    vo=minimax(mesa2, mano, fichas, True)
                    print(vo[0])
                    print(vo[1])
                    ficha = vo[0]
                    if vo[1] == True: 
                        if ficha.a != mesa2[-1].b:
                            ficha.swap()
                        mesa2.append(ficha)
                        b3.config(state=tk.NORMAL)
                        mano.remove(ficha)
                        print("El numero de fichas del rival")
                        print(n_rival)
                        resultados_juego(n_rival)
                        print(pozo)
                    else:
                        if ficha.b != mesa2[0].a:
                            ficha.swap()
                        mesa2.insert(0,ficha)
                        b3.config(state=tk.NORMAL)
                        mano.remove(ficha)
                        print("El numero de fichas del rival")
                        print(n_rival)
                        resultados_juego(n_rival)
                        print(pozo)
        
        #Imprimimos la mesa, como la extensión puede ser muy larga y no cabe en la ventana 
        #la dividimos en 4 renglones de lectura izquierda a derecha 
        if len(mesa2) < 7:
            mess3 = tk.Label(ventana2, text=mesa2)
            mess3.place(x=80, y=300)
        else: 
            mesa_aux=mesa2.copy()
            mesa2_pt1=[]
            mesa2_pt2=[]
            mesa2_pt3=[]
            mesa2_pt4=[]
            for i in range(0,6):
                mesa2_pt1.append(mesa_aux[i])
            for i in range(7,len(mesa)):
                mesa2_pt2.append(mesa_aux[i])
            for i in range(14,len(mesa)):
                mesa2_pt3.append(mesa_aux[i])
            for i in range(21,len(mesa)):
                mesa2_pt4.append(mesa_aux[i])
   
            mesa_pt1 = tk.Label(ventana2, text=mesa2_pt1)
            mesa_pt1.place(x=80, y=300)
            mesa_pt2 = tk.Label(ventana2, text=mesa2_pt2)
            mesa_pt2.place(x=80, y=320)
            mesa_pt3 = tk.Label(ventana2, text=mesa2_pt3)
            mesa_pt3.place(x=80, y=340)
            mesa_pt4 = tk.Label(ventana2, text=mesa2_pt4)
            mesa_pt4.place(x=80, y=360)
                
                
                
        etiqueta3 = tk.Label(ventana2, text=mano)
        etiqueta3.place(x=150, y=100)
        mess3 = tk.Label(ventana2, text=mesa2)
        mess3.place(x=80, y=300)
        
    b3 = tk.Button(ventana2, text="Ingresar", command= lambda:[juega_rival(mesa),juega_minimax(mesa)])
    b3.place(x=400, y=150)
    #-----------------------------ACÁ TERMINA EL TIRO DE JUGADORES-----------------------------
    
    
    #---------------------------------------BOTON PASAR----------------------------------
    b_pasar = tk.Button(ventana2, text="Paso", command=juega_minimax, state=tk.DISABLED)
    b_pasar.place(x=535, y=150)

    #-----------------------LA COMPUTADORA TIENE QUE TOMAR FICHAS DEL POZO----------------------
    def tomo_fichas():
        global mano 
        global fichas 
        txt= ficha_r.get()
        c=int(txt[0])
        d=int(txt[2])
        fr=Ficha(c,d)
        if fr in fichas:
            mano.append(fr)
            fichas.remove(fr)
            ficha_r.delete(0,tk.END)
        else:
            messagebox.showwarning("ERROR", "No puedes robar esta ficha")
    
    b_robar = tk.Button(ventana2, text="Ingresar", command=lambda: [tomo_fichas(),juega_minimax(mesa)], state=tk.DISABLED)
    b_robar.place(x=425, y=225)    
    
    #----------------SI PRESIONO EL BOTÓN "TOMÉ" INDICA QUE SE TOMARON FICHAS DEL --------------
    # ---------------POZO ANTES DE REALIZAR EL TIRO Y HABILITA EL ALGORTMO DE ABAJO-------------
    def activa_ingreso():
        ficgame.config(state=tk.DISABLED)
        b3.config(state=tk.DISABLED)
        come.config(state=tk.NORMAL)
        ing.config(state=tk.NORMAL)
        comidas.config(state=tk.NORMAL)
    
    rival_toma_fichas = tk.Button(ventana2, text="Tome", command= activa_ingreso)
    rival_toma_fichas.place(x=470, y=150)
    
    #---------------------PROCESO PARA INGRESAR CUANTAS FICHAS COMIO EL RIVAL-----------------
    def regresa_normalidad():
        ficgame.config(state=tk.NORMAL)
        b3.config(state=tk.NORMAL)
        come.config(state=tk.DISABLED)
        ing.config(state=tk.DISABLED)
        comidas.config(state=tk.DISABLED)
        
    def recibe_fichas():
        global tomadas
        global pozo
        global n_rival 
        txt= come.get()
        if pozo >= int(txt[0]):
            tomadas=int(txt[0])
            pozo=pozo-tomadas
            n_rival= n_rival+tomadas
            come.delete(0, tk.END)
        else:
            messagebox.showwarning("ERROR", "No puedes tomar tantas fichas")
            
        
        
    ing = tk.Button(ventana2, text="Ingresar", command= lambda:[recibe_fichas(), regresa_normalidad()], state=tk.DISABLED)
    ing.place(x=400, y=185)
    come= tk.Entry(ventana2, state=tk.DISABLED)
    come.place(x=260, y=185)
    comidas = tk.Label(ventana2, text = "Ingresa cuantas fichas comiste: ", state=tk.DISABLED)
    comidas.place(x=80, y=185)
    
    #----------------FUNCIÓN PARA ESTABLECER QUÉ SE HACE SI TIRA PRIMERO MINIMAX---------------
    def tira_primero_minimax(mesa4): 
        global mano
        global fichas 
        
        if len(mesa4) == 0:
            b3.config(state=tk.DISABLED)
            va=minimax(mesa4,mano,fichas,True)    
            mesa.append(va[0])
            mano.remove(va[0])
            b3.config(state=tk.DISABLED)
            mess3 = tk.Label(ventana2, text=mesa)
            mess3.place(x=80, y=300)
        else:
            b3.config(state=tk.NORMAL)
            
    #Se manda a llamar la función anterior y se habilita el boton de ingreso después de tirar
    if tira_primero == "yes":
        tira_primero_minimax(mesa)
        if len(mesa) != 0: 
            b3.config(state=tk.NORMAL)
        
    #--------------------FUNCION QUE DEFINE EL RESULTADO DEL JUEGO----------------------   
    def resultados_juego(numero_fichas_rival):
        global mano
        global mesa
        global pozo
        juego_cerrado=False
        ext1=mesa[0].a 
        ext2=mesa[-1].b
        num_ext1=mesa.count(ext1)
        num_ext2=mesa.count(ext2)
        if num_ext1 == 8 and num_ext2 == 8:
            juego_cerrado=True 
            
        if len(mano)==0:
            messagebox.showwarning("Resultado", "YO GANÉ B)")
            
        elif numero_fichas_rival == 0:
            messagebox.showwarning("Resultado", "GANASTE ):") 
            
        elif juego_cerrado: 
            messagebox.showwarning("Resultado", "EMPATE") 
    
    mess = tk.Label(ventana2, text = "MESA DE JUEGO:")
    mess.place(x=80, y=275)
    
#----------RECIBE LAS FICHAS PARA LA COMPUTADORA Y VERIFICA QUE LO INGRESADO CUMPLA ------------ 
#----------CON LAS REGLAS DEL JUEGO, EN CASO CONTRARIO ENVÍA MENSAJES SEGÚN EL CASO ------------
mano= []
def button_command():    
    global mano
    fi= Transf_coord()
    #Nos dice si ya tenemos las 7 fichas
    if len(mano) <= 6:
            #Nos indica si la ficha ingresada es valida
            if fi[0] <= 6 and fi[1] <= 6:
                d= Ficha(fi[0], fi[1])
                if not(d in mano):
                    mano.append(d)
                    #Borra el contenido del TextBox
                    mis_fichas.delete(0,tk.END)
                else:
                    messagebox.showwarning("ERROR", "Esa ficha ya la ingresaste")
                    mis_fichas.delete(0,tk.END)
            else: 
                messagebox.showwarning("ERROR", "Esa ficha no existe!")
                mis_fichas.delete(0,tk.END)
    else:
        
        mis_fichas.delete(0,tk.END)
        respuesta= messagebox.askquestion("", "Empezamos?",)
        if respuesta == "yes":
          Ventana_juego()
          ventana.destroy()
        else:
          ventana.destroy()
        
    return None


        
b1 = tk.Button(ventana, text="Ingresar", command=  button_command)
b1.place(x=370, y=100)

ventana.mainloop();