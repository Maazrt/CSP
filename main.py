import tkinter as tk
from tkinter import simpledialog, messagebox, font
import random
from algorithms import GameAnalyzer
from graph_visualizer import GraphVisualizer

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("بازی تیک‌تاک‌تو")
        self.root.configure(bg='#f0f0f0')  # رنگ پس‌زمینه اصلی
        
        # تنظیم فونت‌های پیش‌فرض
        self.title_font = font.Font(family="B Nazanin", size=16, weight="bold")
        self.button_font = font.Font(family="B Nazanin", size=12)
        self.cell_font = font.Font(family="Arial", size=20, weight="bold")
        
        self.size = None
        self.buttons = []
        self.board = []
        self.player_symbol = 'X'
        self.bot_symbol = 'O'
        self.analyzer = GameAnalyzer()
        self.graph_visualizer = GraphVisualizer()

        # رنگ‌های بازی
        self.colors = {
            'bg': '#f0f0f0',
            'button': '#4a90e2',
            'button_text': 'white',
            'button_hover': '#357abd',
            'cell': '#ffffff',
            'cell_hover': '#e8e8e8',
            'win': '#90EE90',
            'title': '#2c3e50'
        }

        self.create_buttons()
        self.start_new_game()

    def create_buttons(self):
        # عنوان بازی
        title_label = tk.Label(
            self.root,
            text="بازی تیک‌تاک‌تو",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['title'],
            pady=10
        )
        title_label.grid(row=99, column=0, columnspan=3)

        # دکمه شروع مجدد
        reset_btn = tk.Button(
            self.root,
            text="شروع دوباره",
            font=self.title_font,
            command=self.start_new_game,
            bg=self.colors['button'],
            fg=self.colors['button_text'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['button_text'],
            relief=tk.RAISED,
            borderwidth=2,
            padx=20,
            pady=10
        )
        reset_btn.grid(row=100, column=0, columnspan=3, pady=10)
        
        # دکمه‌های الگوریتم‌ها
        algorithms = [
            ("جستجوی پس‌گرد", self.show_backtracking),
            ("هیوریستیک درجه", self.show_degree_heuristic),
            ("بررسی رو به جلو", self.show_forward_checking),
            ("انتشار محدودیت", self.show_constraint_propagation),
            ("سازگاری قوس", self.show_arc_consistency),
            ("k-سازگاری", self.show_k_consistency),
            ("کمترین تعارض", self.show_min_conflicts)
        ]
        
        # محاسبه تعداد دکمه‌ها در هر ستون
        buttons_per_column = (len(algorithms) + 2) // 3
        
        # ایجاد دکمه‌ها در سه ستون
        for i, (text, command) in enumerate(algorithms):
            row = i % buttons_per_column
            col = i // buttons_per_column
            btn = tk.Button(
                self.root,
                text=text,
                font=self.button_font,
                command=command,
                bg=self.colors['button'],
                fg=self.colors['button_text'],
                activebackground=self.colors['button_hover'],
                activeforeground=self.colors['button_text'],
                relief=tk.RAISED,
                borderwidth=2,
                width=15,
                padx=10,
                pady=5
            )
            btn.grid(row=101 + row, column=col, padx=10, pady=5)

    def start_new_game(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] not in ['شروع دوباره'] + [text for text, _ in [
                ("جستجوی پس‌گرد", None),
                ("هیوریستیک درجه", None),
                ("بررسی رو به جلو", None),
                ("انتشار محدودیت", None),
                ("سازگاری قوس", None),
                ("k-سازگاری", None),
                ("کمترین تعارض", None)
            ]]:
                widget.destroy()

        self.size = simpledialog.askinteger("ابعاد بازی", "چند در چند بازی کنیم؟ (مثلاً 3 یا 4 یا 5...)")
        if not self.size or self.size < 2:
            messagebox.showerror("خطا", "ابعاد معتبر وارد نشده!")
            self.root.destroy()
            return

        self.buttons = []
        self.board = [['' for _ in range(self.size)] for _ in range(self.size)]

        # ایجاد فریم برای صفحه بازی
        game_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=20, pady=20)
        game_frame.grid(row=0, column=0, columnspan=3, pady=10)

        for row in range(self.size):
            button_row = []
            for col in range(self.size):
                btn = tk.Button(
                    game_frame,
                    text='',
                    font=self.cell_font,
                    width=4,
                    height=2,
                    bg=self.colors['cell'],
                    activebackground=self.colors['cell_hover'],
                    relief=tk.RAISED,
                    borderwidth=2,
                    command=lambda r=row, c=col: self.player_move(r, c)
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
                button_row.append(btn)
            self.buttons.append(button_row)

    def player_move(self, row, col):
        if self.board[row][col] == '':
            self.set_cell(row, col, self.player_symbol)
            if self.check_winner(self.player_symbol):
                self.highlight_winner(self.player_symbol)
                messagebox.showinfo("برد", "شما بردید!")
                return
            elif self.is_full():
                messagebox.showinfo("مساوی", "بازی مساوی شد.")
                return
            self.root.after(500, self.bot_move)

    def bot_move(self):
        row, col = self.find_best_move()
        if row is not None:
            self.set_cell(row, col, self.bot_symbol)
            if self.check_winner(self.bot_symbol):
                self.highlight_winner(self.bot_symbol)
                messagebox.showinfo("باخت", "ربات برنده شد!")
            elif self.is_full():
                messagebox.showinfo("مساوی", "بازی مساوی شد.")

    def set_cell(self, row, col, symbol):
        self.board[row][col] = symbol
        self.buttons[row][col]['text'] = symbol
        if symbol == self.player_symbol:
            self.buttons[row][col]['fg'] = '#e74c3c'  # رنگ قرمز برای X
        else:
            self.buttons[row][col]['fg'] = '#2ecc71'  # رنگ سبز برای O

    def is_full(self):
        return all(self.board[r][c] != '' for r in range(self.size) for c in range(self.size))

    def check_winner(self, symbol):
        for i in range(self.size):
            if all(self.board[i][j] == symbol for j in range(self.size)):
                return [(i, j) for j in range(self.size)]
            if all(self.board[j][i] == symbol for j in range(self.size)):
                return [(j, i) for j in range(self.size)]

        if all(self.board[i][i] == symbol for i in range(self.size)):
            return [(i, i) for i in range(self.size)]
        if all(self.board[i][self.size - 1 - i] == symbol for i in range(self.size)):
            return [(i, self.size - 1 - i) for i in range(self.size)]

        return None

    def highlight_winner(self, symbol):
        win_cells = self.check_winner(symbol)
        if win_cells:
            for r, c in win_cells:
                self.buttons[r][c].config(bg=self.colors['win'])

    def find_best_move(self):
        # اول سعی کنه خودش ببره
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == '':
                    self.board[r][c] = self.bot_symbol
                    if self.check_winner(self.bot_symbol):
                        self.board[r][c] = ''
                        return r, c
                    self.board[r][c] = ''

        # بعد سعی کنه جلوی برد بازیکن رو بگیره
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == '':
                    self.board[r][c] = self.player_symbol
                    if self.check_winner(self.player_symbol):
                        self.board[r][c] = ''
                        return r, c
                    self.board[r][c] = ''

        # در نهایت یه خونه خالی تصادفی انتخاب کنه
        empty = [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == '']
        return random.choice(empty) if empty else (None, None)

    def show_backtracking(self):
        """نمایش نتیجه الگوریتم جستجوی پس‌گرد"""
        move = self.analyzer.backtracking_search(self.board, self.size)
        if move:
            row, col = move
            messagebox.showinfo("جستجوی پس‌گرد", 
                              f"پیشنهاد می‌شود در خانه ({row+1}, {col+1}) قرار دهید.")
            self.graph_visualizer.update_and_show(self.board, self.size, self.root)
        else:
            messagebox.showinfo("جستجوی پس‌گرد", "هیچ حرکت مناسبی یافت نشد.")

    def show_degree_heuristic(self):
        """نمایش نتیجه الگوریتم هیوریستیک درجه"""
        move = self.analyzer.degree_heuristic(self.board, self.size)
        if move:
            row, col = move
            messagebox.showinfo("هیوریستیک درجه", 
                              f"پیشنهاد می‌شود در خانه ({row+1}, {col+1}) قرار دهید.")
            self.graph_visualizer.update_and_show(self.board, self.size, self.root)
        else:
            messagebox.showinfo("هیوریستیک درجه", "هیچ حرکت مناسبی یافت نشد.")

    def show_forward_checking(self):
        """نمایش نتیجه الگوریتم بررسی رو به جلو"""
        move = self.analyzer.forward_checking(self.board, self.size)
        if move:
            row, col = move
            messagebox.showinfo("بررسی رو به جلو", 
                              f"پیشنهاد می‌شود در خانه ({row+1}, {col+1}) قرار دهید.")
            self.graph_visualizer.update_and_show(self.board, self.size, self.root)
        else:
            messagebox.showinfo("بررسی رو به جلو", "هیچ حرکت مناسبی یافت نشد.")

    def show_constraint_propagation(self):
        """نمایش نتیجه الگوریتم انتشار محدودیت"""
        move = self.analyzer.constraint_propagation(self.board, self.size)
        if move:
            row, col = move
            messagebox.showinfo("انتشار محدودیت", 
                              f"پیشنهاد می‌شود در خانه ({row+1}, {col+1}) قرار دهید.")
            self.graph_visualizer.update_and_show(self.board, self.size, self.root)
        else:
            messagebox.showinfo("انتشار محدودیت", "هیچ حرکت مناسبی یافت نشد.")

    def show_arc_consistency(self):
        """نمایش نتیجه الگوریتم سازگاری قوس"""
        move = self.analyzer.arc_consistency(self.board, self.size)
        if move:
            row, col = move
            messagebox.showinfo("سازگاری قوس", 
                              f"پیشنهاد می‌شود در خانه ({row+1}, {col+1}) قرار دهید.")
            self.graph_visualizer.update_and_show(self.board, self.size, self.root)
        else:
            messagebox.showinfo("سازگاری قوس", "هیچ حرکت مناسبی یافت نشد.")

    def show_k_consistency(self):
        """نمایش نتیجه الگوریتم k-سازگاری"""
        move = self.analyzer.k_consistency(self.board, self.size)
        if move:
            row, col = move
            messagebox.showinfo("k-سازگاری", 
                              f"پیشنهاد می‌شود در خانه ({row+1}, {col+1}) قرار دهید.")
            self.graph_visualizer.update_and_show(self.board, self.size, self.root)
        else:
            messagebox.showinfo("k-سازگاری", "هیچ حرکت مناسبی یافت نشد.")

    def show_min_conflicts(self):
        """نمایش نتیجه الگوریتم کمترین تعارض"""
        move = self.analyzer.min_conflicts(self.board, self.size)
        if move:
            row, col = move
            messagebox.showinfo("کمترین تعارض", 
                              f"پیشنهاد می‌شود در خانه ({row+1}, {col+1}) قرار دهید.")
            self.graph_visualizer.update_and_show(self.board, self.size, self.root)
        else:
            messagebox.showinfo("کمترین تعارض", "هیچ حرکت مناسبی یافت نشد.")


# اجرای برنامه
if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
