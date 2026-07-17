
# Kubetenes system n number of services
# m dependency list --> [(a,b), (b,c), (b,a) ]
# return a list of order of deploying service [] else -1

# n = [a,b,c,d,e]
# m = [(a,b), (b,c), (b,a)] --> -1

# m2 = [(a,b), (b,c)]
# result = [d,e,c,b,a] or [c,b,a,d,e]

# m3 = [(a,b), (b,c), (c,d) ,(a,d) ,(a,c)]  --> -1

a --> b --> c -->d
 a = 0
 b = 1 
 c = 2
 d = 3
 [a,b,c,d,e]
 
 
 [(a,b), (a,d) ,(a,c), (b,c), (c,d) ] 
 
 cache = {a:0, b:1,  d:2, c:2}
 cache = {b:0,c:1,d:1}
 cache = {c:0,d:0}
 cache = {}
 
 [a,b,c,d]
 
 
 
#  [(a,b), (a,d) ,(b,c), (c,d) ,(c,a)]

cache = {a:0, b:2,  d:2, c:2}
{ b:1,  d:1, c:1}
 
for i in range(len(m)):
    if m[i][0] not in cache:
        cache[m[i][0]] = 0
        cache[m[i][1]] = cache[m[i][0]] + 1
    else:
        if m[i][1] not in cache:
            cache[m[i][1]] = cache[m[i][0]] + 1  
             
            
        

