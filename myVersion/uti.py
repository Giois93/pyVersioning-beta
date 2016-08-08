import os.path as path
import shutil
import re

"""TODO: sostituire le .compile() e .search() con .findall() es. re.findall(r"\w+ly", text)
https://docs.python.org/2/library/re.html#finding-all-adverbs
"""

#costanti
PENDING_FILE	= "pending.txt"
BRANCH_FILE		= "branch.txt"
CHANGESET_FILE	= "changeset.txt"
LAST_RUN_FILE	= "lastrun.txt"


#legge l'intero file in una stringa
def readFile(filePath):
	try:
		file = open(filePath, "r")
		fileStr = str(file.read())
		file.close()
	except:
		raise
	
	return fileStr

	
#ritorna il valore del tag passato, letto da file
def readFileByTag(tag, filePath):
	#se ho trovato il tag lo restituisco
	try:
		return re.findall("{}=(.+)".format(tag), readFile(filePath))
	except:
		raise	


#scrive il file in append o in sovrascrittura
def writeFile(string, filePath, append = True):
	#apro il file
	if(append): 
		file = open(filePath, "a")
	else: 
		file = open(filePath, "w")
		
	#scrivo la stringa nel file
	print(string, file=file)

	#chiudo il file
	file.close()


#cambia il valore al tag passato, scritto su file
def writeFileByTag(tag, value, filePath):

	#apro il file
	try:
		fileStr = readFile(filePath)

		#cerco il tag
		results = re.findall("{}=(\w+)".format(tag), fileStr)

		if(len(results) == 0):
			#se non ho trovato il tag lo aggiungo
			writeFile("{}={}".format(tag, str(value)), filePath)
		else:
			#se ho trovato il tag lo sostituisco
			#prendo tutte le occorrenze del tag e le sostituisco con i nuovi valori	
			newFileStr = re.sub("{}=(\w+)".format(tag), "{}={}".format(tag, str(value)), fileStr)

			#sovrascrivo il file
			writeFile(newFileStr, filePath, False)
	except:
		#se non ho trovato il tag lo aggiungo
		writeFile("{}={}".format(tag, str(value)), filePath)


#chiede all'utente se rimuovere/sovrascrivere la cartella "dir" ed eventualmente la rimuove
def askAndRemoveDir(dir, ask=True, askOverride=False):

	#verifico se la cartella esiste
	if(path.isdir(dir)):
		if(ask == False):
			shutil.rmtree(dir)
		else:
			#chiedo all'utente se procede e sovrascrivere la cartella
			while True:
				if(askOverride):
					msg = "La cartella {} è già presente, sovrascrivere?".format(getPathForPrint(dir))
				else:
					msg = "Rimuovere la cartella {}?".format(getPathForPrint(dir))
				
				if(askQuestion(msg)):
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


#rivolge la domanda "question" all'utente, attende una risposta 
#"s": ritorna True - "n": ritorna False - altrimenti ripete la domanda
def askQuestion(question):
	while True:
		print(question, "(s/n)")
		userInput = input()
		if(userInput == "s"):
			return True
		elif(userInput == "n"):
			return False


def getPathForPrint(path):
	return path.replace("/", "\\")