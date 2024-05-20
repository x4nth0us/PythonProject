import random
import time
from tkinter import *

COLORS = {
    1: 'blue',
    2: 'green',
    3: 'red',
    4: 'purple',
    5: 'orange',
    6: '#00999c',
    7: '#f702a5',
    8: 'black'
}

DIFFICULTIES = {
    'easy': 'Простой',
    'medium': 'Средний',
    'hard': 'Сложный'
}


class MyButton(Button):
    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, height=1, font="Calibri 13 bold", *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_mines = 0
        self.is_open = False
        self.is_flag = False

    def __repr__(self):
        return f'MyButton {self.x} {self.y} {self.number} {self.is_mine}'


class Minesweeper:
    window = Tk()
    window.title('Сапер')
    difficulty = 'easy'
    rows = 8
    columns = 10
    mines = 10
    is_game_over = False
    is_first_click = True
    GAME_RECORDS_FILE = "game_records.txt"
    best_times = {
        'easy': float('inf'),
        'medium': float('inf'),
        'hard': float('inf')
    }

    def __init__(self):
        self.time_label = None
        self.flag_label = None
        self.time_start = 0
        self.count_flags = 0
        self.buttons = []
        self.load_game_records()
        self.create_buttons()

    def create_buttons(self):
        for i in range(self.rows + 2):
            temp = []
            for j in range(self.columns + 2):
                btn = MyButton(self.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind('<Button-3>', self.right_click)
                temp.append(btn)
            self.buttons.append(temp)

    def load_game_records(self):
        with open(self.GAME_RECORDS_FILE, 'r') as file:
            for line in file:
                try:
                    record_time, status, diff = line.strip().split(',')
                    record_time = float(record_time)
                    if status == 'win':
                        self.best_times[diff] = min(self.best_times[diff], record_time)
                except ValueError:
                    continue

    def right_click(self, event):
        if self.is_first_click:
            return
        if self.is_game_over:
            return
        current_btn = event.widget
        if not current_btn.is_flag and not current_btn.is_open:
            if self.count_flags == 0:
                return
            current_btn.config(state='disabled', text='🚩', disabledforeground='red')
            current_btn.is_flag = True
            self.count_flags -= 1
            self.flag_label.config(text=f'🚩: {self.count_flags}')
        elif current_btn.is_flag and not current_btn.is_open:
            current_btn.config(state='normal', text='')
            current_btn.is_flag = False
            self.count_flags += 1
            self.flag_label.config(text=f'🚩: {self.count_flags}')
        self.check_win()

    def click(self, clicked_button: MyButton):
        if self.is_game_over:
            return

        if self.is_first_click:
            self.insert_mines(clicked_button)
            self.count_mines_in_neigh()
            self.print_buttons()
            self.is_first_click = False
            self.time_start = time.time()
            self.tick()

        if clicked_button.is_mine:
            clicked_button.config(text="💣", background='red', disabledforeground='black')
            clicked_button.is_open = True
            self.is_game_over = True
            self.show_all_mines()
            self.show_results('lose')
        else:
            color = COLORS.get(clicked_button.count_mines)
            if clicked_button.count_mines:
                clicked_button.config(text=clicked_button.count_mines, disabledforeground=color)
                clicked_button.is_open = True
            else:
                self.open_all_zeros(clicked_button)
        clicked_button.config(state='disabled', relief=SUNKEN)
        self.check_win()

    def open_all_zeros(self, btn: MyButton):
        queue = [btn]
        while queue:
            current_btn = queue.pop()
            color = COLORS.get(current_btn.count_mines)
            if current_btn.count_mines:
                current_btn.config(text=current_btn.count_mines, disabledforeground=color)
            else:
                current_btn['text'] = ''
            current_btn.is_open = True
            current_btn.config(state='disabled', relief=SUNKEN)

            if current_btn.count_mines == 0:
                x, y = current_btn.x, current_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        next_btn = self.buttons[x + dx][y + dy]
                        if not next_btn.is_open and next_btn not in queue \
                                and 1 <= next_btn.x <= self.rows and 1 <= next_btn.y <= self.columns:
                            queue.append(next_btn)

    def create_widgets(self):
        menubar = Menu(self.window)
        self.window.config(menu=menubar)

        difficulty_menu = Menu(menubar, tearoff=0)
        difficulty_menu.add_command(label='Простой', command=lambda: self.set_difficulty('easy'))
        difficulty_menu.add_command(label='Средний', command=lambda: self.set_difficulty('medium'))
        difficulty_menu.add_command(label='Сложный', command=lambda: self.set_difficulty('hard'))
        diff = DIFFICULTIES.get(self.difficulty)
        menubar.add_cascade(label=diff, menu=difficulty_menu)

        self.count_flags = self.mines
        self.time_label = Label(text='⏰: 0', font='12')
        self.time_label.grid(row=0, column=1, columnspan=(self.columns // 2))
        self.flag_label = Label(text=f'🚩: {self.count_flags}', font='12')
        self.flag_label.grid(row=0, column=(self.columns // 2) + 1, columnspan=(self.columns // 2))

        count = 1
        for i in range(1, self.rows + 1):
            for j in range(1, self.columns + 1):
                btn = self.buttons[i][j]
                btn.number = count
                count += 1
                btn.grid(row=i, column=j, stick='NWES')

        for i in range(1, self.rows + 1):
            Grid.rowconfigure(self.window, i, weight=1)
        for i in range(1, self.columns + 1):
            Grid.columnconfigure(self.window, i, weight=1)

    def set_difficulty(self, diff: str):
        if diff == 'easy':
            self.rows = 8
            self.columns = 10
            self.mines = 10
            self.difficulty = 'easy'
        elif diff == 'medium':
            self.rows = 14
            self.columns = 18
            self.mines = 40
            self.difficulty = 'medium'
        elif diff == 'hard':
            self.rows = 20
            self.columns = 24
            self.mines = 99
            self.difficulty = 'hard'
        self.restart()

    def tick(self):
        if self.is_game_over:
            return
        timer = time.time() - self.time_start
        self.time_label.config(text=f'⏰: {timer:.0f}')
        self.time_label.after(500, self.tick)

    def restart(self, result_window=None):
        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.create_widgets()
        self.is_first_click = True
        self.is_game_over = False
        if result_window:
            result_window.destroy()

    def show_all_mines(self):
        for i in range(self.rows + 2):
            for j in range(self.columns + 2):
                btn = self.buttons[i][j]
                if btn.is_mine and btn.is_flag:
                    btn['disabledforeground'] = 'green'
                elif not btn.is_mine and btn.is_flag:
                    btn['text'] = 'X'
                elif btn.is_mine:
                    btn['text'] = '💣'

    def insert_mines(self, clicked_btn: MyButton):
        mines_places = self.get_mines_places(clicked_btn)
        for i in range(1, self.rows + 1):
            for j in range(1, self.columns + 1):
                btn = self.buttons[i][j]
                if btn.number in mines_places:
                    btn.is_mine = True

    def get_mines_places(self, clicked_btn: MyButton):
        indexes = list(range(1, self.rows * self.columns + 1))

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbor_x = clicked_btn.x + dx
                neighbor_y = clicked_btn.y + dy
                if 1 <= neighbor_x <= self.rows and 1 <= neighbor_y <= self.columns:
                    neighbor_number = (neighbor_x - 1) * self.columns + neighbor_y
                    indexes.remove(neighbor_number)

        random.shuffle(indexes)
        return indexes[:self.mines]

    def count_mines_in_neigh(self):
        for i in range(1, self.rows + 1):
            for j in range(1, self.columns + 1):
                btn = self.buttons[i][j]
                count_mines = 0
                if not btn.is_mine:
                    for row_neigh in [-1, 0, 1]:
                        for col_neigh in [-1, 0, 1]:
                            neighbor = self.buttons[i + row_neigh][j + col_neigh]
                            if neighbor.is_mine:
                                count_mines += 1
                btn.count_mines = count_mines

    def open_all_buttons(self):
        for i in range(self.rows + 2):
            for j in range(self.columns + 2):
                btn = self.buttons[i][j]
                self.click(btn)

    def print_buttons(self):
        for i in range(1, self.rows + 1):
            for j in range(1, self.columns + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print("*", end=" ")
                else:
                    print(btn.count_mines, end=" ")
            print()
        print('------------------------------------------------')

    def check_win(self):
        if self.count_flags == 0:
            open_buttons = 0
            right_flags = 0
            for i in range(1, self.rows + 1):
                for j in range(1, self.columns + 1):
                    btn = self.buttons[i][j]
                    if btn.is_open or btn.is_flag:
                        open_buttons += 1
                    if btn.is_mine and btn.is_flag:
                        right_flags += 1
            if open_buttons == self.rows * self.columns:
                if right_flags == self.mines:
                    self.is_game_over = True
                    self.show_all_mines()
                    self.show_results('win')

    def show_results(self, game_status: str):
        result_window = Toplevel(self.window)
        result_window.geometry("200x150")

        game_time = time.time() - self.time_start
        if game_status == 'win':
            result_window.title('Победа!')
            self.best_times[self.difficulty] = min(self.best_times[self.difficulty], game_time)
        elif game_status == 'lose':
            result_window.title('Поражение!')

        Label(result_window, text=f'Ваше время: {game_time:.0f} \n'
                                  f'Лучшее время: {self.best_times[self.difficulty]:.0f}').pack(anchor=CENTER,
                                                                                                expand=1)
        Button(result_window, text='Сыграть снова?', command=lambda: self.restart(result_window)).pack(anchor=CENTER,
                                                                                                       expand=1)

        self.append_game_record(game_time, game_status, self.difficulty)

    def append_game_record(self, game_time, status, diff):
        with open(self.GAME_RECORDS_FILE, 'a') as file:
            file.write(f"{game_time},{status},{diff}\n")

    def start(self):
        self.create_widgets()
        # self.open_all_buttons()
        self.window.mainloop()


game = Minesweeper()
game.start()
