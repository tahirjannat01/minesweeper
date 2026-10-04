import tkinter as tk
import random
import os

ROWS = 9
COLS = 9
MINES = 10

root = tk.Tk()
root.title("Minesweeper")
root.resizable(False, False)

_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "logo.png")
try:
    logo_image = tk.PhotoImage(file=_logo_path)
    root.iconphoto(False, logo_image)
except Exception as _e:
    logo_image = None

board = []
buttons = []
mines_set = []
flags_count = 0
game_active = True

status_label = tk.Label(root, text="", font=("Helvetica", 12, "bold"))
status_label.grid(row=0, column=0, columnspan=COLS, pady=(5, 2))

new_game_btn = tk.Button(root, text="New Game", font=("Helvetica", 11, "bold"),
                         command=lambda: new_game())
new_game_btn.grid(row=1, column=0, columnspan=COLS, pady=(2, 8))

NUMBER_COLORS = {
    1: "#0000FF",
    2: "#008000",
    3: "#FF0000",
    4: "#000080",
    5: "#800000",
    6: "#008080",
    7: "#000000",
    8: "#808080",
}


def create_board():
    global board, buttons
    board = []
    buttons = []
    for r in range(ROWS):
        row_data = []
        btn_row = []
        for c in range(COLS):
            cell = {
                "mine": False,
                "revealed": False,
                "flagged": False,
                "neighbor_mines": 0,
            }
            row_data.append(cell)
            btn = tk.Button(root, width=2, height=1, font=("Helvetica", 12, "bold"),
                            bg="#C0C0C0", relief="raised",
                            command=lambda rr=r, cc=c: reveal_cell(rr, cc))
            btn.bind("<Button-3>", lambda e, rr=r, cc=c: toggle_flag(rr, cc))
            btn.grid(row=r + 2, column=c, padx=1, pady=1)
            btn_row.append(btn)
        board.append(row_data)
        buttons.append(btn_row)


def place_mines():
    global mines_set
    mines_set = []
    all_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]
    mines_set = random.sample(all_cells, MINES)
    for (r, c) in mines_set:
        board[r][c]["mine"] = True


def calculate_numbers():
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]["mine"]:
                continue
            count = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        if board[nr][nc]["mine"]:
                            count += 1
            board[r][c]["neighbor_mines"] = count


def reveal_cell(r, c):
    global game_active
    if not game_active:
        return
    cell = board[r][c]
    if cell["revealed"] or cell["flagged"]:
        return

    if cell["mine"]:
        game_over(r, c)
        return

    _flood_reveal(r, c)
    check_win()


def _flood_reveal(r, c):
    cell = board[r][c]
    if cell["revealed"] or cell["flagged"] or cell["mine"]:
        return

    cell["revealed"] = True
    btn = buttons[r][c]
    n = cell["neighbor_mines"]
    btn.config(bg="#E0E0E0", relief="sunken", state="disabled")
    if n > 0:
        btn.config(text=str(n), fg=NUMBER_COLORS.get(n, "#000000"))
    else:
        btn.config(text="")

    if n == 0:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = r + dr
                nc = c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    _flood_reveal(nr, nc)


def toggle_flag(r, c):
    global flags_count, game_active
    if not game_active:
        return
    cell = board[r][c]
    if cell["revealed"]:
        return
    btn = buttons[r][c]
    if cell["flagged"]:
        cell["flagged"] = False
        flags_count -= 1
        btn.config(text="", bg="#C0C0C0", fg="#000000")
    else:
        cell["flagged"] = True
        flags_count += 1
        btn.config(text="F", bg="#FFCC00", fg="#000000")
    update_status()


def check_win():
    global game_active
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            if not cell["mine"] and not cell["revealed"]:
                return
    game_active = False
    for (mr, mc) in mines_set:
        buttons[mr][mc].config(text="M", bg="#00CC00", fg="#000000")
    status_label.config(text="You Win!  Mines: {}  Flags: {}".format(MINES, flags_count),
                         fg="#008000")


def game_over(r, c):
    global game_active
    game_active = False
    buttons[r][c].config(text="M", bg="#FF0000", fg="#FFFFFF")
    for (mr, mc) in mines_set:
        if not (mr == r and mc == c):
            if not board[mr][mc]["flagged"]:
                buttons[mr][mc].config(text="M", bg="#FF6666", fg="#000000")
    for rr in range(ROWS):
        for cc in range(COLS):
            if board[rr][cc]["flagged"] and not board[rr][cc]["mine"]:
                buttons[rr][cc].config(text="X", bg="#FFAA00", fg="#000000")
    status_label.config(text="Game Over  Mines: {}  Flags: {}".format(MINES, flags_count),
                         fg="#FF0000")


def update_status():
    status_label.config(text="Mines: {}  Flags: {}".format(MINES, flags_count),
                        fg="#000000")


def new_game():
    global flags_count, game_active
    flags_count = 0
    game_active = True
    for r in range(ROWS):
        for c in range(COLS):
            buttons[r][c].config(text="", bg="#C0C0C0", fg="#000000",
                                 relief="raised", state="normal")
    for r in range(ROWS):
        for c in range(COLS):
            board[r][c]["mine"] = False
            board[r][c]["revealed"] = False
            board[r][c]["flagged"] = False
            board[r][c]["neighbor_mines"] = 0
    place_mines()
    calculate_numbers()
    update_status()


create_board()
place_mines()
calculate_numbers()
update_status()

root.mainloop()