cd /home/pi/python_server

spawn jarsigner git pull origin master
expect "Enter passphrase for key '/home/pi/.ssh/id_rsa':"
send "raspberry"