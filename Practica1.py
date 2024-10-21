import json
import time
import queue
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
                if segmento['origin'] == identificador:
                    self.interseccionAccion[identificador].append((
                        segmento['destination'],
                        segmento['distance'] / (segmento['speed'] / 3.6)
                    ))

        self.distancia = problema['segments']['distance']
        self.velocidad = problema['segments']['speed']

        # Distancia en metros y velocidad km/h --> (a lo mejor) m/s Aclaración


class Estado(Problema):

    def __init__(self, longitud, latitud):
        self.longitud = longitud
        self.latitud = latitud

    def __hash__(self):
        return hash((self.longitud, self.latitud))

    def __eq__(self, otro):
        return self.longitud == otro.longitud and self.latitud == otro.latitud


class Accion(Problema):
    def __init__(self, problema: Problema):
        self.problema = problema
        self.count = 0

    def coste(self):
        self.metros = self.problema.distancia
        self.velocidad_m = (self.problema.velocidad / 3.6)  # para así pasarlo a m/s

        return self.metros / self.velocidad_m


class Nodo:

    def __init__(self, id: int, longitud: int, latitud: int, profundidad: int = 0, padre: 'Nodo' = None,
                 coste: float = 0.0, costeMasDistancia: float = 0.0):
        self.id = id
        self.estado = Estado(longitud, latitud)
        self.profundidad = profundidad
        self.padre = padre
        self.coste = coste
        self.costeMasDistancia = costeMasDistancia

    def __eq__(self, otro):
        return self.estado == otro.estado

    def __lt__(self, otro):

        if self.id < otro.id:
            return True
        elif self.id == otro.id:
            return self.coste < otro.coste

        else:
            return False


class Heuristica:

    def __init__(self):
        pass  # No hará nada aparte de usarse la heuristica de manhattan

    def calculo_heuristica(self, estado1: Estado, estado2: Estado):
        # Teniendo en cuenta que estado1 es el origen y estado2 el destino
        return abs(estado1.longitud - estado2.longitud) + abs(estado1.latitud - estado2.latitud)


# Se pone que hereda de ABC para así decir que es una clase Abstracta por lo que cualquiera que herede de esta
# deberá de implementar los metodos que tiene esta misma.
class Busqueda(ABC):
    @abstractmethod
    def insertar_nodo(self, nodo: Nodo, lista_nodo):
        pass

    # def insertarNuevoAbierto(self, nuevoAbierto: Nodo):
    #   self.listaAbiertos.put(nuevoAbierto)

    @abstractmethod
    def extraerNodo(self, lista_nodo):
        pass

    @abstractmethod
    def vacio(self):
        pass

    def __init__(self):
        self.accion = Accion
        self.listaExpantidos = set()
        self.listaAbiertos = None

    def nodoSucesores(self, nodo: Nodo, estadoFinal: Estado, algoritmo: str):
        sucesores = []
        for accion in self.problema.interseccionAccion[nodo.id]:
            nodoNuevo = Nodo(accion[0], self.problema.interseccionesCoordenadas[accion[0]][0],
                             self.problema.interseccionesCoordenadas[accion[0]][1],
                             nodo.profundidad + 1, nodo, nodo.coste + accion[1], 0)

            sucesores.append(nodoNuevo)
        return sucesores

    def Busqueda(self, estadoDeseado: Estado, algoritmo: str):
        longitud, latitud = self.accion.problema.interseccionesCoordenadas[self.accion.problema.inicio]
        nodoProgenitor = Nodo(self.accion.problema.inicio, longitud, latitud)
        self.profundidad = 0
        hashDeseado = hash(estadoDeseado)
        listaExpandidos = set()
        expandidos = 1
        abiertos = 0
        self.listaAbiertos = self.crearListaAbiertos(nodoProgenitor)
        # start = time.time()

        while self.listaAbiertos:
            nodoExpandido = self.extraerAbierto()
            hashExpandido = hash(nodoExpandido)
            if hashExpandido not in listaExpandidos:
                expandidos += 1
                if hashExpandido == hashDeseado:
                    return True
                nuevosAbiertos = self.accion.nodoSucesores(nodoExpandido, estadoDeseado, algoritmo)
                abiertos += len(nuevosAbiertos)
                for abierto in nuevosAbiertos:
                    self.profundidad = max(self.profundidad, abierto.profundidad)
                    self.insertarNuevoAbierto(abierto)
                listaExpandidos.add(hashExpandido)
        return None


class BusquedaAnchura(Busqueda):





    def crearColeccion(self, primerAbierto: Nodo):
        self.listaExpantidos = list()
        self.listaExpantidos.append(primerAbierto)


    def insertar(self, nodoAbierto: Nodo):
        self.listaExpantidos.append(nodoAbierto)


    def extraer(self):
        return self.listaExpantidos.pop(0)



class BusquedaProfundidad(Busqueda):

    def __init__(self):
        super().__init__()



    def insertar_nodo(self, nodo: Nodo, lista_nodo):
        pass

    def extraerNodo(self, lista_nodo):
        pass

    def vacio(self):
        pass
