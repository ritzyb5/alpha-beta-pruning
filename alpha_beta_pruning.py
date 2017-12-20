import sys
import copy

class Node:
    def __init__(self, state_name, color, parent):
        self.state_name = state_name
        self.color = color
        self.depth = 0
        self.parent = parent
        if parent:
            self.depth = parent.depth + 1
            if parent.player=='1':
                self.player = '2'
            else:
                self.player='1'
            self.board = copy.deepcopy(parent.board)
            self.domain = copy.deepcopy(parent.domain)
        else:
            self.board={}
            self.domain={}
        self.alpha=float('-inf')
        self.beta=float('inf')

    def __repr__(self):
        return '(%s, %s, %d)' % (self.state_name,self.color,self.depth)
        
    
#-------------------------------------------------------------------------------   
lines=[]
initial_move={}   
colored_states={}


#Read Input File
with open(sys.argv[2]) as f:
    lines.extend(f.read().splitlines()) 
f.close()

#colors
colors = map(str.strip,lines[0].strip().split(','))

#initial move
splits = lines[1].split(',')
for item in splits:
    sub_items = item.strip().split(':')
    state = sub_items[0]
    splits2 = sub_items[1].strip().split('-')
    initial_move[splits2[1]]={}
    initial_move[splits2[1]][state]=splits2[0]
    colored_states[state]=splits2[0]
last_move = state 


#search depth
depth = int(lines[2].strip())

#color preference
color_weights = {}
player = 1

for line in lines[3:5]:
    color_weights[player]={}
    splits = line.strip().split(',')
    for item in splits:
        sub_items = item.strip().split(':')
        color_weights[player][sub_items[0]]=sub_items[1]
    player+=1

#map
map_graph={}
for line in lines[5:]:
    splits = line.strip().split(':')
    map_graph[splits[0]]=[]
    splits2 = splits[1].strip().split(',')
    for item in splits2:
        map_graph[splits[0]].append(item.strip())
    map_graph[splits[0]].sort()

#------------------------------------------------------------------------------
#calculate initial move scores
p1_score=0
p2_score=0
for color in initial_move['1'].values():
    p1_score += int(color_weights[1][color])

for color in initial_move['2'].values():
    p2_score += int(color_weights[2][color])
#------------------------------------------------------------------------------

#Create a node for last move
root_node = Node(last_move,initial_move['2'][last_move],None)
root_node.player='2'
root_node.board = copy.deepcopy(colored_states)

#Apply arc consistency on neighbouring states
domain={}
for state in map_graph.keys():
    domain_list=list(colors)
    domain_list.sort()
    domain[state]=list(domain_list)
    
for key in initial_move.keys():
    for state in initial_move[key].keys():
        domain[state]=[]
        domain[state].append(initial_move[key][state])
        
for state in colored_states.keys():
    for neighbour in map_graph[state]:
        if colored_states[state] in domain[neighbour]:
            domain[neighbour].remove(colored_states[state])

root_node.domain = copy.deepcopy(domain)

fo= open("output.txt", "wb")
#-------------------------------------------------------------------------------

def successor(parent):
    successor_list=[]
    explored=[]
    
    temp_board = copy.deepcopy(parent.board)
    colored_states = temp_board.keys()
    colored_states.sort()
    
    for state in colored_states:
        for neighbour in map_graph[state]:
            if (neighbour not in parent.board) and (neighbour not in explored):
                for color in parent.domain[neighbour]:
                    node = Node(neighbour,color,parent)
                    node.board[neighbour]=color
                    for n in map_graph[neighbour]:
                        if n not in node.board and (color in node.domain[n]):
                            node.domain[n].remove(node.board[neighbour])
                            node.domain[n].sort()
                           
                    explored.append(neighbour)
                    successor_list.append(node)
    res = sorted(successor_list, key=lambda x: (x.state_name,x.color))
    return res

def cutoff_test(node):
    if node.depth>=depth:
        return True
    elif cmp(node.board.keys(),map_graph.keys())==0:
        return True
    else:
        successors = successor(node)
        if not successors:
            return True
    return False

def eval_fn(node):
    p1=p1_score
    p2=p2_score
    parent_node = node

    while parent_node is not root_node:
        if parent_node.player=='1':
            p1 += int(color_weights[1][parent_node.color])
        else:
            p2 += int(color_weights[2][parent_node.color])
        parent_node=parent_node.parent
    return p1-p2
        


#-------------------------------------------------------------------------------

def alpha_beta_search(node):
    alpha = float("-inf")
    beta = float("inf")
    minimax = float("-inf")
    
    #not sure about this
    global best_move
    if node is root_node:
        children = successor(node)
        best_move=children[0]
    
    value= max_value(node,alpha,beta)
    if value>minimax:
        minimax = value
    print_node(node, minimax, node.alpha, node.beta)
    fo.write(str(best_move.state_name)+', '+str(best_move.color)+', '+str(minimax))
    
    return minimax

def max_value(node,alpha,beta):
    global best_move
    
    if cutoff_test(node):
        node.alpha=alpha
        return eval_fn(node)
        
    value = float('-inf')
    
    for child in successor(node):
        print_node(node,value,alpha,beta)
        
        child_val = min_value(child,alpha,beta)
        value = max(value,child_val)
        print_node(child,child_val,alpha,child.beta)
        
        if value >= beta:
            node.alpha=alpha
            return value
            
        if value > alpha:
            alpha = value
            if node is root_node:
                best_move = child
        node.alpha = alpha
            
    return value
    
def min_value(node,alpha,beta):
    global best_move
    
    if cutoff_test(node):
        node.beta=beta
        return eval_fn(node)
    
    value = float('inf')
    
    for child in successor(node):
        print_node(node,value,alpha,beta)
        
        child_val = max_value(child,alpha,beta)
        value=min(child_val,value)
        
        print_node(child,child_val,child.alpha,beta)
        
        if value <= alpha:
            node.beta = beta
            return value
    
        if value < beta:
            beta = value
            if node is root_node:
                best_move = child
        node.beta = beta
    return value

def print_node(node,minimax,alpha,beta):
    fo.write(node.state_name+', '+node.color+', '+str(node.depth)+', '+str(minimax)+', '+str(alpha)+', '+str(beta)+'\n')
    
val = alpha_beta_search(root_node)
fo.close()
