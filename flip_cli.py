import numpy as np

# # for plotting solution steps with matshow and custom cmap
# import matplotlib.pyplot as plt
# from matplotlib.colors import LinearSegmentedColormap

colors = {0:"🔳",1:"🔲",2:"🟦",3:"🟨",4:"🟩",5:"🟧",6:"🟪",7:"🟫",8:"🟥"}

# colors_map = [
#     (0.1725, 0.6275, 0.9725),  # Bright sky blue
#     (1.0000, 0.8431, 0.0000),  # Vibrant yellow
#     (0.0000, 0.8078, 0.4196),  # Emerald green
#     (1.0000, 0.3412, 0.1333),  # Vivid orange
#     (0.5412, 0.1686, 0.8863),  # Electric purple
#     (0.0000, 0.6784, 0.9373),  # Cyan
#     (0.9569, 0.2627, 0.2118),  # Bright red
#     (0.1803, 0.8000, 0.4431),  # Lime green
#     (1.0000, 0.4118, 0.7059),  # Hot pink
# ]

# Input N (2 - 9), number of colors in the game or the modular system, in which the game takes place
N = 0
while N<2 or N>9:
    N = int(input("Enter N, the number of colors in the game. (2-9):"))

# cmap = LinearSegmentedColormap.from_list('custom cmap', colors_map[:N], N)

# dimensions of the grid
m = 0
while m<1:
    m = int(input("Enter the number of rows in the board:"))
n = 0
while n<1:
    n = int(input("Enter the number of columns in the board:"))

# connectivity rule
conn = 0
while conn!=4 and conn!=8:
    conn = int(input("Enter type of connectivity between cells of the board. (4 or 8 connectivity):"))

# choose one of the colors as winning condition
win_cond = -1
while win_cond<0 or win_cond>=N:
    win_cond = int(input(f"Winning condition would be to turn all of the lights into any one of the following colors {list(range(N))}.\nChoose the winning color: "))

# make direction vector according to connectivity rule
dirx = []
diry = []
if conn == 4:
    dirx=[0,1,0,-1,0]
    diry=[0,0,1,0,-1]
elif conn == 8:
    dirx=[0,1,0,-1,0,1,-1,1,-1]
    diry=[0,0,1,0,-1,-1,1,1,-1]

# display (m*n, 1) vector as (m,n) board
def show_board(board, m,n):
    for i in range(m):
        for j in range(n):
            idx = (n*i)+j
            print(colors[board[idx,0]], end="  ")
        print("\n")

# dispaly augmented matrix [A|b]
def show_aug_board(a, b, m,n):
    for i in range(m*n):
        for j in range(m*n):
            print(a[i,j], end="  ")
        print(f"|  {b[i,0]}")

initial_state = np.random.randint(N, size=(m*n, 1), dtype=np.int8)
final_state = np.array([win_cond for i in range(m*n)]).reshape(-1,1)

print("Initial Board:-")
show_board(initial_state, m,n)
print("Final Board:-")
show_board(final_state, m,n)

"""
We model the desired final state as, final = initial + A*X,
A = transformation matrix;  X = strategy matrix, where X[i] represent the number of time i_th cell needs to be pressed.
Hence we get, A*X = (final - initial) ===>  A*X = b 
"""

# get transformation matrix according to connectivity rule. This matrix will alway be of size (m*n, m*n) as it captures 
# cell to cell interactions and will alway be symmetric, becuase if x flips y then y flips x.
def get_transformation_matrix(m,n, dirx, diry):
    a = np.zeros((m*n, m*n), dtype=np.uint8) 

    for i in range(0, m*n):
        # print(f"cell number: {i}")
        x,y = i//n,i%n
        for j in range(len(dirx)):
            nx,ny = x+dirx[j],y+diry[j]
            if nx>=0 and nx<m and ny>=0 and ny<n:
                # print(f"connects to cell: ({nx}, {ny}) with cell number: {(n*nx)+ny}")
                a[i, (n*nx)+ny] = 1
    return a

# constant b matrix, b = (final-initial)
def get_constant_matrix(final_state, initial_state, N):
    return (final_state-initial_state)%N


a = get_transformation_matrix(m,n, dirx, diry)
b = get_constant_matrix(final_state, initial_state, N)
print("Transformation and constant matrix:-")
print(a, a.shape)
print(b, b.shape)
print("Augmented Matrix:-")
show_aug_board(a, b, m, n)
print("\n")

# inverse of num under modulo N
def get_inverse(num, N):
    for i in range(2, N):
        if (num*i)%N==1:
            return i
    raise Exception(f'Multiplicative inverse of {num} does not exists in Modulo {N}! \
                    \nIt is preferable for N to be prime, so that every number under mod N has a definite multiplicative inverse.')

