import numpy as np
import itertools
import random
class Board():
    def __init__(self, grid_w, grid_h):
        self.grid = np.array([[0 for i in range(grid_w)] for j in range(grid_h)])
        self.grid_dim = (grid_h, grid_w)
        self.direction = {'l':(-1,0),'r':(1,0),'u':(0,1),'d':(0,-1)}
        self.alpha = 'ABCDEFGHIJKMNOPQRSTUVWXYZ'
    
    def get_value(self, point):
        x, y = point
        if x<0 or x>=self.grid_dim[0] or y<0 or y>=self.grid_dim[1]:
            return None
        else:
            return self.grid[point]
    
    def point_away(self, point, direction, step = 1):
        x, y = point
        x_d, y_d = self.direction[direction]
        x, y = x+x_d*step, y+y_d*step
        return (x,y)
    
    def point_to_str(self, point):
        return str(point[0]) + self.alpha[point[1]]
    
    def str_to_point(self, str_):
        list_ = [''.join(j) for i,j in itertools.groupby(str_, str.isalpha)]
        list_dig = [int(i) for i in list_[::2]]
        list_str = [self.alpha.index(i) for i in list_[1::2]]
        return list(zip(list_dig, list_str))


class BS():
    def __init__(self, Board, grid_w, grid_h, ships):
        self.s = ships
        self.b = Board(grid_w, grid_h)
    
    def put_(self,):
        def check_(point, grid):
            return self.b.get_value(point) == 0
        
        for s in self.s:
            placed = False
            while not placed:
                #assume fit
                init_point = (random.choice(range(self.b.grid_dim[0])), random.choice(range(self.b.grid_dim[1])))
                dir_ = random.choice(list(self.b.direction.keys()))
                if not placed and all(self.b.get_value(self.b.point_away(init_point, dir_, step))==0 for step in range(s)): 
                    for temp_p in [self.b.point_away(init_point, dir_, step) for step in range(s)]:
                        self.b.grid[temp_p] = 1
                    placed = True
                    
    def print_(self):
        res = ''
        for i in range(self.b.grid_dim[0]):
            for j in range(self.b.grid_dim[1]):
                if self.b.grid[(i,j)] == 1:
                    res += self.b.point_to_str((i,j))
        return res
            

class P():
    def __init__(self, BS, Board, grid_w, grid_h, ships, BS1, BS2):
        self.a = BS(Board, grid_w, grid_h, ships)
        self.b = BS(Board, grid_w, grid_h, ships)
        self.bs1 = BS1(Board, grid_w, grid_h, ships)
        self.bs2 = BS2(Board, grid_w, grid_h, ships)
        self.a.put_()
        self.b.put_()
        
    def start(self, pla, board):
        hit_p = pla.hit()
        assert board.b.get_value(hit_p) in [0,1,-1,2,-2]
        if board.b.get_value(hit_p)==1 or board.b.get_value(hit_p)==-1:
            board.b.grid[hit_p] = -1
            pla.callback(hit_p, True)
        else:
            board.b.grid[hit_p] = -2
            pla.callback(hit_p, False)
    def ini_g(self):
        while True:
            self.start(self.bs1, self.b)
            self.start(self.bs2, self.a)
#             print('#a')
#             print(self.b.b.grid)
#             print('#b')
#             print(self.a.b.grid)
            if not any(self.b.b.grid.ravel() == 1):
#                 print('a w')
                return 1
            if not any(self.a.b.grid.ravel() == 1):
#                 print('b w')
                return 0

class BS_a0():
#strategy 1: randomly choose point
    def __init__(self, Board, grid_w, grid_h, ships):
        self.s = ships
        self.pb = Board(grid_w, grid_h)
        
    def hit(self, ):
        while True:
            point = (random.choice(range(self.pb.grid_dim[0])), random.choice(range(self.pb.grid_dim[1])))            
            return point
        
    def callback(self, point, TF):
        if TF:
            self.pb.grid[point] = 1
        else:
            self.pb.grid[point] = -1
            
