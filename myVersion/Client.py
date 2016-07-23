"""TODO
Client v0.1.0
- cartella root
- lista dei repo
- lista dei branch
- map di un repository (deve limitarsi a creare la cartella)
- map di un branch (deve limitarsi a creare la cartella)
- rimozione map di un repository
- rimozione map di un branch
- settare/selezionare un repo (serve la classe Repository)
- settare/selezionare un branch (serve la classe Branch)
- getlatest (devo scaricare solo il backup non tutto il branch/repo)
- checkout di file (segnare nel file .txt i file checkati out)
- checkin (copia dei file in pending nella cartella pending_changes temporanea nel branch)
- undo (rimozione di record dal file)
- compare (richiede una copia temporanea del file dal server)
- takeServerVersion
- takeLocalVersion

"""

import os
import os.path as path
import distutils.dir_util as dir_uti
import uti
import Server


#mostra la lista dei repository presenti sul server
def showRepos():
	print("\nList of repositories on MyVersion server")
	
	for repo in Server.showRepos():
		print("- " + repo)
	print()


#mostra la lista dei branch presenti sul server
def showBranches(repoName):
	print("\nList of branches on Repository: {}", repoName)
	for branch in Server.showBranches(repoName):
		print("- " + branch)
	print()


#mappa il repository nella cartella del client
def mapRepository(repoName):

	#ottengo il path del repository
	clientDir = path.join(myRoot, repoName)

	#chiedo all'utente se sovrascrivere la cartella
	if(uti.askAndRemoveDir(clientDir, True)):
		#mappo il repository nella cartella del client
		try:
			Server.mapRepository(repoName, clientDir)
			print("Repository mappato in:", clientDir, end = "\n\n")
		except:
			print("Impossibile completare l'operazione", end = "\n\n")


#mappa il branch nella cartella del client
def mapBranch(repoName, branchName):

	#ottengo il path del branch
	clientDir = path.join(myRoot, repoName, branchName)

	#chiedo all'utente se sovrascrivere la cartella
	if(uti.askAndRemoveDir(clientDir, True)):
		#mappo il branch nella cartella del client
		try:
			Server.mapBranch(repoName, branchName, clientDir)
			print("Branch mappato in: ", clientDir, end = "\n\n")
		except:
			print("Impossibile completare l'operazione", end = "\n\n")

#rimuove la cartella del repo sul client
def removeRepositoryMap(repoName):
	uti.askAndRemoveDir(path.join(root, repoName))


#rimuove la cartella del branch sul client
def removeBranchMap(repoName, branchName):
	uti.askAndRemoveDir(path.join(root, repoName, branchName))


#
def setRepo(repoName):
	try:
		currRepo = getRepo(repoName) #qui va la getrepo del client
	except:
		print("Il repository", repoName, "non esiste o non è stato mappato") 


#
def setBranch(branchName):
	try:
		currBranch = getBranch(branchName) #qui va la getBranch del client
	except:
		print("Il branch", branchName, "non esiste o non è stato mappato")

###################################

def menuMyVersion():
	while True:
		print("> ", end="")
		userInput = input()
		menu(userInput)

		if(userInput == "exit"):
			break


def menu(userInput):
	
	command = ""

	#costruisco una lista di comando e argomenti
	commandList = userInput.split()
	commandList.reverse()
	if(len(commandList) > 0):
		command = commandList.pop()
	
	#eseguo l'azione corrispondente al comando, default: "None"
	if (command == "exit")			: print("Programma terminato.", end="\n\n")
	elif (command == "repolist")	: showRepos()
	elif (command == "branchlist")	: showBranches(commandList.pop())
	elif (command == "maprepo")		: mapRepository(commandList.pop()) 
	elif (command == "mapbranch")	: mapBranch(commandList.pop(), commandList.pop())
	elif (command == "delrepo")		: removeRepositoryMap(commandList.pop())
	elif (command == "delbranch")	: removeBranchMap(commandList.pop(), commandList.pop())
	elif (command == "setrepo")		: setRepo(commandList.pop())
	elif (command == "setbranch")	: setBranch(commandList.pop())
	else							: print("Valore non ammesso", end="\n\n")
	

	"""COMANDI:
	> exit
	> repolist
	> branchlist [repoName]
	> maprepo [repoName]
	> mapbranch [repoName] [branchName]
	> delrepo [repoName]
	> delbranch [repoName] [branchName]
	> setrepo [repoName]
	> setbranch [branchName]
	"""




#### MAIN ####
myRoot = "C:/Users/Gioele/Desktop/myClient"
#if(path.exists(root)):
#	dir_uti.remove_tree(root)
#my = MyVersion(root)

currRepo = None
currBranch = None

menuMyVersion()

"""QUESTA DOVRA' ESSERE LA CLASSE CHE SI INTERFACCIA DIRETTAMENTE AL SERVER"""
#TODO: comunicazione con il server e ftp