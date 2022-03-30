# Fenómeno curioso: esto tiende una velocidad de 0,8
# Llego a la conclusión de que un número n dividido entre 2 más un número m
# repetidamente tiende a 2m.
# n/2 + m -> 2m
# Por ejemplo: n/2 + 0,4 -> 0,8

n = 10
m = 0.5

while n != 2 * m:
    print(n/2 + m)
    n = n/2 + m

print(n)
