import sys
import csv
import math
import time

class Nodo:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.tipo_anterior = tipo
        self.vecinos = []
        if self.tipo == "N" or self.tipo == "C" or self.tipo == "P" or self.tipo == "CC" or self.tipo == "CN" or self.tipo == "X":
            self.coste = 1
        else:
            self.coste = int(self.tipo)



class AEstrella:
    def __init__(self, mapa, bus, heuristica):
        self.heuristica = heuristica
        self.mapa = mapa
        self.bus = bus
        self.objetivo_actual = "P"
        self.camino = []
        objetivo = True

        self.reseteo = False

        self.modo_bucle= False
        self.visitados = []
        gasolinas = []
        tipos = []
        self.expandidos = 0

        self.camino.append([self.bus.y, self.bus.x])
        gasolinas.append(self.bus.gasolina)
        tipos.append(self.bus.nodo_actual.tipo_anterior)

        while objetivo:
            self.comprobar_reinicio()
            if self.reseteo:
                return None
            self.detectar_bucle()
            self.iteracion()
            self.accion()
            self.camino.append([self.bus.y, self.bus.x])
            if len(self.camino) >= 1000:
                try :
                    raise Exception("Sin solucion" + str(self.bus.archivo))
                except Exception as e:
                    print(e)
                    return None
            gasolinas.append(self.bus.gasolina)
            tipos.append(self.bus.nodo_actual.tipo_anterior)
            if self.bus.pacientes_dejados == self.mapa.pacientes_totales and self.bus.x == self.mapa.P[0].x and self.bus.y == self.mapa.P[0].y:
                objetivo = False


        salida_archivo = self.bus.archivo.split("/")[-1]
        salida_archivo = salida_archivo.split(".")[0]
        with open("./ASTAR-tests/"+str(salida_archivo)+"-"+str(self.heuristica) + ".output", "w") as f:
            for i in range(0, len(self.camino) ):
                f.write(str(self.camino[i]) + ":" + str(tipos[i]) + ":" + str(gasolinas[i]) + "\n")
            f.write("Tiempo total: "+ str(time.time() - self.bus.tiempo) + "\n")
            f.write("Coste total: "+ str(self.bus.coste_energetico_total) + "\n")
            f.write("Logitud del plan: "+ str(len(self.camino)) + "\n")
            f.write("Nodos expandidos: "+ str(self.expandidos) + "\n")
            f.close()




    def comprobar_reinicio(self):
        if self.bus.gasolina <= 0:
            if self.bus.gasolina_minima >= 45:
                print("No se puede llegar al objetivo")
                return None
            self.bus.gasolina = 50
            self.bus.asientos_ocupados_C = 0
            self.bus.asientos_ocupados_N = 0
            self.bus.pacientes_dejados = 0
            self.bus.coste_energetico_total = 0
            self.reseteo = True
            reinicio(self.bus)


    def accion(self):
        tipo = self.bus.nodo_actual.tipo
        if tipo == "N":
            if self.bus.asientos_ocupados_N < self.bus.asientos and self.bus.asientos_ocupados_C < 1:
                self.bus.asientos_ocupados_N += 1
                self.mapa.N.remove(self.bus.nodo_actual)
                self.bus.nodo_actual.tipo = "1"
            self.bus.gasolina -= 1
            self.bus.coste_energetico_total += 1
        elif tipo == "C":
            if self.bus.asientos_ocupados_C < self.bus.asientos_C:
                self.bus.asientos_ocupados_C += 1
                self.mapa.C.remove(self.bus.nodo_actual)
                self.bus.nodo_actual.tipo = "1"
            self.bus.gasolina -= 1
            self.bus.coste_energetico_total += 1

        elif tipo == "P":
            self.bus.gasolina = 50

        elif tipo == "CC":
            self.bus.pacientes_dejados += self.bus.asientos_ocupados_C
            self.bus.asientos_ocupados_C = 0
            self.bus.gasolina -= 1
            self.bus.coste_energetico_total += 1

        elif tipo == "CN":
            self.bus.pacientes_dejados += self.bus.asientos_ocupados_N
            self.bus.asientos_ocupados_N = 0
            self.bus.gasolina -= 1
            self.bus.coste_energetico_total += 1

        else:
            self.bus.gasolina -= int(tipo)
            self.bus.coste_energetico_total += int(tipo)

    def detectar_bucle(self):
        if self.modo_bucle == False:
            if len(self.camino) > 5:
                if self.camino[-1] == self.camino[-3] and self.camino[-2] == self.camino[-4]:
                    self.modo_bucle = True
                    self.visitados.append(self.bus.nodo_anterior)
                    self.visitados.append(self.bus.nodo_actual)



        else:
            if self.objetivo_actual == "ind":
                if self.bus.nodo_actual.tipo == "N" or self.bus.nodo_actual.tipo == "C":
                    self.modo_bucle = False
                    self.visitados = []

            elif self.objetivo_actual == self.bus.nodo_actual.tipo:
                self.modo_bucle = False
                self.visitados = []



    def iteracion(self):
        if self.modo_bucle == False:
            costes = []
            for vecino in self.bus.nodo_actual.vecinos:
                self.expandidos += 1
                if vecino.tipo != "X":
                    costes.append(self.coste(vecino))
                else:
                    costes.append(1000000)

            pos = 0
            for i in range(0, len(costes)):
                 if costes[i] < costes[pos]:
                     pos = i
            self.siguiente_nodo(self.bus.nodo_actual.vecinos[pos])

        else:
            costes = []
            for vecino in self.bus.nodo_actual.vecinos:
                self.expandidos += 1
                if vecino.tipo != "X":
                    if vecino not in self.visitados:
                        costes.append(self.coste(vecino))
                    else:
                        costes.append(1000000)
                else:
                    costes.append(1000000)


            pos = 0
            for i in range(0, len(costes)):
                if costes[i] < costes[pos]:
                    pos = i

            self.visitados.append(self.bus.nodo_actual.vecinos[pos])
            self.siguiente_nodo(self.bus.nodo_actual.vecinos[pos])



    def coste(self, nodo):
        if self.heuristica == "1":
            coste = nodo.coste + self.heuristica_1(nodo)
        elif self.heuristica == "2":
            coste = nodo.coste + self.heuristica_2(nodo)

        return coste


    def heuristica_1(self, nodo):
        if self.bus.gasolina < self.bus.gasolina_minima:
            cercanos = []
            for p in self.mapa.P:
                cercanos.append( math.sqrt(pow(abs(p.x - nodo.x),2) + pow(abs(p.y - nodo.y),2)) )
            self.objetivo_actual = "P"
            return min(cercanos)

        elif self.mapa.C == [] and self.bus.asientos_ocupados_C != 0:
            cercanos =[]
            for cc in self.mapa.CC:
                cercanos.append( math.sqrt(pow(abs(cc.x - nodo.x),2) + pow(abs(cc.y - nodo.y),2)) )
            self.objetivo_actual = "CC"
            return min(cercanos)

        elif self.mapa.N == [] and self.mapa.C ==[] and self.bus.asientos_ocupados_C != 0:
            cercanos = []
            for cc in self.mapa.CC:
                cercanos.append( math.sqrt(pow(abs(cc.x - nodo.x),2) + pow(abs(cc.y - nodo.y),2)) )
            self.objetivo_actual = "CC"
            return min(cercanos)

        elif self.mapa.N == [] and self.mapa.C ==[] and self.bus.asientos_ocupados_N != 0:
            cercanos = []
            for cn in self.mapa.CN:
                cercanos.append( math.sqrt(pow(abs(cn.x - nodo.x),2) + pow(abs(cn.y - nodo.y),2)) )
            self.objetivo_actual = "CN"
            return min(cercanos)

        elif self.bus.asientos_ocupados_C == self.bus.asientos_C:
            cercanos = []
            for cc in self.mapa.CC:
                cercanos.append(math.sqrt(pow(abs(cc.x - nodo.x), 2) + pow(abs(cc.y - nodo.y), 2)))
            self.objetivo_actual = "CC"
            return min(cercanos)

        elif self.bus.asientos_ocupados_N == self.bus.asientos_N:
            cercanos = []
            for cn in self.mapa.CN:
                cercanos.append(math.sqrt(pow(abs(cn.x - nodo.x), 2) + pow(abs(cn.y - nodo.y), 2)))
            self.objetivo_actual = "CN"
            return min(cercanos)

        elif self.mapa.C != [] and self.mapa.N == []:
            cercanos = []
            for c in self.mapa.C:
                cercanos.append( math.sqrt(pow(abs(c.x - nodo.x),2) + pow(abs(c.y - nodo.y),2)) )
            self.objetivo_actual = "C"
            return min(cercanos)

        elif self.bus.asientos_ocupados_C !=0:
            cercanos = []
            for c in self.mapa.C:
                cercanos.append( math.sqrt(pow(abs(c.x - nodo.x),2) + pow(abs(c.y - nodo.y),2)) )
            self.objetivo_actual = "C"
            return min(cercanos)

        elif self.bus.pacientes_dejados == self.mapa.pacientes_totales:
            cercanos = []
            for p in self.mapa.P:
                cercanos.append( math.sqrt(pow(abs(p.x - nodo.x),2) + pow(abs(p.y - nodo.y),2)) )
            self.objetivo_actual = "P"
            return min(cercanos)
        else:
            cercanos = []
            for ns in self.mapa.N:
                cercanos.append( math.sqrt(pow(abs(ns.x - nodo.x),2) + pow(abs(ns.y - nodo.y),2)) )

            for cs in self.mapa.C:
                cercanos.append( math.sqrt(pow(abs(cs.x - nodo.x),2) + pow(abs(cs.y - nodo.y),2)) )

            self.objetivo_actual = "ind"

            return min(cercanos)





    def heuristica_2(self, nodo):
        numero_C = len(self.mapa.C)
        numero_N = len(self.mapa.N)
        min_viaje_C = math.ceil(numero_C/2)
        num_viajes = 0
        for i in range(0, numero_C):
            numero_N -=8
        num_viajes += min_viaje_C

        while numero_N > 0:
            num_viajes +=1
            numero_N -= 10

        if self.bus.gasolina < self.bus.gasolina_minima or self.bus.pacientes_dejados == self.mapa.pacientes_totales:
            cercanos = []
            for p in self.mapa.P:
                cercanos.append( math.sqrt(pow(abs(p.x - nodo.x),2) + pow(abs(p.y - nodo.y),2)) )
            self.objetivo_actual = "P"
            return min(cercanos)

        elif (self.mapa.C == [] and self.bus.asientos_ocupados_C != 0) or self.bus.asientos_ocupados_C == self.bus.asientos_C:
            cercanos =[]
            for cc in self.mapa.CC:
                cercanos.append( math.sqrt(pow(abs(cc.x - nodo.x),2) + pow(abs(cc.y - nodo.y),2)) )
            self.objetivo_actual = "CC"
            return min(cercanos)

        elif (self.mapa.N == [] and self.mapa.C ==[] and self.bus.asientos_ocupados_N != 0) or self.bus.asientos_ocupados_N == self.bus.asientos:
            cercanos = []
            for cn in self.mapa.CN:
                cercanos.append( math.sqrt(pow(abs(cn.x - nodo.x),2) + pow(abs(cn.y - nodo.y),2)) )
            self.objetivo_actual = "CN"
            return min(cercanos)

        elif (self.bus.asientos_N == self.bus.asientos_ocupados_N and self.mapa.C !=[]) or (self.mapa.N ==[] and self.mapa.C !=[]):
            cercanos = []
            for c in self.mapa.C:
                cercanos.append( math.sqrt(pow(abs(c.x - nodo.x),2) + pow(abs(c.y - nodo.y),2)) )
            self.objetivo_actual = "C"
            return min(cercanos)

        elif self.bus.asientos_ocupados_N < self.bus.asientos_N or ( self.mapa.N != [] and self.mapa.C == []):
            cercanos = []
            for ns in self.mapa.N:
                cercanos.append( math.sqrt(pow(abs(ns.x - nodo.x),2) + pow(abs(ns.y - nodo.y),2)) )
            self.objetivo_actual = "N"
            return min(cercanos)
        print("lo has hecho mal crack")
        return 0




    def siguiente_nodo(self, nodo):
        self.bus.nodo_anterior = self.bus.nodo_actual
        self.bus.nodo_actual = nodo
        self.bus.x = nodo.x
        self.bus.y = nodo.y
        return None




