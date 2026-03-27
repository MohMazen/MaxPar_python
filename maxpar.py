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

import threading
import networkx as nx
import matplotlib.pyplot as plt


# Création d'une classe Task pour représenter une tâche [cite: 17, 18]
class Task:
    def __init__(self, name="", reads=None, writes=None, run=None):
        self.name = name
        self.reads = reads or []
        self.writes = writes or []
        self.run = run


# Création d'une classe TaskSystem pour représenter un système de tâches [cite: 115]
class TaskSystem:
    def __init__(self, tasks=None, precedences_dict=None):
        self.tasks = tasks or []
        self.precedences_dict = precedences_dict or {}

        # Récupérer la liste de tous les noms
        task_names = [t.name for t in self.tasks]

        # 1. Vérifier les noms dupliqués [cite: 127]
        if len(task_names) != len(set(task_names)):
            raise ValueError("Erreur : Des tâches ont le même nom.")

        # 2. Vérifier que les tâches du dictionnaire existent bien [cite: 127]
        for task, deps in self.precedences_dict.items():
            if task not in task_names:
                raise ValueError(f"Erreur : La tâche '{task}' du dictionnaire n'existe pas.")
            for dep in deps:
                if dep not in task_names:
                    raise ValueError(f"Erreur : La dépendance '{dep}' n'existe pas.")

    # Méthode pour récupérer les dépendances d'une tâche [cite: 123]
    def getDependencies(self, task):
        task_names = [t.name for t in self.tasks]
        if task not in task_names:
            raise ValueError(f"Erreur : La tâche '{task}' n'existe pas.")
        return self.precedences_dict.get(task, [])

    # Méthode pour exécuter les tâches dans l'ordre séquentiel [cite: 124]
    def runSeq(self):
        tasks_todo = self.tasks.copy()
        completed = set()
        while tasks_todo:
            progress = False
            for task in tasks_todo:
                deps = self.getDependencies(task.name)
                # Si toutes les dépendances sont terminées, on l'exécute
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

    # Méthode pour exécuter les tâches dans l'ordre parallèle maximal [cite: 125]
    def run(self):
        tasks_todo = self.tasks.copy()
        completed = set()
        while tasks_todo:
            ready_tasks = []
            # 1. Trouver toutes les tâches prêtes
            for task in tasks_todo:
                deps = self.getDependencies(task.name)
                if all(dep in completed for dep in deps):
                    ready_tasks.append(task)

            if not ready_tasks:
                raise ValueError("Erreur : Cycle détecté, exécution bloquée.")

            # 2. Lancer toutes les tâches prêtes en même temps avec des Threads
            threads = []
            for task in ready_tasks:
                thread = threading.Thread(target=task.run)
                threads.append(thread)
                thread.start()

            # 3. Attendre que toutes les tâches soient finies
            for thread in threads:
                thread.join()

            # 4. Marquer ces tâches comme terminées
            for task in ready_tasks:
                completed.add(task.name)
                tasks_todo.remove(task)

    # Méthode pour afficher le graphe de précédence
    def draw(self):
        G = nx.DiGraph()
        # Créer les flèches allant des dépendances vers les tâches
        for task_name, deps in self.precedences_dict.items():
            for dep in deps:
                G.add_edge(dep, task_name)

        # Dessiner et afficher la fenêtre
        plt.figure(figsize=(6, 4))
        nx.draw(G, with_labels=True, node_color='lightblue', node_size=2000)
        plt.title("Graphe de précédence")
        plt.show()

