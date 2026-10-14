import pygame
import sys
import numpy as np
pygame.init()

# setup
SCREEN_WIDTH = 1150
SCREEN_HEIGHT = 780
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Vector Calculator")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (120, 120, 120)
DARK = (30, 30, 36)
PANEL = (20, 20, 26)
BLUE = (0, 191, 255)
YELLOW = (255, 210, 80)
RED = (255, 90, 90)
GREEN = (120, 220, 120)
clock = pygame.time.Clock()
title_font = pygame.font.Font(None, 48)
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 26)
TYPES = ["Point", "Line", "Plane"]
ORDER = {"Point": 0, "Line": 1, "Plane": 2}
EPS = 1e-9
INPUT_Y = [150, 215]
OUTPUT_RECT = pygame.Rect(30, 285, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 305)
LINE_HEIGHT = 26

#number formatting
def fmt(x):
    x = float(x)
    if abs(x) < EPS:
        return "0"
    if abs(x - round(x)) < EPS:
        return str(int(round(x)))
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s
def vec(v):
    return "(" + ", ".join(fmt(c) for c in v) + ")"
def term(coef, symbol, first):
    #one term of an expression like 2x - 3y + z, with the right sign
    if abs(coef) < EPS:
        return ""
    sign = "-" if coef < 0 else "+"
    size = "" if abs(abs(coef) - 1) < EPS else fmt(abs(coef))
    if first:
        return ("-" if coef < 0 else "") + size + symbol
    return f" {sign} {size}{symbol}"
def angle_text(theta):
    return f"{fmt(np.degrees(theta))}°  ({fmt(theta)} rad)"
def is_zero(v):
    return np.linalg.norm(v) < EPS

#other forms of a line
def line_forms(a, b, param):
    lines = [f"Vector form:\tr = {vec(a)} + {param}{vec(b)}"]
    parts = []
    for coord, a0, d in zip("xyz", a, b):
        expr = fmt(a0) if abs(a0) >= EPS else ""
        t = term(d, param, expr == "")
        expr = (expr + t) if (expr + t) else "0"
        parts.append(f"{coord} = {expr}")
    lines.append("Parametric form:\t" + ",   ".join(parts))
    fractions = []
    fixed = []
    for coord, a0, d in zip("xyz", a, b):
        if abs(d) < EPS:
            fixed.append(f"{coord} = {fmt(a0)}")
            continue
        top = coord if abs(a0) < EPS else f"{coord} {'-' if a0 > 0 else '+'} {fmt(abs(a0))}"
        if abs(d - 1) < EPS:
            fractions.append(top)
        else:
            bottom = fmt(d) if d > 0 else f"({fmt(d)})"
            fractions.append(f"{top}/{bottom}" if top == coord else f"({top})/{bottom}")
    if len(fractions) == 1:
        #the line is parallel to an axis, so only the other two coordinates are fixed
        lines.append("Cartesian form:\t" + ",   ".join(fixed) + f"   ({'xyz'[int(np.argmax(np.abs(b)))]} is any value)")
    else:
        lines.append("Cartesian form:\t" + ",   ".join([" = ".join(fractions)] + fixed))
    lines.append(f"Direction vector:\t{vec(b)}")
    return lines

#other forms of a plane
def plane_cartesian(n, d):
    expr = ""
    for coef, symbol in zip(n, "xyz"):
        expr += term(coef, symbol, expr == "")
    return f"{expr} = {fmt(d)}"
def plane_point(n, d):
    #a simple point on the plane: set two of x, y, z to 0
    for i in [2, 1, 0]:
        if abs(n[i]) >= EPS:
            p = np.zeros(3)
            p[i] = d / n[i]
            return p
def plane_directions(n):
    #two direction vectors in the plane, both perpendicular to n
    if abs(n[0]) >= EPS or abs(n[1]) >= EPS:
        b = np.array([-n[1], n[0], 0.0])
    else:
        b = np.array([1.0, 0.0, 0.0])
    c = np.cross(n, b)
    return b, c