class BS_a1():
#strategy 2: randomly choose point, avoid picked ones
    def __init__(self, Board, grid_w, grid_h, ships):
        self.s = ships
        self.pb = Board(grid_w, grid_h)
        
    def hit(self, ):
        while True:
            point = (random.choice(range(self.pb.grid_dim[0])), random.choice(range(self.pb.grid_dim[1])))
            if self.pb.get_value(point) != 1 and self.pb.get_value(point) != -1:
                return point
        
    def callback(self, point, TF):
        if TF:
            self.pb.grid[point] = 1
        else:
            self.pb.grid[point] = -1

class BS_a2():
#strategy 3: simulate possible layouts, choose the most possible one
    def __init__(self, Board, grid_w, grid_h, ships):
        self.s = ships
        self.b_list = [Board(grid_w, grid_h) for _ in range(1000)]
        self.pb = Board(grid_w, grid_h)
        self.put_()

    def put_(self,):
        def check_(point, grid, simulation_board):
            return simulation_board.get_value(point) == 0 and self.pb.get_value(point) != -1
        def check_board(simulation_board):
            return not any((np.ravel(self.pb)==1) & (np.ravel(simulation_board)==0))
        
        for idx, simulation_board in enumerate(self.b_list):
            while True:
                for s in self.s:
                    placed = False
                    while not placed:
                        init_point = (random.choice(range(simulation_board.grid_dim[0])), random.choice(range(simulation_board.grid_dim[1])))
                        dir_ = random.choice(list(simulation_board.direction.keys()))
                        if not placed and all(simulation_board.get_value(simulation_board.point_away(init_point, dir_, step))==0 for step in range(s)): 
                            for temp_p in [simulation_board.point_away(init_point, dir_, step) for step in range(s)]:
                                simulation_board.grid[temp_p] = 1
                            placed = True
                if check_board(simulation_board):
                    break
                else:
                    self.b_list[idx] = Board(grid_w, grid_h)
    
    def hit(self):
        sim_sum_board = sum([i.grid for i in self.b_list])
        sim_sum_board = sim_sum_board - np.dot(abs(self.pb.grid), 100000)
        return np.unravel_index(np.argmax(sim_sum_board), sim_sum_board.shape)
        
    def callback(self, point, TF):
        if TF:
            self.pb.grid[point] = 1
        else:
            self.pb.grid[point] = -1
        def check_(point, grid, simulation_board):
            return simulation_board.get_value(point) == 0 and self.pb.get_value(point) != -1
        def check_board(simulation_board):
            return ((not any((np.ravel(self.pb)==1) & (np.ravel(simulation_board)==0))) and 
                     not any((np.ravel(self.pb)==-1) & (np.ravel(simulation_board)!=0)))
        
        for idx, simulation_board in enumerate(self.b_list):
            if check_board(simulation_board):
                continue
            self.b_list[idx] = Board(grid_w, grid_h)
            while True:
                for s in self.s:
                    placed = False
                    while not placed:
                        init_point = (random.choice(range(simulation_board.grid_dim[0])), random.choice(range(simulation_board.grid_dim[1])))
                        dir_ = random.choice(list(simulation_board.direction.keys()))
                        if not placed and all(simulation_board.get_value(simulation_board.point_away(init_point, dir_, step))==0 for step in range(s)): 
                            for temp_p in [simulation_board.point_away(init_point, dir_, step) for step in range(s)]:
                                simulation_board.grid[temp_p] = 1
                            placed = True
                if check_board(simulation_board):
                    break
                else:
                    self.b_list[idx] = Board(grid_w, grid_h)

