import sys

# Constantes
ASIENTOS_CONTAGIOSOS = 8
ASIENTOS_NO_CONTAGIOSOS = 2


def leer_argumentos() -> (str, str):
    """ Función que lee los argumentos del programa """
    # Argumento 1: path al archivo csv
    # Argumento 2: identificador de la función heurística
    return sys.argv[1], sys.argv[2]


def generar_matriz(path_mapa) -> [[str,],]:
    """ Función que lee el archivo de entrada y lo convierte en una matriz """
    with open(path_mapa, "r") as file:
        file_data = file.readlines()
    mtrx = []
    for i in range(len(file_data)):
        mtrx.append([])
        for chars in file_data[i].split(";"):
            mtrx[i].append(chars)
        if i != len(file_data)-1:
            mtrx[i][-1] = mtrx[i][-1][:-1]
    return mtrx


class Estado:
    def __init__(self, mapa: [[str,],], pos_vehiculo: [str,], asientos_contagiados: [str,],
                 asientos_no_contagiados: [str,], energia: int, recogiendo_contagiosos: bool = False) -> None:
        self.mapa = mapa
        self.pos_vehiculo = pos_vehiculo
        self.asientos_contagiados = asientos_contagiados
        self.asientos_no_contagiados = asientos_no_contagiados
        self.energia = energia
        self.recogiendo_contagiosos = recogiendo_contagiosos
        self.realizar_efectos()

    def realizar_efectos(self):
        casilla_actual = self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]]
        if casilla_actual == "N":
            print("hola")
            if not self.recogiendo_contagiosos:
                self.energia -= 1
                self.recoger_no_contagioso()
        elif casilla_actual == "C":
            self.energia -= 1
            self.recoger_contagioso()
        elif casilla_actual == "1":
            # Quitamos la energía al coste de la casilla
            self.energia -= 1
        elif casilla_actual == "2":
            # Quitamos la energía del coste de la casilla
            self.energia -= 2
        elif casilla_actual == "P":
            # Cuando volvemos al parking se recupera la energía de la ambulancia
            self.energia = 50
        elif casilla_actual == "CN":
            self.energia -= 1
            if "C" in self.asientos_contagiados:
                # Si hay paciente contagioso no hacemos nada
                return
            # Si no hay pacientes contagiosos vaciamos la ambulancia
            self.asientos_no_contagiados = []
            self.asientos_contagiados = []
        elif casilla_actual == "NN":
            self.energia -= 1
            if "C" in self.asientos_contagiados:
                self.asientos_contagiados = []

    def mover(self, direccion):
        """ Función que mueve el vehículo en cualquiera de las cuatro direcciones (arriba, abajo, derecha, izquierda)
            generando así un nuevo estado """
        nueva_posicion = []
        if direccion == "arriba":
            nueva_posicion = [self.pos_vehiculo[0], self.pos_vehiculo[1]-1]
            if self.pos_vehiculo[1] <= 0:
                return None
        elif direccion == "abajo":
            nueva_posicion = [self.pos_vehiculo[0], self.pos_vehiculo[1]+1]
            if self.pos_vehiculo[1] >= len(self.mapa):
                return None
        elif direccion == "derecha":
            nueva_posicion = [self.pos_vehiculo[0]+1, self.pos_vehiculo[1]]
            if self.pos_vehiculo[0] >= len(self.mapa):
                return None
        elif direccion == "izquierda":
            nueva_posicion = [self.pos_vehiculo[0]-1, self.pos_vehiculo[1]]
            if self.pos_vehiculo[0] <= 0:
                return None

        if self.mapa[nueva_posicion[1]][nueva_posicion[0]] == "X":
            return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia)

    def recoger_no_contagioso(self):
        if (len(self.asientos_contagiados) >= ASIENTOS_CONTAGIOSOS
                and len(self.asientos_no_contagiados) >= ASIENTOS_NO_CONTAGIOSOS):
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
        ...

    def __str__(self):
        string = f"mapa:\n"
        for file in self.mapa:
            string += f"{file}\n"
        string += (f"pos_vehiculo: ({self.pos_vehiculo[0]}, {self.pos_vehiculo[1]})\n"
                   f"casilla actual: {self.mapa[self.pos_vehiculo[1]][self.pos_vehiculo[0]]}\n"
                   f"asientos contagiosos: {self.asientos_contagiados}\n"
                   f"asientos no contagiados: {self.asientos_no_contagiados}\n"
                   f"energía: {self.energia}\n"
                   f"recogiendo contagiosos: {self.recogiendo_contagiosos}")
        return string


def generar_estado_inicial(mapa: [[str,],]) -> Estado:
    indice_parking = []
    for i, fila in enumerate(mapa):
        for j, casilla in enumerate(fila):
            if casilla == "P":
                indice_parking = [j, i]
                break
    # La energía es 51 porque en la primera iteración se le va a quitar 1
    return Estado(mapa, indice_parking, [], [], 51, False)


def main() -> None:
    # Leemos los argumentos del programa
    path, num_h = leer_argumentos()
    print(path, num_h)
    mapa = generar_matriz(path)
    estado_inicial = generar_estado_inicial(mapa)
    print(estado_inicial)
    print(estado_inicial.mover("izquierda").mover("izquierda").mover("izquierda").mover("arriba"))


if __name__ == "__main__":
    main()
