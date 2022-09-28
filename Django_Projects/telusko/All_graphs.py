import yaml
import matplotlib.pyplot as plt
from time import sleep

def plot_graph(param_name,param_vals,param_metric):
    
    
    plt.scatter(param_vals,param_metric,c='blue')
    plt.xlabel(param_name)
    plt.ylabel("Frames Per Second  ---->")
    #plt.legend()
    plt.savefig("graphs/{}.png".format(param_name)) #static/css/   C:\\Users\\rtejac\\
    plt.clf()
    
with open("Data_from_PAT.yaml") as f:
	data = yaml.full_load(f)
	data ={k:data[k] for k in sorted(data.keys())}


with open("Names_of_params.yaml") as f:
	n_data = yaml.full_load(f)

def get_key(val):
	global d_i
	for key, value in d_i.items():
		if val == value:
			return key

d = dict()
d_i = dict()


def plot():
	
	l = []

	for k,v in n_data.items():
		for e in v:
			d[e] = []
			l.append(e)
			d[e+"_met"] = []
			d_i[e] = v.index(e)

	
	for k,v in data.items():
		for ind,ele in enumerate(v):
			d[get_key(ind)].append(ele)
			d[get_key(ind)+"_met"].append(k)


	f = open("graphs/images_names.txt",'w')

	for i in l:
		print("Plotting",i+'.png')
		f.write(i+'\n')
		plot_graph(i,d[i],d[i+"_met"])

plot()