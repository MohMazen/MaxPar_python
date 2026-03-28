import time
from maxpar import Task, TaskSystem

# Variables globales pour simuler la mémoire partagée
A, B, C, D, E = 0, 0, 0, 0, 0

# Définition des fonctions d'exécution (avec un petit délai pour simuler un calcul)
def runT1(): global A; time.sleep(0.2); A = 10
def runT2(): global B; time.sleep(0.2); B = 20
def runT3(): global A, B, C; time.sleep(0.2); C = A + B
def runT4(): global C, D; time.sleep(0.2); D = C * 2
def runT5(): global A, E; time.sleep(0.2); E = A + 5

# Création des objets tâches
t1 = Task("T1", writes=["A"], run=runT1)
t2 = Task("T2", writes=["B"], run=runT2)
t3 = Task("T3", reads=["A", "B"], writes=["C"], run=runT3)
t4 = Task("T4", reads=["C"], writes=["D"], run=runT4)
t5 = Task("T5", reads=["A"], writes=["E"], run=runT5)

# Dictionnaire des précédences initiales
precedences = {
    "T1": [],
    "T2": [],
    "T3": ["T1", "T2"],
    "T4": ["T3"],
    "T5": ["T1"]
}

# Initialisation du système
sys = TaskSystem([t1, t2, t3, t4, t5], precedences)

print("=== TEST DES DÉPENDANCES ===")
print(f"Les dépendances de T4 sont : {sys.getDependencies('T4')}\n")

print("=== TEST SÉQUENTIEL ===")
A, B, C, D, E = 0, 0, 0, 0, 0
sys.runSeq()
print(f"Résultats après runSeq : A={A}, B={B}, C={C}, D={D}, E={E}\n")

print("=== TEST PARALLÈLE ===")
A, B, C, D, E = 0, 0, 0, 0, 0
sys.run()
print(f"Résultats après run : A={A}, B={B}, C={C}, D={D}, E={E}\n")

print("=== COMPARAISON DES PERFORMANCES ===")
sys.parCost(nb_exectutions=3) # Utilise un petit nombre pour ne pas trop attendre

print("\n=== AFFICHAGE DU GRAPHE ===")
sys.draw()