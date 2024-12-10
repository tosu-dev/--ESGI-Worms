from scripts.entities.physics_entity import PhysicsEntity

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size, outline=(0, 0, 0, 180))
        self.air_time = 0
        self.jumps = 1
        self.max_jumps= 1

    def jump(self):
        if self.jumps > 0 and self.air_time < 8:
            self.game.play_sfx('jump')
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 8

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)

        if self.collisions['bottom']:
            self.air_time = 0
            self.jumps = self.max_jumps

        if (self.collisions['left'] or self.collisions['right']) and self.air_time > 4:
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True

        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=[0, 0]):
        super().render(surf, offset)
