import logging
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from pixoo import Pixoo

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

DEFAULT_PIXOO_IP = "192.168.1.215"
PIXOO_SIZE = 64
SNAKE_SPEED = 200
DIFFICULTIES = {
    "Easy": 8,
    "Medium": 4,
    "Hard": 2,
    "Insane": 1
}
current_difficulty = "Hard"
block_size = DIFFICULTIES[current_difficulty]
show_grid = False
game_running = False
game_paused = False
pixoo = None
snake = []
snake_direction = (0, 0)
food = None
score = 0
last_frame_img = None
root = None
preview_label = None
ip_entry = None
difficulty_var = None

def connect_to_pixoo(ip_address):
    global pixoo
    try:
        pixoo = Pixoo(ip_address)
        return True
    except Exception as e:
        logging.error(f"Failed to connect to Pixoo: {e}")
        return False

def start_game():
    global snake, snake_direction, food, score, game_running, block_size, game_paused
    diff_name = difficulty_var.get()
    if diff_name in DIFFICULTIES:
        block_size = DIFFICULTIES[diff_name]
    else:
        block_size = 2
    snake = [(PIXOO_SIZE // 2, PIXOO_SIZE // 2)]
    snake_direction = (1, 0)
    food = place_food()
    score = 0
    game_running = True
    game_paused = False
    root.title(f"Pixoo Snake ({diff_name}) — Score: {score}")
    draw_and_push_frame()
    schedule_next_update()

def stop_game():
    global game_running
    game_running = False
    show_device_message("Game Stopped")

def pause_game():
    global game_paused
    if game_running:
        game_paused = True
        show_device_message("Paused")

def resume_game():
    global game_paused
    if game_running and game_paused:
        game_paused = False
        draw_and_push_frame()
        schedule_next_update()

def schedule_next_update():
    if game_running and not game_paused:
        root.after(SNAKE_SPEED, game_loop)

def game_loop():
    global snake, snake_direction, food, game_running, score, game_paused
    if not game_running or game_paused:
        return
    head_x, head_y = snake[0]
    dx, dy = snake_direction
    if dx == 0 and dy == 0:
        schedule_next_update()
        return
    new_x = (head_x + dx * block_size) % PIXOO_SIZE
    new_y = (head_y + dy * block_size) % PIXOO_SIZE
    head_coverage = get_coverage(new_x, new_y, block_size)
    body_coverage = set()
    for (sx, sy) in snake:
        body_coverage |= get_coverage(sx, sy, block_size)
    old_head_coverage = get_coverage(head_x, head_y, block_size)
    body_coverage -= old_head_coverage
    if head_coverage & body_coverage:
        game_over()
        return
    snake.insert(0, (new_x, new_y))
    food_coverage = get_coverage(food[0], food[1], block_size)
    if head_coverage & food_coverage:
        score += 1
        root.title(f"Pixoo Snake ({difficulty_var.get()}) — Score: {score}")
        food = place_food()
        if len(snake) > 50:
            show_device_message("You Win!")
            game_running = False
            return
    else:
        snake.pop()
    draw_and_push_frame()
    schedule_next_update()

def game_over():
    global game_running
    game_running = False
    show_device_message("Game Over!")

def show_device_message(msg):
    global last_frame_img
    if last_frame_img is None:
        last_frame_img = Image.new("RGB", (PIXOO_SIZE, PIXOO_SIZE), (0, 0, 0))
    if pixoo:
        try:
            pixoo.clear()
            pixoo.draw_image(last_frame_img)
            pixoo.draw_text(msg, (0, 0), (255, 255, 255))
            pixoo.push()
        except Exception as e:
            logging.error(f"Failed to show device message '{msg}': {e}")

def place_food():
    while True:
        fx = random.randrange(0, PIXOO_SIZE, block_size)
        fy = random.randrange(0, PIXOO_SIZE, block_size)
        food_cov = get_coverage(fx, fy, block_size)
        snake_cov = set()
        for (sx, sy) in snake:
            snake_cov |= get_coverage(sx, sy, block_size)
        if not (food_cov & snake_cov):
            return (fx, fy)

def get_coverage(x, y, size):
    coords = set()
    for dx in range(size):
        for dy in range(size):
            px = (x + dx) % PIXOO_SIZE
            py = (y + dy) % PIXOO_SIZE
            coords.add((px, py))
    return coords

def draw_and_push_frame():
    global last_frame_img
    img = Image.new("RGB", (PIXOO_SIZE, PIXOO_SIZE), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    for (fx, fy) in get_coverage(food[0], food[1], block_size):
        draw.point((fx, fy), fill=(255, 0, 0))
    for seg in snake:
        for (px, py) in get_coverage(seg[0], seg[1], block_size):
            draw.point((px, py), fill=(0, 255, 0))
    if show_grid:
        draw_grid(draw, img.size)
    last_frame_img = img.copy()
    if pixoo is not None:
        try:
            pixoo.clear()
            pixoo.draw_image(img)
            pixoo.draw_text(f"Score: {score}", (0, 0), (255, 255, 255))
            pixoo.push()
        except Exception as e:
            logging.error(f"Failed to render to Pixoo: {e}")
    preview_img = img.resize((PIXOO_SIZE * 8, PIXOO_SIZE * 8), Image.NEAREST)
    preview_img_tk = ImageTk.PhotoImage(preview_img)
    preview_label.config(image=preview_img_tk)
    preview_label.image = preview_img_tk

def draw_grid(draw, size, grid_size=8, line_color=(100, 100, 100), line_width=1):
    width, height = size
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=line_color, width=line_width)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=line_color, width=line_width)

def on_key_press(event):
    global snake_direction
    dx, dy = snake_direction
    if event.keysym == "Up" and dy == 0:
        snake_direction = (0, -1)
    elif event.keysym == "Down" and dy == 0:
        snake_direction = (0, 1)
    elif event.keysym == "Left" and dx == 0:
        snake_direction = (-1, 0)
    elif event.keysym == "Right" and dx == 0:
        snake_direction = (1, 0)

def toggle_grid():
    global show_grid
    show_grid = not show_grid
    if game_running or snake:
        draw_and_push_frame()

def on_difficulty_change(event=None):
    pass

def on_connect_button_click():
    ip_address = ip_entry.get().strip()
    if not ip_address:
        tk.messagebox.showwarning("Empty IP", "Please enter a valid IP address.")
        return
    success = connect_to_pixoo(ip_address)
    if success:
        tk.messagebox.showinfo("Connected", f"Successfully connected to Pixoo at {ip_address}")
    else:
        tk.messagebox.showerror("Connection Failed", f"Could not connect to Pixoo at {ip_address}")

def main():
    global root, preview_label, ip_entry, difficulty_var
    root = tk.Tk()
    root.title("Pixoo Snake")
    ip_frame = ttk.Frame(root)
    ip_frame.pack(padx=10, pady=10, fill="x")
    ip_label = ttk.Label(ip_frame, text="Pixoo IP:")
    ip_label.pack(side=tk.LEFT, padx=5)
    ip_entry_ = ttk.Entry(ip_frame, width=20)
    ip_entry_.pack(side=tk.LEFT, padx=5)
    ip_entry_.insert(0, DEFAULT_PIXOO_IP)
    connect_button = ttk.Button(ip_frame, text="Connect", command=on_connect_button_click)
    connect_button.pack(side=tk.LEFT, padx=5)
    global ip_entry
    ip_entry = ip_entry_
    diff_frame = ttk.Frame(root)
    diff_frame.pack(padx=10, pady=5, fill="x")
    diff_label = ttk.Label(diff_frame, text="Difficulty:")
    diff_label.pack(side=tk.LEFT, padx=5)
    diff_var = tk.StringVar(value=current_difficulty)
    diff_combobox = ttk.Combobox(
        diff_frame,
        textvariable=diff_var,
        values=["Easy", "Medium", "Hard", "Insane"],
        state="readonly"
    )
    diff_combobox.pack(side=tk.LEFT, padx=5)
    diff_combobox.bind("<<ComboboxSelected>>", on_difficulty_change)
    global difficulty_var
    difficulty_var = diff_var
    preview_label_ = ttk.Label(root)
    preview_label_.pack(padx=10, pady=10)
    global preview_label
    preview_label = preview_label_
    button_frame = ttk.Frame(root)
    button_frame.pack(padx=10, pady=10)
    start_button = ttk.Button(button_frame, text="Start Game", command=start_game)
    start_button.pack(side=tk.LEFT, padx=5)
    stop_button = ttk.Button(button_frame, text="Stop Game", command=stop_game)
    stop_button.pack(side=tk.LEFT, padx=5)
    pause_button = ttk.Button(button_frame, text="Pause", command=pause_game)
    pause_button.pack(side=tk.LEFT, padx=5)
    resume_button = ttk.Button(button_frame, text="Resume", command=resume_game)
    resume_button.pack(side=tk.LEFT, padx=5)
    grid_button = ttk.Button(button_frame, text="Toggle Grid", command=toggle_grid)
    grid_button.pack(side=tk.LEFT, padx=5)
    root.bind("<Up>", on_key_press)
    root.bind("<Down>", on_key_press)
    root.bind("<Left>", on_key_press)
    root.bind("<Right>", on_key_press)
    connected = connect_to_pixoo(DEFAULT_PIXOO_IP)
    if not connected:
        logging.error("Initial connection to Pixoo failed.")
    root.mainloop()

if __name__ == "__main__":
    main()
