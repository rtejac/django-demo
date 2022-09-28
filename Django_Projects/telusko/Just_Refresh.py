from selenium import webdriver
from time import sleep
import argparse


def get_args():
    # Getting the values from the user by command line interface
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", help="IP address of the machine to listen on", type=str)
    parser.add_argument("-port", help="Port number to listen on", type=str)
    parser.add_argument("-path", help="Path to chromedriver executable",default="../../Update/chromedriver.exe", type=str)

    args = parser.parse_args()

    return args



def Get_Browser():

	browser = webdriver.Chrome(executable_path=args.path)
	try:
		browser.get("http://{}:{}/".format(args.host,args.port))
		browser.maximize_window()
	except Exception as e:
			print(e)

	return browser


def Update(browser):

	print("This is an infinetly refreshing process, This is under working of making it more effecient and close when not required")
	print("Press Ctrl+C to terminate this process")
	
	while True:
		sleep(2)
		browser.refresh()


try:
	args = get_args()
	browser = Get_Browser()
	Update(browser)
except Exception as e:
	print(e)
