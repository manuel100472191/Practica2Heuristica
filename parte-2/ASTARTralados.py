import sys

def leer_argumentos() -> (str, str):
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

class State:
    def __init__(self, mapa: [[str]], ) -> None:
        self.mapa = mapa
        self.ambulancia

def main() -> None:
    # Leemos los argumentos del programa
    path, num_h = leer_argumentos()
    print(path, num_h)
    matrix = generar_matriz(path)
    print(matrix)


if __name__ == "__main__":
    main()
    



