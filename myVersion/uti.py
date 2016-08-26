import os
import os.path as path
import shutil
import re
import difflib
import datetime
import socket               

#costanti
LOCAL_VERSION_FILE	= "local.txt"
BRANCH_FILE			= "branch.txt"
CHANGESET_FILE		= "changeset.txt"
LAST_RUN_FILE		= "lastrun.txt"

###utilities lettura e scrittura su file###

def readFile(filePath):
	"""legge l'intero file in una stringa"""

	try:
		file = open(filePath, "r")
		fileStr = str(file.read())
		file.close()
	except:
		raise
	
	return fileStr

	
def readFileByTag(tag, filePath):
	"""ritorna il valore del tag passato, letto da file"""

	#se ho trovato il tag lo restituisco
	try:
		return re.findall("{}=(.*)".format(tag), readFile(filePath))
	except:
		raise	


def writeFile(string, filePath, append=True):
	"""scrive sul file in append o in sovrascrittura"""

	#apro il file
	if (append): 
		file = open(filePath, "a")
	else: 
		file = open(filePath, "w")

	#scrivo la stringa nel file (cancello righe bianche)
	print(string, file=file)

	#chiudo il file
	file.close()


def writeFileByTag(tag, value, filePath):
	"""cambia il valore al tag passato, scritto su file"""

	#apro il file
	try:
		fileStr = readFile(filePath)

		#cerco il tag
		results = re.findall("{}=(.*)".format(tag), fileStr)

		if (len(results) == 0):
			#se non ho trovato il tag lo aggiungo
			writeFile("{}={}".format(tag, str(value)), filePath)
		else:
			#se ho trovato il tag lo sostituisco
			#prendo tutte le occorrenze del tag e le sostituisco con i nuovi valori	
			newFileStr = re.sub("{}=(.*)".format(tag), "{}={}".format(tag, str(value)), fileStr)

			#sovrascrivo il file
			writeFile(newFileStr, filePath, False)
	except:
		#se non ho trovato il tag lo aggiungo
		writeFile("{}={}".format(tag, str(value)), filePath)


def removeByTag(tag, filePath):
	"""cancella la riga contenente il tag dal file filePath"""

	newFileStr = re.sub("{}=(.*)".format(tag), "", readFile(filePath))
	writeFile(newFileStr, filePath, False)


def removeByTagAndVal(tag, value, filePath):
	"""cancella la riga dal file "filePath" """
	
	newFileStr = re.sub("{}=(.*){}(.*)\n".format(tag, value), "", readFile(filePath))
	writeFile(newFileStr, filePath, False)


###utilities lettura e scrittura tramite socket###

def sendBySocket(dest, port, toSendPath):
	""" invia tramite socket il file "toSendPath" o i file contenuti nella directory se "toSendPath" è una directory"""
	
	#creo una socket con il ricevente
	sock = socket.socket() 
	sock.connect(dest, port)

	#invio il file o directory
	if (path.isdir(toSendPath)):
		sendDirBySocket(sock, toSendPath)
	elif (path.isfile(toSendPath)):
		sendFileBySocket(sock, toSendPath)
	else:
		raise Exception("Path non valido")

	#chiudo la socket
	sock.send("pyVCLOSE")
	sock.shutdown(socket.SHUT_WR)
	sock.close()


def sendDirBySocket(sock, dirPath):
	"""invia tutti i file in una directory via socket """

	for dir, dirNames, files in os.walk(dirPath):
		for fileName in files:
			sendFileBySocket(sock, path.join(dir, fileName))


def sendFileBySocket(sock, filePath):#TODO: il path non può essere assoluto, deve essere relativo
	"""invia il file "filePath" tramite la socket "sock" """
	
	#invio il path del file da scrivere
	sock.send(filePath)
	#apro il file da copiare
	file = open(filePath,"rb")

	#invio il file
	while (True):
		line = file.read(1024)
		if (not line): 
			break
		sock.send(line)

	file.close()


def receiveBySocket(sender, port):
	"""riceve e scrive il file "filePath" tramite la socket "sock" """

	#creo una socket con il mittente e attedo
	sock = socket.socket()
	sock.bind(sender, port)
	sock.listen(5)

	#creo la connesione
	connection, addr = sock.accept()

	while (True):

		#acquisisco lo stream 
		msg = connection.recv(1024)
		
		#se ricevo un comando di chiusura interrompo la scrittura
		if (data == "pyVCLOSE"):
			break
		else:
			filePath = msg #TODO: il path non può essere assoluto, deve essere relativo

		#apro il file da scrivere
		file = open(filePath, "wb") #TODO prima devo assicurarmi che esista il basepath delle cartelle

		#scrivo il file
		while (True):
			line = connection.recv(1024)
			if not line:
				break

			file.write(line)

		file.close()

	sock.shutdown(socket.SHUT_RD)
	sock.close()
	connection.close()


###utilities per formulare richieste###

def askAndRemoveDir(dir, ask=True, askOverride=False):
	"""chiede all'utente se rimuovere/sovrascrivere la cartella "dir" ed eventualmente la rimuove"""

	#verifico se la cartella esiste
	if (path.isdir(dir)):
		if (ask == False):
			shutil.rmtree(dir)
		else:
			#chiedo all'utente se procede e sovrascrivere la cartella
			while True:
				if (askOverride):
					msg = "La cartella {} è già presente, sovrascrivere?".format(getPathForPrint(dir))
				else:
					msg = "Rimuovere la cartella {}?".format(getPathForPrint(dir))
				
				if (askQuestion(msg)):
					#l'utente ha scelto di sovrascrivere
					#rimuovo la cartella
					shutil.rmtree(dir)
					print("Cartella rimossa:", getPathForPrint(dir), end = "\n\n")
					return True
				else:
					#l'utente ha scelto di non sovrascrive
					print("Operazione annullata", end = "\n\n")
					return False
	return True



def askQuestion(question):
	"""rivolge la domanda "question" all'utente, attende una risposta 
	"s": ritorna True - "n": ritorna False - altrimenti ripete la domanda"""

	while True:
		try:
			print(question, "(s/n)")
			userInput = input()
			if ((userInput == "s") | (userInput == "S")):
				return True
			elif ((userInput == "n") | (userInput == "N")):
				return False
		finally:
			print()


###utilies varie###

def listDir(dir):
	"""ritorna tutti i file e sottocartelle della dir selezionata"""
		
	#creo la lista di tutti i file e sottocartelle
	list = ()
	for root, dirs, files in os.walk(dir):
		for fileName in files:
			list += (path.join(root, fileName).replace(dir, ""), )
		for dirName in dirs:
			list += (path.join(root, dirName).replace(dir, ""), )
		
	return list


def getPathForPrint(path):
	"""formatta un path per la stampa a video"""

	return path.replace("/", "\\")


def getDate(dateStr):
	"""ritorna un oggetto data da una stringa "dd/mm/YY HH:MM:SS" """

	[day,month,year] = map(int, dateStr.split()[0].split('/'))
	return datetime.date(year, month, day)


def diff(file1, file2):
	"""effettua un diff di due file"""

	return difflib.ndiff(open(file1).readlines(), open(file2).readlines())

	#ottengo le differenze frai due file
	#diff = difflib.ndiff(open(file1).readlines(), open(file2).readlines())
	#
	##stampo tutte le differenze con il numero di riga corrispondente
	#line = 0
	#changes = ()
	#for change in diff:
	#	++line
	#	if (change.startswith("+") or change.startswith("-")):
	#		changes += ("{}: {}".format(str(line), change), )
	#
	#return changes

