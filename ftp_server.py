import commands
import socket
import time
import sys
import os


#------------------------------------------------------------------------------
def recvAll(sock, numBytes):
#------------------------------------------------------------------------------

        # The buffer
        recvBuff = ""

        # The temporary buffer
        tmpBuff = ""

        # Keep receiving till all is received
        while len(recvBuff) < numBytes:

                # Attempt to receive bytes
                tmpBuff =  sock.recv(numBytes)

                # The other side has closed the socket
                if not tmpBuff:
                        break

                # Add the received bytes to the buffer
                recvBuff += tmpBuff

        return recvBuff
#------------------------------------------------------------------------------

# check if there are 2 arguments passed, if not then no port-number implied, exit
if len(sys.argv) < 2:
	sys.exit("MISSING ARGUMENTS: " + sys.argv[0] + " <PORT NUMBER>")

serverPort = int(sys.argv[1])
serverAddress = "localhost"
recvSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recvSock.bind(('', serverPort))
recvSock.listen(1)


# loop until control connection becomes available	
print "--   WAITING FOR CONNECTIONS   --"

control_socket, addr = recvSock.accept()

print "-- CONTROL CONNECTION ACCEPTED --"

# connected to control connection
# determine what command client wants

while addr:
	# get the command value from the client
	commandSizeBuff = ""
	command = ""
	commandSizeBuff = recvAll(control_socket, 10)
	command = recvAll(control_socket, int(commandSizeBuff))

	# if the command is 'get', send file to client
	if "get" in command:
		# get the ephermal port-number from the client
		ephPortSizeBuff = ""
		ephermal_port = ""
		ephPortSizeBuff = recvAll(control_socket, 10)
		ephermal_port = recvAll(control_socket, int(ephPortSizeBuff))

		# get the filename from the command
		commandList = command.split()
		filename = "".join(commandList[1:])

		# delay to allow client to open socket before we connect
		time.sleep(0.5)

		# open a temporary data socket for file transfer
		dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		dataSocket.connect((serverAddress, int(ephermal_port)))
	
		# check if file is in the directory	
		if (not(os.path.isfile(filename))):
		# { 
			# send a D.N.E. signal to the client
			# signifying that the file is not in the directory
			contents =  "D.N.E" # Does Not Exist
			dataSizeStr = str(len(contents))
			
			dataSizeStr = str(len(contents))
			
			while len(dataSizeStr) < 10:
				dataSizeStr = "0" + dataSizeStr	
				
			contents = dataSizeStr + contents
			numSent = 0

			while len(contents) > numSent:
				numSent += dataSocket.send(contents[numSent:])	

			print "FAILURE"				
		# }
		# if the file does exist, create a data socket
		else:
		# {
			# read contents of the file
			f = open(filename, 'rb')	
			numSent = 0

			contents = f.read()
			dataSizeStr = str(len(contents))
			
			while len(dataSizeStr) < 10:
				dataSizeStr = "0" + dataSizeStr	
				
			contents = dataSizeStr + contents

			while len(contents) > numSent:
				numSent += dataSocket.send(contents[numSent:])
				
			f.close()

			print "SUCCESS"
		# }
	
		dataSocket.close()
	# }	
	# receive data from client and save it to directory
	elif "put" in command:
		# receive ephermal port-number from the client
		ephPortSizeBuff = ""
		ephermal_port = ""
		ephPortSizeBuff = recvAll(control_socket, 10)
		ephermal_port = recvAll(control_socket, int(ephPortSizeBuff))

		# parse filename from the command
		commandList = command.split()
		filename = "".join(commandList[1:])

		dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		dataSocket.bind(('', int(ephermal_port)))
		dataSocket.listen(1)

		dataSocketOne, addr = dataSocket.accept()
		contentSizeBuff = ""
		contentData = ""

		contentSizeBuff = recvAll(dataSocketOne, 10)
		contentData = recvAll(dataSocketOne, int(contentSizeBuff))			
		
		# file not found in the client
		if "D.N.E." in contentData:
			print "FAILURE"
		else:
			f = open(filename, 'wb')
			f.write(contentData)
			f.close()
			print "SUCCESS"
		dataSocket.close()
	
	elif "lls" in command:
		pass

	elif "ls" in command:
		ephPortSizeBuff = ""
		ephermal_port = ""
		ephPortSizeBuff = recvAll(control_socket, 10)
		ephermal_port = recvAll(control_socket, int(ephPortSizeBuff))


		time.sleep(0.5)

		dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		dataSocket.connect(("localhost", int(ephermal_port)))
		
		contents = ""
		numSent = 0
	
		for line in commands.getstatusoutput('ls -l'):
			contents = contents + str(line)	
		
		dataSizeStr = str(len(contents))
			
		while len(dataSizeStr) < 10:
			dataSizeStr = "0" + dataSizeStr	
				
		contents = dataSizeStr + contents

		while len(contents) > numSent:
			numSent += dataSocket.send(contents[numSent:])				

		print "SUCCESS"

		dataSocket.close()		
	
	elif "quit" in command:
		control_socket.close()
		recvSock.close()
		break


	
