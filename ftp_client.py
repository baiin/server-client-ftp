import commands
import socket
import time
import sys
import os


if len(sys.argv) < 3:
	sys.exit("MISSING ARGUMENTS: " + sys.argv[0] + " <server_machine> <server_port>")

serverAddr = sys.argv[1]
serverPort = int(sys.argv[2])
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connSock.connect((serverAddr, serverPort))

#------------------------------------------------------------------------------
def recvAll(sock, numBytes):			
#------------------------------------------------------------------------------
	recvBuff = ""
	tmpBuff = ""
	
	while len(recvBuff) < numBytes:
		tmpBuff = sock.recv(numBytes)

		if not tmpBuff:
			break

		recvBuff += tmpBuff

	return recvBuff
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
def getEphermalPort(sock):
#------------------------------------------------------------------------------
	ephermal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ephermal_socket.bind(('', 0))
	ephermal_socket.listen(1)
	ephermal_port = str(ephermal_socket.getsockname()[1])
	numSent = 0
	
	# send the ephermal port number to the server
	dataSizeStr = str(len(ephermal_port))

	while len(dataSizeStr) < 10:
		dataSizeStr = "0" + dataSizeStr

	eport = int(ephermal_port)
	ephermal_port = dataSizeStr + ephermal_port

	while len(ephermal_port) > numSent:
		numSent += sock.send(ephermal_port[numSent:])
	
	ephermal_socket.close()

	return eport
#------------------------------------------------------------------------------


while True:
	# display "ftp>"
	# new command to send
	command = raw_input("ftp> ")

	# if valid command
	if command:
		numSent = 0

		dataSizeStr = str(len(command))

		while len(dataSizeStr) < 10:
			dataSizeStr = "0" + dataSizeStr

		command = dataSizeStr + command
	
		# send the command through the control connection
		while len(command) > numSent:
			numSent += connSock.send(command[numSent:])

		# fetch file from the server
		if "get" in command:
		# {
			# get an ephermal port number
			eport = getEphermalPort(connSock)

			# get filename
			commandList = command.split()
			filename = "".join(commandList[1:])

			dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			dataSocket.bind(('', eport))
			dataSocket.listen(1)
			dataSocketOne, addr = dataSocket.accept()	

			contentSizeBuff = ""
			contentData = ""

			contentSizeBuff = recvAll(dataSocketOne, 10)
			contentData = recvAll(dataSocketOne, int(contentSizeBuff))

			if "D.N.E" in contentData: # file does not exist in server
			# {
				print "FILE NOT IN SERVER"	
			# }
			else:
			# {
				# store the contents into the file
				f = open(filename, 'wb')
				f.write(contentData)
				f.close()				
			# }
		
			dataSocket.close()
		# }
		elif "put" in command:
		# {
			# create an ephermal port number for the data transfer
			eport = getEphermalPort(connSock)

			# get filename
			commandList = command.split()
			filename = "".join(commandList[1:])

			# check if file is in the directory
			if (not(os.path.isfile(filename))):
			# {
				time.sleep(0.5)
				dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				dataSocket.connect((serverAddr, int(eport)))

				contents = "D.N.E."
	
				dataSizeStr = str(len(contents))
			
				while len(dataSizeStr) < 10:
					dataSizeStr = "0" + dataSizeStr

				contents = dataSizeStr + contents
				numSent = 0

				while len(contents) > numSent:
					numSent += dataSocket.send(contents[numSent:])
		
				print "FILE NOT IN CLIENT"
			# }
			# if the file does exist, create a data socket
			else:
			# {
				print "EPHERMAL PORT: " , eport
				time.sleep(0.5)
				dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				dataSocket.connect((serverAddr, int(eport)))
				
				# read contents of the file
				f = open(filename, 'rb')
				numSent = 0
				
				contents = f.read()
				dataSizeStr = str(len(contents))
			
				while len(dataSizeStr) < 10:
					dataSizeStr = "0" + dataSizeStr

				contents = dataSizeStr + contents

				print "TRANSFERRING FILE: ", filename
		
				while len(contents) > numSent:
					numSent += dataSocket.send(contents[numSent:])
		
				f.close()
			# }
		
			dataSocket.close()
		# }
		elif "lls" in command:
			print "CLIENT FILES:"
			for line in commands.getstatusoutput('ls -l'):
				print line
		
		elif "ls" in command:
			# get an ephermal port number
			eport = getEphermalPort(connSock)

			dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			dataSocket.bind(('', eport))
			dataSocket.listen(1)
			dataSocketOne, addr = dataSocket.accept()	

			contentSizeBuff = ""
			contentData = ""

			contentSizeBuff = recvAll(dataSocketOne, 10)
			contentData = recvAll(dataSocketOne, int(contentSizeBuff))

			print "SERVER FILES:"
			print contentData
			dataSocket.close()		   

		elif "quit" in command:
			connSock.close()
			break
	else:
		break