def plane_forms(n, d):
    a = plane_point(n, d)
    b, c = plane_directions(n)
    return [
        f"Cartesian form:\t{plane_cartesian(n, d)}",
        f"Normal vector:\tn = {vec(n)},   unit normal = {vec(n / np.linalg.norm(n))}",
        f"Normal form:\tr · {vec(n)} = {fmt(d)}",
        f"Vector form:\tr = {vec(a)} + λ{vec(b)} + μ{vec(c)}",
    ]

#point and point
def point_point(P, Q):
    p, q, P_name, Q_name = P["p"], Q["p"], P["name"], Q["name"]
    pq = q - p
    cross = np.cross(p, q)
    out = [("Results", BLUE)]
    if is_zero(pq):
        out.append((f"Relationship:  {P_name} and {Q_name} coincide (same point)", GREEN))
    else:
        out.append((f"Relationship:  {P_name} and {Q_name} are different points", GREEN))
    out.append((f"Shortest distance:  |{P_name}{Q_name}| = {fmt(np.linalg.norm(pq))}", WHITE))
    if is_zero(p) or is_zero(q):
        out.append(("Angle between position vectors:  not defined (one of them is the zero vector)", WHITE))
    else:
        cos_t = np.clip(np.dot(p, q) / (np.linalg.norm(p) * np.linalg.norm(q)), -1, 1)
        out.append((f"Angle between position vectors:  θ = {angle_text(np.arccos(cos_t))}", WHITE))
    out.append((f"Dot product:  {P_name} · {Q_name} = {fmt(np.dot(p, q))}", WHITE))
    out.append((f"Cross product:  {P_name} × {Q_name} = {vec(cross)}", WHITE))
    out.append((f"Area of parallelogram with sides O{P_name}, O{Q_name}:  |{P_name} × {Q_name}| = {fmt(np.linalg.norm(cross))}", WHITE))
    out.append((f"Vector {P_name}{Q_name} = {Q_name} - {P_name} = {vec(pq)}", WHITE))
    out.append(("", WHITE))
    if is_zero(pq):
        out.append(("Line through the two points:  not defined, the points are the same", WHITE))
    else:
        out.append((f"Line through {P_name} and {Q_name}", BLUE))
        out += [(s, WHITE) for s in line_forms(p, pq, "λ")]
    return out

#point and line
def point_line(P, L):
    p, a, b = P["p"], L["a"], L["b"]
    t = np.dot(p - a, b) / np.dot(b, b)
    foot = a + t * b
    dist = np.linalg.norm(np.cross(p - a, b)) / np.linalg.norm(b)
    out = [("Results", BLUE)]
    if dist < EPS:
        out.append((f"Relationship:  {P['name']} lies on {L['name']} ({L['param']} = {fmt(t)})", GREEN))
    else:
        out.append((f"Relationship:  {P['name']} does not lie on {L['name']}", GREEN))
    out.append((f"Shortest distance:  |({P['name']} - a) × b| / |b| = {fmt(dist)}", WHITE))
    out.append((f"Closest point on {L['name']} (foot of perpendicular):  {vec(foot)}   ({L['param']} = {fmt(t)})", WHITE))
    out.append(("Angle:  not defined between a point and a line (a point has no direction)", WHITE))
    return out

#point and plane
def point_plane(P, S):
    p, n, d = P["p"], S["n"], S["d"]
    side = np.dot(n, p) - d
    dist = abs(side) / np.linalg.norm(n)
    foot = p - side / np.dot(n, n) * n
    out = [("Results", BLUE)]
    if dist < EPS:
        out.append((f"Relationship:  {P['name']} lies on {S['name']}", GREEN))
    else:
        out.append((f"Relationship:  {P['name']} does not lie on {S['name']}", GREEN))
    out.append((f"Shortest distance:  |n · {P['name']} - D| / |n| = {fmt(dist)}", WHITE))
    out.append((f"Closest point on {S['name']} (foot of perpendicular):  {vec(foot)}", WHITE))
    out.append(("Angle:  not defined between a point and a plane (a point has no direction)", WHITE))
    return out

