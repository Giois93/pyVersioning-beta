import re
import distutils.dir_util as dir_uti


#legge l'intero file in una stringa
def readFile(filePath):
	file = open(filePath, "r")
	fileStr = str(file.read())
	file.close()
	return fileStr

	
#ritorna il valore del tag passato, letto da file
def readFileByTag(tag, filePath):
	#se ho trovato il tag lo restituisco
	pattern = re.compile(tag + "(\w+)")
	results = pattern.search(readFile(filePath))
	if(results != None):
		return results.group(1)
	else:
		raise Exception("Tag not present")
	#return re.search(tag + "(\w+)", readFile(filePath)).group(1)

	
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
	fileStr = readFile(filePath)

	#try:
	#se ho trovato il tag lo sostituisco
	pattern = re.compile(tag + "(\w+)")
	if(pattern.search(fileStr) != None):
		#re.search(tag + "(\w+)", fileStr)
		#prendo le occorrenze del tag e le sostituisco con i nuovi valori	
		newFileStr = re.sub(tag + "(\w+)", tag + str(value), fileStr)
		#sovrascrivo il file
		writeFile(newFileStr, filePath, False)
	else:
	#except:
		#se non ho trovato il tag lo aggiungo
		writeFile(tag + value, filePath)


#chiede all'utente se rimuovere/sovrascrivere la cartella "dir" ed eventualmente la rimuove
def askAndRemoveDir(dir, askOverride=False):
	#verifico se la cartella esiste
	if(path.isdir(dir)):
		#chiedo all'utente se procede e sovrascrivere la cartella
		if(askOverride):
			print("La cartella {} è già presente, sovrascrivere? 0.No - 1.Sì", dir)
		else:
			print("Rimuovere la cartella {} ? 0.No - 1.Sì", dir)

		if(int(input()) == 1):
			#l'utente ha scelto di sovrascrivere
			#rimuovo la cartella
			dir_uti.remove_tree(dir)
			print("Cartella rimossa: {}", dir)
			return True
		else:
			#l'utente ha scelto di non sovrascrive
			print("Operazione annullata")
			return False
	
	return False

#chiede all'utente il nome del repository
def askRepoName():
	print("Digitare il nome del Repository:")
	return input()


#chiede all'utente il nome del branch
def askBranchName():
	print("Digitare il nome del Branch:")
	return input()


#chiede all'utente il path del repository
def askRepoDestDir():
	print("Digitare il path del Repository:")
	return input()