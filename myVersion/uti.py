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


def askAndRemoveDir(dir, askOverride=False):
	"""chiede all'utente se rimuovere/sovrascrivere la cartella "dir" ed eventualmente la rimuove"""

	#verifico se la cartella esiste
	if (path.isdir(dir)):
		
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


def listDir(dir):
	"""ritorna tutti i file e sottocartelle della dir selezionata"""
		
	#creo la lista di tutti i file e sottocartelle
	list = []
	for root, dirs, files in os.walk(dir):
		for fileName in files:
			list.append(path.join(root, fileName))
		for dirName in dirs:
			list.append(path.join(root, dirName))
		
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

	return difflib.ndiff(open(file1, errors="ignore").readlines(), open(file2, errors="ignore").readlines())

	#ottengo le differenze frai due file
	#diff = difflib.ndiff(open(file1, errors="ignore").readlines(), open(file2, errors="ignore").readlines())
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

