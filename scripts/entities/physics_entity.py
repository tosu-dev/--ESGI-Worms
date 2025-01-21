from pygame import transform, Rect, mask

from scripts.core.utils import pg_debug


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size, outline=None):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        self.outline = outline


    def rect(self):
        return Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action: str):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0), delta_time=1):
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        frame_movement = ((movement[0]+self.velocity[0]) * 0.5 * delta_time, (movement[1]+self.velocity[1]) * delta_time)

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                elif frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['bottom'] = True
                elif frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['top'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.velocity[1] = min(3, self.velocity[1] + 0.1)

        if self.collisions['top'] or self.collisions['bottom']:
            self.velocity[1] = 0

        self.animation.update(delta_time=delta_time)

    def get_render_pos(self, offset=(0, 0)):
        return [self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]]

    def render(self, surf, offset=(0, 0)):
        pos = self.get_render_pos(offset)
        if self.outline:
            entity_mask = mask.from_surface(transform.flip(self.animation.img(), self.flip, False))
            entity_silouhette = entity_mask.to_surface(setcolor=self.outline, unsetcolor=(0, 0, 0, 0))
            for mask_offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                surf.blit(entity_silouhette, (pos[0]-mask_offset[0], pos[1]-mask_offset[1]))
        surf.blit(transform.flip(self.animation.img(), self.flip, False), pos)
