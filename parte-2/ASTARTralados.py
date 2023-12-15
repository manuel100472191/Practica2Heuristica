import sys
import math
import copy
import time
import os

# Constantes
ASIENTOS_CONTAGIOSOS = 8
ASIENTOS_NO_CONTAGIOSOS = 2


def leer_argumentos() -> (str, str):
    """ Función que lee los argumentos del programa """
    # Argumento 1: path al archivo csv
    # Argumento 2: identificador de la función heurística
    return sys.argv[1], sys.argv[2]


def generar_matriz(path_mapa) -> [[str, ], ]:
    """ Función que lee el archivo de entrada y lo convierte en una matriz """
    with open(path_mapa, "r") as file:
        file_data = file.readlines()
    mapa = []
    for i in range(len(file_data)):
        mapa.append([])
        for chars in file_data[i].split(";"):
            mapa[i].append(chars)
        # Quita el \n de el valor final
        if i != len(file_data) - 1:
            mapa[i][-1] = mapa[i][-1][:-1]
    return mapa


class Estado:
    def __init__(self, mapa: [[str, ], ], pos_vehiculo: [str, ], asientos_contagiados: [str, ],
                 asientos_no_contagiados: [str, ], energia: int, padre, num_h: int) -> None:
        self.mapa = copy.deepcopy(mapa)
        self.pos_vehiculo = copy.deepcopy(pos_vehiculo)
        self.asientos_contagiosos = copy.deepcopy(asientos_contagiados)
        self.asientos_no_contagiosos = copy.deepcopy(asientos_no_contagiados)
        self.energia = energia
        self.padre = padre
        self.num_h = num_h
        # Usamos el valor del coste de la acción actual para el calculo de la función f(x)
        g_actual = self.realizar_efectos()
        if padre is None:
            self.gx = 0
        else:
            self.gx = self.padre.gx + g_actual
        self.hx = self.calcular_hx()
        self.fx = self.gx + self.hx

    def realizar_efectos(self) -> int:
        """
        Método que realiza las consecuencias de la acción que le ha llevado a crearse dependiendo en la casilla
        en la que ha caído
        """
        casilla_actual = self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]]
        if casilla_actual == "N":
            self.energia -= 1
            self.recoger_no_contagioso()
            return 1
        if casilla_actual == "C":
            self.energia -= 1
            self.recoger_contagioso()
            return 1
        if casilla_actual == "P":
            # Cuando volvemos al parking se recupera la energía de la ambulancia
            self.energia = 50
            return 1
        if casilla_actual == "CN":
            self.energia -= 1
            self.dejar_no_contagiosos()
            return 1
        if casilla_actual == "CC":
            self.energia -= 1
            self.dejar_contagiosos()
            return 1
        # Si la casilla es un número se los restamos a la energía
        self.energia -= int(casilla_actual)
        return int(casilla_actual)

    def mover(self, direccion):
        """ Función que mueve el vehículo en cualquiera de las cuatro direcciones (arriba, abajo, derecha, izquierda)
            generando así un nuevo estado """
        nueva_posicion = []
        # Para cada dirección se comprueba que la casilla a la que vamos no sea una "X" o que se haya salido del mapa
        # Si la nueva posicion es válida se devuelve
        if direccion == "arriba":
            nueva_posicion = [self.pos_vehiculo[0], self.pos_vehiculo[1] - 1]
            if nueva_posicion[1] < 0 or self.mapa[nueva_posicion[1]][nueva_posicion[0]] == "X":
                return None
        elif direccion == "abajo":
            nueva_posicion = [self.pos_vehiculo[0], self.pos_vehiculo[1] + 1]
            if nueva_posicion[1] >= len(self.mapa) or self.mapa[nueva_posicion[1]][nueva_posicion[0]] == "X":
                return None
        elif direccion == "derecha":
            nueva_posicion = [self.pos_vehiculo[0] + 1, self.pos_vehiculo[1]]
            if nueva_posicion[0] >= len(self.mapa[0]) or self.mapa[nueva_posicion[1]][nueva_posicion[0]] == "X":
                return None
        elif direccion == "izquierda":
            nueva_posicion = [self.pos_vehiculo[0] - 1, self.pos_vehiculo[1]]
            if nueva_posicion[0] < 0 or self.mapa[nueva_posicion[1]][nueva_posicion[0]] == "X":
                return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiosos, self.asientos_no_contagiosos, self.energia,
                      self, self.num_h)

    def recoger_no_contagioso(self):
        """ Método que sirve para comprobar si se puede reboger a un paciente no contagioso dada la casilla en
        la que está el vehículo """
        # Si la ambulancia está llena de pacientes no hacemos nada
        if ((len(self.asientos_contagiosos) >= ASIENTOS_CONTAGIOSOS and
             len(self.asientos_no_contagiosos) >= ASIENTOS_NO_CONTAGIOSOS)
                or "C" in self.asientos_contagiosos):
            return
        elif len(self.asientos_no_contagiosos) < ASIENTOS_NO_CONTAGIOSOS:
            # Si la ambulancia tiene la sección de no contagiados sin llenar
            # añadimos al no contagiado y lo quitamos del mapa
            self.asientos_no_contagiosos.append("N")
            self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]] = "1"
        elif len(self.asientos_contagiosos) > 0 and not ("C" in self.asientos_contagiosos):
            # Si la sección de no contagiados está llena y la de contagiados no tiene pacientes contagiados
            self.asientos_contagiosos.append("N")
            self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]] = "1"

    def recoger_contagioso(self):
        """ Método que comprueba si se puede recoger a un paciente contagioso """
        if len(self.asientos_contagiosos) >= ASIENTOS_CONTAGIOSOS or "N" in self.asientos_contagiosos:
            return
        # Si hay hueco en los asientos de contagiosos y no son no contagiosos los que están en ellos añadimos el
        # paciente al vehículo y ponemos que se están recogiendo contagiosos para que no se admitan más no contagiosos
        self.asientos_contagiosos.append("C")
        self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]] = "1"

    def dejar_no_contagiosos(self):
        """ Método que deja los pacientes no contagiosos en el centro """
        if "C" in self.asientos_contagiosos:
            # Si hay paciente contagioso no hacemos nada
            return
        # Si no hay pacientes contagiosos vaciamos el vehículo
        self.asientos_no_contagiosos = []
        self.asientos_contagiosos = []

    def dejar_contagiosos(self):
        """ Método que deja a los pacientes contagiosos en el centro"""
        # Solo los deja en caso de que haya contagiosos en los asientos para contagiosos
        if "C" in self.asientos_contagiosos:
            self.asientos_contagiosos = []

    def calcular_hx(self) -> float:
        if self.num_h == 1:
            pos_pacientes_n, pos_pacientes_c, pos_parking, pos_cn, pos_cc = datos_del_mapa(self.mapa)
            # Cuando no quedan pacientes por entregar los llevamos al parking directamente
            if ((len(pos_pacientes_n) +
                 len(pos_pacientes_c) +
                 len(self.asientos_contagiosos) +
                 len(self.asientos_no_contagiosos)) == 0):
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_parking)
            # Dejar pacientes contagiosos si no quedan pacientes contagiosos en el mapa o si están llenos
            # los asientos de contagiosos
            elif ((len(pos_pacientes_c) == 0 or len(self.asientos_contagiosos) == ASIENTOS_CONTAGIOSOS)
                  and "C" in self.asientos_contagiosos):
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cc)
            # Dejar pacientes no contagiosos
            elif ((len(pos_pacientes_n) == 0 or len(self.asientos_no_contagiosos) == ASIENTOS_NO_CONTAGIOSOS)
                  and not ("C" in self.asientos_contagiosos)):
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cn)
            # Recoger al paciente no contagioso más cercano
            elif not ("C" in self.asientos_contagiosos):
                pos_cercano = min(pos_pacientes_n, key=lambda pos: calcular_distancia(self.pos_vehiculo, pos))
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cercano)
            # Recoger al paciente contagioso más cercano
            else:
                pos_cercano = min(pos_pacientes_c, key=lambda pos: calcular_distancia(self.pos_vehiculo, pos))
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cercano)

            if distancia_objetivo > self.energia:
                dis_parking = calcular_distancia(self.pos_vehiculo, pos_parking)
                if dis_parking > self.energia:
                    distancia_objetivo = float('inf')
                else:
                    distancia_objetivo = dis_parking

            return distancia_objetivo*0.2 + ((len(pos_pacientes_c) + len(pos_pacientes_n))*0.5
                                             + (len(self.asientos_contagiosos) + len(self.asientos_no_contagiosos))*0.3)*len(self.mapa[0])
        if self.num_h == 2:
            pos_pacientes_n, pos_pacientes_c, pos_parking, pos_cn, pos_cc = datos_del_mapa(self.mapa)
            # Cuando no quedan pacientes por entregar los llevamos al parking directamente
            if ((len(pos_pacientes_n) +
                 len(pos_pacientes_c) +
                 len(self.asientos_contagiosos) +
                 len(self.asientos_no_contagiosos)) == 0):
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_parking)
            # Dejar pacientes contagiosos si no quedan pacientes contagiosos en el mapa o si están llenos
            # los asientos de contagiosos
            elif ((len(pos_pacientes_c) == 0 or len(self.asientos_contagiosos) == ASIENTOS_CONTAGIOSOS)
                  and "C" in self.asientos_contagiosos):
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cc)
                if len(pos_pacientes_c) != 0:
                    pos_cercano = min(pos_pacientes_c, key=lambda pos: calcular_distancia(self.pos_vehiculo, pos))
                    if distancia_objetivo > calcular_distancia(self.pos_vehiculo, pos_cercano):
                        distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cercano)
            # Dejar pacientes no contagiosos
            elif ((len(pos_pacientes_n) == 0 or len(self.asientos_no_contagiosos) == ASIENTOS_NO_CONTAGIOSOS)
                  and not ("C" in self.asientos_contagiosos)):
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cn)
            # Recoger al paciente no contagioso más cercano
            elif not ("C" in self.asientos_contagiosos):
                pos_cercano = min(pos_pacientes_n, key=lambda pos: calcular_distancia(self.pos_vehiculo, pos))
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cercano)
                if distancia_objetivo < calcular_distancia(self.pos_vehiculo, pos_cn):
                    distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cn)
            # Recoger al paciente contagioso más cercano
            else:
                pos_cercano = min(pos_pacientes_c, key=lambda pos: calcular_distancia(self.pos_vehiculo, pos))
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cercano)
                if distancia_objetivo < calcular_distancia(self.pos_vehiculo, pos_cc):
                    distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cc)

            if distancia_objetivo > self.energia:
                dis_parking = calcular_distancia(self.pos_vehiculo, pos_parking)
                if dis_parking > self.energia:
                    distancia_objetivo = float('inf')
                else:
                    distancia_objetivo = dis_parking

            return distancia_objetivo + ((len(pos_pacientes_c) + len(pos_pacientes_n)) * 2
                                         + (len(self.asientos_contagiosos) + len(self.asientos_no_contagiosos)))*10

    def __str__(self):
        """ Método que ayuda a la hora de imprimir en pantalla un estado. Sirve para el debugging """
        string = f"mapa:\n"
        for file in self.mapa:
            string += f"{file}\n"
        string += (f"pos_vehiculo: ({self.pos_vehiculo[0]}, {self.pos_vehiculo[1]})\n"
                   f"casilla actual: {self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]]}\n"
                   f"asientos contagiosos: {self.asientos_contagiosos}\n"
                   f"asientos no contagiosos: {self.asientos_no_contagiosos}\n"
                   f"energía: {self.energia}\n")
        return string

    def __eq__(self, other):
        """ Método que devuelve si dos estados con iguales. Lo son en caso de que todos sus atributos lo sean """
        return (self.mapa == other.mapa and
                self.pos_vehiculo == other.pos_vehiculo and
                self.asientos_contagiosos == other.asientos_contagiosos and
                self.asientos_no_contagiosos == other.asientos_no_contagiosos and
                self.energia == other.energia)


