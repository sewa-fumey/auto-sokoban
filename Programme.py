import pygame
from collections import deque
import numpy as np

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

SIZE = 40
WINDOW_WIDTH = 380
WINDOW_HEIGHT = 500  # Agrandi pour les boutons
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Sokoban BFS")

# États du jeu
MENU = "menu"
PLAYING = "playing"
game_state = MENU

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)

# Fonction pour générer des sons synthétiques
def generate_push_sound():
    """Génère un son de poussée de caisse"""
    duration = 0.3
    sample_rate = 22050
    frames = int(duration * sample_rate)
    
    # Son de type "thud" avec fréquences basses
    arr = np.zeros((frames, 2))
    
    # Enveloppe décroissante
    envelope = np.linspace(1.0, 0.0, frames)
    
    # Mélange de fréquences pour un son de choc
    for freq in [80, 120, 160]:
        wave = np.sin(2 * np.pi * freq * np.linspace(0, duration, frames))
        arr[:, 0] += wave * envelope * 0.3
        arr[:, 1] += wave * envelope * 0.3
    
    # Ajouter du bruit pour l'effet "thud"
    noise = np.random.normal(0, 0.1, (frames, 2))
    arr += noise * envelope.reshape(-1, 1) * 0.2
    
    # Normaliser et convertir
    arr = np.clip(arr, -1, 1)
    sound_array = (arr * 32767).astype(np.int16)
    
    sound = pygame.sndarray.make_sound(sound_array)
    return sound

def generate_victory_music():
    """Génère une mélodie de victoire"""
    duration = 3.0
    sample_rate = 22050
    frames = int(duration * sample_rate)
    
    # Mélodie simple et joyeuse (Do-Mi-Sol-Do)
    notes = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 261.63]  # C-E-G-C-G-E-C
    note_duration = duration / len(notes)
    note_frames = int(note_duration * sample_rate)
    
    arr = np.zeros((frames, 2))
    
    for i, freq in enumerate(notes):
        start = i * note_frames
        end = min(start + note_frames, frames)
        note_length = end - start
        
        if note_length > 0:
            # Enveloppe douce pour chaque note
            t = np.linspace(0, note_duration, note_length)
            envelope = np.exp(-t * 2) * (1 - np.exp(-t * 10))
            
            # Son de cloche/piano synthétique
            wave = (np.sin(2 * np.pi * freq * t) * 0.5 +
                   np.sin(2 * np.pi * freq * 2 * t) * 0.2 +
                   np.sin(2 * np.pi * freq * 3 * t) * 0.1) * envelope
            
            arr[start:end, 0] += wave
            arr[start:end, 1] += wave
    
    # Normaliser
    arr = np.clip(arr, -1, 1)
    sound_array = (arr * 16383).astype(np.int16)  # Volume plus doux
    
    sound = pygame.sndarray.make_sound(sound_array)
    return sound

# Générer les sons
push_sound = generate_push_sound()
victory_music = generate_victory_music()

# Niveau simple
level = [
    "##########",
    "##      ##",
    "## $    ##",
    "##     P##",
    "##      ##",
    "####  ####",
    "##### ####",
    "##      ##",
    "### .  ###",
    "##########",
]

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.hover_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
        self.pressed_color = (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 30))
        self.is_pressed = False
        self.is_hovered = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed:
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    return True
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False
    
    def draw(self, screen):
        # Choisir la couleur selon l'état
        if self.is_pressed:
            color = self.pressed_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
        
        # Dessiner le bouton avec bordure
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 3)
        
        # Dessiner le texte centré
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Game:
    def __init__(self):
        self.reset()
        self.victory_played = False
    
    def reset(self):
        self.boxes = set()
        self.goals = set()
        self.victory_played = False
        for y, row in enumerate(level):
            for x, cell in enumerate(row):
                if cell == 'P':
                    self.player = (x, y)
                elif cell == '$':
                    self.boxes.add((x, y))
                elif cell == '.':
                    self.goals.add((x, y))
    
    def move(self, dx, dy):
        px, py = self.player
        nx, ny = px + dx, py + dy
        
        # Vérifier mur
        if level[ny][nx] == '#':
            return False
        
        box_pushed = False
        
        # Vérifier boîte
        if (nx, ny) in self.boxes:
            bx, by = nx + dx, ny + dy
            if level[by][bx] == '#' or (bx, by) in self.boxes:
                return False
            self.boxes.remove((nx, ny))
            self.boxes.add((bx, by))
            box_pushed = True
        
        self.player = (nx, ny)
        
        # Jouer le son de poussée si une boîte a été déplacée
        if box_pushed:
            push_sound.play()
        
        return True
    
    def is_solved(self):
        solved = self.boxes == self.goals
        # Jouer la musique de victoire une seule fois
        if solved and not self.victory_played:
            victory_music.play()
            self.victory_played = True
        return solved
    
    def get_state(self):
        return (self.player, tuple(sorted(self.boxes)))