#line and line
def line_line(L1, L2):
    a1, b1, a2, b2 = L1["a"], L1["b"], L2["a"], L2["b"]
    n1, n2 = L1["name"], L2["name"]
    cross = np.cross(b1, b2)
    cos_t = np.clip(abs(np.dot(b1, b2)) / (np.linalg.norm(b1) * np.linalg.norm(b2)), 0, 1)
    out = [("Results", BLUE)]
    if is_zero(cross):
        dist = np.linalg.norm(np.cross(a2 - a1, b1)) / np.linalg.norm(b1)
        if dist < EPS:
            out.append((f"Relationship:  {n1} and {n2} coincide (they are the same line)", GREEN))
        else:
            out.append((f"Relationship:  {n1} and {n2} are parallel", GREEN))
        out.append((f"Shortest distance:  |(a2 - a1) × b1| / |b1| = {fmt(dist)}", WHITE))
    else:
        dist = abs(np.dot(a2 - a1, cross)) / np.linalg.norm(cross)
        #least squares gives the closest point on each line, which is the intersection if they meet
        (lam, mu), *_ = np.linalg.lstsq(np.column_stack([b1, -b2]), a2 - a1, rcond=None)
        c1 = a1 + lam * b1
        c2 = a2 + mu * b2
        perpendicular = "  (they are perpendicular)" if abs(np.dot(b1, b2)) < EPS else ""
        if dist < EPS:
            out.append((f"Relationship:  {n1} and {n2} intersect{perpendicular}", GREEN))
            out.append((f"Point of intersection:  {vec(c1)}   (λ = {fmt(lam)}, μ = {fmt(mu)})", WHITE))
        else:
            out.append((f"Relationship:  {n1} and {n2} are skew{perpendicular}", GREEN))
            out.append((f"Closest points:  {vec(c1)} on {n1} (λ = {fmt(lam)}),   {vec(c2)} on {n2} (μ = {fmt(mu)})", WHITE))
        out.append((f"Shortest distance:  |(a2 - a1) · (b1 × b2)| / |b1 × b2| = {fmt(dist)}", WHITE))
    out.append((f"Angle between the lines:  θ = {angle_text(np.arccos(cos_t))}", WHITE))
    return out

#line and plane
def line_plane(L, S):
    a, b, n, d = L["a"], L["b"], S["n"], S["d"]
    nb = np.dot(n, b)
    sin_t = np.clip(abs(nb) / (np.linalg.norm(b) * np.linalg.norm(n)), 0, 1)
    out = [("Results", BLUE)]
    if abs(nb) < EPS:
        dist = abs(np.dot(n, a) - d) / np.linalg.norm(n)
        if dist < EPS:
            out.append((f"Relationship:  {L['name']} lies in {S['name']} (they coincide)", GREEN))
        else:
            out.append((f"Relationship:  {L['name']} is parallel to {S['name']}", GREEN))
        out.append((f"Shortest distance:  |n · a - D| / |n| = {fmt(dist)}", WHITE))
    else:
        t = (d - np.dot(n, a)) / nb
        perpendicular = "  (the line is perpendicular to the plane)" if is_zero(np.cross(b, n)) else ""
        out.append((f"Relationship:  {L['name']} intersects {S['name']}{perpendicular}", GREEN))
        out.append((f"Point of intersection:  {vec(a + t * b)}   ({L['param']} = {fmt(t)})", WHITE))
        out.append(("Shortest distance:  0 (they intersect)", WHITE))
    out.append((f"Angle between the line and the plane:  θ = {angle_text(np.arcsin(sin_t))}", WHITE))
    out.append(("   (sin θ = |b · n| / (|b||n|), the angle between the line and its projection on the plane)", GREY))
    return out

