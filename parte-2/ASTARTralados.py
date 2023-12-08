import sys

# Constantes
ASIENTOS_CONTAGIOSOS = 8
ASIENTOS_NO_CONTAGIOSOS = 2


def leer_argumentos() -> (str, str):
    """ Función que lee los argumentos del programa """
    # Argumento 1 : path al archivo csv
    # Argumento 2 : identificador de la función heurística
    return sys.argv[1], sys.argv[2]


def generar_matriz(path_mapa) -> [[str]] :
    """ Función que lee el archivo de entrada y lo convierte en una matriz """
    with open(path_mapa, "r") as file:
        file_data = file.readlines()
    mtrx = []
    for i in range(len(file_data)):
        mtrx.append([])
        for chars in file_data[i].split(";"):
            mtrx[i].append(chars)
        mtrx[i][-1] = mtrx[i][-1][:-1]
    return mtrx


class Estado:
    def __init__(self, mapa: [[str,],], pos_vehiculo: [str,], asientos_contagiados: [str,]
                 , asientos_no_contagiados: [str,], energia: int, recogiendo_contagiosos: bool = False) -> None:
        self.mapa = mapa
        self.pos_vehiculo = pos_vehiculo
        self.asientos_contagiados = asientos_contagiados
        self.asientos_no_contagiados = asientos_no_contagiados
        self.energia = energia
        self.recogiendo_contagiosos = recogiendo_contagiosos

    def realizar_efectos(self):
        casilla_actual = self.mapa[self.pos_vehiculo[0]][self.pos_vehiculo[1]]
        if casilla_actual == "N":
            if not self.recogiendo_contagiosos:
                self.recoger_no_contagioso()
        elif casilla_actual == "C":
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
            if "C" in self.asientos_contagiados:
                # Si hay paciente contagioso no hacemos nada
                return
            # Si no hay pacientes contagiosos vaciamos la ambulancia
            self.asientos_no_contagiados = []
            self.asientos_contagiados = []
        elif casilla_actual == "NN":
            if "C" in self.asientos_contagiados:
                self.asientos_contagiados = []

    def mover_arriba(self):
        if self.pos_vehiculo[1] <= 0:
            return None
        
        nueva_posicion = [self.pos_vehiculo[0], self.pos_vehiculo[1]-1]

        if self.mapa[nueva_posicion[0]][nueva_posicion[1]] == "X":
            return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia)

    def mover_abajo(self):
        if self.pos_vehiculo[1] >= len(self.mapa):
            return None
        
        nueva_posicion = [self.pos_vehiculo[0], self.pos_vehiculo[1]+1]

        if self.mapa[nueva_posicion[0]][nueva_posicion[1]] == "X":
            return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia)
    
    def mover_derecha(self):
        """ Operación de moverse a la derecha """
        if self.pos_vehiculo[0] <= len(self.mapa[0]):
            return None

        nueva_posicion = [self.pos_vehiculo[0]+1, self.pos_vehiculo[1]]

        if self.mapa[nueva_posicion[0]][nueva_posicion[1]] == "X":
            return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia)

    def mover_izquierda(self):
        """ Operación de moverse a la izquierda """
        if self.pos_vehiculo[0] >= 0:
            return None

        nueva_posicion = [self.pos_vehiculo[0]-1, self.pos_vehiculo[1]]

        if self.mapa[nueva_posicion[0]][nueva_posicion[1]] == "X":
            return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia)

    def recoger_no_contagioso(self):
        if (len(self.asientos_contagiados) >= ASIENTOS_CONTAGIOSOS
                and len(self.asientos_no_contagiados) >= ASIENTOS_NO_CONTAGIOSOS):
            # Si la ambulancia esta llena de pacientes no hacemos nada
            return
        elif self.asientos_no_contagiados < ASIENTOS_NO_CONTAGIOSOS:
            # Si la ambulancia tiene la sección de no contagiados sin llenar
            # añadimos al no contagiado y lo quitamos del mapa
            self.asientos_no_contagiados.append("N")
            self.mapa[self.pos_vehiculo[0]][self.pos_vehiculo[1]] = "1"
        elif len(self.asientos_contagiados) > 0 and not "C" in self.asientos_contagiados:
            # Si la sección de no contagiados esta llena y la de contagiados no tiene pacientes contagiados
            self.asientos_contagiados.append("N")
            self.mapa[self.pos_vehiculo[0]][self.pos_vehiculo[1]] = "1"

    def recoger_contagioso(self):
        ...


def main() -> None:
    # Leemos los argumentos del programa
    path, num_h = leer_argumentos()
    print(path, num_h)
    matrix = generar_matriz(path)
    print(matrix)


if __name__ == "__main__":
    main()
    



