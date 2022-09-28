from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep



def Get_Browser():

	
	#print("Running the browser : {}".format(os.getpid()))

	browser = webdriver.Chrome(executable_path="C:\\Users\\rtejac\\Downloads\\chromedriver_win32_1\\chromedriver.exe")
	try:
		browser.get("http://127.0.0.1:8000/")
		#browser.maximize_window()
	except Exception as e:
			print(e)

	return browser




def Update(browser):

	i = 0
	
	c_prev = None

	#print("Updating the browser by thread : {}".format(os.getpid()))

	while True:

		f = open("../../Update/Status.txt",'r')
		d = f.readlines()

		c = int(d[0].split(":")[1])
		t = int(d[1].split(":")[1])
		print(c,t)

		#sleep(1)

		if c == t:
			sleep(5)
			browser.close()
			break


browser = Get_Browser()
Update(browser)