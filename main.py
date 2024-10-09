import pygame
import random
import math

pygame.init()

# Configuración de pantalla
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Prefijo de la ruta para los sprites
SPRITE_PATH = './src/assets/images/sprites/player/'

# Cargar sprites del jugador
def load_sprite(filename):
    return pygame.image.load(SPRITE_PATH + filename).convert_alpha()

# Cargar sprites del jugador en diferentes direcciones
sprites = {
    'down': [load_sprite(f'down_{i}.png') for i in range(4)],
    'left': [load_sprite(f'left_{i}.png') for i in range(4)],
    'right': [load_sprite(f'right_{i}.png') for i in range(4)],
    'up': [load_sprite(f'up_{i}.png') for i in range(4)],
}

# Propiedades del jugador
player = pygame.Rect(400, 300, 30, 30)
speed = 7  # Velocidad del jugador
lives = 3
score = 0
angle = 0  # Ángulo del jugador
current_direction = 'down'

# Variables para la animación de sprites
animation_index = 0
animation_speed = 0.1
animation_counter = 0

# Propiedades de los disparos
bullets = []
bullet_speed = 10  # Velocidad de los disparos

# Propiedades de las armas
current_weapon = "normal"  # Arma actual
max_bullets = {
    "normal": 5,
    "metralleta": 15,
    "escopeta": 3
}

# Propiedades de los enemigos
enemies = []
enemy_speed = 2  # Velocidad de los enemigos
spawn_interval = 30  # Aparición de enemigos cada 30 cuadros
max_enemies = 15  # Máximo de enemigos en pantalla

# Niveles
level = 1
next_level_score = 200  # Puntos para el siguiente nivel
level_score_increase = 100
max_levels = 10
enemy_speed_increase = 0.01
spawn_rate_decrease = 1

# Pausa
paused = False

# Función para mostrar texto en pantalla
def draw_text(text, font, color, surface, x, y):
    surface.blit(font.render(text, True, color), (x, y))

# Función para generar enemigos
def spawn_enemy():
    if len(enemies) < max_enemies:
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return pygame.Rect(random.randint(0, 770), 0, 30, 30)
        if side == 'bottom':
            return pygame.Rect(random.randint(0, 770), 600, 30, 30)
        if side == 'left':
            return pygame.Rect(0, random.randint(0, 570), 30, 30)
        return pygame.Rect(800, random.randint(0, 570), 30, 30)

# Función para disparar
def shoot():
    if current_weapon == "normal" and len(bullets) < max_bullets[current_weapon]:
        angle_rad = math.radians(angle)
        bullet_dx = math.cos(angle_rad) * bullet_speed
        bullet_dy = -math.sin(angle_rad) * bullet_speed
        bullets.append({'rect': pygame.Rect(player.x + 12, player.y + 12, 5, 5), 'dx': bullet_dx, 'dy': bullet_dy})

    elif current_weapon == "escopeta" and len(bullets) < max_bullets[current_weapon]:
        angle_rad = math.radians(angle)
        spread = 0.2  # Ángulo de dispersión
        for i in range(-1, 2):  # Dispara tres balas
            bullet_dx = math.cos(angle_rad + i * spread) * bullet_speed
            bullet_dy = -math.sin(angle_rad + i * spread) * bullet_speed
            bullets.append({'rect': pygame.Rect(player.x + 12, player.y + 12, 5, 5), 'dx': bullet_dx, 'dy': bullet_dy})

    elif current_weapon == "metralleta":
        for _ in range(max_bullets[current_weapon]):  # Dispara múltiples balas
            angle_rad = math.radians(angle)
            bullet_dx = math.cos(angle_rad) * bullet_speed
            bullet_dy = -math.sin(angle_rad) * bullet_speed
            bullets.append({'rect': pygame.Rect(player.x + 12, player.y + 12, 5, 5), 'dx': bullet_dx, 'dy': bullet_dy})

# Función para obtener el sprite actual según la dirección y animación
def get_player_sprite():
    global animation_index, animation_counter
    
    # Actualizar la animación del sprite
    animation_counter += animation_speed
    if animation_counter >= 1:
        animation_counter = 0
        animation_index = (animation_index + 1) % len(sprites[current_direction])
    
    return sprites[current_direction][animation_index]

