#!/usr/bin/env python3
# ----------------------------------------------------------------------------
#
# INTEL CONFIDENTIAL
#
# Copyright 2020 (c) Intel Corporation.
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them  is governed by the  express license under which  they were
# provided to you ("License"). Unless the License provides otherwise, you  may
# not  use,  modify,  copy, publish,  distribute,  disclose  or transmit  this
# software or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no  express
# or implied  warranties, other  than those  that are  expressly stated in the
# License.
#
# ----------------------------------------------------------------------------

# Reference link for hardware knobs : https://wiki.ith.intel.com/display/cloudperf/Linux+Kernel+Tuning+Knobs+and+Ranges
# Run this program to find out what are the best parameters for a given application to work
# Benchmark of OpenVINO is deined in this code, we can change to required application we want.
# Here we login to a machine using SSH and execute the commands
# Run 'python3 auto_tune.py -h  -un username -pw password'

import os
import sys
import time
from time import sleep
import yaml
import optuna
import datetime
import threading
import argparse
import paramiko
import random
from selenium import webdriver
import matplotlib.pyplot as plt
from selenium.webdriver.common.keys import Keys





# def Get_Browser_Access():

#     global browser

#     browser = webdriver.Chrome(executable_path="C:\\Users\\rtejac\\Downloads\\chromedriver_win32_1\\chromedriver.exe")
#     try:
#         browser.get("http://127.0.0.1:8000/")
#     except Exception as e:
#         print(e)

#     #return browser





# To store the values for each iteration
Iterations_list = []

# Print the final output
def Stats(args,l, study):

    if(args.direction == 'maximize'):
        #Shouldn't be removed because This line will be searched to find fps info.
        print("Maximum FPS {} is acheived with the knob values as follows".format(max(Iterations_list)))
    else:
        #Shouldn't be removed because This line will be searched to find fps info.
        print("Minimum FPS {} is acheived with the knob values as follows".format(min(Iterations_list)))
    for key, value in study.best_trial.params.items():
        print("{}::{}".format(key, value))


# Function to reboot.
# Mostly required when we made any hardware changes in the machine.
# Used in the Performance_Optimizer function where the values are generated for the hardware and software.
def Reboot(args):

    """
    Reboot will take some time and machine won't be accepting any commands.
    So waiting for some time which may differ from machine to machine.
    Here we are waiting for 180 seconds.

    """
    if args.reboot == 'yes':
        print("\nReboot flag is Set")
        print("Rebooting the system, All changes in the hardware knobes will be set to default")
        reboot = "echo {} | sudo -S reboot".format(args.password)

        _, stdout, _ = ssh.exec_command(reboot)
        print("Reboot cmd issued")

    else:
        print("\nReboot flag is Unset")



def getCmdsFromYAML():

    cmds = []
    tune = []

    try:
        with open(args.config_file) as file:
            config_params = yaml.full_load(file)
    except:
        print(args.config_file," not Found")
        sys.exit(1)

    for i in config_params:
        for k, v in i.items():
            try:
                result = v['result']
            except:
                pass

            for a,b in v.items():
                if a == 'tune':
                    for i in b:
                        if i not in tune:
                            tune.append(i)

            for c,d in v['parameters'].items():
                v['cmd'] = v['cmd'].replace('{'+c+'}',d)

            cmds.append(v['cmd'])

    return cmds,tune,result


# def Refresh(browser):

#     #global browser

#     while T_no <= args.num_trials:
#         browser.refresh()
#         #sleep(1)

def Update(Current_iter,Total,Iter_val,best):

    with open("../../Update/Status.txt",'w') as f:

        f.write("Current iteration : {}".format(Current_iter)+'\n')
        f.write("Total : {}".format(Total)+'\n')
        f.write("Iteration value : {}".format(Iter_val)+'\n')
        f.write("Best : {}".format(best)+'\n')
        

    with open("../../Update/RT.yaml",'w') as f:
        yaml.dump(dict_for_yaml,f,sort_keys=False)


    



