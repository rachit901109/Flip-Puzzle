import numpy as np

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


def solve(a, b, m,n,N):
    a_inv, b_inv = modular_gss_elemination(a.copy(), b.copy(), m,n,N)
    basis_nullspace = get_basis(a_inv, m,n,N)
    print("After gaussian elimination we get the below augmented matrix:")
    # show_aug_board(a_inv, b_inv, m,n)
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
