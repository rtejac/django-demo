import matplotlib.pyplot as plt
import sys

def plot_graph(trials,it,d):
    
    x = [i for i in range(1,trials+1)] # X-axis values
    l = []                             # For Max values trace
    mx = it[0]
    #Trace of Maximum value

    if (d == "minimize"):
        for i in it:
            if i <= mx:
                l.append(i)
                mx = i
            else:
                l.append(mx)
    else:
       for i in it:
            if i >= mx:
                l.append(i)
                mx = i
            else:
                l.append(mx)

    
    plt.scatter(x,it,c='blue',label="Each iteration values")
    plt.plot(x,l,c='orange',label="Trace of Best value")
    plt.xlabel("Trails  ---->")
    plt.ylabel("Frames Per Second  ---->")
    plt.legend()

    plt.savefig("static/css/graph.png") #static/css/   C:\\Users\\rtejac\\


print("Hello from plot.py")


l = sys.argv[1]
d = sys.argv[2]
print(l,d)

a = str(l[1:len(l)-1]).split(',')
#print(a)
for i in range(len(a)):
    a[i] = float(a[i])


plot_graph(len(a),a,d)