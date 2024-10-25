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

    def __repr__(self):
        padre_id = self.padre.id if self.padre is not None else None
        return f"Nodo(id={self.id}, longitud={self.longitud}, latitud={self.latitud}, padre={padre_id}, coste={self.coste})"

    def __eq__(self, otro):
        return hash(self.estado) == hash(otro)

    def __hash__(self):
        return hash(self.estado)

    def __lt__(self, otro):
        if self.coste != otro.coste:
            return self.coste < otro.coste
        return self.id < otro.id

class Heuristica:
    @staticmethod
    def calculo_heuristica(estado1: Estado, tuplaCoordenadas):
        return abs(estado1.longitud - tuplaCoordenadas[0]) + abs(estado1.latitud - tuplaCoordenadas[1])


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
        expandidos = 1
        abiertos = 0
        tiempo_inicio = timeit.default_timer()
        self.listaAbiertos = self.insertarNodo(nodoProgenitor, self.listaAbiertos)
        while not self.vacio():
            nodoExpandido = self.extraerNodo(self.listaAbiertos)
            estadoNodoExpandido = Estado(nodoExpandido.id, nodoExpandido.longitud, nodoExpandido.latitud)
            if estadoNodoExpandido not in listaExpandidos:
                expandidos += 1
                if estadoNodoExpandido.__eq__(estadoFinal):
                    tiempo_final = timeit.default_timer()
                    segundos = tiempo_final - tiempo_inicio
                    self.camino(segundos, expandidos, abiertos, self.profundidad, nodoExpandido, listaExpandidos)
                    return "Retorno del metodo buscar() = Exito"
                nuevosAbiertos = self.nodosSucesores(nodoExpandido)
                abiertos += len(nuevosAbiertos)
                for abierto in nuevosAbiertos:
                    self.profundidad = max(profundidad, abierto.profundidad)
                    self.insertarNodo(abierto, self.listaAbiertos)
                    listaExpandidos.add(nodoExpandido)
        return "Retorno del metodo buscar() = Fracaso"

    def camino(self, segundos, expandidos, abiertos, profundidad, nodoExpandido, listaExpantidos):
        print(f" Tiempo empleado: {segundos:.10f} segundos")
        print("Nodos expandidos: ", expandidos)
        print("  Nodos abiertos: ", abiertos)
        print("     Profundidad: ", profundidad)
        print("    Nodo destino: ", nodoExpandido)
        print("             Fin: ",self.problema.final)
        print("          Origen: ",self.problema.inicio)
        #print("Lista expandidos: ", listaExpantidos)
        nodo = nodoExpandido
        lista = []
        while nodo.padre is not None:
            lista.append([(nodo.padre.id),(nodo.id),(nodo.coste)])
            nodo = nodo.padre
        lista = reversed(lista)
        print("Camino")
        for x in lista:
            print(f"{x[0]} ------({x[2]:<19})-----> {x[1]}")

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

    def vacio(self):
        return len(self.listaAbiertos) == 0


class BusquedaProfundidad(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = []

    def insertarNodo(self, nodo, listaNodos):
        listaNodos.append(nodo)
        return listaNodos

    def extraerNodo(self, listaNodos):
        valor = listaNodos.pop()
        return valor

    def vacio(self):
        return len(self.listaAbiertos) == 0


class PrimeroMejor(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = queue.PriorityQueue()


    def insertarNodo(self, nodo, listaNodos):
        disManh = Heuristica.calculo_heuristica(nodo.estado, self.problema.interseccionesCoordenadas[self.problema.final])
        nodo.costeMasDistancia = disManh
        listaNodos.put((nodo.costeMasDistancia, nodo))
        return listaNodos

    def extraerNodo(self, listaNodos):
        return listaNodos.get()[1]

    def vacio(self):
        return self.listaAbiertos.empty()


class AEstrella(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = queue.PriorityQueue()

    def insertarNodo(self, nodo, listaNodos):
        disManh = Heuristica.calculo_heuristica(nodo.estado, self.problema.interseccionesCoordenadas[self.problema.final])
        nodo.costeMasDistancia = disManh + nodo.coste
        listaNodos.put((nodo.costeMasDistancia, nodo))
        return listaNodos

    def extraerNodo(self, listaNodos):
        return listaNodos.get()[1]

    def vacio(self):
        return self.listaAbiertos.empty()


if __name__ == "__main__":
    while True:
        print("         1) Búsqueda en Anchura")
        print("         2) Búsqueda en Profundidad")
        print("         3) Primero es mejor")
        print("         4) A Estrella")
        print("Otro valor) Salir")
        try:
            valor = int(input("Introduce un valor numérico, por favor: "))
        except ValueError:
            print("Ese no es un número válido.")
            continue

        match valor:
            case 1:
                z = BusquedaAnchura()
            case 2:
                z = BusquedaProfundidad()
            case 3:
                z = PrimeroMejor()
            case 4:
                z = AEstrella()
            case _:
                print("Fin programa.....")
                break

        print(z.buscar(Estado(z.problema.final,
                              z.problema.interseccionesCoordenadas[z.problema.final][0],
                              z.problema.interseccionesCoordenadas[z.problema.final][1])))
