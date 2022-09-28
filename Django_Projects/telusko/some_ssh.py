import paramiko


def CreateSSH(args):
    
    global ssh

    ssh = None
    i = 1

    while i<10:
        try:
            ssh = paramiko.SSHClient()  # "ssh" Created
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Addedd to Keys if missing
            ssh.load_system_host_keys()
            ssh.connect(host, port=port, username=username, password=password)#, banner_timeout=200)  # Logging into host
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




host = '10.99.114.167'
username = 'wlc'
password = 'intel123'
port = 22

ssh = CreateSSH()

_,o,_ = ssh.exec_command('hostname')
print(o.readlines())