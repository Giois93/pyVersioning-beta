import os.path as path
import shutil
import re
import difflib
import datetime

#costanti
PENDING_FILE	= "pending.txt"
BRANCH_FILE		= "branch.txt"
CHANGESET_FILE	= "changeset.txt"
LAST_RUN_FILE	= "lastrun.txt"


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


def writeFile(string, filePath, append = True):
	"""scrive sul file in append o in sovrascrittura"""

	#apro il file
	if (append): 
		file = open(filePath, "a")
	else: 
		file = open(filePath, "w")
		
	#scrivo la stringa nel file
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


def getPathForPrint(path):
	"""formatta un path per la stampa a video"""

	return path.replace("/", "\\")


def diff(file1, file2):
	"""effettua un diff di due file"""

	#ottengo le differenze frai due file
	diff = difflib.ndiff(open(file1).readlines(), open(file2).readlines())
	
	#stampo tutte le differenze con il numero di riga corrispondente
	line = 0
	changes = ()
	for change in diff:
		++line
		if (change.startswith("+") or change.startswith("-")):
			changes += ("{}: {}".format(str(line), change), )

	return changes


def getDate(dateStr):
	"""ritorna un oggetto data da una stringa "dd/mm/YY HH:MM:SS" """

	[day,month,year] = map(int, dateStr.split()[0].split('/'))
	return datetime.date(year, month, day)
