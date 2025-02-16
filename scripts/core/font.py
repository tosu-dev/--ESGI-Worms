import pygame


def clip(surf,x,y,x_size,y_size):
    handle_surf = surf.copy()
    clipR = pygame.Rect(x,y,x_size,y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()

class Font():
    def __init__(self, path, colorkey=(0, 0, 0), scale=1):
        self.spacing = 1
        self.character_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','.','-',',',':','+','\'','!','?','0','1','2','3','4','5','6','7','8','9','(',')','/','_','=','\\','[',']','*','"','<','>',';']
        font_img = pygame.image.load(path).convert()
        font_img.set_colorkey(colorkey)
        current_char_width = 0
        self.characters = {}
        character_count = 0
        for x in range(font_img.get_width()):
            c = font_img.get_at((x, 0))
            if c[0] == 127:
                char_img = clip(font_img, x - current_char_width, 0, current_char_width, font_img.get_height())
                self.characters[self.character_order[character_count]] = pygame.transform.scale_by(char_img.copy(), scale)
                character_count += 1
                current_char_width = 0
            else:
                current_char_width += 1
        self.space_width = self.characters['A'].get_width()

    def render(self, surf, text, loc, center=False, bg=None, padding=8):
        # Get width and height
        height = self.characters['A'].get_height()
        width = 0
        for char in text:
            if char != ' ':
                width += self.characters[char].get_width() + self.spacing
            else:
                width += self.space_width + self.spacing

        # Get offet
        x_offset = 0
        if center:
            x_offset = -(width / 2)

        # Background
        if bg is not None:
            pygame.draw.rect(surf, bg, (loc[0] + x_offset - padding, loc[1] - padding, width + padding*2, height + padding*2))

        # Text
        for char in text:
            old_x_offset = x_offset
            if char != ' ':
                x_offset += self.characters[char].get_width() + self.spacing
                surf.blit(self.characters[char], (loc[0] + old_x_offset, loc[1]))
            else:
                x_offset += self.space_width + self.spacing
