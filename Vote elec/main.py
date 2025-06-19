import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd
import csv
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Chemins des fichiers
FICHIER_ELECTEURS = "etudiants.csv"
FICHIER_CANDIDATS = "candidats.csv"
FICHIER_VOTES = "votes.csv"
FICHIER_ADMIN = "admin_login.txt"

# Chargement des candidats depuis le fichier CSV
# Ce fichier contient id, nom, prenom, classe, mot, image

def charger_candidats():
    return pd.read_csv(FICHIER_CANDIDATS)

# Vérifier si les informations fournies par un etudiants sont correctes
# On compare ID, nom, prénom et CNIB avec ceux du fichier etudiants.csv

def verifier_etudiants(id, nom, prenom, cnib):
    try:
        df = pd.read_csv(FICHIER_ELECTEURS)
        match = df[(df['id'].astype(str) == id) &
                   (df['nom'].str.lower() == nom.lower()) &
                   (df['prenom'].str.lower() == prenom.lower()) &
                   (df['cnib'].astype(str) == cnib)]
        return not match.empty
    except:
        return False

# Vérifie si un etudiants a déjà voté en regardant son ID dans votes.csv

def a_deja_vote(id):
    if not os.path.exists(FICHIER_VOTES):
        return False
    df = pd.read_csv(FICHIER_VOTES)
    return id in df['id'].astype(str).values

# Enregistre le vote d'un etudiants dans votes.csv

