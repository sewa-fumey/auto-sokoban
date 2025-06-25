import pygame
from collections import deque

pygame.init()
SIZE = 40
screen = pygame.display.set_mode((720, 740))
pygame.display.set_caption("Sokoban BFS")

# Niveau simple
level = [
    "########",
    "#      #",
    "#  $$  #",
    "#  P # #",
    "#   .  #",
    "###  ###",
    "#### ###",
    "#      #",
    "## .  ##",
    "########",

]

class Game:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.boxes = set()
        self.goals = set()
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
        
        # Vérifier boîte
        if (nx, ny) in self.boxes:
            bx, by = nx + dx, ny + dy
            if level[by][bx] == '#' or (bx, by) in self.boxes:
                return False
            self.boxes.remove((nx, ny))
            self.boxes.add((bx, by))
        
        self.player = (nx, ny)
        return True
    
    def is_solved(self):
        return self.boxes == self.goals
    
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
        
        if game.is_solved():
            return path
        
        # Essayer tous les mouvements
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            old_player, old_boxes = game.player, game.boxes.copy()
            
            if game.move(dx, dy):
                new_state = game.get_state()
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [(dx, dy)]))
            
            # Restaurer
            game.player, game.boxes = old_player, old_boxes
    
    return []

game = Game()
solution = bfs_solve(game)
game.reset()

move_index = 0
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and move_index < len(solution):
                dx, dy = solution[move_index]
                game.move(dx, dy)
                move_index += 1
    
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
    elif move_index < len(solution):
        font = pygame.font.Font(None, 24)
        text = font.render(f"ESPACE: {move_index}/{len(solution)}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)