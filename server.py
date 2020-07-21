import subprocess 
with open("output.txt","w+") as output:
	subprocess.call(["python3", "./Server_Pyjnius.py"], stdout=output);