def generar_estado_inicial(mapa: [[str, ], ], num_h: int) -> Estado:
    """ Genera el estado inicial comprobando donde está el parking en el mapa """
    # Buscamos la posicion del parking porque ahi es donde se pondrá a al vehículo
    indice_parking = []
    for i, fila in enumerate(mapa):
        for j, casilla in enumerate(fila):
            if casilla == "P":
                indice_parking = [j, i]
                break
    # La energía es 51 porque en la primera iteración se le va a quitar 1
    return Estado(mapa, indice_parking, [], [], 51, None, num_h)


def datos_del_mapa(mapa: [[str, ], ]) -> (int, [(int,), ], [int, ], [int,], [int,]):
    """
        Devuelve las posiciones de las casillas relevantes del mapa, como son el parking los centros de recogidas y
        dos listas con la ubicación de los pacientes contagiosos y no contagiosos
    """
    posiciones_pacientes_n = []
    posiciones_pacientes_c = []
    posicion_parking = []
    posicion_cn = []
    posicion_cc = []
    for i, fila in enumerate(mapa):
        for j, casilla in enumerate(fila):
            if casilla == "N":
                posiciones_pacientes_n.append([i, j])
            elif casilla == "C":
                posiciones_pacientes_c.append([i, j])
            elif casilla == "P":
                posicion_parking = [i, j]
            elif casilla == "CC":
                posicion_cc = [i, j]
            elif casilla == "CN":
                posicion_cn = [i, j]
    return posiciones_pacientes_n, posiciones_pacientes_c, posicion_parking, posicion_cn, posicion_cc


