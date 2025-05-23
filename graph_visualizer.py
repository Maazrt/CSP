import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class GraphVisualizer:
    def __init__(self):
        self.G = nx.Graph()
        self.fig = None
        self.canvas = None

    def create_csp_graph(self, board, size):
        """ایجاد گراف CSP بر اساس وضعیت فعلی بازی"""
        self.G.clear()
        
        # اضافه کردن گره‌ها (خانه‌های خالی)
        empty_cells = []
        for i in range(size):
            for j in range(size):
                if board[i][j] == '':
                    node = f"({i+1},{j+1})"
                    empty_cells.append((i, j))
                    self.G.add_node(node, pos=(j, -i))  # معکوس کردن i برای نمایش صحیح

        # اضافه کردن یال‌ها (محدودیت‌ها)
        for i, (r1, c1) in enumerate(empty_cells):
            for j, (r2, c2) in enumerate(empty_cells[i+1:], i+1):
                # اگر دو خانه در یک سطر، ستون یا قطر باشند
                if (r1 == r2 or c1 == c2 or abs(r1-r2) == abs(c1-c2)):
                    self.G.add_edge(f"({r1+1},{c1+1})", f"({r2+1},{c2+1})")

    def show_graph(self, parent):
        """نمایش گراف در پنجره جدید"""
        # ایجاد پنجره جدید
        graph_window = tk.Toplevel(parent)
        graph_window.title("گراف CSP")
        graph_window.geometry("600x600")

        # ایجاد نمودار
        self.fig = plt.figure(figsize=(8, 8))
        pos = nx.get_node_attributes(self.G, 'pos')
        
        # رسم گراف
        nx.draw(self.G, pos,
                with_labels=True,
                node_color='lightblue',
                node_size=1000,
                font_size=10,
                font_weight='bold',
                edge_color='gray',
                width=2,
                arrows=True)

        # اضافه کردن نمودار به پنجره
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # اضافه کردن توضیحات
        description = tk.Label(graph_window,
                             text="گراف CSP: هر گره نشان‌دهنده یک خانه خالی است.\n"
                                  "یال‌ها نشان‌دهنده محدودیت‌های بین خانه‌ها هستند.",
                             font=("B Nazanin", 10),
                             pady=10)
        description.pack()

    def update_and_show(self, board, size, parent):
        """به‌روزرسانی و نمایش گراف"""
        self.create_csp_graph(board, size)
        self.show_graph(parent) 