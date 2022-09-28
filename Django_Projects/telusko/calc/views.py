from django.shortcuts import render
from django.http import HttpResponse
import os,sys,time
from subprocess import run,PIPE
import yaml
import paramiko
import datetime
import matplotlib.pyplot as plt
# Create your views here.

def home(request):
    return render(request,'home.html',{'name':'Teja'})#HttpResponse("Hello from Django")

#
# knobes_dict = {}
# base_per = None
# workload = None
# best = None
# cmp_base = None
# improvment = None
# direction = None

def fetch_fps(s):

    o = ''
    for i in range(len(s)):
        if s[i].isdigit():
            o += s[i]
        if s[i] == '.' and s[i-1].isdigit() and s[i+1].isdigit():
            o += s[i]
        if len(o) != 0 and s[i] == ' ':
            break

    return float(o)



def optimize(request):

    print('Optimizing........')
    global trials
    host = request.POST['host']
    un = request.POST['un']
    pw = request.POST['pw']
    Tuning_file = request.POST['Tuning file']
    Config_file = request.POST['Config file']
    trials = request.POST['trials']
    apptune = request.POST['Application Tuning']
    ostune = request.POST['OS Tuning']
    hwtune = request.POST['Hardware Tuning']
    direction = request.POST['direction']
    reboot = request.POST['reboot']
    cmp_base = request.POST['cmp_base']

    global workload
    workload = Tuning_file.split('_')[1].split('.')[0]

    #Executing base case
    if cmp_base == 'yes':
        base_cmd = [sys.executable,"base.py",host,un,pw,'../../Tuning_Files/'+Tuning_file,'../../Config_Files/'+Config_file]
        out = run(base_cmd,shell=False,stdout=PIPE)

        if out.returncode == 1:
            msg = "Problem in loading YAML files/ files missing in base"
            print(msg)
            #os.system("color 7")
            return render(request,'error.html',{'message':msg})
        if out.returncode == 2:
            msg = "Problem in establishing SSH Connection in base"
            print(msg)
            #os.system("color 7")
            return render(request,'error.html',{'message':msg})
        if out.returncode == 3:
            msg = "Problem in executing commands"
            print(msg)
            os.system("color 7")
            return render(request,'error.html',{'message':msg})

        #print(out)
        search = out.stdout.decode("utf-8")
        #print(search)
        s_l = search.split('\n')
        for i in s_l:
            print(i)
            if 'Base FPS' in i:
                base = i

        base_per = fetch_fps(base)
        print("Base FPS : {}".format(base_per))


    command = [sys.executable,"auto_tune.py",'-host',host,
                                         '-username',un,
                                         '-password',pw,
                                         '-tuning_file','../../Tuning_Files/'+Tuning_file,
                                         '-config_file','../../Config_Files/'+Config_file,
                                         '-apptune',apptune,
                                         '-ostune',ostune,
                                         '-hwtune',hwtune,
                                         '-num_trials',trials,
                                         '-reboot',reboot,
                                         '-direction',direction]



    #print(command)
    out = run(command,shell=False,stdout=PIPE)

    if out.returncode == 1:
        msg = "Problem in loading YAML files/ files missing"
        print(msg)
        os.system("color 7")
        return render(request,'error.html',{'message':msg})
    if out.returncode == 2:
        msg = "Problem in establishing SSH Connection/Machine stopped suddenly"
        print(msg)
        os.system("color 7")
        search = out.stdout.decode("utf-8")
        s_l = search.split('\n')
        for i in s_l:
            print(i)
        return render(request,'error.html',{'message':msg})
    if out.returncode == 3:
        msg = "Problem in executing commands"
        print(msg)
        os.system("color 7")
        search = out.stdout.decode("utf-8")
        s_l = search.split('\n')
        for i in s_l:
            print(i)
        return render(request,'error.html',{'message':msg})

    os.system("color 7") #To change the prompt color to White from Green(Which is caused by Optuna)
    search = out.stdout.decode("utf-8")
    sp = b'\r\n'
    s_l = search.split('\n')
    res = []
    print('\n'*10)
    for i in s_l:
        print(i)
        if 'finished with ' in i:
            res.append(i)
        if 'is acheived with the knob values' in i:
            best_str = i

    res_fps = []
    res = [i.split('with ')[1] for i in res]
    for st in res:
        res_fps.append(fetch_fps(st))

    best = fetch_fps(best_str)
    #print("Base FPS : {}".format(base_per))
    print("List of all iterations FPS :",res_fps)
    print("Best FPS : {}".format(best))

    global knobes_dict
    knobes_dict = {}
    s = search
    for line in s_l[s_l.index(best_str):]:
        try:
            d = line.split('::')
            knobes_dict[d[0]] = d[1]
        except:
            pass

    if cmp_base == 'yes':
        improvment = (best - base_per)/base_per * 100
    else:
        improvment = 0
        base_per = 0
    #Graph
    run([sys.executable,'plot_graph.py',str(res_fps),direction],shell=False,stdout=PIPE) #For Graph
