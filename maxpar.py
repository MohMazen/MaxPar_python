"""
==============================================================================
Projet      : Parallélisation maximale automatique
Matière     : Systèmes d'exploitation
Fichier     : maxpar.py
Auteurs     : CHAABANE Mohamed-Mazen, EL HARRAK Ahmed, YOUSSEF Edris
Description : Bibliothèque Python pour automatiser la parallélisation
              maximale d'un système de tâches.
==============================================================================
"""
import random
import threading
import time
import networkx as nx
import matplotlib.pyplot as plt


class Task:
    def __init__(self, name="", reads=None, writes=None, run=None):
        self.name = name
        self.reads = reads or []
        self.writes = writes or []
        self.run = run


class TaskSystem:
    def __init__(self, tasks=None, precedences_dict=None):
        self.tasks = tasks or []
        self.precedences_dict = precedences_dict or {}

        task_names = [t.name for t in self.tasks]

        if len(task_names) != len(set(task_names)):
            raise ValueError("Erreur : Des tâches ont le même nom.")

        for task, deps in self.precedences_dict.items():
            if task not in task_names:
                raise ValueError(f"Erreur : La tâche '{task}' du dictionnaire n'existe pas.")
            for dep in deps:
                if dep not in task_names:
                    raise ValueError(f"Erreur : La dépendance '{dep}' n'existe pas.")

        # On calcule le vrai parallélisme maximal via les conditions de Bernstein
        self.precedences_dict = self._calculer_parallelisme_maximal()

    def _sont_en_conflit(self, t1, t2):
        # Conditions de Bernstein : deux tâches interfèrent si elles partagent
        # une variable en écriture, ou si l'une écrit ce que l'autre lit
        w1, w2 = set(t1.writes), set(t2.writes)
        r1, r2 = set(t1.reads), set(t2.reads)
        return bool((w1 & r2) or (r1 & w2) or (w1 & w2))

    def _calculer_parallelisme_maximal(self):
        task_map = {t.name: t for t in self.tasks}
        nouveau_dict = {}

        for task_name, deps in self.precedences_dict.items():
            tache_courante = task_map[task_name]
            # On ne garde que les dépendances qui causent vraiment un conflit
            deps_utiles = [d for d in deps if self._sont_en_conflit(tache_courante, task_map[d])]
            nouveau_dict[task_name] = deps_utiles

        return nouveau_dict

    def getDependencies(self, task):
        task_names = [t.name for t in self.tasks]
        if task not in task_names:
            raise ValueError(f"Erreur : La tâche '{task}' n'existe pas.")
        return self.precedences_dict.get(task, [])

    def runSeq(self):
        tasks_todo = self.tasks.copy()
        completed = set()
        while tasks_todo:
            progress = False
            for task in tasks_todo:
                deps = self.getDependencies(task.name)
                if all(dep in completed for dep in deps):
                    if task.run is None:
                        raise ValueError(f"Erreur : La tâche '{task.name}' n'a pas de fonction.")
                    task.run()
                    completed.add(task.name)
                    tasks_todo.remove(task)
                    progress = True
                    break
            if not progress:
                raise ValueError("Erreur : Cycle détecté, ordre d'exécution impossible.")

    def run(self):
        # Un sémaphore par tâche, bloqué à 0 au départ
        semaphores = {task.name: threading.Semaphore(0) for task in self.tasks}

        def executer_tache(task):
            # On attend que chaque dépendance ait terminé
            for dep_name in self.getDependencies(task.name):
                semaphores[dep_name].acquire()
                semaphores[dep_name].release()  # on remet le jeton pour les autres

            if task.run is None:
                raise ValueError(f"Erreur : La tâche '{task.name}' n'a pas de fonction.")
            task.run()

            # On signale que cette tâche est terminée
            semaphores[task.name].release()

        threads = [threading.Thread(target=executer_tache, args=(task,)) for task in self.tasks]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def draw(self):
        G = nx.DiGraph()
        for task_name, deps in self.precedences_dict.items():
            for dep in deps:
                G.add_edge(dep, task_name)

        for task in self.tasks:
            if task.name not in G:
                G.add_node(task.name)

        plt.figure(figsize=(6, 4))
        nx.draw(G, with_labels=True, node_color='lightblue', node_size=2000)
        plt.title("Graphe de précédence")
        plt.show()

    def parCost(self, nb_executions=10):
        # Chauffe du cache avant de mesurer
        self.runSeq()
        self.run()

        temps_seq = []
        for _ in range(nb_executions):
            debut = time.perf_counter()
            self.runSeq()
            temps_seq.append(time.perf_counter() - debut)

        temps_par = []
        for _ in range(nb_executions):
            debut = time.perf_counter()
            self.run()
            temps_par.append(time.perf_counter() - debut)

        moyenne_seq = sum(temps_seq) / nb_executions
        moyenne_par = sum(temps_par) / nb_executions
        difference = moyenne_seq - moyenne_par

        if difference > 0:
            print(f"Le parallélisme est plus rapide avec un gain de {difference:.6f} secondes !")
        elif difference < 0:
            print(f"Le séquentiel est plus rapide avec une perte de {abs(difference):.6f} secondes !")
        else:
            print("Les deux exécutions sont identiques.")

        print(f"\nVoici les temps moyens sur {nb_executions} exécutions :")
        print(f"Temps moyen séquentiel : {moyenne_seq:.6f} secondes")
        print(f"Temps moyen parallèle  : {moyenne_par:.6f} secondes")

    def detTestRnd(self, globals_dict, nb_tests=5):
        for _ in range(nb_tests):
            # On initialise les variables avec des valeurs aléatoires
            for task in self.tasks:
                for var in task.writes + task.reads:
                    if var in globals_dict:
                        globals_dict[var] = random.randint(1, 100)

            self.run()
            etat_1 = tuple(globals_dict.get(var) for t in self.tasks for var in t.writes)

            # On remet les mêmes valeurs et on relance pour comparer
            for task in self.tasks:
                for var in task.writes + task.reads:
                    if var in globals_dict:
                        globals_dict[var] = random.randint(1, 100)

            self.run()
            etat_2 = tuple(globals_dict.get(var) for t in self.tasks for var in t.writes)

            if etat_1 != etat_2:
                print("Erreur : Le système n'est pas déterminé.")
                return

        print("Succès : Le système est déterminé.")