import pygame, sys, random
pygame.init()
COLORS = {
    "bg": (25, 25, 25),
    "cell": (170, 170, 170),
    "open": (100, 100, 100),
    "flag": (230, 30, 30),
    "pole": (80, 80, 80),
    "mine": (200, 0, 0),
    "text": (255, 255, 255),
    "button": (60, 60, 60),
    "hover": (90, 90, 90),
}
MIN_WIDTH, MIN_HEIGHT = 300, 300

def font(size): return pygame.font.SysFont(None, int(size))
def make_board(r, c, p):
    b = [['*' if random.random() < p else ' ' for _ in range(c)] for _ in range(r)]
    for i in range(r):
        for j in range(c):
            if b[i][j] == ' ':
                n = sum(0 <= x < r and 0 <= y < c and b[x][y] == '*'
                        for x in range(i-1, i+2) for y in range(j-1, j+2))
                if n: b[i][j] = str(n)
    return b
def reveal(b, show, r, c):
    if show[r][c]: return
    show[r][c] = 1
    if b[r][c] == ' ':
        for x in range(max(0, r-1), min(len(b), r+2)):
            for y in range(max(0, c-1), min(len(b[0]), c+2)):
                reveal(b, show, x, y)
def draw_text(surf, text, size, color, pos, center=True):
    t = font(size).render(text, True, color)
    rect = t.get_rect(center=pos if center else pos)
    surf.blit(t, rect)
def draw_button(surf, rect, text, hover, size):
    pygame.draw.rect(surf, COLORS["hover"] if hover else COLORS["button"], rect, border_radius=5)
    draw_text(surf, text, size, COLORS["text"], rect.center)