# 
#     return HttpResponse("Process Completed")
#
# def results(request):
#
#     global knobes_dict,base_per,workload,best,cmp_base,improvment,direction

    return render(request,'results.html',{'k':knobes_dict,
                                          'base':base_per,
                                          'workload':workload,
                                          'fps':best,
                                          'cmp_base':cmp_base,
                                          'improvment':round(improvment,2),
                                           'dir':direction,
                                           })



def download(request):

    cwd = os.getcwd()
    print(os.getcwd())
    os.chdir('../../Knob_Files/')
    global workload
    #print(workload)
    fname = workload+'_'+'Knobes_file_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'.txt'
    global knobes_dict

    with open(fname,'w') as f:
        #yaml.dump(knobes_dict,f)
        for k,v in knobes_dict.items():
            f.write(k+':'+v+'\n')

    os.chdir(cwd)
    return HttpResponse("Config file {} has been downloaded".format(fname))




def hadfile(request):

    return render(request,'apply.html')




def view_all(request):

    with open('Data_from_PAT.yaml','r') as f:
        data_to_page = yaml.full_load(f)
    with open('Names_of_params.yaml','r') as f:
        names_to_page = yaml.full_load(f)

    return render(request,'view_all.html',{'iter_data':data_to_page,
                                            'names':names_to_page,
                                            })




def apply(request):

    host = request.POST['host']
    un = request.POST['un']
    pw = request.POST['pw']
    Tune_file = '../../Tuning_Files/'+request.POST['tuning']
    knobes = '../../Knob_Files/'+request.POST['knobes']
    #global workload
    try:
        with open(Tune_file) as file:
            parameters = yaml.full_load(file)
            #print(parameters)
    except Exception as e:
        print("Couldn't find the file '{}'".format(Tune_file))
        return render(request,'error.html',{'message':"Couldn't find the file '{}'".format(Tune_file)})

    try:
        with open(knobes,'r') as f:
            s = f.read()
    except Exception as e:
        print("Couldn't find the file '{}'".format(knobes))
        return render(request,'error.html',{'message':"Couldn't find the file '{}'".format(knobes)})


    def split_out():

        for i in s.split('\n'):
            try:
                if i == '':
                    continue

                v = i.split(":")[1]
                d1.append([i.split(":")[0],str(i.split(":")[1]).replace(" ","")])

            except Exception as e:
                print(e)
                pass


    def get_commands():
        for i in parameters:
            for k,v in i.items():

                if k == 'os_params':
                    for a,b in v.items():
                        t = ['os']
                        t.append(a)
                        for e in b:
                            if 'category' in e.keys():
                                t.append(e['category'])
                            if 'cmd' in e.keys():
                                t.append(e['cmd'])
                        l.append(t)

                if k == 'hw_params':
                    for a,b in v.items():
                        t = ['hw']
                        t.append(a)
                        for e in b:
                            if 'reg' in e.keys():
                                t.append(hex(e['reg']))
                            if 'cmd' in e.keys():
                                t.append(e['cmd'])
                        l.append(t)
    def execute():
        for i in d1:
            for j in l:
                if i[0] == j[1]:
                    if j[0] == 'os':
                        cmd  = "echo {} | sudo -S ".format(pw)+j[3].format(j[2],j[1],i[1])
                        cmds.append(j[3].format(j[2],j[1],i[1]))
                        _, stdout,_ = ssh.exec_command(cmd)
                        print(cmd)
                    if j[0] == 'hw':
                        cmd = "echo {} | sudo -S ".format(pw)+j[3].format(j[2],i[1])
                        cmds.append(j[3].format(j[2],i[1]))
                        _, stdout,_ = ssh.exec_command(cmd)
                        print(cmd)


    def CreateSSH():

        try:
            ssh = paramiko.SSHClient()  # "ssh" Created
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Addedd to Keys if missing
            ssh.load_system_host_keys()
            ssh.connect(host, port=22, username=un, password=pw)  # Logging into host
            print("Connected to " + host + " and executing command(s)")

        except paramiko.AuthenticationException:  # Wrong password
            print("Authentication failed when connecting to %s" % host)
            return None  # Exit

        except Exception as e:
            print(e)
            return None

        return ssh


    l = []
    d1 = []
    cmds = []
    split_out()
    get_commands()
    ssh = CreateSSH()
    if ssh == None:
        l = ['Check the details of the machine properly','Entered details :','IP : {}'.format(host),'Username : {}'.format(un),'Password : {}'.format(pw)]
        msg = "Problem in connecting to {}...\n\n\t\n\t\n\t".format(host,host,un,pw)
        print(msg)
        return render(request,'error.html',{'message':msg,'extra':l})
    execute()
    time.sleep(5)


    return render(request,'apply.html',{'msg':'{} is applied to {}'.format(knobes,host),
                                            'cmds':cmds})
