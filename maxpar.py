"""
==============================================================================
Projet      : Parallélisation maximale automatique
Matière     : Systèmes d'exploitation
Fichier     : maxpar.py
Auteurs     : CHAABANE Mohamed-Mazen
Description : Bibliothèque Python pour automatiser la parallélisation
              maximale d'un système de tâches.
==============================================================================
"""
import threading


# Création d'une classe Task pour représenter une tâche dans le système de tâches
class Task:
    def __init__(self, name="", reads=None, writes=None, run=None):
        self.name = name
        self.reads = reads or []
        self.writes = writes or []
        self.run = run


# Création d'une classe TaskSystem pour représenter un système de tâches avec leurs précédences
class TaskSystem:
    def __init__(self, tasks=None, precedences_dict=None):
        self.tasks = tasks or []
        self.precedences_dict = precedences_dict or {}

        # Récupérer la liste de tous les noms
        task_names = [t.name for t in self.tasks]

        # 1. Vérifier les noms dupliqués
        if len(task_names) != len(set(task_names)):
            raise ValueError("Erreur : Des tâches ont le même nom.")

        # 2. Vérifier que les tâches du dictionnaire existent bien
        for task, deps in self.precedences_dict.items():
            if task not in task_names:
                raise ValueError(f"Erreur : La tâche '{task}' du dictionnaire n'existe pas.")
            for dep in deps:
                if dep not in task_names:
                    raise ValueError(f"Erreur : La dépendance '{dep}' n'existe pas.")

    # Méthode pour récupérer les dépendances d'une tâche
    def getDependencies(self, task):
        task_name = [t.name for t in self.tasks]
        # Vérifier que la tâche existe dans le système de tâches
        if task not in task_name:
            raise ValueError(f"Erreur : La tâche '{task}' n'existe pas.")
        return self.precedences_dict.get(task, [])

    # Méthode pour lancer les tâches dans l'ordre séquentiel en respectant les dépendances
    def runSeq(self):
        tasks_todo = self.tasks.copy()
        completed = set()
        while tasks_todo:
            progress = False
            for task in tasks_todo:
                deps = self.getDependencies(task.name)
                # Si toutes les dépendances de la tâche sont terminées, on l'exécute
                if all(dep in completed for dep in deps):
                    if task.run is None:
                        raise ValueError(f"Erreur : La tâche '{task.name}' n'a pas de fonction.")
                    task.run()
                    completed.add(task.name)
                    tasks_todo.remove(task)
                    progress = True
                    break
            # Si aucune tâche n'a pu être exécutée, il y a un blocage
            if not progress:
                raise ValueError("Erreur : Cycle détecté, ordre d'exécution impossible.")

    # Méthode pour exécuter les tâches dans l'ordre parallèle maximal
    def run(self):
        tasks_todo = self.tasks.copy()
        completed = set()
        while tasks_todo:
            ready_tasks = []
            # 1. Trouver toutes les tâches prêtes (dépendances terminées)
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
            # 3. Attendre que toutes les tâches de cette vague soient finies
            for thread in threads:
                thread.join()
            # 4. Marquer ces tâches comme terminées et les retirer de la liste d'attente
            for task in ready_tasks:
                completed.add(task.name)
                tasks_todo.remove(task)
