import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from typing import List, Dict, Set, Tuple, Optional
import random

class GameAnalyzer:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.constraints = {}  # محدودیت‌های بازی
        self.domains = {}      # دامنه‌های ممکن برای هر خانه
        
    def initialize_csp(self, board: List[List[str]], size: int):
        """مقداردهی اولیه CSP برای بازی"""
        self.constraints = {}
        self.domains = {}
        
        # تعریف دامنه‌ها برای هر خانه
        for i in range(size):
            for j in range(size):
                if board[i][j] == '':
                    self.domains[(i, j)] = {'X', 'O'}
                else:
                    self.domains[(i, j)] = {board[i][j]}
        
        # تعریف محدودیت‌ها
        # محدودیت ردیف‌ها
        for i in range(size):
            row = [(i, j) for j in range(size)]
            self.constraints[f'row_{i}'] = row
            
        # محدودیت ستون‌ها
        for j in range(size):
            col = [(i, j) for i in range(size)]
            self.constraints[f'col_{j}'] = col
            
        # محدودیت قطر اصلی
        diag1 = [(i, i) for i in range(size)]
        self.constraints['diag1'] = diag1
        
        # محدودیت قطر فرعی
        diag2 = [(i, size-1-i) for i in range(size)]
        self.constraints['diag2'] = diag2

    def backtracking_search(self, board: List[List[str]], size: int) -> Optional[Tuple[int, int]]:
        """الگوریتم جستجوی پس‌گرد"""
        self.initialize_csp(board, size)
        assignment = {}
        
        def backtrack(assignment: Dict) -> Optional[Dict]:
            if len(assignment) == sum(1 for i in range(size) for j in range(size) if board[i][j] == ''):
                return assignment
                
            var = self.select_unassigned_variable(board, size, assignment)
            if var is None:
                return None
                
            for value in self.order_domain_values(var):
                if self.is_consistent(var, value, assignment):
                    assignment[var] = value
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                    del assignment[var]
            return None
            
        result = backtrack(assignment)
        if result:
            # برگرداندن اولین خانه خالی که مقداردهی شده
            for i in range(size):
                for j in range(size):
                    if board[i][j] == '' and (i, j) in result:
                        return (i, j)
        return None

    def degree_heuristic(self, board: List[List[str]], size: int) -> Optional[Tuple[int, int]]:
        """الگوریتم هیوریستیک درجه"""
        self.initialize_csp(board, size)
        
        # محاسبه درجه هر متغیر (تعداد محدودیت‌های مرتبط)
        degrees = {}
        for i in range(size):
            for j in range(size):
                if board[i][j] == '':
                    degree = 0
                    # بررسی محدودیت‌های مرتبط
                    for constraint in self.constraints.values():
                        if (i, j) in constraint:
                            degree += len([x for x in constraint if board[x[0]][x[1]] == ''])
                    degrees[(i, j)] = degree
        
        # انتخاب متغیر با بیشترین درجه
        if degrees:
            return max(degrees.items(), key=lambda x: x[1])[0]
        return None

    def forward_checking(self, board: List[List[str]], size: int) -> Optional[Tuple[int, int]]:
        """الگوریتم بررسی رو به جلو"""
        self.initialize_csp(board, size)
        assignment = {}
        
        def forward_check(var: Tuple[int, int], value: str) -> bool:
            # به‌روزرسانی دامنه‌های متغیرهای مرتبط
            for constraint in self.constraints.values():
                if var in constraint:
                    for neighbor in constraint:
                        if neighbor != var and board[neighbor[0]][neighbor[1]] == '':
                            if value in self.domains[neighbor]:
                                self.domains[neighbor].remove(value)
                                if not self.domains[neighbor]:
                                    return False
            return True
            
        def backtrack(assignment: Dict) -> Optional[Dict]:
            if len(assignment) == sum(1 for i in range(size) for j in range(size) if board[i][j] == ''):
                return assignment
                
            var = self.select_unassigned_variable(board, size, assignment)
            if var is None:
                return None
                
            for value in self.order_domain_values(var):
                if self.is_consistent(var, value, assignment):
                    assignment[var] = value
                    domains_copy = {k: v.copy() for k, v in self.domains.items()}
                    
                    if forward_check(var, value):
                        result = backtrack(assignment)
                        if result is not None:
                            return result
                            
                    self.domains = domains_copy
                    del assignment[var]
            return None
            
        result = backtrack(assignment)
        if result:
            for i in range(size):
                for j in range(size):
                    if board[i][j] == '' and (i, j) in result:
                        return (i, j)
        return None

    def constraint_propagation(self, board: List[List[str]], size: int) -> Optional[Tuple[int, int]]:
        """الگوریتم انتشار محدودیت"""
        self.initialize_csp(board, size)
        
        def propagate_constraints():
            changed = True
            while changed:
                changed = False
                for constraint in self.constraints.values():
                    # بررسی محدودیت‌های ردیف، ستون و قطر
                    values = [board[i][j] for i, j in constraint if board[i][j] != '']
                    if len(set(values)) == 1 and values[0] != '':
                        # اگر همه مقادیر یکسان هستند، خانه‌های خالی را محدود کن
                        for i, j in constraint:
                            if board[i][j] == '':
                                if values[0] in self.domains[(i, j)]:
                                    self.domains[(i, j)].remove(values[0])
                                    changed = True
                                    
        propagate_constraints()
        
        # انتخاب خانه با کمترین دامنه
        min_domain = float('inf')
        selected_move = None
        for i in range(size):
            for j in range(size):
                if board[i][j] == '' and len(self.domains[(i, j)]) < min_domain:
                    min_domain = len(self.domains[(i, j)])
                    selected_move = (i, j)
                    
        return selected_move

    def arc_consistency(self, board: List[List[str]], size: int) -> Optional[Tuple[int, int]]:
        """الگوریتم سازگاری قوس"""
        self.initialize_csp(board, size)
        
        def revise(x: Tuple[int, int], y: Tuple[int, int]) -> bool:
            revised = False
            for value_x in list(self.domains[x]):
                has_support = False
                for value_y in self.domains[y]:
                    if value_x != value_y:
                        has_support = True
                        break
                if not has_support:
                    self.domains[x].remove(value_x)
                    revised = True
            return revised
            
        queue = []
        # اضافه کردن تمام قوس‌ها به صف
        for constraint in self.constraints.values():
            for i in range(len(constraint)):
                for j in range(i+1, len(constraint)):
                    if board[constraint[i][0]][constraint[i][1]] == '' and \
                       board[constraint[j][0]][constraint[j][1]] == '':
                        queue.append((constraint[i], constraint[j]))
                        queue.append((constraint[j], constraint[i]))
        
        while queue:
            x, y = queue.pop(0)
            if revise(x, y):
                if not self.domains[x]:
                    return None
                for constraint in self.constraints.values():
                    if x in constraint:
                        for z in constraint:
                            if z != x and z != y and board[z[0]][z[1]] == '':
                                queue.append((z, x))
        
        # انتخاب خانه با کمترین دامنه
        min_domain = float('inf')
        selected_move = None
        for i in range(size):
            for j in range(size):
                if board[i][j] == '' and len(self.domains[(i, j)]) < min_domain:
                    min_domain = len(self.domains[(i, j)])
                    selected_move = (i, j)
                    
        return selected_move

    def k_consistency(self, board: List[List[str]], size: int, k: int = 2) -> Optional[Tuple[int, int]]:
        """الگوریتم k-سازگاری"""
        self.initialize_csp(board, size)
        
        def check_k_consistency(variables: List[Tuple[int, int]], k: int) -> bool:
            if len(variables) < k:
                return True
                
            from itertools import combinations
            for subset in combinations(variables, k):
                if not self._is_subset_consistent(list(subset)):
                    return False
            return True
            
        def _is_subset_consistent(subset: List[Tuple[int, int]]) -> bool:
            # بررسی اینکه آیا این زیرمجموعه در یک محدودیت قرار دارد
            for constraint in self.constraints.values():
                if all(var in constraint for var in subset):
                    # بررسی مقادیر فعلی
                    values = [board[i][j] for i, j in subset if board[i][j] != '']
                    if len(values) > 1 and len(set(values)) == 1:
                        return False
            return True
            
        # بررسی k-سازگاری برای تمام زیرمجموعه‌های k تایی
        variables = [(i, j) for i in range(size) for j in range(size) if board[i][j] == '']
        
        # اگر هیچ خانه خالی وجود ندارد، برگردان None
        if not variables:
            return None
            
        # بررسی k-سازگاری
        if not check_k_consistency(variables, k):
            return None
            
        # انتخاب خانه با کمترین دامنه
        min_domain = float('inf')
        selected_move = None
        for i in range(size):
            for j in range(size):
                if board[i][j] == '' and len(self.domains[(i, j)]) < min_domain:
                    min_domain = len(self.domains[(i, j)])
                    selected_move = (i, j)
                    
        return selected_move

    def min_conflicts(self, board: List[List[str]], size: int, max_steps: int = 100) -> Optional[Tuple[int, int]]:
        """الگوریتم کمترین تعارض"""
        self.initialize_csp(board, size)
        
        def count_conflicts(var: Tuple[int, int], value: str) -> int:
            conflicts = 0
            for constraint in self.constraints.values():
                if var in constraint:
                    for neighbor in constraint:
                        if neighbor != var and board[neighbor[0]][neighbor[1]] == value:
                            conflicts += 1
            return conflicts
            
        # مقداردهی اولیه تصادفی
        assignment = {}
        for i in range(size):
            for j in range(size):
                if board[i][j] == '':
                    assignment[(i, j)] = random.choice(list(self.domains[(i, j)]))
        
        for _ in range(max_steps):
            # بررسی تعارض‌ها
            conflicted_vars = []
            for var in assignment:
                if count_conflicts(var, assignment[var]) > 0:
                    conflicted_vars.append(var)
            
            if not conflicted_vars:
                # پیدا کردن اولین خانه خالی که مقداردهی شده
                for i in range(size):
                    for j in range(size):
                        if board[i][j] == '' and (i, j) in assignment:
                            return (i, j)
                return None
                
            # انتخاب یک متغیر تعارض‌دار
            var = random.choice(conflicted_vars)
            
            # انتخاب مقدار با کمترین تعارض
            min_conflicts = float('inf')
            best_value = None
            for value in self.domains[var]:
                conflicts = count_conflicts(var, value)
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_value = value
                    
            assignment[var] = best_value
            
        return None

    def select_unassigned_variable(self, board: List[List[str]], size: int, assignment: Dict) -> Optional[Tuple[int, int]]:
        """انتخاب متغیر تخصیص نیافته"""
        for i in range(size):
            for j in range(size):
                if board[i][j] == '' and (i, j) not in assignment:
                    return (i, j)
        return None

    def order_domain_values(self, var: Tuple[int, int]) -> List[str]:
        """مرتب‌سازی مقادیر دامنه"""
        return list(self.domains[var])

    def is_consistent(self, var: Tuple[int, int], value: str, assignment: Dict) -> bool:
        """بررسی سازگاری مقدار با تخصیص فعلی"""
        for constraint in self.constraints.values():
            if var in constraint:
                for neighbor in constraint:
                    if neighbor in assignment and assignment[neighbor] == value:
                        return False
        return True

    def create_game_tree(self, board, current_player, depth=3):
        """ایجاد درخت بازی تا عمق مشخص شده"""
        self.graph.clear()
        self._build_tree(board, current_player, depth)
        return self.graph
    
    def _build_tree(self, board, current_player, depth, parent_node=None):
        """ساخت درخت بازی به صورت بازگشتی"""
        if depth == 0:
            return
            
        board_state = str(board)
        if parent_node is not None:
            self.graph.add_edge(parent_node, board_state)
            
        # بررسی تمام حرکات ممکن
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == '':
                    # ایجاد یک کپی از صفحه و انجام حرکت
                    new_board = [row[:] for row in board]
                    new_board[i][j] = current_player
                    
                    # محاسبه امتیاز این حالت
                    score = self._evaluate_position(new_board, current_player)
                    
                    # اضافه کردن به گراف
                    self.graph.add_node(str(new_board), 
                                     score=score,
                                     move=(i, j))
                    
                    # ادامه ساخت درخت با عمق کمتر
                    next_player = 'O' if current_player == 'X' else 'X'
                    self._build_tree(new_board, next_player, depth-1, str(new_board))
    
    def _evaluate_position(self, board, player):
        """ارزیابی وضعیت فعلی بازی"""
        size = len(board)
        score = 0
        
        # بررسی ردیف‌ها و ستون‌ها
        for i in range(size):
            row_score = self._evaluate_line([board[i][j] for j in range(size)], player)
            col_score = self._evaluate_line([board[j][i] for j in range(size)], player)
            score += row_score + col_score
            
        # بررسی قطر اصلی
        diag1 = [board[i][i] for i in range(size)]
        score += self._evaluate_line(diag1, player)
        
        # بررسی قطر فرعی
        diag2 = [board[i][size-1-i] for i in range(size)]
        score += self._evaluate_line(diag2, player)
        
        return score
    
    def _evaluate_line(self, line, player):
        """ارزیابی یک خط (ردیف، ستون یا قطر)"""
        opponent = 'O' if player == 'X' else 'X'
        score = 0
        
        # شمارش تعداد مهره‌های بازیکن و حریف
        player_count = line.count(player)
        opponent_count = line.count(opponent)
        empty_count = line.count('')
        
        # محاسبه امتیاز
        if player_count == len(line):
            score += 100  # برد
        elif opponent_count == len(line):
            score -= 100  # باخت
        elif player_count == len(line) - 1 and empty_count == 1:
            score += 10   # یک حرکت تا برد
        elif opponent_count == len(line) - 1 and empty_count == 1:
            score -= 10   # یک حرکت تا باخت
            
        return score
    
    def suggest_move(self, board, player):
        """پیشنهاد بهترین حرکت با استفاده از درخت بازی"""
        self.create_game_tree(board, player)
        
        # یافتن بهترین حرکت با استفاده از الگوریتم مینیمکس
        best_score = float('-inf')
        best_move = None
        
        for node in self.graph.nodes():
            if self.graph.in_degree(node) == 0:  # گره‌های ریشه
                score = self._minimax(node, True)
                if score > best_score:
                    best_score = score
                    best_move = self.graph.nodes[node].get('move')
        
        return best_move
    
    def _minimax(self, node, is_maximizing):
        """الگوریتم مینیمکس برای پیدا کردن بهترین حرکت"""
        if self.graph.out_degree(node) == 0:  # گره برگ
            return self.graph.nodes[node].get('score', 0)
            
        if is_maximizing:
            best_score = float('-inf')
            for child in self.graph.successors(node):
                score = self._minimax(child, False)
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for child in self.graph.successors(node):
                score = self._minimax(child, True)
                best_score = min(score, best_score)
            return best_score
    
    def visualize_tree(self):
        """نمایش گراف درخت بازی"""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)
        
        # رسم گره‌ها
        nx.draw_networkx_nodes(self.graph, pos, 
                             node_color='lightblue',
                             node_size=500)
        
        # رسم یال‌ها
        nx.draw_networkx_edges(self.graph, pos, 
                             edge_color='gray',
                             arrows=True)
        
        # اضافه کردن برچسب‌ها
        labels = {node: f"Score: {self.graph.nodes[node].get('score', 0)}" 
                 for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels)
        
        plt.title("درخت بازی")
        plt.axis('off')
        plt.show() 