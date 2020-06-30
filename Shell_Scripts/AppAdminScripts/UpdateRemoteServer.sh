cd /home/pi/python_server

spawn jarsigner git add .
expect "Enter passphrase for key '/home/pi/.ssh/id_rsa':"
send "raspberry"

spawn jarsigner git commit -m "update from Rpi3"
expect "Enter passphrase for key '/home/pi/.ssh/id_rsa':"
send "raspberry"

spawn jarsigner git push origin master
expect "Enter passphrase for key '/home/pi/.ssh/id_rsa':"
send "raspberry"