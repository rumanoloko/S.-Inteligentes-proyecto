import json
import time
import queue
import timeit
from abc import abstractmethod, ABC



class Problema:
    def __init__(self):
        nombre_archivo = r"C:\Users\Vlad\OneDrive - Universidad de Castilla-La Mancha\Escritorio\S.-Inteligentes-proyecto\avenida_de_espania_250_0.json"
        with open(nombre_archivo, 'r') as archivo:
            problema = json.load(archivo)

        self.inicio = problema['initial']
        self.final = problema['final']
        self.interseccionAccion = {}
        self.interseccionesCoordenadas = {}

        for interseccion in problema['intersections']:
            identificador = interseccion['identifier']
            self.interseccionesCoordenadas[identificador] = (interseccion['longitude'], interseccion['latitude'])
            self.interseccionAccion[identificador] = []

        for segmento in problema['segments']:
            self.interseccionAccion[segmento['origin']].append((
                segmento['destination'],
                segmento['distance'] / (segmento['speed'] / 3.6)
            ))

class Estado():

    def __init__(self, id, longitud, latitud):
        self.id = id
        self.longitud = longitud
        self.latitud = latitud

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, otro):
        return self.id == otro.id

class Nodo:

    def __init__(self, id, longitud, latitud, profundidad= 0, padre = None,
                 coste = 0.0, costeMasDistancia = 0.0):
        self.id = id
        self.longitud = longitud
        self.latitud = latitud
        self.estado = Estado(self.id, self.longitud, self.latitud)
        self.profundidad = profundidad
        self.padre = padre
        self.coste = coste
        self.costeMasDistancia = costeMasDistancia

    def __eq__(self, otro):
        return hash(self.estado) == hash(otro)
    def __hash__(self):
        return hash(self.estado)
    def __lt__(self, otro):

        if self.id < otro.id:
            return True
        elif self.id == otro.id:
            return self.coste < otro.coste

        else:
            return False


class Heuristica:

    def calculo_heuristica(self, estado1: Estado, estado2: Estado):
        return abs(estado1.longitud - estado2.longitud) + abs(estado1.latitud - estado2.latitud)


# Se pone que hereda de ABC para así decir que es una clase Abstracta por lo que cualquiera que herede de esta
# deberá de implementar los metodos que tiene esta misma.
class Busqueda(ABC):

    def __init__(self):
        self.problema = Problema()
        self.listaExpantidos = set()
        self.listaAbiertos = None

    @abstractmethod
    def insertarNodo(self, nodo, listaNodos):
        pass

    @abstractmethod
    def extraerNodo(self, listaNodos):
        pass

    @abstractmethod
    def vacio(self, lista_nodo):
        pass

    def nodosSucesores(self, nodo):
        sucesores = []
        for accion in self.problema.interseccionAccion[nodo.id]:
            nodoNuevo = Nodo(accion[0], self.problema.interseccionesCoordenadas[accion[0]][0],
                             self.problema.interseccionesCoordenadas[accion[0]][1],
                             nodo.profundidad + 1, nodo, nodo.coste + accion[1])
            sucesores.append(nodoNuevo)
        return sucesores

    def buscar(self, estadoFinal):
        longitud, latitud = self.problema.interseccionesCoordenadas[self.problema.inicio]
        nodoProgenitor = Nodo(self.problema.inicio, longitud, latitud)
        profundidad = 0
        listaExpandidos = set()
        listaExpandidos.add(1)
        expandidos = 1
        abiertos = 0
        tiempo_inicio = timeit.default_timer()
        self.listaAbiertos = self.insertarNodo(nodoProgenitor, self.listaAbiertos)
        print(len(self.listaAbiertos))
        while self.listaAbiertos:
            nodoExpandido = self.extraerNodo(self.listaAbiertos)
            estadoNodoExpandido = Estado(nodoExpandido.id, nodoExpandido.longitud, nodoExpandido.latitud)
            if estadoNodoExpandido not in listaExpandidos:
                expandidos += 1
                if estadoNodoExpandido.__eq__(estadoFinal):
                    tiempo_final = timeit.default_timer()
                    segundos = tiempo_final - tiempo_inicio
                    print("Estado        actual: ", estadoNodoExpandido.id)
                    print("Estado final deseado: ", estadoFinal.id)
                    print(f"{segundos:.10f} segundos")
                    print(self.listaExpantidos)
                    return True
                nuevosAbiertos = self.nodosSucesores(nodoExpandido)
                abiertos += len(nuevosAbiertos)
                for abierto in nuevosAbiertos:
                    self.profundidad = max(profundidad, abierto.profundidad)
                    self.insertarNodo(abierto, self.listaAbiertos)
                listaExpandidos.add(nodoExpandido)
        return None

class BusquedaAnchura(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = []

    def insertarNodo(self, nodo, listaNodos):
        listaNodos.append(nodo)
        return listaNodos

    def extraerNodo(self, listaNodos):
        valor = listaNodos.pop(0)
        return valor

    def vacio(self, lista_nodo):
        if len(lista_nodo) == 0:
            return True
        else:
            return False


class BusquedaProfundidad(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = []

    def crearLista(self, nodo):
        lista = []
        lista.append(nodo)
        return lista

    def insertarNodo(self, nodo, listaNodos):
        listaNodos.append(nodo)
        return listaNodos

    def extraerNodo(self, listaNodos):
        valor = listaNodos.pop()
        return valor

    def vacio(self, lista_nodo):
        if len(lista_nodo) == 0:
            return True
        else:
            return False


class PrimeroMejor(Busqueda):

    def __init__(self):
        super().__init__()

    def crearLista(self, nodo):
        pass

    def insertar_nodo(self, nodo, listaNodos):
        pass

    def extraerNodo(self, listaNodos):
        pass

    def vacio(self):
        pass


class AEstrella(Busqueda):

    def __init__(self):
        super().__init__()

    def crearLista(self, nodo):
        pass

    def insertarNodo(self, nodo, listaNodos):
        pass

    def extraerNodo(self, listaNodos):
        pass

    def vacio(self):
        pass

ba = BusquedaAnchura()

print(ba.buscar(Estado(ba.problema.final, ba.problema.interseccionesCoordenadas[ba.problema.final][0],
                      ba.problema.interseccionesCoordenadas[ba.problema.final][1])))