#plane and plane
def plane_plane(S1, S2):
    m, d1, n, d2 = S1["n"], S1["d"], S2["n"], S2["d"]
    cross = np.cross(m, n)
    cos_t = np.clip(abs(np.dot(m, n)) / (np.linalg.norm(m) * np.linalg.norm(n)), 0, 1)
    out = [("Results", BLUE)]
    if is_zero(cross):
        k = np.dot(m, n) / np.dot(m, m)
        dist = abs(d1 - d2 / k) / np.linalg.norm(m)
        if dist < EPS:
            out.append((f"Relationship:  {S1['name']} and {S2['name']} coincide (they are the same plane)", GREEN))
        else:
            out.append((f"Relationship:  {S1['name']} and {S2['name']} are parallel", GREEN))
        out.append((f"Shortest distance:  |D1 - D2/k| / |n1| = {fmt(dist)}   (n2 = k·n1, k = {fmt(k)})", WHITE))
        out.append((f"Angle between the planes:  θ = {angle_text(np.arccos(cos_t))}", WHITE))
    else:
        #a point on both planes, picked so it is also the closest one to the origin
        point = np.linalg.solve(np.array([m, n, cross]), np.array([d1, d2, 0.0]))
        perpendicular = "  (they are perpendicular)" if abs(np.dot(m, n)) < EPS else ""
        out.append((f"Relationship:  {S1['name']} and {S2['name']} intersect in a line{perpendicular}", GREEN))
        out.append(("Shortest distance:  0 (they intersect)", WHITE))
        out.append((f"Angle between the planes:  θ = {angle_text(np.arccos(cos_t))}", WHITE))
        out.append(("   (cos θ = |n1 · n2| / (|n1||n2|), the angle between the normal vectors)", GREY))
        out.append(("", WHITE))
        out.append(("Line of intersection  (direction = n1 × n2)", BLUE))
        out += [(s, WHITE) for s in line_forms(point, cross, "λ")]
    return out

CALCULATIONS = {
    ("Point", "Point"): point_point,
    ("Point", "Line"): point_line,
    ("Point", "Plane"): point_plane,
    ("Line", "Line"): line_line,
    ("Line", "Plane"): line_plane,
    ("Plane", "Plane"): plane_plane,
}

#read the input boxes of one object
def parse_number(text):
    text = text.replace(" ", "")
    if "/" in text:
        top, bottom = text.split("/", 1)
        return float(top) / float(bottom)
    return float(text)
def read_object(kind, boxes, index):
    values = []
    for box in boxes:
        if box.text.strip() == "":
            raise ValueError(f"Fill in every box for object {index}")
        try:
            values.append(parse_number(box.text))
        except (ValueError, ZeroDivisionError):
            raise ValueError(f"'{box.text}' is not a number (object {index})")
    if kind == "Point":
        return {"type": kind, "name": f"P{index}", "p": np.array(values)}
    if kind == "Line":
        b = np.array(values[3:])
        if is_zero(b):
            raise ValueError(f"The direction vector of L{index} cannot be (0, 0, 0)")
        return {"type": kind, "name": f"L{index}", "a": np.array(values[:3]), "b": b, "param": "λ" if index == 1 else "μ"}
    n = np.array(values[:3])
    if is_zero(n):
        raise ValueError(f"A, B and C of Π{index} cannot all be 0")
    return {"type": kind, "name": f"Π{index}", "n": n, "d": values[3]}
def describe(obj):
    if obj["type"] == "Point":
        return [(f"{obj['name']} = {vec(obj['p'])},   |O{obj['name']}| = {fmt(np.linalg.norm(obj['p']))}", WHITE)]
    if obj["type"] == "Line":
        return [(s, WHITE) for s in line_forms(obj["a"], obj["b"], obj["param"])]
    return [(s, WHITE) for s in plane_forms(obj["n"], obj["d"])]
