# -*- coding: utf-8 -*-
"""Copia de RetoAgentes.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1A5fwZVusZAaw47wMr523psnE5obdUCGF

#Reto: Movilidad Urbana
### Emiliano García Aguirre A00827638
### Juan Pablo David Lerma A01283879
### Valeria Moreno Elizondo A01280603
### Jesús Urquídez Calvo A00828368


Link de Colab: https://colab.research.google.com/drive/19sJ7zU3ErFyVfG4YgArFp4XshH-RA4lS?usp=sharing

Link de repositorio: https://github.com/JesusU076/Multiagentes
"""

#from google.colab import drive
#drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %cd "/content/drive/MyDrive/TC2008B"

# Commented out IPython magic to ensure Python compatibility.
#from vector import Vector

#!pip install mesa
from mesa import Agent, Model 

from mesa.space import MultiGrid

from mesa.time import SimultaneousActivation

from mesa.time import BaseScheduler

from mesa.datacollection import DataCollector
# mathplotlib lo usamos para graficar/visualizar como evoluciona el autómata celular.
# %matplotlib inline
'''
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128
'''
# Install pyngrok to propagate the http server
'''
# Load the required packages
from pyngrok import ngrok
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import os
'''
import numpy as np
import pandas as pd

import time
import datetime
import random

def sum_tuple(x, y):
  return(x[0] + y[0], x[1] + y[1])

def get_grid(model):
    grid = np.zeros((model.grid.width, model.grid.height))

    for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        for obj in cell_content:
          if isinstance(obj, Carro):
            grid[x][y] = 4
          elif isinstance(obj, Celda):
            grid[x][y] = obj.estado
          #elif isinstance(obj, Semaforo):
            #grid[x][y] = obj.estado
          elif isinstance(obj, Luz):
            grid[x][y] = obj.estado
    return grid

class Carro(Agent):

  def __init__(self, unique_id, model, direction):
    super().__init__(unique_id, model)
    self.sig_pos = None
    self.moves = 0
    self.direction = direction
    self.cont = 0
    self.estilo = random.randint(0,3)

  def step(self):
    if(not self.pos == None):
      change = 1
      vecinos = self.model.grid.get_neighbors(
          self.pos, 
          moore = False,
          include_center = True)
      
      a = sum_tuple(self.pos, self.direction)

      for vecino in vecinos:
        if isinstance(vecino, Semaforo) and vecino.pos == a:
          if (vecino.estado == 5 and self.direction == (1,0)) or (vecino.estado == 1 and self.direction == (0,1)):
            pepe = 1
          else:
            change = 0

      if change:
        for vecino in vecinos:
          if isinstance(vecino, Celda) and vecino.pos == a:
            self.model.grid.move_agent(self, a)
            self.pos = a
            self.cont += 1

      if(self.cont == 8):
        self.model.grid.remove_agent(self)
    else: 
      self.pos = (-1,-1)

class Celda(Agent):
  # 1 -> sucio
  # 0 -> limpio

  def __init__(self, unique_id, model, estado):
    super().__init__(unique_id, model)
    self.pos = unique_id
    self.estado = estado
    self.sig_estado = None

class Luz(Agent):

  def __init__(self, unique_id, model, orientacion):
    super().__init__(unique_id, model)
    self.pos = unique_id
    self.estado = 3
    self.orientacion = orientacion

  def step(self):
    vecinos = self.model.grid.get_neighbors(
        self.pos, 
        moore = True,
        include_center = False)
    for vecino in vecinos:
      if isinstance(vecino, Semaforo):
        if self.orientacion == 1:
          self.estado = vecino.estado
        else:
          self.estado = 6 - vecino.estado


class Semaforo(Agent):
  def __init__(self, unique_id, model, ticks):
    super().__init__(unique_id, model)
    self.ticks = ticks
    self.pos = unique_id
    self.estado = 3
    self.otro = 3
    self.tiempo = 0

  def step(self):
    up = sum_tuple(self.pos, (1,0))
    down = sum_tuple(self.pos, (-1,0))
    left = sum_tuple(self.pos, (0,-1))
    right = sum_tuple(self.pos, (0,1))

    vecinos = self.model.grid.get_neighbors(
        self.pos, 
        moore = False,
        include_center = False)
    
    change = 1

    if self.tiempo == 0:
      for vecino in vecinos:
        if isinstance(vecino, Carro) and (vecino.pos == up or vecino.pos == down):
          self.tiempo = self.ticks
          self.estado = 5
          break

      if self.tiempo == 0:
        for vecino in vecinos:
          if isinstance(vecino, Carro) and (vecino.pos == right or vecino.pos == left):
            self.tiempo = self.ticks
            self.estado = 1
            break
      
      if self.tiempo == 0:
        self.estado = 3

    elif self.tiempo > 0:
      self.tiempo -= 1

class Habitacion(Model):
  def __init__(self, ticks):
    self.grid = MultiGrid(9, 9, False)
    self.schedule = BaseScheduler(self)
    self.ticks = ticks
    self.cont = 0
    self.lista_carros = list()
    self.lista_luces = list()

    for(content, x, y) in self.grid.coord_iter():
      if x == 4 or y == 4:
        a = Celda((x,y), self, 2)
      else:
        a = Celda((x,y), self, 0)
      self.grid.place_agent(a,(x,y))
      self.schedule.add(a)

    #Agentes

    #Carro
    r = Carro(self.cont, self, (1,0))
    self.cont = self.cont + 1
    self.grid.place_agent(r, (0,4))
    self.schedule.add(r)
    self.lista_carros.append(r)

    #Semaforo
    r = Semaforo(self.cont, self, self.ticks)
    self.cont = self.cont + 1
    self.grid.place_agent(r, (4,4))
    self.schedule.add(r)

    #Luces
    r = Luz(self.cont, self, 1)
    self.cont = self.cont + 1
    self.grid.place_agent(r, (3,3))
    self.schedule.add(r)
    self.lista_luces.append(r)
    r = Luz(self.cont, self, 0)
    self.cont = self.cont + 1
    self.grid.place_agent(r, (5,5))
    self.schedule.add(r)
    self.lista_luces.append(r)

    self.datacollector = DataCollector(
        model_reporters = {"Grid":get_grid}, 
        agent_reporters = {'Movimientos': lambda a: getattr(a, 'movimientos', None),
                           'Posicion': lambda a: getattr(a, 'sig_pos', None)}
        )
  
  def infoAgentes(self):
    data = list()
    for c in self.lista_carros:
      posicion ={'x': c.pos[0], 'y': 0.5, 'z': c.pos[1]} 
      data.append({'position': posicion, "kind": "Carro", "colour": c.estilo})
    for l in self.lista_luces:
      posicionLuz ={'x': -1, 'y': -1, 'z': -1} 
      data.append({'position': posicionLuz, "kind": "Luz", "colour": l.estado})
    return data

  def step(self):
    
    #Simulacion
    p = 1
    while(p < 4):
      num = random.randint(0,5)
      num = 1
      if(num == 1):
        r = Carro(self.cont, self, (1,0))
        self.cont = self.cont + 1
        self.grid.place_agent(r, (0,4))
        self.schedule.add(r)
        self.lista_carros.append(r)
        p += 1

      num = random.randint(0,5)
      if(num == 1):
        r = Carro(self.cont, self, (0,1))
        self.cont = self.cont + 1
        self.grid.place_agent(r, (4,0))
        self.schedule.add(r)
        self.lista_carros.append(r)
        p += 1
      

      self.datacollector.collect(self)
      self.schedule.step()