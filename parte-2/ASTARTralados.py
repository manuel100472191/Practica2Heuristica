import sys
import math
import copy
import time

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
    mtrx = []
    for i in range(len(file_data)):
        mtrx.append([])
        for chars in file_data[i].split(";"):
            mtrx[i].append(chars)
        if i != len(file_data) - 1:
            mtrx[i][-1] = mtrx[i][-1][:-1]
    return mtrx


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
        casilla_actual = self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]]
        if casilla_actual == "N":
            self.energia -= 1
            if not ("C" in self.asientos_contagiosos):
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
        # Si la casilla es número se los restamos a la energía
        self.energia -= int(casilla_actual)
        return int(casilla_actual)

    def mover(self, direccion):
        """ Función que mueve el vehículo en cualquiera de las cuatro direcciones (arriba, abajo, derecha, izquierda)
            generando así un nuevo estado """
        nueva_posicion = []
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
        if ((len(self.asientos_contagiosos) >= ASIENTOS_CONTAGIOSOS and
             len(self.asientos_no_contagiosos) >= ASIENTOS_NO_CONTAGIOSOS)
                or "C" in self.asientos_contagiosos):
            # Si la ambulancia está llena de pacientes no hacemos nada
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
        if len(self.asientos_contagiosos) >= ASIENTOS_CONTAGIOSOS or "N" in self.asientos_contagiosos:
            return
        # Si hay hueco en los asientos de contagiosos y no son no contagiosos los que están en ellos añadimos el
        # paciente al vehículo y ponemos que se están recogiendo contagiosos para que no se admitan más no contagiosos
        self.asientos_contagiosos.append("C")
        self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]] = "1"

    def dejar_no_contagiosos(self):
        """ Función que deja los pacientes no contagiosos en el centro """
        if "C" in self.asientos_contagiosos:
            # Si hay paciente contagioso no hacemos nada
            return
        # Si no hay pacientes contagiosos vaciamos el vehículo
        self.asientos_no_contagiosos = []
        self.asientos_contagiosos = []

    def dejar_contagiosos(self):
        """ Función que deja a los pacientes contagiosos en el centro"""
        if "C" in self.asientos_contagiosos:
            self.asientos_contagiosos = []

    def calcular_hx(self) -> int:
        if self.num_h == 2:
            # h(x) = (distancia_objetivo + n_pacientes) * 10 + penalizacion
            # distancia_objetivo: ambulancia vacía -> paciente más cercano

            pos_pacientes_n, pos_pacientes_c, pos_parking, pos_cn, pos_cc = datos_del_mapa(self.mapa)
            penalizacion = 10 ** 10 if self.energia - calcular_distancia(self.pos_vehiculo, pos_parking) < 0 else 0
            if ((len(pos_pacientes_n) + len(pos_pacientes_c)) == 0 and len(self.asientos_contagiosos) == 0
                    and len(self.asientos_no_contagiosos) == 0):
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_parking)
                return distancia_objetivo
            # Calculamos la distancia al proximo objetivo más cercano
            elif "C" in self.asientos_contagiosos:
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cc)
            elif "N" in self.asientos_no_contagiosos or "N" in self.asientos_contagiosos:
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, pos_cn)
            elif (len(pos_pacientes_n) + len(pos_pacientes_c)) > 0:
                paciente_cercano = min(pos_pacientes_n + pos_pacientes_c, key=lambda pos: calcular_distancia(self.pos_vehiculo, pos))
                distancia_objetivo = calcular_distancia(self.pos_vehiculo, paciente_cercano)
            else:
                distancia_objetivo = 0

            return (distancia_objetivo + (len(pos_pacientes_n) + len(pos_pacientes_c)))*10 + penalizacion
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
                  and not ("C" in self.asientos_no_contagiosos)):
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

            return distancia_objetivo + ((len(pos_pacientes_c) + len(pos_pacientes_n))*5
                                         + (len(self.asientos_contagiosos) + len(self.asientos_no_contagiosos))) * 100

    def __str__(self):
        string = f"mapa:\n"
        for file in self.mapa:
            string += f"{file}\n"
        string += (f"pos_vehiculo: ({self.pos_vehiculo[0]}, {self.pos_vehiculo[1]})\n"
                   f"casilla actual: {self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]]}\n"
                   f"asientos contagiosos: {self.asientos_contagiosos}\n"
                   f"asientos no contagiados: {self.asientos_no_contagiosos}\n"
                   f"energía: {self.energia}\n")
        return string

    def __eq__(self, other):
        """ Devuelve si dos estados con iguales. Lo son en caso de que todos sus atributos lo sean """
        return (self.mapa == other.mapa and self.pos_vehiculo == other.pos_vehiculo and
                self.asientos_contagiosos == other.asientos_contagiosos and
                self.energia == other.energia and
                self.asientos_no_contagiosos == other.asientos_no_contagiosos)


