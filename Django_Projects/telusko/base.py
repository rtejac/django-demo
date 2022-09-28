import paramiko
import sys
import yaml
import random


def CreateSSH(host,username,password):
    

    try:
        ssh = paramiko.SSHClient()  # "ssh" Created
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Addedd to Keys if missing
        ssh.load_system_host_keys()
        ssh.connect(host, port=22, username=username, password=password)  # Logging into host
        print("Connected to " + host + " and executing command(s)")
    
    except paramiko.AuthenticationException:  # Wrong password
        print("Authentication failed when connecting to %s" % host)
        return None  # Exit

    except Exception as e:
        print(e)
        return None

    return ssh


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


def base(ssh,tuning,config):


    try:
        with open(tuning) as f:
            t_data = yaml.full_load(f)
    except:
        print("Problem in finding/reading Tuning file")
        sys.exit(1)

    try:
        with open(config) as f:
            c_data = yaml.full_load(f)
    except:
        print("Problem in finding/reading Config file")
        sys.exit(1)
    cmds = []

    for i in c_data:
        for k,v in i.items():

            for a,b in v['parameters'].items():
                v['cmd'] = v['cmd'].replace('{'+a+'}',b)

            for c,d in t_data[0]['base'].items():
                v['cmd'] = v['cmd'].replace(c,str(d))

            try:
                result = v['result']
            except:
                pass
            cmds.append(v['cmd'])

    print(cmds)
    # cmd = "echo {} | sudo -S sysctl -w {}.{}={}".format("wlc","vm","swappiness",random.randint(0,50))
    # print(cmd)
    # _,stdout,stderr = ssh.exec_command(cmd)
    # for l in stdout.readlines():
    #     print(l)
    # for l in stderr.readlines():
    #     print(l)
    for cmd in cmds:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        lines = stdout.readlines()
        # for line in stderr.readlines():
        #     print(line)

        for line in lines:
            print(line)
            if result in line:
                print('Base FPS',round(find_fps(line),2))



if __name__ == "__main__":

    #print(sys.argv)
    ssh = CreateSSH(sys.argv[1],sys.argv[2],sys.argv[3])

    if ssh != None:
        print("SSH connection established successfully to {}".format(sys.argv[1]))
        try:
            base(ssh,sys.argv[4],sys.argv[5])
            print("Base case executed")
            # base(ssh,sys.argv[4],sys.argv[5])
            # print("Base case executed twice")
            ssh.close()
        except Exception as e:
            print(e)
            print("An error occured")
            sys.exit(3)
        
    else:
        print("Problem in connecting to {}".format(sys.argv[1]))
        sys.exit(2)