def calcular_distancia(posicion_1: (int,), posicion_2: (int,)):
    """ Función que calcula la distancia en línea recta de dos puntos """
    if posicion_2 is not None:
        return math.sqrt((posicion_1[0] - posicion_2[0]) ** 2 + (posicion_1[1] - posicion_2[1]) ** 2)
    else:
        return int('inf')


def comprobar_estado_final(estado: Estado) -> bool:
    """ Comprueba que el estado actual sea un estado final """
    datos = datos_del_mapa(estado.mapa)
    if (len(datos[0]) + len(datos[1])) != 0:
        return False
    if len(estado.asientos_contagiosos) != 0:
        return False
    if len(estado.asientos_no_contagiosos) != 0:
        return False
    if estado.mapa[estado.pos_vehiculo[1]][estado.pos_vehiculo[0]] != "P":
        return False
    return True


def estado_valido(estado: Estado):
    """ Función que comprueba que un estado sea válido"""
    if estado is None or estado.energia <= 0:
        return False
    return True


def estado_en_lista(estado: Estado, lista: [Estado,]):
    for estado_lista in lista:
        if estado == estado_lista:
            return True
    return False


def a_star(estado_inicial: Estado):
    """ Función que implementa el algoritmo A* para el problema propuesto"""
    abierta = [estado_inicial]
    cerrada = []
    nodos_expandidos = 0
    while len(abierta) > 0:
        # Obtenemos el estado con el coste minimo en la función f(x) ademas de su indice
        indice_estado, estado_actual = min(enumerate(abierta), key=lambda estado: estado[1].fx)
        nodos_expandidos += 1
        # Cambiamos dicho estado de la lista abierta a la lista cerrada
        cerrada.append(abierta.pop(indice_estado))
        print(estado_actual.fx, estado_actual.gx)
        # Si el estado actual es un estado final se termina la búsqueda y se devuelven
        # los estados expandidos junto al estado
        if comprobar_estado_final(estado_actual):
            return estado_actual, nodos_expandidos
        # Se generan los nuevos estados a partir del actual ejecutan las distintas operaciones
        for operador in ("arriba", "abajo", "derecha", "izquierda"):
            nuevo_estado = estado_actual.mover(operador)
            # Comprobamos que el nuevo estado sea válido, en caso contrario nos saltamos lo que queda de iteración
            if not estado_valido(nuevo_estado):
                continue
            # Comprobamos que no esté el estado ya ne la lista de abierta y si lo está dejamos el de menor f(x)
            # Si no esta se añade a la lista de abierta
            if estado_en_lista(nuevo_estado, abierta):
                indice_viejo = abierta.index(nuevo_estado)
                if nuevo_estado.fx < abierta[indice_viejo].fx:
                    abierta.pop(indice_viejo)
                    abierta.append(nuevo_estado)
            elif estado_en_lista(nuevo_estado, cerrada):
                continue
            else:
                abierta.append(nuevo_estado)
    return None, nodos_expandidos


