import pygame as p


class Spinner:

    def __init__(self, left, top, width, height, min_val=0, max_val=1000, button_width=None, value=0, color=p.Color("black")):
        self.left = left
        self.top = top
        self.right = left + width
        self.bottom = top - height
        self.width = width
        self.height = height
        self.rect = p.Rect(left, top, width, height)
        self.max_val = max_val
        self.min_val = min_val
        self.button_width = height if button_width is None else button_width
        self.value = value
        self.incr_btn_rect = p.Rect(self.left + (self.width - self.button_width), self.top, self.button_width, self.height//2)
        self.decr_btn_rect = p.Rect(self.left + (self.width - self.button_width), self.top + self.height//2,
                                    self.button_width, self.height // 2)
        self.color = color

    def increase(self, diff=1):
        self.value = min(self.value + diff, self.max_val)

    def decrease(self, diff=1):
        self.value = max(self.value - diff, self.min_val)

    def draw(self, surface):
        p.draw.rect(surface, self.color, self.rect, 2)
        p.draw.rect(surface, self.color, self.incr_btn_rect, 2)
        p.draw.rect(surface, self.color, self.decr_btn_rect, 2)
        font = p.font.SysFont("monospace", self.height, bold=True)
        label = font.render(str(self.value), True, self.color)
        x_label = self.left + (self.width - self.button_width) // 2
        y_label = self.bottom + self.height
        surface.blit(label, (x_label, y_label))
        # the up and down symbols
        down_label = p.font.SysFont("monospace", self.height//2, bold=True).render("v", True, self.color)
        x_up_label = x_down_label = self.decr_btn_rect.left + self.decr_btn_rect.width // 2
        y_up_label = self.incr_btn_rect.bottom - self.height//2
        up_label = p.transform.rotate(p.font.SysFont("monospace", self.height//2, bold=True).render("v", True, self.color), 180)
        y_down_label = self.decr_btn_rect.bottom - self.height//2
        surface.blit(down_label, (x_down_label, y_down_label))
        surface.blit(up_label, (x_up_label, y_up_label))

    def onClick(self, pos):
        if self.incr_btn_rect.collidepoint(pos[0], pos[1]):
            self.increase(1)
            return True
        if self.decr_btn_rect.collidepoint(pos[0], pos[1]):
            self.decrease(1)
            return True
        return False


