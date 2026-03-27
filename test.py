import time
from maxpar import *

# Variables globales de test
X, Y, Z = 0, 0, 0


def runT1(): global X; time.sleep(0.1); X = 1


def runT2(): global Y; time.sleep(0.1); Y = 2


def runTsomme(): global X, Y, Z; time.sleep(0.1); Z = X + Y


# 1. Création des tâches
t1 = Task(name="T1", writes=["X"], run=runT1)
t2 = Task(name="T2", writes=["Y"], run=runT2)
tSomme = Task(name="somme", reads=["X", "Y"], writes=["Z"], run=runTsomme)

# 2. Création du système avec ses précédences
precedences = {"T1": [], "T2": ["T1"], "somme": ["T1", "T2"]}
sys = TaskSystem([t1, t2, tSomme], precedences)

# 3. Tests des différentes fonctionnalités
print("Dépendances de 'somme' :", sys.getDependencies("somme"))

sys.runSeq()
print(f"Après runSeq() : X={X}, Y={Y}, Z={Z}")

X, Y, Z = 0, 0, 0  # Réinitialisation
sys.run()
print(f"Après run() : X={X}, Y={Y}, Z={Z}")

sys.draw()
sys.parCost()
# sys.detTestRnd(globals())
