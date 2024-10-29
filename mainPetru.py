import json
import time
import queue
import timeit
from abc import abstractmethod, ABC


class Problema:
    def __init__(self, info_json):
        # nombre_archivo = r"C:\Users\Vlad\OneDrive - Universidad de Castilla-La Mancha\Escritorio\S.-Inteligentes-proyecto\avenida_de_espania_250_0.json"
        # nombre_archivo = r"C:\Users\Vlad\OneDrive - Universidad de Castilla-La Mancha\Escritorio\S.-Inteligentes-proyecto\calle_de_francisco_5000_3.json"
        #nombre_archivo = r"C:\Users\Vlad\OneDrive - Universidad de Castilla-La Mancha\Escritorio\S.-Inteligentes-proyecto\calle_agustina_aroca_albacete_5000_0.json"
        with open(info_json, 'r') as archivo:
            problema = json.load(archivo)

        self.inicio = problema['initial']
        self.final = problema['final']
        self.interseccionAccion = {}
        self.interseccionesCoordenadas = {}
        self.velMax = 0
        for interseccion in problema['intersections']:
            identificador = interseccion['identifier']
            self.interseccionesCoordenadas[identificador] = (interseccion['longitude'], interseccion['latitude'])

        for segmento in problema['segments']:
            if segmento['origin'] not in self.interseccionAccion:
                self.interseccionAccion[segmento['origin']] = queue.PriorityQueue()
            self.velMax = max(self.velMax, segmento['speed'])
            self.interseccionAccion[segmento['origin']].put((
                segmento['destination'],
                segmento['distance'] / (segmento['speed'] / 3.6)
            ))


class Estado:

    def __init__(self, id, longitud, latitud):
        self.id = id
        self.longitud = longitud
        self.latitud = latitud

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, otro):
        return self.id == otro.id


class Nodo:

    def __init__(self, id, longitud, latitud, profundidad=0, padre=None,
                 coste=0.0):
        self.id = id
        self.longitud = longitud
        self.latitud = latitud
        self.estado = Estado(self.id, self.longitud, self.latitud)
        self.profundidad = profundidad
        self.padre = padre
        self.coste = coste


    def __repr__(self):
        padre_id = self.padre.id if self.padre is not None else None
        return f"Nodo(id={self.id}, longitud={self.longitud}, latitud={self.latitud}, padre={padre_id}, coste={self.coste})"

    def __eq__(self, otro):
        return isinstance(otro, Nodo) and self.id == otro.id

    def __hash__(self):
        return hash(self.estado)

    def __lt__(self, otro):
        if self.coste != otro.coste:
            return self.coste < otro.coste
        return self.id < otro.id


class Heuristica:

    def calculo_heuristica(estado1: Estado, tuplaCoordenadas, velMax):
        return abs(estado1.longitud - tuplaCoordenadas[0]) + abs(estado1.latitud - tuplaCoordenadas[1]) / (velMax / 3.6)