app_n = []
osp_n = []
hwp_n = []
# Objective function to optimize
def Performance_Optimzer(trial):

    """
    Objective function that performs the operation and returns the score
    """

    global T_no,now

    try:
        with open(args.tuning_file) as file:
            parameters = yaml.full_load(file)
    except:
        print(args.tuning_file," not Found")
        sys.exit(1)
    #------------ Application Parameters -----------------#
    app = []            #Stores data(Names)
    # if T_no == 1:
    #     app_n = []      #Stores name of app for printing
    app_data = []       #Stores data(Values)
    app_data_type = []  #Stores type of data
    #------------ OS Parameters -----------------#
    osp = []            #Stores data(Name)
    # if T_no == 1:
    #     osp_n = []      #Stores name of app for printing
    osp_cat = []        #Stores category of the data in osp list
    osp_data = []       #Stores data(Values)
    osp_data_type = []  #Stores type of data
    #------------ Harware Parameters -----------------#
    hwp = []            #Stores data(Name)
    # if T_no == 1:
    #     hwp_n = []      #Stores name of app for printing
    hwp_data_type = []  #Stores type of data
    hwp_data = []       #Stores data(Values)
    hwp_reg = []        #Stores the register numbers associated with hwp list
    hwp_cmd = []        #Stores the commands associated with hwp list
    #------------ Application commands -----------------#
    cmds = []           #Stores the commands that are to be executed
    tune = []           #Stores the tunables from the args.config_file

    give_data_to_yaml = []

    global names_to_yaml,ssh
    
    for i in parameters:
        for k, v in i.items():
            if k == "app_params" and args.apptune == 'yes':
                #print("Application Parameters")
                for a, b in v.items():
                    app.append(a)
                    if T_no == 1:
                        app_n.append(a)
                        names_to_yaml.append(a)
                    
                    if b[0]["type"] == "list":
                        app_data_type.append('list')
                        app_data.append(b[1]['values'])
                        
                    if b[0]["type"] == "range":
                        app_data_type.append('range')
                        app_data.append([b[1]['min'],b[2]['max']])

                #print(app_n)
                        
                for i in range(len(app)):
                    if(app_data_type[i]=='list'):
                        app[i] = trial.suggest_categorical(app_n[i],app_data[i])
                    if(app_data_type[i]=='range'):
                        app[i] = trial.suggest_int(app_n[i],app_data[i][0],app_data[i][1])
                    give_data_to_yaml.append(app[i])
                    
            if k == "os_params" and args.ostune == 'yes':
                #print("OS Parameters")
                for a, b in v.items():
                    osp.append(a)
                    if T_no == 1:
                        osp_n.append(a)
                        names_to_yaml.append(a)
                    osp_cat.append(b[0]['category'])
                    if b[1]["type"] == "list":
                        osp_data_type.append('list')
                        osp_data.append(b[2]['values'])
                    if b[1]["type"] == "range":
                        osp_data_type.append('range')
                        osp_data.append([b[2]['min'],b[3]['max']])
                #print(osp_n)
                for i in range(len(osp)):
                    osp[i] = trial.suggest_int(osp_n[i],osp_data[i][0],osp_data[i][1])
                    cmd = "echo {} | sudo -S sysctl -w {}.{}={}".format(args.password,osp_cat[i],osp_n[i],osp[i])
                    give_data_to_yaml.append(osp[i])
                    #print(cmd)
                    
                    try:
                        _, stdout, _ = ssh.exec_command(cmd)
                        #print(cmd)
                    except Exception as error:
                        print(error,"@ ",cmd)
                        print("Error in setting OS params......{}\nTrying to reconnect...".format(cmd))
                        # sleep(5)
                        ssh = CreateSSH(args)
                        if ssh == None:
                            print("Host lost")
                            sys.exit(2)
                        # _, stdout, _ = ssh.exec_command(cmd)
                        #sys.exit(3)

            if k == "hw_params" and args.hwtune == 'yes':
                #print("Harware Parameters")
                for a, b in v.items():
                    hwp.append(a)
                    if T_no == 1:
                        hwp_n.append(a)
                        names_to_yaml.append(a)
                    hwp_reg.append(b[3]['reg'])
                    hwp_cmd.append(b[4]['cmd'])
                    if b[0]["type"] == "list":
                        hwp_data_type.append('list')
                        hwp_data.append(b[1]['values'])
                    if b[0]["type"] == "range":
                        hwp_data_type.append('range')
                        hwp_data.append([b[1]['min'],b[2]['max']])

                #print(hwp_n)
                cmd =  "echo {} | sudo -S modprobe msr".format(args.password)
                _, stdout, _ = ssh.exec_command(cmd)
                for i in range(len(hwp)):
                    hwp[i] = trial.suggest_int(hwp_n[i],hwp_data[i][0],hwp_data[i][1])
                    if hwp_reg[i] == int('0x1AD',16):
                        a = hwp[i]
                        a = a  | a<<16 | a<<32 | a<<48
                        cmd = "echo {} | sudo -S ".format(args.password)+hwp_cmd[i].format(hex(hwp_reg[i]),hex(a))
                    else:
                        cmd = "echo {} | sudo -S ".format(args.password)+hwp_cmd[i].format(hex(hwp_reg[i]),hex(hwp[i]))
                    give_data_to_yaml.append(hwp[i])
                    
                    try:
                        #_, stdout, _ = ssh.exec_command(cmd)
                        print(cmd)
                    except Exception as error:
                        print(error)
                        print("Error in setting Hardware params......{}\nTrying to reconnect...".format(cmd))
                        sleep(5)
                        ssh = CreateSSH(args)
                        
                        #sys.exit(3)



    
    # cmds,tune,result = getCmdsFromYAML()
    
    # index = 0
    # for i in range(len(cmds)):
    #     for par in tune:
    #         if par in cmds[i]:
    #             cmds[i] = cmds[i].replace(par,str(app[index]))
    #             index += 1

    per = []
    for loop in range(2):
        # for cmd in cmds:
        #     _, stdout, _ = ssh.exec_command(cmd)
        #     lines = stdout.readlines()
        #     #performance = 0#random.randint(600,1000)#0
        #     for line in lines:
        #         print(line)
        #         if result in line:
        #             per.append(round(find_fps(line),2))
        #_,_,_ = ssh.exec_command("cd /home/intel/rtejac/squeezenet1.1/;/bin/bash run_multi.sh &") #For Squeezenet
        #_,_,_ = ssh.exec_command("cd /home/intel/rtejac/COVID/application/;/bin/bash run_multi.sh &")  #For Covid
        _,_,_ = ssh.exec_command("cd /home/intel/rtejac/COVID/application/;/bin/bash run_multi.sh &".format(n)  #For PCB
        #for line in err.readlines():
        #    print(line)
        #for line in out.readlines():
        #    print(line)
        print("bg and fg processes are started")
        pid = []
        sleep(0.5)
        _,stdout,_ = ssh.exec_command("ps -el | grep -e PID -e python3")
        
        pid_lines = stdout.readlines()
        for l_no in range(len(pid_lines)):
            #print(pid_lines[l_no])
            pid_lines[l_no] = pid_lines[l_no].split()
        
        #_,stdout,stderr = ssh.exec_command("cd rtejac/squeezenet1.1/;source /opt/intel/openvino/bin/setupvars.sh;python3 /opt/intel/openvino/deployment_tools/tools/benchmark_tool/benchmark_app.py -m  squeezenet1.1.xml -i car.png -progress true  -t 10") #For Squeezenet
        #_,stdout,stderr = ssh.exec_command("cd rtejac/COVID/application/;source /opt/intel/openvino_2021.3.394/bin/setupvars.sh;python3 main.py --person_detector ../intel/person-detection-retail-0013/FP16/person-detection-retail-0013.xml -d1 CPU -m1_width 625 -m1_height 350 --width 640 --height 360 -n_s 1 -n_c 1 -n_th 4 -min_social_distance 70 -decode_device CPU --no_show -i ../resources/station.mp4")  #For Covid
        _,stdout,stderr = ssh.exec_command("cd rtejac/src-ai_modeling/WLC_KPI_AI_CODE;source /opt/intel/openvino_2020.4.287/bin/setupvars.sh;python3 ai_max.py -i 10 -t 30 -d CPU")  #For PCB
        for pid_line in pid_lines:
            try:
                if 'PID' in pid_line:
                    index = pid_line.index('PID')
                    continue
            #print(line.split(' '))
                pid.append(pid_line[index])
            except NameError:
                print("Include 'PID' in the grep command")

        #print("List of processes running in background are : ",pid)

        print(f"{len(pid)} instances of the application is running in bg for loop {loop+1} of trial {T_no}, they are {pid}")
        lines = stdout.readlines()
        for err in stderr.readlines():
            print(err)
        for line in lines:
            #if 'Throughput' in line: # For Squeezenet
            #if 'Frames processed per second' in line: #For Covid
            if 'Average FPS' in line: #For PCB
                print("Loop number {} of Trial {}".format(loop+1,T_no),line)
                per.append(round(find_fps(line),2))

    # Forming the list for the final output
    print(per)
    sleep(1) 
    _,_,_ = ssh.exec_command("pkill -f python3")
    sleep(1)
    performance = round(sum(per)/len(per),2) #round(random.uniform(600, 1000),2)#
    print(performance)
    Iterations_list.append(performance)

    dict_for_yaml[str(performance)] = give_data_to_yaml
    Update(T_no,args.num_trials,performance,max(Iterations_list))
    if T_no == 1:
        with open("../../Update/Names.yaml",'w') as f:
            names = {'FPS/Parameter Values' : names_to_yaml}
            yaml.dump(names,f,sort_keys=False)

    print("Trial {} finished with {} FPS".format(T_no,performance)) #Shouldn't be removed because This line will be searched to find fps info.
    T_no += 1
    return performance


def find_fps(s):

    o = ''
    for i in range(len(s)):
        if s[i].isdigit():
            o += s[i]
        if s[i] == '.' and s[i-1].isdigit() and s[i+1].isdigit():
            o += s[i]
        if len(o) != 0 and s[i] == ' ':
            break

    return float(o)

def get_args():
    # Getting the values from the user by command line interface
    parser = argparse.ArgumentParser(
        description="Program to auto-tune platform for OpenVINO benchmark"
    )
    parser.add_argument("-host", help="Host name or IP address", type=str)
    parser.add_argument("-username", help="User name", type=str)
    parser.add_argument("-password", help="Password",default = "", type=str)
    parser.add_argument("-num_trials", help="Number of trails", type=int)
    parser.add_argument("-direction", help="Optimize to Maximum/Minimum")
    parser.add_argument("-reboot", help="Do you want to rebbot the system in the last",default = 'no', type=str)
    parser.add_argument("-tuning_file", help="File name consisting tuning parameters", type=str)
    parser.add_argument("-config_file", help="File name consisting config", type=str)
    parser.add_argument("-ostune", help="yes/no for OS tuning",default = 'False', type=str)
    parser.add_argument("-apptune", help="yes/no for Application tuning",default = 'False', type=str)
    parser.add_argument("-hwtune", help="yes/no for Hardware tuning",default = 'False', type=str)

    args = parser.parse_args()

    # if args.apptune != 'yes':
    #     print("Application tuning is must")
    #     sys.exit(0)

    return args


def CreateSSH(args):
    
    global ssh

    ssh = None
    i = 1

    while i<10:
        try:
            ssh = paramiko.SSHClient()  # "ssh" Created
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Addedd to Keys if missing
            ssh.load_system_host_keys()
            ssh.connect(args.host, port=22, username=args.username, password=args.password)#, banner_timeout=200)  # Logging into host
            print("Connected to " + args.host + " and executing command(s)")
        
            break
        
        except paramiko.AuthenticationException:  # Wrong password
            print("Authentication failed when connecting to %s".format(args.host))
            return None  # Exit

        except Exception as e:
            print(e)

        i += 1
        print("Unable to connect for the {} time, Trying ({}/10)".format(i-1,i))
        #sleep(5)

    return ssh


def Run_Update():

    os.system("pythonw.exe Update_data.pyw")

# Connecting to the machine/Server
if __name__ == "__main__":

    args = get_args() #Parsing inputs
    T_no = 1 #For Printing data inside Performance_Optimizer
    
    # Connecting to the machine
    ssh = CreateSSH(args)
    if ssh == None :
        print("Problem in Creating an SSH Connection")
        sys.exit(2)
    
    dict_for_yaml = {}
    names_to_yaml = []
    browser = None#Get_Browser_Access()

    # t1 = threading.Thread(target=Run_Update)
    # t1.start()
    now = datetime.datetime.now().strftime("%H:%M:%S")
    try:
    # Creating an Study object for Optuna      
        study = optuna.create_study(direction=args.direction)#,study_name="Sq_test1",storage='sqlite:///db.sqlite3',load_if_exists=True) #For debug purpose,Can remove study_name,storage,load_if_exists later. They are kept in case if previous study stopped by some reasons
        study.optimize(Performance_Optimzer, n_trials=args.num_trials)

        Stats(args,Iterations_list, study)

        sleep(5)
        #browser.close()
    except Exception as e:
        print(e)
    
    with open('Data_from_PAT.yaml','w') as f:
        yaml.dump(dict_for_yaml,f,sort_keys=False)
    with open('Names_of_params.yaml','w') as f:
        names = {'FPS/Parameter Values' : names_to_yaml}
        yaml.dump(names,f)
    try:
        Reboot(args)
    except Exception as e:
        print(e)
        
    finally:
        ssh.close()
        #browser.close()
        print("\n\nSession Completed and and closed...\n")
