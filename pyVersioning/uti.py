import os
import os.path as path
import shutil
import re
import difflib
import datetime

def readFile(filePath):
	"""legge l'intero file in una stringa"""

	try:
		file = open(filePath, "r", errors="ignore")
		fileStr = str(file.read())
		file.close()
	except:
		raise
	
	return fileStr

	
def readFileByTag(tag, filePath):
	"""ritorna i valori del tag passato, letto da file"""

	#se ho trovato il tag lo restituisco
	try:
		return re.findall("{}=(.*)".format(tag), readFile(filePath))
	except:
		raise	


def writeFile(string, filePath, append=True):
	"""scrive sul file in append o in sovrascrittura"""

	#apro il file
	if (append): 
		file = open(filePath, "a", errors="ignore")
	else: 
		file = open(filePath, "w", errors="ignore")

	#scrivo la stringa nel file
	print(string, file=file)

	#chiudo il file
	file.close()

	#trimFile(filePath) #rimossa - troppo lenta


def writeFileByTag(tag, value, filePath, add=False):
	"""scrive/cambia il valore al tag passato, scritto su file"""

	#rimuovo il tag già presente 
	if (add==False):
		removeByTag(tag, filePath)

	#aggiungo il tag
	writeFile("{}={}".format(tag, str(value)), filePath)



def removeByTag(tag, filePath):
	"""cancella le righe contenenti il tag dal file filePath"""

	try:
		newFileStr = re.sub("{}=(.*)".format(tag), "", readFile(filePath))
		writeFile(newFileStr, filePath, False)
	except:
		pass


def removeByTagAndVal(tag, value, filePath):
	"""cancella la riga dal file "filePath" """

	try:
		newFileStr = re.sub("{}=(.*){}(.*)".format(tag, value), "", readFile(filePath))
		writeFile(newFileStr, filePath, False)
	except:
		pass

	
def trimFile(filePath):
	"""elimina righe vuote dal file"""

	writeFile(re.sub("\n\Z", "", re.sub("\A\n", "", re.sub("(\n)+", "\n", readFile(filePath)))), filePath)


def askAndRemoveDir(dirPath, askOverride=False):
	"""chiede all'utente se rimuovere/sovrascrivere la cartella "dir" ed eventualmente la rimuove"""

	#verifico se la cartella esiste
	if (path.isdir(dirPath)):
		
		#chiedo all'utente se procede e sovrascrivere la cartella
		while True:
			if (askOverride):
				msg = "La cartella {} è già presente, sovrascrivere?".format(getPathForPrint(dirPath))
			else:
				msg = "Rimuovere la cartella {}?".format(getPathForPrint(dirPath))
				
			if (askQuestion(msg)):
				#l'utente ha scelto di sovrascrivere
				#rimuovo la cartella
				shutil.rmtree(dirPath)
				print("Cartella rimossa:", getPathForPrint(dirPath), end ="\n\n")
				return True
			else:
				#l'utente ha scelto di non sovrascrive
				print("Operazione annullata", end = "\n\n")
				return False

	#se la cartella non esiste non serve rimuoverla
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


def listDir(dirPath):
	"""ritorna tutti i file e sottocartelle della dir selezionata"""
		
	#creo la lista di tutti i file e sottocartelle
	elemsList = []
	for root, dirs, files in os.walk(dirPath):
		for fileName in files:
			elemsList.append(path.join(root, fileName))
		for dirName in dirs:
			elemsList.append(path.join(root, dirName))
		
	return elemsList


def getPathForPrint(pathToPrint):
	"""formatta un path per la stampa a video"""

	return pathToPrint.replace("/", "\\")


def getDate(dateStr):
	"""ritorna un oggetto data da una stringa "dd/mm/YY HH:MM:SS" """

	[day,month,year] = map(int, dateStr.split()[0].split('/'))
	return datetime.date(year, month, day)


def diff(file1, file2):
	"""effettua un diff di due file"""

	return difflib.ndiff(open(file1, errors="ignore").readlines(), open(file2, errors="ignore").readlines())
