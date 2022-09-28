import matplotlib.pyplot as plt
import sys,os

def plot_graph(trials,it):
    
    x = [i for i in range(trials)]
    l = []
    mx = it[0]
    for i in it:
        if i >= mx:
            l.append(i)
            mx = i
        else:
            l.append(mx)

    #print(l,it,x)
    plt.scatter(x,it,c='blue')
    plt.plot(x,l,c='red')
    plt.xlabel("Trail number  ---->")
    plt.ylabel("Frames Per Second  ---->")
    #plt.show()
    print("os.getcwd() : ",os.getcwd())
    os.chdir("static/css")
    print("os.getcwd() : ",os.getcwd())
    plt.savefig("static/css/graph.png")

l = sys.argv[1]
a = str(l[1:len(l)-1]).split(',')

for i in range(len(a)):
    a[i] = int(a[i])


plot_graph(len(a),a)