def draw_flag(s, x, y, cell):
    pygame.draw.line(s, COLORS["pole"], (x+cell//3, y+5), (x+cell//3, y+cell-5), 3)
    pygame.draw.polygon(s, COLORS["flag"], [
        (x+cell//3, y+5),
        (x+cell-8, y+cell//4),
        (x+cell//3, y+cell//2)
    ])
def menu():
    s = pygame.display.set_mode((500, 400), pygame.RESIZABLE)
    pygame.display.set_caption("Minesweeper Menu")
    options = [("Small (6x6)", 6, 6, 0.15), ("Medium (10x10)", 10, 10, 0.15),
               ("Large (15x15)", 15, 15, 0.15), ("Custom", None, None, None)]
    while True:
        w, h = s.get_size()
        if w < MIN_WIDTH: w = MIN_WIDTH
        if h < MIN_HEIGHT: h = MIN_HEIGHT
        s.fill(COLORS["bg"])
        draw_text(s, "Select Board Size", h*0.08, COLORS["text"], (w//2, h*0.15))
        btn_w, btn_h = w*0.5, h*0.1
        rects = [pygame.Rect(w*0.25, h*(0.35 + i*0.15), btn_w, btn_h) for i in range(4)]
        mpos = pygame.mouse.get_pos()
        for i, (t, r, c, p) in enumerate(options):
            draw_button(s, rects[i], t, rects[i].collidepoint(mpos), h*0.045)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                for i, (t, r, c, p) in enumerate(options):
                    if rects[i].collidepoint(e.pos):
                        if t == "Custom": return custom_input()
                        return minesweeper(r, c, p)
def custom_input():
    s = pygame.display.set_mode((500, 350), pygame.RESIZABLE)
    pygame.display.set_caption("Custom Board")
    fields, labels = ["", "", ""], ["Rows:", "Cols:", "Mine %:"]
    active = [False, False, False]
    while True:
        w, h = s.get_size()
        if w < MIN_WIDTH: w = MIN_WIDTH
        if h < MIN_HEIGHT: h = MIN_HEIGHT
        s.fill(COLORS["bg"])
        draw_text(s, "Custom Settings", h*0.08, COLORS["text"], (w//2, h*0.15))
        input_w, input_h = w*0.25, h*0.08
        rects = [pygame.Rect(w*0.55, h*(0.25+i*0.15), input_w, input_h) for i in range(3)]
        mpos = pygame.mouse.get_pos()
        for i, label in enumerate(labels):
            draw_text(s, label, h*0.05, COLORS["text"], (w*0.3, h*(0.29+i*0.15)))
            pygame.draw.rect(s, COLORS["hover"] if active[i] else COLORS["button"], rects[i])
            draw_text(s, fields[i], h*0.045, COLORS["text"], (rects[i].x+10, rects[i].y+input_h/2), center=False)
        ok_btn = pygame.Rect(w*0.35, h*0.75, w*0.3, h*0.1)
        draw_button(s, ok_btn, "Start", ok_btn.collidepoint(mpos), h*0.05)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(rects): active[i] = rect.collidepoint(e.pos)
                if ok_btn.collidepoint(e.pos):
                    try:
                        r, c, p = int(fields[0]), int(fields[1]), float(fields[2])/100
                        r = max(3, min(r, 40)); c = max(3, min(c, 40)); p = max(0.05, min(p, 0.5))
                        return minesweeper(r, c, p)
                    except: pass
            elif e.type == pygame.KEYDOWN:
                for i in range(3):
                    if active[i]:
                        if e.key == pygame.K_BACKSPACE: fields[i] = fields[i][:-1]
                        elif len(fields[i]) < 4 and (e.unicode.isdigit() or (i==2 and e.unicode=='.')):
                            fields[i] += e.unicode
def minesweeper(r, c, p):
    b = make_board(r, c, p)
    show = [[0]*c for _ in range(r)]
    flag = [[0]*c for _ in range(r)]
    s = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Minesweeper")
    state, msg, clock = "play", "", pygame.time.Clock()
    while True:
        clock.tick(60)
        w, h = s.get_size()
        w, h = max(w, MIN_WIDTH), max(h, MIN_HEIGHT)
        grid_h = h - 120
        cell = min((w-40)//c, (grid_h-20)//r)
        start_x = (w - (c*cell))//2
        start_y = (grid_h - (r*cell))//2 + 50
        mpos = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                x, y = e.pos
                if state != "play":
                    if menu_btn.collidepoint(mpos): return menu()
                    if restart_btn.collidepoint(mpos): return minesweeper(r, c, p)
                elif start_y <= y <= start_y + r*cell:
                    C, R = (x-start_x)//cell, (y-start_y)//cell
                    if 0 <= R < r and 0 <= C < c:
                        if e.button == 1 and not flag[R][C]:
                            if b[R][C] == '*': show[R][C]=1; state, msg="lose", "You Hit a Mine!"
                            else: reveal(b, show, R, C)
                        elif e.button == 3: flag[R][C] ^= 1
        if state == "play" and all(show[i][j] or b[i][j]=='*' for i in range(r) for j in range(c)):
            state, msg = "win", "You Win!"
        s.fill(COLORS["bg"])
        for i in range(r):
            for j in range(c):
                x, y = start_x + j*cell, start_y + i*cell
                rect = pygame.Rect(x, y, cell-1, cell-1)
                color = COLORS["open"] if show[i][j] else COLORS["cell"]
                pygame.draw.rect(s, color, rect, border_radius=3)
                if show[i][j]:
                    if b[i][j] == '*': pygame.draw.circle(s, COLORS["mine"], rect.center, cell//4)
                    elif b[i][j] != ' ': draw_text(s, b[i][j], cell*0.6, COLORS["text"], rect.center)
                elif flag[i][j]: draw_flag(s, x, y, cell)
        menu_btn = pygame.Rect(w*0.25-60, h-60, 120, 40)
        restart_btn = pygame.Rect(w*0.75-60, h-60, 120, 40)
        if state != "play": draw_text(s, msg, h*0.05, COLORS["text"], (w//2, 25))
        draw_button(s, menu_btn, "Menu", menu_btn.collidepoint(mpos), h*0.045)
        draw_button(s, restart_btn, "Restart", restart_btn.collidepoint(mpos), h*0.045)
        pygame.display.flip()
if __name__ == "__main__":
    menu()