def calculate(kinds, boxes):
    objects = [read_object(kinds[i], boxes[i], i + 1) for i in range(2)]
    out = []
    for obj in objects:
        out.append((f"{obj['name']}  ({obj['type'].lower()})", BLUE))
        out += describe(obj)
        out.append(("", WHITE))
    if ORDER[objects[0]["type"]] > ORDER[objects[1]["type"]]:
        objects.reverse()
    out += CALCULATIONS[(objects[0]["type"], objects[1]["type"])](objects[0], objects[1])
    return out

# Input Box Class
class InputBox:
    def __init__(self, x, y, width=70):
        self.rect = pygame.Rect(x, y, width, 36)
        self.text = ""
        self.active = False
    def handle_key(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.unicode in "0123456789.-/" and event.unicode != "" and len(self.text) < 9:
            self.text += event.unicode
    def draw(self):
        pygame.draw.rect(screen, DARK, self.rect)
        pygame.draw.rect(screen, BLUE if self.active else GREY, self.rect, 2)
        text_surface = font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + 8, self.rect.y + 9))

# Dropdown Class
class Dropdown:
    def __init__(self, x, y, label, options, selected):
        self.rect = pygame.Rect(x, y, 170, 40)
        self.label = label
        self.options = options
        self.selected = selected
        self.open = False
    def option_rect(self, i):
        return pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height, self.rect.width, self.rect.height)
    def click(self, pos):
        #returns True if the choice changed
        if self.open:
            for i, option in enumerate(self.options):
                if self.option_rect(i).collidepoint(pos):
                    self.open = False
                    changed = option != self.selected
                    self.selected = option
                    return changed
            self.open = False
        elif self.rect.collidepoint(pos):
            self.open = True
        return False
    def draw(self):
        label_surface = small_font.render(self.label, True, GREY)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 22))
        pygame.draw.rect(screen, DARK, self.rect)
        pygame.draw.rect(screen, BLUE if self.open else WHITE, self.rect, 2)
        screen.blit(font.render(self.selected, True, WHITE), (self.rect.x + 12, self.rect.y + 11))
        x, y = self.rect.right - 24, self.rect.centery
        pygame.draw.polygon(screen, WHITE, [(x - 7, y - 4), (x + 7, y - 4), (x, y + 5)])
    def draw_options(self):
        if not self.open:
            return
        for i, option in enumerate(self.options):
            rect = self.option_rect(i)
            hover = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (50, 50, 60) if hover else DARK, rect)
            pygame.draw.rect(screen, GREY, rect, 1)
            screen.blit(font.render(option, True, WHITE), (rect.x + 12, rect.y + 11))

# Button Class
class Button:
    def __init__(self, x, y, text, width=150):
        self.rect = pygame.Rect(x, y, width, 40)
        self.text = text
    def draw(self):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, BLUE if hover else DARK, self.rect)
        pygame.draw.rect(screen, BLUE, self.rect, 2)
        text_surface = font.render(self.text, True, BLACK if hover else WHITE)
        screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))

#build the equation row for one object: text pieces with input boxes between them
def build_row(kind, index, y):
    name = {"Point": f"P{index}", "Line": f"L{index}", "Plane": f"Π{index}"}[kind]
    param = "λ" if index == 1 else "μ"
    if kind == "Point":
        pieces = [f"{name} = (", 0, ",", 0, ",", 0, ")"]
    elif kind == "Line":
        pieces = [f"{name}:  r = (", 0, ",", 0, ",", 0, f")  +  {param}(", 0, ",", 0, ",", 0, ")"]
    else:
        pieces = [f"{name}:", 0, "x  +", 0, "y  +", 0, "z  =", 0]
    x = 40
    labels = []
    boxes = []
    for piece in pieces:
        if piece == 0:
            box = InputBox(x, y)
            boxes.append(box)
            x += box.rect.width + 8
        else:
            surface = font.render(piece, True, WHITE)
            labels.append((surface, (x, y + 9)))
            x += surface.get_width() + 8
    return labels, boxes

