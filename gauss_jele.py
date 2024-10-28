import numpy as np

n =3

a = np.array([[4,6,2],[-6,5,1],[-1,5,9]], dtype=float) 
b = np.array([4,6,1], dtype=float)

print(a[2,0])

print(a,b,a.shape,b.shape,sep="\n")

#print(np.linalg.det(a))

x = np.linalg.inv(a)@b.reshape(-1,1) 
print(x)

def gaussj(a,b,n):
    for k in range(0,n):
        pv = a[k][k]
        for j in range(k,n):
            a[k][j]/=pv
        b[k]/=pv

        for i in range(0,n):
            if i!=k and a[i][k]!=0:
                fc=a[i][k]
                for j in range(k,n):
                    a[i][j] -= (fc*a[k][j])
                b[i] -= (b[k]*fc)

    return a,b

ga,gx = gaussj(a.copy(),b.reshape(-1,1),n)
gb = a@gx
print(ga,gx,gb,sep="\n")