# Función para reiniciar el juego
def reset_game():
    global lives, score, level, enemies, bullets, current_weapon
    lives = 3
    score = 0
    level = 1
    enemies = []
    bullets = []
    current_weapon = "normal"

# Ciclo principal del juego
running, frames = True, 0
while running:
    frames += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_p]:
        paused = not paused
        pygame.time.wait(200)

    if paused:
        draw_text("PAUSA", font, (255, 255, 255), screen, 360, 300)
        pygame.display.flip()
        clock.tick(30)
        continue

    if keys[pygame.K_ESCAPE]:
        running = False

    # Cambio de arma
    if keys[pygame.K_1]:
        current_weapon = "normal"
    elif keys[pygame.K_2]:
        current_weapon = "metralleta"
    elif keys[pygame.K_3]:
        current_weapon = "escopeta"

    # Movimiento del jugador
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= speed
        angle = 180
        current_direction = 'left'
    if keys[pygame.K_RIGHT] and player.right < 800:
        player.x += speed
        angle = 0
        current_direction = 'right'
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= speed
        angle = 90
        current_direction = 'up'
    if keys[pygame.K_DOWN] and player.bottom < 600:
        player.y += speed
        angle = 270
        current_direction = 'down'

    # Disparar
    if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
        shoot()

    # Actualizar balas
    bullets = [b for b in bullets if 0 < b['rect'].x < 800 and 0 < b['rect'].y < 600]
    for bullet in bullets:
        bullet['rect'].x += bullet['dx']
        bullet['rect'].y += bullet['dy']

    # Generar enemigos
    if frames % spawn_interval == 0:
        enemy = spawn_enemy()
        if enemy:
            enemies.append(enemy)

    # Mover enemigos hacia el jugador
    for enemy in enemies[:]:
        direction_x = player.x - enemy.x
        direction_y = player.y - enemy.y
        distance = math.sqrt(direction_x**2 + direction_y**2)
        if distance:
            enemy.x += int(enemy_speed * (direction_x / distance))
            enemy.y += int(enemy_speed * (direction_y / distance))

        if player.colliderect(enemy):
            enemies.remove(enemy)
            lives -= 1

        if enemy.top > 600 or enemy.left > 800 or enemy.right < 0 or enemy.bottom < 0:
            enemies.remove(enemy)

    # Colisiones balas-enemigos
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if enemy.colliderect(bullet['rect']):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                break

    # Subir de nivel
    if score >= next_level_score and level < max_levels:
        level += 1
        next_level_score += level_score_increase
        enemy_speed += enemy_speed_increase
        spawn_interval = max(5, spawn_interval - spawn_rate_decrease)

        # Incrementar la vida del jugador
        lives += 1  # Agregar una vida adicional al jugador

    # Dibujar pantalla
    screen.fill((0, 0, 0))
    
    # Dibujar al jugador con sprites
    player_sprite = get_player_sprite()
    screen.blit(player_sprite, player.topleft)

    # Dibujar balas
    for bullet in bullets:
        pygame.draw.rect(screen, (255, 255, 255), bullet['rect'])
    
    # Dibujar enemigos
    for enemy in enemies:
        pygame.draw.rect(screen, (0, 255, 0), enemy)

    # Mostrar puntaje, vidas, nivel y arma
    draw_text(f"Puntos: {score}", font, (255, 255, 255), screen, 10, 10)
    draw_text(f"Vidas: {lives}", font, (255, 255, 255), screen, 700, 10)
    draw_text(f"Nivel: {level}", font, (255, 255, 255), screen, 360, 10)
    draw_text(f"Arma: {current_weapon}", font, (255, 255, 255), screen, 360, 40)

    pygame.display.flip()
    clock.tick(30)  # Limitar a 30 FPS

    if lives <= 0:
        screen.fill((0, 0, 0))
        draw_text("GAME OVER", font, (255, 0, 0), screen, 320, 250)
        draw_text(f"Puntos: {score}", font, (255, 255, 255), screen, 350, 300)
        draw_text("Presiona R para reiniciar o ESC para salir", font, (255, 255, 255), screen, 150, 350)
        pygame.display.flip()

        # Esperar entrada para reiniciar o salir
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reiniciar juego
                        reset_game()
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:  # Salir del juego
                        waiting = False

pygame.quit()
