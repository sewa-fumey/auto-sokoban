# 🧠 Auto Sokoban

> Un projet réalisé par **Zakaria Maanane**, **Sewa Fumey** et **Marie Thomassin**

## 🕹️ Sokoban : un entrepôt, un gardien, un jeu !

Sokoban est un jeu de puzzle classique dans lequel le joueur incarne un gardien d’entrepôt. Son objectif ? **Déplacer des caisses** sur des emplacements précis tout en évitant de les coincer dans un angle ou contre un mur.  
Les règles sont simples :
- Les caisses **peuvent être poussées**, mais **pas tirées** ;
- Il faut **anticiper** chaque mouvement ;
- La partie se termine quand **toutes les caisses sont à leur place**.

---

## 🚀 Objectif du projet

Après s’être aventurés dans le monde des Sudokus et des papyrus, nous avons voulu aller plus loin en combinant **jeu** et **intelligence artificielle**. Le but : développer **un Sokoban jouable** puis y ajouter une **résolution automatique** via un algorithme de recherche.

---

## 🛠️ Partie 1 : Création du jeu

Nous avons développé un Sokoban interactif avec :

- Une **matrice représentant la grille** du jeu  
  (ex. : `-1` pour les obstacles, `0` pour les cases vides, `1` pour les cibles, `2` pour les caisses, `3` pour le joueur)
- Une **interface graphique** conviviale
- Les **fonctionnalités suivantes** :
  - ➕ Bouton d’annulation du dernier mouvement
  - 🔁 Réinitialisation de la partie
  - 🧩 Niveaux de difficulté variés
  - 🏆 Système de **classement** (stocké en base de données, basé sur le score, le temps ou le nombre de coups)
  - 🎵 Musique de fond
  - 🎶 Effets sonores spécifiques
  - ❌ Bouton pour quitter le jeu

---

## 🤖 Partie 2 : Intelligence Artificielle

À partir de la matrice du niveau, nous avons développé un algorithme de résolution automatique.  
L’objectif est de **résoudre le puzzle en un minimum de coups**, grâce à :

- 🔍 **Breadth-First Search (BFS)** et/ou **Depth-First Search (DFS)**
- 📲 Un bouton dans l'interface permet de **lancer la résolution automatique**, visible **étape par étape**.

---

## 🧠 Compétences mobilisées

- Conception et structuration d’un jeu en Python
- Gestion d’une interface graphique avec PyGame
- Algorithmes de recherche dans un graphe
- Sauvegarde en fichier txt


---

## 📁 Structure du projet