# Se pone que hereda de ABC para así decir que es una clase Abstracta por lo que cualquiera que herede de esta
# deberá de implementar los metodos que tiene esta misma.
class Busqueda(ABC):

    def __init__(self):
        self.problema = Problema()
        self.listaExpandidos = None
        self.listaAbiertos = None

    @abstractmethod
    def insertarNodo(self, nodo, lista_nodos):
        pass

    @abstractmethod
    def extraerNodo(self, lista_nodos):
        pass

    @abstractmethod
    def vacio(self, lista_nodo):
        pass

    def nodosSucesores(self, nodo):
        sucesores = []
        if nodo.id in self.problema.interseccionAccion:
            pq = self.problema.interseccionAccion[nodo.id]
            while not pq.empty():
                accion = pq.get()
                nodoNuevo = Nodo(accion[0], self.problema.interseccionesCoordenadas[accion[0]][0],
                                 self.problema.interseccionesCoordenadas[accion[0]][1],
                                 nodo.profundidad + 1, nodo, nodo.coste + accion[1])
                sucesores.append(nodoNuevo)
        return sucesores

    def buscar(self, estadoFinal):
        longitud, latitud = self.problema.interseccionesCoordenadas[self.problema.inicio]
        nodo_progenitor = Nodo(self.problema.inicio, longitud, latitud)
        profundidad = 0
        lista_expandidos = set()
        expandidos = 1
        generados = 0
        tiempo_inicio = timeit.default_timer()
        self.listaAbiertos = self.insertarNodo(nodo_progenitor, self.listaAbiertos)
        while not self.vacio(self.listaAbiertos):
            nodo = self.extraerNodo(self.listaAbiertos)
            estado_nodoExpandido = Estado(nodo.id, nodo.longitud, nodo.latitud)
            if estado_nodoExpandido not in lista_expandidos:
                if estado_nodoExpandido.__eq__(estadoFinal):
                    tiempo_final = timeit.default_timer()
                    segundos = tiempo_final - tiempo_inicio
                    self.camino(segundos, expandidos, generados, self.profundidad, nodo, lista_expandidos)
                    return "Retorno del metodo buscar() = Exito"
                nuevosAbiertos = self.nodosSucesores(nodo)
                expandidos += 1
                generados += len(nuevosAbiertos)
                for abierto in nuevosAbiertos:
                    self.profundidad = max(profundidad, abierto.profundidad)
                    self.insertarNodo(abierto, self.listaAbiertos)
                    lista_expandidos.add(nodo)
        return "Retorno del metodo buscar() = Fracaso"

    def camino(self, segundos, expandidos, abiertos, profundidad, nodoExpandido, listaExpantidos):
        nodo = nodoExpandido
        lista = []
        while nodo.padre is not None:
            lista.append([nodo.padre.id, nodo.id, nodo.coste])
            nodo = nodo.padre
        lista = reversed(lista)
        print("Camino")
        for x in lista:
            print(f"{x[0]} ------({x[2]:<19})-----> {x[1]}")

        print(f" Tiempo empleado: {segundos:.10f} segundos")
        print("Nodos expandidos: ", expandidos)
        print("  Nodos generados: ", abiertos)
        print("     Profundidad: ", profundidad)
        print("Velocidad máxima: ", self.problema.velMax)
        print("    Nodo destino: ", nodoExpandido)
        print("             Fin: ", self.problema.final)
        print("          Origen: ", self.problema.inicio)
        print("   Tamaño camino:", lista.__sizeof__())
        # print("Lista expandidos: ", listaExpandidos)


class BusquedaAnchura(Busqueda):

    def __init__(self):

        super().__init__()
        self.listaAbiertos = []

    def insertarNodo(self, nodo, lista_nodos):
        lista_nodos.append(nodo)
        return lista_nodos

    def extraerNodo(self, lista_nodos):
        valor = lista_nodos.pop(0)
        return valor

    def vacio(self, lista_nodo):
        return len(self.listaAbiertos) == 0


class BusquedaProfundidad(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = []

    def insertarNodo(self, nodo, lista_nodos):
        lista_nodos.insert(0, nodo)
        return lista_nodos

    def extraerNodo(self, lista_nodos):
        valor = lista_nodos.pop()
        return valor

    def vacio(self,lista_nodos):
        return len(lista_nodos) == 0


class PrimeroMejor(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = queue.PriorityQueue()

    def insertarNodo(self, nodo, lista_nodos):
        disManh = Heuristica.calculo_heuristica(nodo.estado,self.problema.interseccionesCoordenadas[self.problema.final], self.problema.velMax)
        nodo.costeMasDistancia = disManh
        lista_nodos.put(nodo)
        return lista_nodos

    def extraerNodo(self, lista_nodos):
        return lista_nodos.get()

    def vacio(self, lista_nodos):
        return lista_nodos.empty()


class AEstrella(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = queue.PriorityQueue()

    def insertarNodo(self, nodo, lista_nodos):
        disManh = Heuristica.calculo_heuristica(nodo.estado,
                                                self.problema.interseccionesCoordenadas[self.problema.final],
                                                self.problema.velMax)
        nodo.costeMasDistancia = disManh + nodo.coste
        lista_nodos.put(nodo)
        return lista_nodos

    def extraerNodo(self, lista_nodos):
        return lista_nodos.get()

    def vacio(self, lista_nodos):
        return lista_nodos.empty()


if __name__ == "__main__":

    archivo_json = "AQUI LA RUTA DEL ARCHIVO QUE QUERAMOS."
    problema = Problema(archivo_json)
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
