import sys

# Constantes
ASIENTOS_CONTAGIOSOS = 8
ASIENTOS_NO_CONTAGIOSOS = 2


def leer_argumentos() -> (str, str):
    """ Función que lee los argumentos del programa """
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

class Ambulancia:
    def __init__(self, mapa: [[str],], posicion: list ,pacientes_no_contagiosos: [str,]
                 , pacientes_contagiosos: [str,], energia: int
                 , recogiendo_contagiosos: bool = False) -> None:
        self.asientos_contagiosos = pacientes_contagiosos
        self.asientos_no_contagiosos = pacientes_no_contagiosos
        self.posicion = posicion
        self.energia = energia
        self.mapa = mapa
        self.recogiendo_contagiosos = recogiendo_contagiosos

    def logica_iteracion(self) -> None:
        casilla_actual = self.mapa[self.posicion[0]][self.posicion[1]]
        if casilla_actual == "N":
            if not self.recogiendo_contagiosos:
                self.recoger_no_contagioso()
        elif casilla_actual == "C":
            self.recoger_contagioso()
        elif casilla_actual == "1":
            # Quitamos la energia al coste de la casilla
            self.energia -= 1
        elif casilla_actual == "2":
            # Quitamos la energia del costa de la casilla
            self.energia -= 2
        elif casilla_actual == "P":
            # Cuando volvemos al parking se recupera la energia de la ambulancia
            self.energia = 50
        elif casilla_actual == "CN":
            if "C" in self.asientos_contagiosos:
                # Si hay paciente contagiosos no hacemos nada
                return
            # Si no hay pacientes contagiosos vaciamos la ambulancia  
            self.asientos_no_contagiosos = []
            self.asientos_contagiosos = []
        elif casilla_actual == "NN":
            if "C" in self.asientos_contagiosos:
                self.asientos_contagiosos = []

    def recoger_no_contagioso(self):
        if len(self.asientos_contagiosos) >= ASIENTOS_CONTAGIOSOS and len(self.asientos_no_contagiosos) >= ASIENTOS_NO_CONTAGIOSOS:
            # Si la ambulancia esta llena de pacientes no hacemos nada
            return
        elif self.asientos_no_contagiosos < ASIENTOS_NO_CONTAGIOSOS:
            # Si la ambulacnia tiene la sección de no contagiados sin llenar añadimos al no contagiado y lo quitamos del mapa
            self.asientos_no_contagiosos.append("N")
            self.mapa[self.posicion[0]][self.posicion[1]] = "1"
        elif len(self.asientos_contagiosos) > 0 and not "C" in self.asientos_contagiosos:
            # Si la sección de no contagiados esta llena y la de contagiados no tiene pacientes contagiados
            self.asientos_contagiosos.append("N") 
            self.mapa[self.posicion[0]][self.posicion[1]] = "1"

    def recoger_contagioso(self):
        if self.recogiendo_contagiosos:
            if len(self.asientos_contagiosos) < ASIENTOS_CONTAGIOSOS:
                self.asein
            



class Estado:
    def __init__(self, mapa: [[str,],], pos_vehiculo: [str,], asientos_contagiados: [str,], asientos_no_contagiados: [str,], energia: int) -> None:
        self.mapa = mapa
        self.pos_vehiculo = pos_vehiculo
        self.asientos_contagiados = asientos_contagiados
        self.asientos_no_contagiados = asientos_no_contagiados
        self.energia = energia

    def generar_estados(self):
        ...

    def mover_arriba(self) -> Estado:
        if self.pos_vehiculo[1] <= 0:
            return None
        
        nueva_posicion = [self.pos_vehiculo[0], self.pos_vehiculo[1]-1]

        if mapa[nueva_posicion[0]][nueva_posicion[1]] == "X":
            return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagidos, self.energia)

    def mover_abajo(self) -> Estado:
        if self.pos_vehiculo[1] >= len(self.mapa):
            return None
        
        nueva_posicion = [self.pos_vehiculo[0], self.pos_vehiculo[1]+1]


        if mapa[nueva_posicion[0]][nueva_posicion[1]] == "X":
            return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia)
    
    def mover_derecha(self) -> Estado:
        """ Operación de moverse a la derecha """
        if self.pos_vehiculo[0] <= len(self.mapa[0]):
            return None

        nueva_posicion = [self.pos_vehiculo[0]+1, self.pos_vehiculo[1]]


        if mapa[nueva_posicion[0]][nueva_posicion[1]] == "X":
            return None

        return Estado(self.mapa, nueva_poscion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia)

    def mover_izquierda(self) -> Estado:
        """ Operación de moverse a la izquierda """
        if self.pos_vehiculo[0] >= 0:
            return None

        nueva_posicion = [self.pos_vehiculo[0]-1, self.pos_vehiculo[1]]

        if mapa[nueva_posicion[0]][nueva_posicion[1]] == "X":
            return None

        return Estado(self.mapa, nueva_posicion, self.asientos_contagiados, self.asientos_no_contagiados, self.energia)


def main() -> None:
    # Leemos los argumentos del programa
    path, num_h = leer_argumentos()
    print(path, num_h)
    matrix = generar_matriz(path)
    print(matrix)


if __name__ == "__main__":
    main()
    



