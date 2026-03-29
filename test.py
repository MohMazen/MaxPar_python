import time
from maxpar import Task, TaskSystem

# var_a_testeriables globales pour simuler la mémoire partagée
A, B, C, D, E = 0, 0, 0, 0, 0


def runT1(): global A; time.sleep(0.2); A = 10
def runT2(): global B; time.sleep(0.2); B = 20
def runT3(): global A, B, C; time.sleep(0.2); C = A + B
def runT4(): global C, D; time.sleep(0.2); D = C * 2
def runT5(): global A, E; time.sleep(0.2); E = A + 5

def reset():
    global A, B, C, D, E
    A, B, C, D, E = 0, 0, 0, 0, 0


t1 = Task("T1", writes=["A"], run=runT1)
t2 = Task("T2", writes=["B"], run=runT2)
t3 = Task("T3", reads=["A", "B"], writes=["C"], run=runT3)
t4 = Task("T4", reads=["C"], writes=["D"], run=runT4)
t5 = Task("T5", reads=["A"], writes=["E"], run=runT5)

precedences = {
    "T1": [],
    "T2": [],
    "T3": ["T1", "T2"],
    "T4": ["T3"],
    "T5": ["T1"]
}

sys1 = TaskSystem([t1, t2, t3, t4, t5], precedences)


print("=== DÉPENDANCES ===")
for nom in ["T1", "T2", "T3", "T4", "T5"]:
    print(f"  {nom} : {sys1.getDependencies(nom)}")

print("\n=== TEST SÉQUENTIEL ===")
reset()
sys1.runSeq()
print(f"  A={A}, B={B}, C={C}, D={D}, E={E}")

print("\n=== TEST PARALLÈLE ===")
reset()
sys1.run()
print(f"  A={A}, B={B}, C={C}, D={D}, E={E}")

print("\n=== COMPARAISON DES PERFORMANCES ===")
sys1.parCost(nb_executions=3)

print("=== TEST DU DETERMINISME ===")
print(sys1.detTestRnd(globals()))

print("\n=== AFFICHAGE DU GRAPHE ===")
sys1.draw()