def enregistrer_vote(id, candidat):
    with open(FICHIER_VOTES, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([id, candidat])

# Vérifie si le mot de passe fourni correspond à celui du fichier admin_login.txt

def verifier_admin(mot_de_passe):
    with open(FICHIER_ADMIN, 'r') as f:
        return f.read().strip() == mot_de_passe

# Classe principale de l'interface Tkinter
class InterfaceVote:
    def __init__(self, root):
        self.root = root
        self.bg_color = "#2c2c2c"  # Gris sombre
        self.root.title("Système de Vote Électronique")
        self.root.configure(bg=self.bg_color)  # Applique le fond à la fenêtre
        self.images_refs = []  # Nécessaire pour que les images s'affichent correctement dans Tkinter
        self.accueil()  # Affiche l'écran d'accueil

    # Supprime tous les éléments de la fenêtre
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.images_refs.clear()

    # Affiche l'écran d'accueil avec les boutons principaux
    def accueil(self):
        self.clear_window()
        tk.Label(self.root, text="Bienvenue dans le système de vote de delegue", font=("Helvetica", 20,"bold"), bg=self.bg_color, fg="white").pack(pady=20)
        tk.Button(self.root, text="Voter",font=("Helvetica", 12, "bold"), command=self.login_etudiants, width=20, bg=self.bg_color, fg="white", activebackground=self.bg_color).pack(pady=10)
        tk.Button(self.root, text="Voir les résultats ", font=("Helvetica", 12, "bold"), command=self.login_admin, width=20, bg=self.bg_color, fg="white", activebackground=self.bg_color).pack(pady=10)
        tk.Button(self.root, text="Quitter", font=("Helvetica", 12, "bold"), command=self.root.quit, bg=self.bg_color, fg="white", activebackground=self.bg_color).pack(pady=10)

    # Écran de connexion pour l'etudiants avec champs d'identification
    def login_etudiants(self):
        self.clear_window()
        tk.Label(self.root, text="Entrer votre ID:").pack(pady=5)
        self.id_entry = tk.Entry(self.root)
        self.id_entry.pack()
        tk.Label(self.root, text="Nom:").pack(pady=5)
        self.nom_entry = tk.Entry(self.root)
        self.nom_entry.pack()
        tk.Label(self.root, text="Prénom:").pack(pady=5)
        self.prenom_entry = tk.Entry(self.root)
        self.prenom_entry.pack()
        tk.Label(self.root, text="Numéro CNIB:").pack(pady=5)
        self.cnib_entry = tk.Entry(self.root)
        self.cnib_entry.pack()
        tk.Button(self.root, text="Valider",font=("Helvetica", 12, "bold"), command=self.verifier_id).pack(pady=10)
        tk.Button(self.root, text="Retour", font=("Helvetica", 12, "bold"), command=self.accueil).pack(pady=5)

    # Vérifie les informations saisies par l'électeur
    def verifier_id(self):
        id = self.id_entry.get()
        nom = self.nom_entry.get()
        prenom = self.prenom_entry.get()
        cnib = self.cnib_entry.get()
        if not verifier_etudiants(id, nom, prenom, cnib):
            messagebox.showerror("Erreur", "Informations incorrectes.")
        elif a_deja_vote(id):
            messagebox.showinfo("Info", "Vous avez déjà voté.")
        else:
            self.afficher_candidats(id)

    # Affiche la liste des candidats sous forme de boutons radio avec images et descriptions
    def afficher_candidats(self, id):
        self.clear_window()
        tk.Label(self.root, text="Choisissez un candidat", font=("Helvetica", 14)).pack(pady=10)
        candidats = charger_candidats()
        self.vote_var = tk.StringVar(value="")

        for index, row in candidats.iterrows():
            frame = tk.Frame(self.root, bg=self.bg_color, bd=0, highlightthickness=0)
            frame.pack(pady=5, anchor="center")

            # Chargement de l'image du candidat si disponible
            try:
                img = Image.open(row['image'])
                img = img.resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                self.images_refs.append(photo)
                tk.Label(frame, image=photo).pack(side="top", padx=5)
            except Exception as e:
                print(f"Erreur de chargement image  {row['image']}: {e}")
                pass  # Ignore les erreurs si l'image est manquante

            # Affiche nom complet, classe et mot de campagne du candidat
            infos = f"{row['nom']} {row['prenom']} - {row['classe']}\n{row['mot'] }"
            tk.Radiobutton(frame, text=infos, justify="center", variable=self.vote_var, value=row['id']).pack(side="top")

        tk.Button(self.root, text="Voter",font=("Helvetica", 12, "bold"), command=lambda: self.valider_vote(id)).pack(pady=10)
        tk.Button(self.root, text="Retour", font=("Helvetica", 12, "bold"), command=self.accueil).pack(pady=5)

    # Enregistre le vote sélectionné pour l'électeur
    def valider_vote(self, id):
        candidat = self.vote_var.get()
        if candidat == "":
            messagebox.showwarning("Attention", "Veuillez sélectionner un candidat.")
            return
        enregistrer_vote(id, candidat)
        messagebox.showinfo("Succès", "Votre vote a été enregistré.")
        self.accueil()

    # Interface de connexion pour l'administrateur
    def login_admin(self):
        self.clear_window()
        tk.Label(self.root, text="Mot de passe administrateur:",font=("Helvetica", 12, "bold")).pack(pady=10)
        self.admin_entry = tk.Entry(self.root, show='*')
        self.admin_entry.pack()
        tk.Button(self.root, text="Connexion", font=("Helvetica", 12, "bold"), command=self.verifier_mdp_admin).pack(pady=10)
        tk.Button(self.root, text="Retour", font=("Helvetica", 12, "bold"), command=self.accueil).pack(pady=5)

    # Vérifie le mot de passe admin et affiche les résultats si correct
    def verifier_mdp_admin(self):
        mdp = self.admin_entry.get()
        if verifier_admin(mdp):
            self.afficher_resultats()
        else:
            messagebox.showerror("Erreur", "Mot de passe incorrect")

    # Affiche les résultats sous forme de graphique
    def afficher_resultats(self):
        self.clear_window()
        if not os.path.exists(FICHIER_VOTES):
            tk.Label(self.root, text="Aucun vote enregistré.").pack(pady=10)
            return

        df = pd.read_csv(FICHIER_VOTES)
        df_candidats = pd.read_csv(FICHIER_CANDIDATS)
        
     # Fusionner pour obtenir le nom complet à partir de l'id du candidat
        df_merged = df.merge(df_candidats, left_on='candidat', right_on='id', how='left')
        df_merged['nom_complet'] = df_merged['nom'] + " " + df_merged['prenom']

        resultats = df_merged['nom_complet'].value_counts()
        
        fig, ax = plt.subplots()
        resultats.plot(kind='bar', ax=ax)
        ax.set_title("Résultats des votes")
        ax.set_ylabel("Nombre de votes")

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()
        tk.Label(self.root, text="").pack(pady=30)  # Ajoute de l'espace avant le bouton Retour
        tk.Button(self.root, text="Retour", font=("Helvetica", 12, "bold"), command=self.accueil).pack(pady=10)

# Lancement de l'application principale
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceVote(root)
    root.mainloop()