class Mapa:
    def __init__(self, archivo, bus):
        self.filas = 0
        self.columnas = 0
        self.nodos = {}
        self.N = []
        self.C = []
        self.CC = []
        self.CN = []
        self.P = []
        self.X = []
        self.pacientes_totales = 0
        self.leer_mapa(archivo, bus)

    def leer_mapa(self, archivo, bus):
        with open(archivo, 'r') as archivo:
            csvreader = csv.reader(archivo, delimiter=';')
            self.filas= 0
            self.columnas = 0
            x = 0
            y = 0
            for fila in csvreader:
                y += 1
                self.filas += 1
                for _tipo in fila:
                    x += 1
                    _nodo = Nodo(x, y, _tipo)
                    self.nodos[str(y)+str(x)] = (_nodo)
                    if _nodo.tipo == "N":
                        self.N.append(_nodo)
                        self.pacientes_totales += 1
                    elif _nodo.tipo == "C":
                        self.C.append(_nodo)
                        self.pacientes_totales += 1
                    elif _nodo.tipo == "CC":
                        self.CC.append(_nodo)
                    elif _nodo.tipo == "CN":
                        self.CN.append(_nodo)
                    elif _nodo.tipo == "P":
                        self.P.append(_nodo)
                        bus.x = _nodo.x
                        bus.y = _nodo.y
                        bus.nodo_actual = _nodo
                    elif _nodo.tipo == "X":
                        self.X.append(_nodo)


                x = 0
                if self.filas == 1:
                    for j in fila:
                        self.columnas += 1

            archivo.close()

            self.conectar_nodos()

    def conectar_nodos(self):
        for fila in range(1, self.filas +1):
            for columna in range(1, self.columnas +1):
                _nodo = self.nodos[str(fila)+str(columna)]
                adyacentez = []
                if fila == 1:
                    if columna == 1:
                        adyacentez.append(self.nodos[str(fila)+str(columna+1)])
                        adyacentez.append(self.nodos[str(fila+1)+str(columna)])
                    elif columna == self.columnas:
                        adyacentez.append(self.nodos[str(fila)+str(columna-1)])
                        adyacentez.append(self.nodos[str(fila+1)+str(columna)])
                    else:
                        adyacentez.append(self.nodos[str(fila)+str(columna+1)])
                        adyacentez.append(self.nodos[str(fila)+str(columna-1)])
                        adyacentez.append(self.nodos[str(fila+1)+str(columna)])

                elif fila == self.filas:
                    if columna == 1:
                        adyacentez.append(self.nodos[str(fila)+str(columna+1)])
                        adyacentez.append(self.nodos[str(fila-1)+str(columna)])
                    elif columna == self.columnas:
                        adyacentez.append(self.nodos[str(fila)+str(columna-1)])
                        adyacentez.append(self.nodos[str(fila-1)+str(columna)])
                    else:
                        adyacentez.append(self.nodos[str(fila)+str(columna+1)])
                        adyacentez.append(self.nodos[str(fila)+str(columna-1)])
                        adyacentez.append(self.nodos[str(fila-1)+str(columna)])
                else:
                    if columna == 1:
                        adyacentez.append(self.nodos[str(fila)+str(columna+1)])
                        adyacentez.append(self.nodos[str(fila+1)+str(columna)])
                        adyacentez.append(self.nodos[str(fila-1)+str(columna)])
                    elif columna == self.columnas:
                        adyacentez.append(self.nodos[str(fila)+str(columna-1)])
                        adyacentez.append(self.nodos[str(fila+1)+str(columna)])
                        adyacentez.append(self.nodos[str(fila-1)+str(columna)])
                    else:
                        adyacentez.append(self.nodos[str(fila)+str(columna+1)])
                        adyacentez.append(self.nodos[str(fila)+str(columna-1)])
                        adyacentez.append(self.nodos[str(fila+1)+str(columna)])
                        adyacentez.append(self.nodos[str(fila-1)+str(columna)])

                _nodo.vecinos = adyacentez
        return None






class BUS:
    def __init__(self,archivo, heuristica, tiempo):
        self.tiempo = tiempo
        self.archivo = archivo
        self.heuristica = heuristica
        self.coste_energetico_total = 0
        self.x = 0
        self.y = 0
        self.nodo_actual = None
        self.nodo_anterior = None
        self.gasolina = 50
        self.gasolina_minima = 10
        self.asientos = 10
        self.asientos_N = 8
        self.asientos_C = 2
        self.asientos_ocupados_N = 0
        self.asientos_ocupados_C = 0
        self.pacientes_dejados = 0


def reinicio(bus):

    bus.gasolina_minima += 5
    mapa = Mapa(bus.archivo, bus)
    aes = AEstrella(mapa, bus, bus.heuristica)

def main(argv):
    tiempo = time.time()
    bus = BUS(argv[1] ,argv[2], tiempo)
    mapa = Mapa(argv[1], bus)


    aes = AEstrella(mapa, bus, bus.heuristica)





if __name__ == "__main__":
    main(sys.argv)
