import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y, color):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = (x, y))

class Coin(Tile):
    def __init__(self, size, x, y, color, player):
        super().__init__(size, x, y, color)
        self.player = player
        
    def update(self):
        if self.rect.colliderect(self.player.rect):
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, size, x, y, color):
        super().__init__()
        self.x = x
        self.y = y
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = (x, y))
        self.direction = pygame.math.Vector2()
        self.gravity = 0.8
        self.jump_speed = -15
        self.speed = 5
        self.on_ground = False
        self.on_ceiling = False

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        if keys[pygame.K_UP] and self.on_ground and self.on_ceiling == False:
            self.jump()

        if self.on_ground:
            self.on_ceiling = False

    def update(self):
        self.get_input()

class Camera:
    def __init__(self, scene, player, distancex, distancey, w, h):
        self.scene = scene
        self.player = player
        self.distancex = distancex
        self.distancey = distancey
        self.w = w
        self.h = h

    def get(self):
        cameraSurf = pygame.Surface((self.w, self.h), flags=pygame.SRCALPHA)
        x = self.player.sprite.rect.x - self.distancex
        y = self.player.sprite.rect.y - self.distancey
        cameraSurf.blit(self.scene, (0, 0), pygame.Rect(x, y, self.w, self.h))
            
        return cameraSurf
        
class Level:
    def __init__(self, current_level, surface, scene, clock):
        self.display_surface = surface
        self.scene = scene

        self.fg_sprites = self.create_tile_group(current_level["fg"], "fg")
        self.player = self.create_tile_group(current_level["player"], "player")
        self.coins = self.create_tile_group(current_level["coin"], "coin")

        self.camera = Camera(scene, self.player, 250, 250, 1920, 1080)

        self.font = pygame.font.Font(None, 50)

        self.clock = clock

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != " ":
                    x = col_index * 64
                    y = row_index * 64

                    if type == "fg":
                        sprite = Tile(64, x, y, "red")
                    elif type == "bg":
                        sprite = Tile(64, x, y, "green")
                    elif type == "player":
                        sprite_group = pygame.sprite.GroupSingle()
                        sprite = Player(64, x, y, "blue")
                    elif type == "coin":
                        sprite = Coin(64, x, y, "yellow", self.player.sprite)

                    sprite_group.add(sprite)

        return sprite_group

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        for sprite in self.fg_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                if player.direction.x > 0:
                    player.rect.right = sprite.rect.left

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        for sprite in self.fg_sprites.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                    player.on_ceiling = False
                if player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
                    player.on_ground = False

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def run(self):
        self.fg_sprites.draw(self.scene)
        self.player.draw(self.scene)
        self.player.update()
        self.coins.draw(self.scene)
        self.coins.update()
        self.horizontal_movement_collision()
        self.vertical_movement_collision()
        cameraResult = self.camera.get()
        # cameraResult = pygame.transform.scale(cameraResult, (self.scene.get_width(), self.scene.get_height()))
        self.display_surface.blit(cameraResult, (0, 0))
        self.display_surface.blit(self.font.render(f"{self.clock.get_fps()}", False, "white"), (25, 25))