#draw the results panel, with scrolling
def draw_output(results, error, scroll):
    pygame.draw.rect(screen, PANEL, OUTPUT_RECT)
    pygame.draw.rect(screen, GREY, OUTPUT_RECT, 1)
    screen.set_clip(OUTPUT_RECT.inflate(-4, -4))
    y = OUTPUT_RECT.y + 12 - scroll
    if error:
        screen.blit(font.render(error, True, RED), (OUTPUT_RECT.x + 16, y))
    elif not results:
        hint = "Choose the two objects, type the numbers, then press Calculate or Enter.  Tab moves to the next box.  Fractions like 1/3 work."
        screen.blit(small_font.render(hint, True, GREY), (OUTPUT_RECT.x + 16, y))
    for text, color in results:
        #a tab splits a label from its value, so the values line up in one column
        if "\t" in text:
            label, text = text.split("\t")
            screen.blit(small_font.render(label, True, color), (OUTPUT_RECT.x + 16, y))
            screen.blit(small_font.render(text, True, color), (OUTPUT_RECT.x + 200, y))
        else:
            screen.blit(small_font.render(text, True, color), (OUTPUT_RECT.x + 16, y))
        y += LINE_HEIGHT
    screen.set_clip(None)
def max_scroll(results):
    return max(0, len(results) * LINE_HEIGHT + 24 - OUTPUT_RECT.height)

def main():
    dropdowns = [Dropdown(40, 70, "Object 1", TYPES, "Line"), Dropdown(240, 70, "Object 2", TYPES, "Line")]
    calculate_button = Button(460, 70, "Calculate")
    clear_button = Button(630, 70, "Clear", 110)
    rows = [build_row(dropdowns[i].selected, i + 1, INPUT_Y[i]) for i in range(2)]
    results = []
    error = ""
    scroll = 0

    def all_boxes():
        return rows[0][1] + rows[1][1]
    def set_active(target):
        for box in all_boxes():
            box.active = box is target
    def run_calculation():
        nonlocal results, error, scroll
        scroll = 0
        try:
            results = calculate([d.selected for d in dropdowns], [rows[0][1], rows[1][1]])
            error = ""
        except ValueError as e:
            results = []
            error = str(e)
    set_active(all_boxes()[0])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #an open dropdown list sits on top, so it gets the click first
                was_open = any(d.open for d in dropdowns)
                for i, dropdown in enumerate(dropdowns):
                    if dropdown.click(event.pos):
                        rows[i] = build_row(dropdown.selected, i + 1, INPUT_Y[i])
                        results, error = [], ""
                        set_active(all_boxes()[0])
                if was_open:
                    continue
                if calculate_button.rect.collidepoint(event.pos):
                    run_calculation()
                elif clear_button.rect.collidepoint(event.pos):
                    for box in all_boxes():
                        box.text = ""
                    results, error = [], ""
                    set_active(all_boxes()[0])
                else:
                    for box in all_boxes():
                        if box.rect.collidepoint(event.pos):
                            set_active(box)
            if event.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(max_scroll(results), scroll - event.y * LINE_HEIGHT))
            if event.type == pygame.KEYDOWN:
                boxes = all_boxes()
                active = [i for i, box in enumerate(boxes) if box.active]
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    run_calculation()
                elif event.key == pygame.K_TAB:
                    step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                    set_active(boxes[(active[0] + step) % len(boxes)] if active else boxes[0])
                elif active:
                    boxes[active[0]].handle_key(event)

        screen.fill(BLACK)
        screen.blit(title_font.render("3D Vector Calculator", True, WHITE), (40, 14))
        for labels, boxes in rows:
            for surface, pos in labels:
                screen.blit(surface, pos)
            for box in boxes:
                box.draw()
        draw_output(results, error, scroll)
        calculate_button.draw()
        clear_button.draw()
        for dropdown in dropdowns:
            dropdown.draw()
        for dropdown in dropdowns:
            dropdown.draw_options()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
