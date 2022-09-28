from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
from time import sleep
import matplotlib.pyplot as plt
import os


def plot_graph(trials,it,d="maximize"):
    
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

    
    plt.scatter(x,it,c='blue')#,label="Each iteration values")
    plt.plot(x,l,c='orange')#,label="Trace of Best value")
    plt.xlabel("Trails  ---->")
    plt.ylabel("Frames Per Second  ---->")

    plt.savefig("../../Update/static/css/graph.png")


def Get_Browser():

	browser = webdriver.Chrome(executable_path="../../Update/chromedriver.exe")
	try:
		browser.get("http://10.223.34.48:8000/")
		browser.maximize_window()
	except Exception as e:
			print(e)

	return browser




iter_list = []


def Update(browser):

	i = 0
	
	while True:

		try:
			f = open("../../Update/Status.txt",'r')
			d = f.readlines()

			for line in d:
				print(d)
			c = int(d[0].split(":")[1])
			t = int(d[1].split(":")[1])
			iter_val = float(d[2].split(":")[1])
			print(c,t)
			if iter_val not in iter_list:
				iter_list.append(iter_val)
			plot_graph(len(iter_list),iter_list)
			browser.refresh()
			sleep(1)
		except Exception as e:
			print(e)
			sleep(1)
			c = 0
			t = 1
			pass

		if c == t:
			sleep(5)
			browser.close()
			break


try:
	browser = Get_Browser()
	Update(browser)
except Exception as e:
	print(e)
finally:
	os.remove("../../Update/Status.txt")