class BS_a3():
#strategy 4: simulate possible layouts, choose the most possible one. Include tracking mode, if stack contains elements, first check stack
    def __init__(self, Board, grid_w, grid_h, ships):
        self.s = ships
        self.b_list = [Board(grid_w, grid_h) for _ in range(10)]
        self.pb = Board(grid_w, grid_h)
        self.put_()
        self.stack = []
        self.dir = ''
        self.visited = set()

    def put_(self,):
        def check_(point, grid, simulation_board):
            return simulation_board.get_value(point) == 0 and self.pb.get_value(point) != -1
        def check_board(simulation_board):
            return not any((np.ravel(self.pb)==1) & (np.ravel(simulation_board)==0))
        
        for idx, simulation_board in enumerate(self.b_list):
            while True:
                for s in self.s:
                    placed = False
                    while not placed:
                        init_point = (random.choice(range(simulation_board.grid_dim[0])), random.choice(range(simulation_board.grid_dim[1])))
                        dir_ = random.choice(list(simulation_board.direction.keys()))
                        if not placed and all(simulation_board.get_value(simulation_board.point_away(init_point, dir_, step))==0 for step in range(s)): 
                            for temp_p in [simulation_board.point_away(init_point, dir_, step) for step in range(s)]:
                                simulation_board.grid[temp_p] = 1
                            placed = True
                if check_board(simulation_board):
                    break
                else:
                    self.b_list[idx] = Board(grid_w, grid_h)
    
    def hit(self):
        if len(self.stack) == 0:
            sim_sum_board = sum([i.grid for i in self.b_list])
            sim_sum_board = sim_sum_board - np.dot(abs(self.pb.grid), 100000)
            point =  np.unravel_index(np.argmax(sim_sum_board), sim_sum_board.shape)
            self.visited.add(point)
            return point
        else:
            point, self.dir = self.stack.pop(0)
            self.visited.add(point)
            return point
            
        
    def callback(self, point, TF):
        if TF:
            self.pb.grid[point] = 1
            if len(self.stack)==0:
                for k in range(1, max(self.pb.grid_dim)):
                    self.stack.append((self.pb.point_away(point, 'l', k), 'l'))
                for k in range(1, max(self.pb.grid_dim)):
                    self.stack.append((self.pb.point_away(point, 'r', k), 'r'))
                for k in range(1, max(self.pb.grid_dim)):
                    self.stack.append((self.pb.point_away(point, 'u', k), 'u'))
                for k in range(1, max(self.pb.grid_dim)):
                    self.stack.append((self.pb.point_away(point, 'd', k), 'd'))
                self.stack = [(i,j) for i,j in self.stack if self.pb.get_value(i) is not None and i not in self.visited]
            else:
                if self.dir in ['l','r']:
                    self.stack = [(i,j) for i,j in self.stack if j not in ['u','d']]
                if self.dir in ['u','d']:
                    self.stack = [(i,j) for i,j in self.stack if j not in ['l','r']]
        else:
            self.pb.grid[point] = -1
            if len(self.stack)!=0:
                self.stack = [(i,j) for i,j in self.stack if j!=self.dir]
        def check_(point, grid, simulation_board):
            return simulation_board.get_value(point) == 0 and self.pb.get_value(point) != -1
        def check_board(simulation_board):
            return ((not any((np.ravel(self.pb)==1) & (np.ravel(simulation_board)==0))) and 
                     not any((np.ravel(self.pb)==-1) & (np.ravel(simulation_board)!=0)))
        if len(self.stack) == 0:
            for idx, simulation_board in enumerate(self.b_list):
                if check_board(simulation_board):
                    continue
                self.b_list[idx] = Board(grid_w, grid_h)
                while True:
                    for s in self.s:
                        placed = False
                        while not placed:
                            init_point = (random.choice(range(simulation_board.grid_dim[0])), random.choice(range(simulation_board.grid_dim[1])))
                            dir_ = random.choice(list(simulation_board.direction.keys()))
                            if not placed and all(simulation_board.get_value(simulation_board.point_away(init_point, dir_, step))==0 for step in range(s)): 
                                for temp_p in [simulation_board.point_away(init_point, dir_, step) for step in range(s)]:
                                    simulation_board.grid[temp_p] = 1
                                placed = True
                    if check_board(simulation_board):
                        break
                    else:
                        self.b_list[idx] = Board(grid_w, grid_h)                    
                    
res = 0                    
for i in range(100):
    p = P(BS, Board, 10, 10, [4,4,4,3,2],BS_a3, BS_a2)
    res+= p.ini_g()
print(res)