def generar_estado_inicial(mapa: [[str, ], ], num_h: int) -> Estado:
    """ Genera el estado inicial comprobando donde está el parking en el mapa """
    indice_parking = []
    for i, fila in enumerate(mapa):
        for j, casilla in enumerate(fila):
            if casilla == "P":
                indice_parking = [j, i]
                break
    # La energía es 51 porque en la primera iteración se le va a quitar 1
    return Estado(mapa, indice_parking, [], [], 51, None, num_h)


def datos_del_mapa(mapa: [[str, ], ]) -> (int, [(int,), ], [int, ], [int,], [int,]):
    """ Cuenta el número de pacientes que quedan en el mapa"""
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
    if estado is None or estado.energia <= 0:
        return False
    return True


def a_star(estado_inicial: Estado):
    abierta = [estado_inicial]
    cerrada = []
    exito = False
    while len(abierta) > 0 and exito is False:
        # Obtenemos el estado con el coste minimo de la función f(x) ademas de su indice
        indice_estado, estado_actual = min(enumerate(abierta), key=lambda estado: estado[1].fx)
        cerrada.append(abierta.pop(indice_estado))
        # Si el estado actual es un estado final se termina la búsqueda
        if comprobar_estado_final(estado_actual):
            return estado_actual, len(abierta)+len(cerrada)
        # Se generan los nuevos estados a partir del actual
        for operador in ("arriba", "abajo", "derecha", "izquierda"):
            nuevo_estado = estado_actual.mover(operador)
            if not estado_valido(nuevo_estado):
                continue
            # Si el nuevo estado está ya en la lista de abiertos dejamos el que menor f(x) tenga
            if nuevo_estado in abierta:
                indice_viejo = abierta.index(nuevo_estado)
                if nuevo_estado.fx < abierta[indice_viejo].fx:
                    abierta.pop(indice_viejo)
                    abierta.append(nuevo_estado)
            else:
                abierta.append(nuevo_estado)
    return None, len(abierta)+len(cerrada)


def back_tracking(estado_final: Estado):
    estado_actual = estado_final
    camino = []
    coste_energetico = estado_final.gx
    while estado_actual is not None:
        camino.append(estado_actual)
        estado_actual = estado_actual.padre

    longitud_plan = len(camino)
    camino = camino[::-1]

    return camino, coste_energetico, longitud_plan


def generar_output(camino: [Estado, ], mapa: [[str,],], tiempo, coste, longitud, nodos_expandidos):
    for estado in camino:
        print((f"({estado.pos_vehiculo[0]},{estado.pos_vehiculo[1]}):"
                       f"{mapa[estado.pos_vehiculo[1]][estado.pos_vehiculo[0]]}:"
                       f"{estado.energia}"))
        casilla_actual = mapa[estado.pos_vehiculo[1]][estado.pos_vehiculo[0]]
        if casilla_actual in ('N', 'C'):
            mapa[estado.pos_vehiculo[1]][estado.pos_vehiculo[0]] = '1'

    print(f"Tiempo total: {tiempo: .2f}\n"
          f"Coste total: {coste}\n"
          f"Longitud del plan: {longitud}\n"
          f"Nodos expandidos: {nodos_expandidos}")


def main() -> None:
    # Leemos los argumentos del programa
    path, num_h = leer_argumentos()
    mapa = generar_matriz(path)
    estado_inicial = generar_estado_inicial(mapa, int(num_h))
    comienzo = time.time()
    estado_final, nodos_expandidos = a_star(estado_inicial)
    final = time.time()
    tiempo = final - comienzo
    camino, coste_total, longitud_plan = back_tracking(estado_final)
    generar_output(camino, mapa, tiempo, coste_total, longitud_plan, nodos_expandidos)



if __name__ == "__main__":
    main()
