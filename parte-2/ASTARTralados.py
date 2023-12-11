import sys
import math

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
        self.mapa = mapa
        self.pos_vehiculo = pos_vehiculo
        self.asientos_contagiados = asientos_contagiados
        self.asientos_no_contagiados = asientos_no_contagiados
        self.energia = energia
        self.padre = padre
        self.num_h = num_h
        # Usamos el valor del coste de la acción actual para el calculo de la función f(x)
        g_actual = self.realizar_efectos()
        self.gx = g_actual
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
            if not ("C" in self.asientos_contagiados):
                self.recoger_no_contagioso()
            return 1
        if casilla_actual == "C":
            self.energia -= 1
            self.recoger_contagioso()
            return 1
        if casilla_actual == "P":
            # Cuando volvemos al parking se recupera la energía de la ambulancia
            self.energia = 50
            return 0
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
            if self.pos_vehiculo[1] <= 0 or self.mapa[nueva_posicion[1]][nueva_posicion[0]] == "X":
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
            if nueva_posicion[0] <= 0 or self.mapa[nueva_posicion[1]][nueva_posicion[0]] == "X":
                return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia,
                      self, self.num_h)

    def recoger_no_contagioso(self):
        if (len(self.asientos_contagiados) >= ASIENTOS_CONTAGIOSOS
            and len(self.asientos_no_contagiados) >= ASIENTOS_NO_CONTAGIOSOS) or "C" in self.asientos_contagiados:
            # Si la ambulancia está llena de pacientes no hacemos nada
            return
        elif len(self.asientos_no_contagiados) < ASIENTOS_NO_CONTAGIOSOS:
            # Si la ambulancia tiene la sección de no contagiados sin llenar
            # añadimos al no contagiado y lo quitamos del mapa
            self.asientos_no_contagiados.append("N")
            self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]] = "1"
        elif len(self.asientos_contagiados) > 0 and not ("C" in self.asientos_contagiados):
            # Si la sección de no contagiados está llena y la de contagiados no tiene pacientes contagiados
            self.asientos_contagiados.append("N")
            self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]] = "1"

    def recoger_contagioso(self):
        if len(self.asientos_contagiados) >= ASIENTOS_CONTAGIOSOS or "N" in self.asientos_contagiados:
            return
        # Si hay hueco en los asientos de contagiosos y no son no contagiosos los que están en ellos añadimos el
        # paciente al vehículo y ponemos que se están recogiendo contagiosos para que no se admitan más no contagiosos
        self.asientos_contagiados.append("N")
        self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]] = "1"

    def dejar_no_contagiosos(self):
        """ Función que deja los pacientes no contagiosos en el centro """
        if "C" in self.asientos_contagiados:
            # Si hay paciente contagioso no hacemos nada
            return
        # Si no hay pacientes contagiosos vaciamos el vehículo
        self.asientos_no_contagiados = []
        self.asientos_contagiados = []

    def dejar_contagiosos(self):
        """ Función que deja a los pacientes contagiosos en el centro"""
        if "C" in self.asientos_contagiados:
            self.asientos_contagiados = []

    def calcular_hx(self) -> int:
        if self.num_h == 1:
            # La heurística uno consiste en añadir el número de pacientes que quedan en el mapa multiplicado por 2 +
            # el número de pacientes que hay en el vehículo sin multiplicar
            n_pacientes, pos_pacientes, pos_parking = contar_numero_pacientes(self.mapa)
            penalizacion = 10 ** 10
            if self.energia - calcular_distancia(self.pos_vehiculo, pos_parking) > 0:
                penalizacion = 0
            if len(pos_pacientes) == 0:
                return penalizacion + 5 * len(self.asientos_contagiados) + 5 * len(self.asientos_no_contagiados)
            paciente_mas_cercano = min(pos_pacientes, key=lambda pos: calcular_distancia(self.pos_vehiculo, pos))
            dis_paciente_cercano = calcular_distancia(self.pos_vehiculo, paciente_mas_cercano)

            return (100 * dis_paciente_cercano + 10 * n_pacientes + 5 * len(self.asientos_no_contagiados)
                    + 5 * len(self.asientos_contagiados) + penalizacion)

    def __str__(self):
        string = f"mapa:\n"
        for file in self.mapa:
            string += f"{file}\n"
        string += (f"pos_vehiculo: ({self.pos_vehiculo[0]}, {self.pos_vehiculo[1]})\n"
                   f"casilla actual: {self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]]}\n"
                   f"asientos contagiosos: {self.asientos_contagiados}\n"
                   f"asientos no contagiados: {self.asientos_no_contagiados}\n"
                   f"energía: {self.energia}\n")
        return string

    def __eq__(self, other):
        """ Devuelve si dos estados con iguales. Lo son en caso de que todos sus atributos lo sean """
        return (self.mapa == other.mapa and self.pos_vehiculo == other.pos_vehiculo and
                self.asientos_contagiados == other.asientos_contagiados and
                self.asientos_no_contagiados == other.asientos_no_contagiados)


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


def contar_numero_pacientes(mapa: [[str, ], ]) -> (int, [(int,), ], [int, ]):
    """ Cuenta el número de pacientes que quedan en el mapa"""
    contador = 0
    posiciones_pacientes = []
    posicion_parking = []
    for i, fila in enumerate(mapa):
        for j, casilla in enumerate(fila):
            if casilla == "C" or casilla == "N":
                contador += 1
                posiciones_pacientes.append([i, j])
            elif casilla == "P":
                posicion_parking = [i, j]
    return contador, posiciones_pacientes, posicion_parking


def calcular_distancia(posicion_1: (int,), posicion_2: (int,)):
    if posicion_2 is not None:
        return math.sqrt((posicion_1[0] - posicion_2[0]) ** 2 + (posicion_1[1] - posicion_2[1]) ** 2)
    else:
        return str("inf")


def comprobar_estado_final(estado: Estado) -> bool:
    """ Comprueba que el estado actual sea un estado final """
    if contar_numero_pacientes(estado.mapa)[0] != 0:
        return False
    if len(estado.asientos_contagiados) != 0:
        return False
    if len(estado.asientos_no_contagiados) != 0:
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
    estado_actual = None
    while len(abierta) > 0 and exito is False:
        # Obtenemos el estado con el coste minimo de la función f(x) ademas de su indice
        indice_estado, estado_actual = min(enumerate(abierta), key=lambda estado: estado[1].fx)
        print(estado_actual.fx, len(abierta) + len(cerrada))
        cerrada.append(abierta.pop(indice_estado))
        # Si el estado actual es un estado final se termina la búsqueda
        if comprobar_estado_final(estado_actual):
            exito = True
            continue
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

    print(estado_actual)


def main() -> None:
    # Leemos los argumentos del programa
    path, num_h = leer_argumentos()
    mapa = generar_matriz(path)

    estado_inicial = generar_estado_inicial(mapa, int(num_h))
    a_star(estado_inicial)


if __name__ == "__main__":
    main()