def bfs_solve(game):
    start_state = game.get_state()
    queue = deque([(start_state, [])])
    visited = {start_state}
    
    while queue:
        state, path = queue.popleft()
        
        # Restaurer l'état
        game.player, boxes = state
        game.boxes = set(boxes)
        
        if game.boxes == game.goals:  # Vérification directe pour éviter de jouer le son
            return path
        
        # Essayer tous les mouvements
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            old_player, old_boxes = game.player, game.boxes.copy()
            
            if game.move_silent(dx, dy):  # Version silencieuse pour l'IA
                new_state = game.get_state()
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [(dx, dy)]))
            
            # Restaurer
            game.player, game.boxes = old_player, old_boxes
    
    return []

# Ajouter une version silencieuse du mouvement pour l'IA
def move_silent(self, dx, dy):
    px, py = self.player
    nx, ny = px + dx, py + dy
    
    if level[ny][nx] == '#':
        return False
    
    if (nx, ny) in self.boxes:
        bx, by = nx + dx, ny + dy
        if level[by][bx] == '#' or (bx, by) in self.boxes:
            return False
        self.boxes.remove((nx, ny))
        self.boxes.add((bx, by))
    
    self.player = (nx, ny)
    return True

# Ajouter la méthode silencieuse à la classe
Game.move_silent = move_silent

def draw_menu():
    screen.fill(DARK_GRAY)
    
    # Titre SOKOBAN
    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("SOKOBAN", True, WHITE)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
    screen.blit(title_text, title_rect)
    
    # Sous-titre
    subtitle_font = pygame.font.Font(None, 24)
    subtitle_text = subtitle_font.render("Résolution automatique par BFS", True, GRAY)
    subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Dessiner le bouton d'entrée
    enter_button.draw(screen)

def draw_game():
    screen.fill((50, 50, 50))
    
    # Dessiner niveau
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * SIZE, y * SIZE, SIZE, SIZE)
            if cell == '#':
                pygame.draw.rect(screen, (100, 100, 100), rect)
    
    # Dessiner objectifs
    for x, y in game.goals:
        pygame.draw.circle(screen, (0, 255, 0), (x * SIZE + SIZE//2, y * SIZE + SIZE//2), SIZE//4)
    
    # Dessiner boîtes
    for x, y in game.boxes:
        color = (255, 255, 0) if (x, y) in game.goals else (139, 69, 19)
        pygame.draw.rect(screen, color, (x * SIZE + 5, y * SIZE + 5, SIZE - 10, SIZE - 10))
    
    # Dessiner joueur
    px, py = game.player
    pygame.draw.circle(screen, (255, 0, 0), (px * SIZE + SIZE//2, py * SIZE + SIZE//2), SIZE//3)
    
    # Afficher statut
    if game.is_solved():
        font = pygame.font.Font(None, 36)
        text = font.render("GAGNE!", True, (255, 255, 255))
        screen.blit(text, (100, 100))
        font_small = pygame.font.Font(None, 24)
        text_reset = font_small.render("Appuyez sur R pour recommencer", True, (200, 200, 200))
        screen.blit(text_reset, (50, 140))
    elif move_index < len(solution):
        font = pygame.font.Font(None, 24)
        text = font.render(f"ESPACE: {move_index}/{len(solution)}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
    else:
        font = pygame.font.Font(None, 24)
        text = font.render("Solution terminée! R pour recommencer", True, (255, 255, 255))
        screen.blit(text, (10, 10))
    
    # Dessiner le bouton de sortie
    exit_button.draw(screen)

# Créer les boutons
enter_button = Button(WINDOW_WIDTH // 2 - 100, 280, 200, 60, "ENTRER", GREEN, WHITE, 36)
exit_button = Button(WINDOW_WIDTH // 2 - 60, 420, 120, 40, "SORTIE", RED, WHITE, 24)

# Initialiser le jeu (mais ne pas encore résoudre)
game = Game()
solution = []
move_index = 0
clock = pygame.time.Clock()

print("Bienvenue dans Sokoban!")
print("Cliquez sur ENTRER pour commencer")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if game_state == MENU:
            if enter_button.handle_event(event):
                # Passer au jeu et résoudre le puzzle
                game_state = PLAYING
                print("Résolution du puzzle...")
                solution = bfs_solve(game)
                game.reset()
                print(f"Solution trouvée en {len(solution)} mouvements!")
                print("Appuyez sur ESPACE pour voir la solution étape par étape")
        
        elif game_state == PLAYING:
            if exit_button.handle_event(event):
                # Retourner au menu
                game_state = MENU
                game.reset()
                move_index = 0
                solution = []
                print("Retour au menu principal")
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and move_index < len(solution):
                    dx, dy = solution[move_index]
                    game.move(dx, dy)
                    move_index += 1
                elif event.key == pygame.K_r:  # Reset avec R
                    game.reset()
                    move_index = 0
                elif event.key == pygame.K_ESCAPE:  # Échap pour retourner au menu
                    game_state = MENU
                    game.reset()
                    move_index = 0
                    solution = []
    
    # Dessiner selon l'état du jeu
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    
    pygame.display.flip()
    clock.tick(60)