# Gauusian Jordan elemination of augmented matrix [A|b] under Modulo N
def modular_gss_elemination(a, b, m, n, N):
    sz = m*n
    # traverse along the main diagonal
    for k in range(0, sz):
    # if pivot element (num on main diagonal) is 0, we replace entire row, where pivot non zero pivot is available.
        if a[k,k] == 0:
            for i in range(k+1, sz):
                if a[i,k] != 0:
                    for j in range(0, sz):
                        a[k,j], a[i,j] = a[i,j], a[k,j]
                    b[i,0], b[k,0] = b[k,0], b[i,0]
        
        # if pivot element is stil zero, skip the respective row.
        if a[k,k] == 0:
            continue
            
        # make leading one by multiplying inverse of pivot under mod N
        if a[k,k] != 1:
            pv = a[k,k]
            pv_inv = get_inverse(pv, N)
            for j in range(0, sz):
                a[k,j] = (a[k,j]*pv_inv)%N
            b[k,0] = (b[k,0]*pv_inv)%N

        # make zero under and above pivot element, Rather than subtracting to make 0, if we add N-k to k we get N which is 0 under modulo N. 
        for i in range(0, sz):
            if i!=k and a[i,k]!=0:
                fc = N-a[i,k]
                for j in range(k, sz):
                    a[i,j] = ((a[i,j]%N) + ((fc*a[k,j])%N))%N
                b[i,0] = ((b[i,0]%N) + ((fc*b[k,0])%N))%N
    return a,b

# returns the basis of null space of A, which is always orthogonal to column space of A in case of symmetrix matrices.
def get_basis(a_inv, m,n,N):
    basis = []
    k = (m*n)-1
    while k>=0 and k<m*n and a_inv[k,k]==0:
        temp = (N-a_inv[:,k].copy())%N
        temp[k]=1
        basis.append(temp)
        k-=1
    return np.array(basis)

# final state is achieve able if basis is null or empty, or if b is orthogonal to all vectors in basis, 
# because if b is orthogonal to all vectors in basis it means tha it lies in column space of A, 
# hence configuration b is attainable as it is a linear combination of column space of A
def check_solvability(a, b, m,n,N):
    a_inv, b_inv = modular_gss_elemination(a.copy(), b.copy(), m,n,N)
    basis_nullspace = get_basis(a_inv, m,n,N)
    print("After gaussian elimination we get the below augmented matrix:")
    show_aug_board(a_inv, b_inv, m,n)
    print("Null space of row reduced transformation matrix:")
    print(basis_nullspace)

    for i in basis_nullspace:
        if np.dot(i, b)[0]%N!=0:
            print(f"The required configuration (final - initial), {b.flatten()}, is not perpendicular to vectors in basis of null space of trasnformation matrix, \
                  which suggests that required configuration is not under the column space of the transformation matrix. \
                  \nMeaning it is not solvable under given game settings.")
            return None
    
    # if solvalbe return solution vector 
    return b_inv  

# click cell, inc number of times
def toggle(board, cell, inc, m,n,N):
    x, y = cell//n, cell%n
    for i in range(len(dirx)):
        nx, ny = x+dirx[i], y+diry[i]
        if nx>=0 and nx<m and ny>=0 and ny<n:
            neighbour_cell = (n*nx)+ny
            board[neighbour_cell,0] = (board[neighbour_cell,0]+inc)%N
    return board

# def save_state(board, index, title):
#     plt.matshow(board, cmap=cmap, interpolation='nearest', vmin=-0.5, vmax=N-0.5)
#     plt.colorbar(ticks=np.arange(0, N, 1))
#     plt.title(title)
#     plt.savefig(f"media/{index:0004}.png")
#     plt.close()

# display the solution by clicking the desired cells in solution vector
def show_solution(initial_state, solution, m,n,N):
    k=0
    show_board(initial_state, m,n)
    # save_state(initial_state.reshape(m,n), k, "Initial State")
    # print("--"*30)
    k+=1
    for i in range(0, m*n):
        if solution[i,0]>0:
            initial_state = toggle(initial_state, i, solution[i,0], m,n,N)
            text = f"cell number: ({i//n}, {i%n}), clicked {solution[i,0]} times."
            # save_state(initial_state.reshape(m,n), k, text)
            print("--"*10,text,"--"*10, sep="  ")
            k+=1
            show_board(initial_state, m,n)
            # print("--"*30)

def solve(a,b,m,n,N):
    solution = check_solvability(a,b,m,n,N)
    if solution is not None:
        print("Solution:")
        print(solution)
        #print(f"showing solution path:-")
        #show_solution(initial_state, solution, m,n,N)
    else:
        print("Puzzle not solvable.")


if __name__=='__main__':
    solve(a, b, m, n, N)
