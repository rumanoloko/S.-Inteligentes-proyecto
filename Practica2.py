import json
import queue
import timeit
from abc import abstractmethod, ABC



class Problema:
    def __init__(self, info_json):
        with open(info_json, 'r') as archivo:
            problema = json.load(archivo)

        #self.inicio = problema['initial']
        #self.final = problema['final']
        self.interseccionAccion = {}
        self.interseccionesCoordenadas = {}
        self.velMax = 1
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
        self.candidatos = tuple(problema['segments']['candidates'])
        self.number_stations = problema['segments']['number_stations']




class Estado:

    def __init__(self, id, longitud, latitud):
        self.id = id
        self.longitud = longitud
        self.latitud = latitud

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, otro):
        return self.id == otro.id




class Accion:

    def __int__(self):
        pass








class Nodo:

    def __init__(self, id, longitud, latitud, profundidad=0, padre=None, coste=0.0):
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
        return self.id == otro.id

    def __hash__(self):
        return hash(self.estado)

    def __lt__(self, otro):
        return self.id < otro.id


class Heuristica:

    def calculo_heuristica(estado1: Estado, tupla_coordenadas, velMax):
        return abs(estado1.longitud - tupla_coordenadas[0]) + abs(estado1.latitud - tupla_coordenadas[1]) / (
                    velMax / 3.6)






class Busqueda(ABC):

    def __init__(self):
        self.problema = Problema(archivo_json)
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
            print(f"{x[0]} ------({  x[2]:<13})-----> {x[1]}") #Coste acumulado

        print("")
        print(f" Tiempo empleado: {segundos:.10f} segundos")
        print("Nodos expandidos: ", expandidos)
        print("  Nodos generados: ", abiertos)
        print("     Profundidad: ", profundidad)
        print("Velocidad máxima: ", self.problema.velMax)
        print("    Nodo destino: ", nodoExpandido)
        print("             Fin: ", self.problema.final)
        print("          Origen: ", self.problema.inicio)
        print("   Tamaño camino:", lista.__sizeof__())
        print("")
        print("")
        # print("Lista expandidos: ", listaExpandidos)


class AEstrella(Busqueda):

    def __init__(self):
        super().__init__()
        self.listaAbiertos = queue.PriorityQueue()

    def insertarNodo(self, nodo, lista_nodos):
        f = Heuristica.calculo_heuristica(nodo.estado,self.problema.interseccionesCoordenadas[self.problema.final],self.problema.velMax)
        f = f + nodo.coste
        lista_nodos.put((f, nodo))
        return lista_nodos

    def extraerNodo(self, lista_nodos):
        return lista_nodos.get()[1]

    def vacio(self, lista_nodos):
        return lista_nodos.empty()




if __name__ == "__main__":
    archivo_json = r"C:\Users\Vlad\OneDrive - Universidad de Castilla-La Mancha\Escritorio\Practica2\sample-problems-lab2\toy\calle_del_virrey_morcillo_albacete_250_3_candidates_15_ns_4.json"
    #archivo_json = r"C:\Users\eduardo\PycharmProjects\S.-Inteligentes-proyecto\calle_de_francisco_5000_3.json"
    #archivo_json = r"C:\Users\eduardo\PycharmProjects\S.-Inteligentes-proyecto\calle_agustina_aroca_albacete_5000_0.json"
    #archivo_json = r"C:\Users\eduardo\PycharmProjects\S.-Inteligentes-proyecto\calle_marila_mariln_500_1.json"
    problema = Problema(archivo_json)
    z = AEstrella()
    print(z.buscar(Estado(z.problema.final,
                    z.problema.interseccionesCoordenadas[z.problema.final][0],
                    z.problema.interseccionesCoordenadas[z.problema.final][1])))





















