from constraint import *
import sys
import re
problem = Problem()
file_path = sys.argv[1]
def read_input_file(file_path):
    with open(file_path, 'r') as file:
        # Leer filas x columnas del parking
        rows, columns = map(int, file.readline().split('x'))

        # Leer listado de plazas con conexión eléctrica
        electric_places_str = file.readline().strip().replace("PE:", "")
        electric_places = [tuple(map(int, coord.split(','))) for coord in re.findall(r'\((.*?)\)', electric_places_str)]

        # Leer información de vehículos
        vehicles = []
        for line in file:
            parts = line.strip().split('-')
            vehicle_id = int(parts[0])
            vehicle_type = parts[1]
            vehicle_cooler = parts[2]

            vehicles.append((vehicle_id, vehicle_type, vehicle_cooler))


    return rows, columns, electric_places, vehicles

def create_parking_matrix(rows, columns):
    # Crea una matriz de parking con todas las plazas inicializadas como '-'
    return [['-' for _ in range(columns)] for _ in range(rows)]
def write_output_file(file_path, num_solutions, solution):
    with open(file_path, 'w') as file:
        # Escribir número de soluciones encontradas
        file.write(f'"N. Sol:",{num_solutions}\n')

        # Escribir solo la primera solución



def create_vehicle_domains(parking_matrix, electric_places, vehicles):
    # Crea un diccionario donde las claves son vehículos y los valores son las plazas disponibles para ese vehículo
    vehicle_domains = {}

    for vehicle_id, vehicle_type, vehicle_cooler in vehicles:
        valid_parking_places = []

        for i in range(len(parking_matrix)):
            for j in range(len(parking_matrix[0])):
                place_coordinates = (i + 1, j + 1)
                if place_coordinates in electric_places or vehicle_cooler == 'X':
                    valid_parking_places.append(place_coordinates)

        vehicle_domains[vehicle_id] = valid_parking_places

    return vehicle_domains

def create_variables(problem, vehicle_domains):
    # Añade las variables al problema, donde cada variable es un vehículo con su dominio correspondiente
    for vehicle_id, valid_places in vehicle_domains.items():
        problem.addVariable(vehicle_id, valid_places)

def tsu_check(x, y):
    if x[0] == y[0]:
        return x < y

def adjacent_spaces_free(x, y):
    x_row, x_col = x
    y_row, y_col = y

    # Verifica si las plazas son adyacentes horizontalmente o verticalmente
    if abs(x_row - y_row) == 1 and x_col == y_col:
        return False
    if x_row == y_row and abs(x_col - y_col) == 1:
        return False

    return True

def notEqual(x, y):
    return x != y




# Obtener datos del archivo de entrada
rows, columns, electric_places, vehicles = read_input_file(file_path)


matrix = create_parking_matrix(rows, columns)


# Crear diccionario de dominios de vehículos
vehicle_domains = create_vehicle_domains(matrix, electric_places, vehicles)


# Crear el problema CSP


# Crear variables para representar cada vehículo y sus dominios
create_variables(problem, vehicle_domains)

# Obtener la lista de todas las variables (vehículos)
vehicle_vars = list(vehicle_domains.keys())

# Agregar restricción de que cada vehículo tiene asignada una plaza y solo una
#problem.addConstraint(AllDifferentConstraint(), vehicle_vars)


tsu_id = []
tnu_id = []
for vehicle in vehicles:
    if vehicle[1] == "TSU":
        tsu_id.append(vehicle[0])
    else:
        tnu_id.append(vehicle[0])

for x in tsu_id:
    for y in vehicle_vars:
        if x != y and y not in tsu_id:
            problem.addConstraint(tsu_check, (x, y))


solutions = problem.getSolutions()

num_solutions = len(solutions)
print(num_solutions)
solution = problem.getSolution()

# Escribir el archivo de salida
output_file_path = file_path.replace(".txt", ".csv")
write_output_file(output_file_path, num_solutions, solution)

