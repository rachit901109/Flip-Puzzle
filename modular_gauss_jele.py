import numpy as np
import matplotlib.pyplot as plt

# ini = np.array([0,1,0,0,0,0,0,1,0,0,0,1,0,1,0,0,1,1,0,1,1,0,0,0,0]).reshape(-1,1)
ini = np.array([1,0,0,1,0,0,0,1,0,0,0,1,1,0,1,0,1,0,0,0,1,0,0,0,0]).reshape(-1,1)
f = np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]).reshape(-1,1)

#print(ini,f,b,sep="\n")
N = 2
n = 5
dirx=[0,1,0,-1,0]
diry=[0,0,1,0,-1]

# ini = np.ones((n*n,1),dtype=np.uint8)
# f = np.ones((n*n,1),dtype=np.uint8)
b = np.array([1,1,0,0,0,0,0,1,0,0,1,1,1,0,1,0,1,1,1,0,1,0,0,0,0]).reshape(-1,1)

a = np.zeros((n*n, n*n), dtype=np.uint8) 

for i in range(n*n):
    x,y = i//n,i%n
    for j in range(len(dirx)):
        nx,ny = x+dirx[j],y+diry[j]
        if nx>=0 and nx<n and ny>=0 and ny<n:
            a[i, (n*nx)+ny] = 1

def show_board(board, n):
    for i in range(n):
        for j in range(n):
            idx = (n*i)+j
            print(board[idx][0], end="\t")
        print("\n")
    print("\n")

def show_aug(a, b, n):
    for i in range(n):
        for j in range(n):
            print(a[i][j], end="  ")
        print(f"|  {b[i][0]}")
    print("\n")

print("Augmented board:-")
show_aug(a,b,n*n)

def get_inv(num, N):
    for i in range(2,N):
        if (num*i)%N==1:
            return i
    raise Exception(f'Multiplicative inverse of {num} does not exists in Modulo {N}!')

def mod_gss_jrdn(a,b,n,N):
    for k in range(0,n):
        if a[k,k] == 0:
            for i in range(k+1,n):
                if a[i,k] != 0:
                    for j in range(k,n):
                        a[i,j],a[k,j] = a[k,j],a[i,j]
                    b[i,0], b[k,0] = b[k,0], b[i,0]
                    print(f"swapping {i},{k}")
                    break
            # show_aug(a,b,n)
        
        if a[k,k]==0:continue

        if a[k,k]!=1:
            pv = a[k,k]
            pv_inv = get_inv(pv, N)
            print(f"pivot and inverse {pv}, {pv_inv}")
            for j in range(k,n):
                a[k,j] = (a[k,j]*pv_inv)%N
            b[k,0] = (b[k,0]*pv_inv)%N 
            # show_aug(a,b,n)

        for i in range(0,n):
            if i!=k and a[i,k]!=0:
                fc = N-a[i,k]
                print(f"factor {fc}")
                for j in range(k,n):
                    a[i,j] = ((a[i,j]%N) + ((fc*a[k,j])%N))%N
                b[i,0] = ((b[i,0]%N) + ((fc*b[k,0])%N))%N
        
        # show_aug(a,b,n)

        # plt.imshow(a, cmap="gray")
        # plt.xticks([],[])
        # plt.yticks([],[])
        # plt.savefig(f"media/{k+1:0004}.png")
        # plt.show()

    return a,b

# plt.imshow(a, cmap="gray")
# plt.xticks([],[])
# plt.yticks([],[])
# plt.savefig("media/0000.png")

ga,gx = mod_gss_jrdn(a.copy(),b.copy(),n*n,N)
print("--"*30)
print(f"After gaussian jordan elimination we get row reduced echelon form of augmented matrix.")
show_aug(ga,gx,n*n)

basis = []
for i in range((n*n)-1, -1, -1):
    if ga[i,i]==0:
        temp = (N-ga[:,i].copy())%N
        temp[i]=1
        basis.append(temp)

basis_null_space = np.array(basis)
print("basis of null space:-")
print(basis_null_space)

# print(basis_null_space[0].reshape(1,-1)@b)
# print(basis_null_space[1].reshape(1,-1)@b)
# print(basis_null_space[2].reshape(1,-1)@b)

def mod_dot(a,b,n):
    dprod = 0
    for i in range(n):
        dprod = ((dprod)%N + ((a[i,0]*b[i,0])%N))%N
    return dprod

for i in basis_null_space:
    # print(i.reshape(1,-1)@b)
    print(np.dot(i,b))
    print(mod_dot(i.reshape(-1,1), b, n*n))