def back_tracking(estado_final: Estado):
    """ Función que se encarga del backtracking desde el nodo final"""
    # Guardamos el coste energético del último estado
    if estado_final is None:
        coste_energetico = float("inf")
        camino = []
        longitud_plan = float("inf")
        return camino, coste_energetico, longitud_plan
    coste_energetico = estado_final.gx
    # Añadimos todos los estados del camino al objectivo a una lista
    estado_actual = estado_final
    camino = []
    while estado_actual is not None:
        camino.append(estado_actual)
        estado_actual = estado_actual.padre
    # Le damos la vuelta a la lista para que esté en orden del primero al último
    camino = camino[::-1]
    # Guardamos la longitud de la lista para saber la longitud del plan
    longitud_plan = len(camino)
    return camino, coste_energetico, longitud_plan


def generar_output(camino: [Estado, ], mapa: [[str,],], tiempo, coste, longitud, nodos_expandidos, nombre_mapa, num_h):
    # Escribimos el archivo de salida con su nombre correspondiente
    with open(f"./ASTAR-tests/{nombre_mapa}-{num_h}.output", "w+") as output_file:
        for estado in camino:
            output_file.write((f"({estado.pos_vehiculo[0]},{estado.pos_vehiculo[1]}):"
                               f"{mapa[estado.pos_vehiculo[1]][estado.pos_vehiculo[0]]}:"
                               f"{estado.energia}\n"))
            casilla_actual = mapa[estado.pos_vehiculo[1]][estado.pos_vehiculo[0]]
            # Usamos el mapa general porque los de cada estado han sida modificádos
            if casilla_actual in ('N', 'C'):
                mapa[estado.pos_vehiculo[1]][estado.pos_vehiculo[0]] = '1'

    with open(f"./ASTAR-tests/{nombre_mapa}-{num_h}.stat", "w+") as stats_file:
        stats_file.write(f"Tiempo total: {tiempo: .2f}\n"
                         f"Coste total: {coste}\n"
                         f"Longitud del plan: {longitud}\n"
                         f"Nodos expandidos: {nodos_expandidos}")


def main() -> None:
    # Leemos los argumentos del programa
    path, num_h = leer_argumentos()
    # Generamos el mapa del programa
    mapa = generar_matriz(path)
    # Sacamos el nombre del mapa del path para crear el archivo de salida
    nombre_mapa = path.split("/")[-1].split(".")[0]
    # Generamos el estado inicial para el mapa y heurística elegida
    estado_inicial = generar_estado_inicial(mapa, int(num_h))
    # Medimos el tiempo que tarda en ejecutarse el programa
    comienzo = time.time()
    # Ejecutamos el algoritmo A* para el estado inicial y guardamos el número de números expandidos
    estado_final, nodos_expandidos = a_star(estado_inicial)
    final = time.time()
    # Calculamos el tiempo que ha tardado
    tiempo = final - comienzo
    # Hacemos el back_tracking para saber el camino, coste_total y la longitud del plan
    camino, coste_total, longitud_plan = back_tracking(estado_final)
    # Escribimos los archivos de salida con los datos necesarios
    generar_output(camino, mapa, tiempo, coste_total, longitud_plan, nodos_expandidos, nombre_mapa, num_h)


if __name__ == "__main__":
    main()
