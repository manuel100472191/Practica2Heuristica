import random
from constraint import Problem, AllDifferentConstraint

class Aparcamiento:
    def __init__(self, id, conexion_electrica):
        self.id = id
        self.conexion_electrica = conexion_electrica

    def obtener_coordenadas(self):
        return self.id[0], self.id[1]

def parkings(dimension):
    espacios_aparcamiento = []
    for i in range(dimension[0]):
        for j in range(dimension[1]):
            espacio_aparcamiento = Aparcamiento((i + 1, j + 1), False)
            espacios_aparcamiento.append(espacio_aparcamiento)
    return espacios_aparcamiento

class Vehiculo:
    def __init__(self, id, tipo, congelar):
        self.id = id
        self.tipo = tipo
        self.congelar = congelar

    def __gt__(self, other):
        return self.id > other.id

def carga_electrica(aparcamiento):
    return aparcamiento.conexion_electrica

def comprobacion_TSU(aparcamiento1, aparcamiento2):
    x1, y1 = aparcamiento1.obtener_coordenadas()
    x2, y2 = aparcamiento2.obtener_coordenadas()
    return x1 != x2 or y2 < y1

def maniobras(aparcamiento1, aparcamiento2, aparcamiento3):
    x1, y1 = aparcamiento1.obtener_coordenadas()
    x2, y2 = aparcamiento2.obtener_coordenadas()
    x3, y3 = aparcamiento3.obtener_coordenadas()
    if y1 == y2 == y3:
        # Verificar si las plazas están una encima o debajo de la otra
        return not(abs(x1 - x2) == 1) and  not(abs(x2 - x3) == 1) and not(abs(x1 - x3) == 1)
    return True

def maniobras_extremos(aparcamiento1, aparcamiento2):
    x1, y1 = aparcamiento1.obtener_coordenadas()
    x2, y2 = aparcamiento2.obtener_coordenadas()
    if y1 == y2:
        if y1 == 1 or y1 == dimension[1]:
            return not (abs(x1 - x2) == 1)
    return True

def problema_principal(lista_vehiculos, mapa):
    problema = Problem()

    problema.addVariables(lista_vehiculos, mapa)
    problema.addConstraint(AllDifferentConstraint())

    for vehiculo in lista_vehiculos:
        if vehiculo.congelar:
            problema.addConstraint(carga_electrica, [vehiculo])

    for vehiculo in lista_vehiculos:
        if vehiculo.tipo == "TSU":
            for otro_vehiculo in lista_vehiculos:
                if vehiculo != otro_vehiculo and otro_vehiculo.tipo != "TSU":
                    problema.addConstraint(comprobacion_TSU, (vehiculo, otro_vehiculo))

    for vehiculo1 in lista_vehiculos:
        for vehiculo2 in lista_vehiculos:
            if vehiculo1 != vehiculo2:
                for vehiculo3 in lista_vehiculos:
                    if vehiculo3 != vehiculo1 and vehiculo3 != vehiculo2:
                        problema.addConstraint(maniobras, (vehiculo1, vehiculo2, vehiculo3))

    for vehiculo1 in lista_vehiculos:
        for vehiculo2 in lista_vehiculos:
            if vehiculo1 != vehiculo2:
                problema.addConstraint(maniobras_extremos, (vehiculo1, vehiculo2))




    soluciones = problema.getSolutions()
    return soluciones

def leer_archivo_entrada(linea):
    partes = linea.split(":")
    if partes[0] == "PE":
        info_plaza = partes[1].strip().strip('()')
        id_plaza = info_plaza.split(")(")
        return id_plaza
    elif "-" in linea:
        info_vehiculo = linea.strip().split("-")
        electrificado = False
        if info_vehiculo[2] == "C":
            electrificado = True
        return Vehiculo(info_vehiculo[0], info_vehiculo[1], electrificado)
    else:
        return None

def escribir_archivo_salida(nombre_archivo_salida, solucion, longitud):
    with open(nombre_archivo_salida, 'w') as archivo_salida:
        archivo_salida.write(f'"N. Sol":{longitud}\n\n')

        for idx, solucion in enumerate(soluciones_seleccionadas, start=1):
            archivo_salida.write(f'SOLUCION ALEATORIA {idx}:\n')

            cuadricula = [['"   −   "' for _ in range(dimension[1])] for _ in range(dimension[0])]

            for vehiculo, aparcamiento in solucion.items():
                fila, columna = aparcamiento.obtener_coordenadas()
                congelar = "C" if vehiculo.congelar else "X"
                cuadricula[fila - 1][columna - 1] = f'"{vehiculo.id}-{vehiculo.tipo}-{congelar}"'

            for fila in cuadricula:
                archivo_salida.write(','.join(fila) + '\n')

            archivo_salida.write('\n')

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python main.py <ruta_estacionamiento>")
        sys.exit(1)

    ruta_entrada = sys.argv[1]
    ruta_salida = ruta_entrada.replace('.txt', '.csv')

    with open(ruta_entrada, "r") as archivo:
        lineas = archivo.readlines()

    lista_vehiculos = []
    mapa_estacionamiento = []

    for linea in lineas:
        if "x" in linea:
            dimensiones = linea.split("x")
            dimension = (int(dimensiones[0]), int(dimensiones[1]))
            mapa_estacionamiento = parkings(dimension)
        elif linea.startswith("PE") or linea[0].isdigit():
            elemento = leer_archivo_entrada(linea)
            if isinstance(elemento, Vehiculo):
                lista_vehiculos.append(elemento)
            else:
                for i in elemento:
                    coordenadas = i.split(",")
                    mapa_estacionamiento[((int(coordenadas[0]) - 1) * int(dimensiones[1])) + (int(coordenadas[1]) - 1)].conexion_electrica = True
    soluciones = problema_principal(lista_vehiculos, mapa_estacionamiento)
    soluciones_seleccionadas = random.sample(soluciones, min(10, len(soluciones)))
    escribir_archivo_salida(ruta_salida, soluciones_seleccionadas, len(soluciones))