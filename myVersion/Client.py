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
import uti
from Server import Server

class Client:
	
	myRoot = ""
	currPath = ""
	currRepo = ""
	currBranch = ""
	server = None

	def __init__(self, server):
		self.myRoot = "C:/Users/Gioele/Desktop/myClient"
		self.currPath = self.myRoot
		self.server = server

	#mostra la lista dei repository presenti sul server
	def showRepos(self):
		print("\nList of repositories on MyVersion server")
	
		for repo in self.server.showRepos():
			print("- " + repo)
		print()


	#mostra la lista dei branch presenti sul server
	def showBranches(self):
		print("\nList of branches on Repository: ")
		for branch in self.server.showBranches(self.getCurrRepo()):
			print("- " + branch)
		print()


	#mappa il repository nella cartella del client
	def mapRepository(self, repoName):

		#ottengo il path del repository
		clientDir = path.join(self.myRoot, repoName)

		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(clientDir, True)):
			#mappo il repository nella cartella del client
			try:
				#se il repository esiste sul server, creo una cartella sul client
				#altrimenti viene generata un'eccezione
				self.server.getRepo(repoName)
				os.makedirs(clientDir)
				print("Repository mappato in:", clientDir, end = "\n\n")
				
				#setto anche il repository mappato come repository corrente di default
				self.setRepo(repoName)
			except:
				print("Impossibile completare l'operazione", end = "\n\n")


	#mappa il branch nella cartella del client
	def mapBranch(self, branchName):

		#ottengo il path del branch
		clientDir = path.join(self.myRoot, self.getCurrRepo(), branchName)

		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(clientDir, True)):
			#mappo il branch nella cartella del client
			try:
				#se il branch esiste sul server, creo il branch sul client
				#altrimenti viene generata un'eccezione
				#scarico anche la LatestVersion di default
				self.server.mapBranch(self.getCurrRepo(), branchName, clientDir)
				print("Branch mappato in: ", clientDir, end = "\n\n")
				
				#setto anche il branch mappato come branch corrente di default
				self.setBranch(branchName)
			except:
				print("Impossibile completare l'operazione", end = "\n\n")


	#rimuove la cartella del repo sul client
	def removeRepositoryMap(self, repoName):
		uti.askAndRemoveDir(path.join(self.myRoot, repoName))


	#rimuove la cartella del branch sul client
	def removeBranchMap(self, branchName):
		uti.askAndRemoveDir(path.join(self.myRoot, self.getCurrRepo(), branchName))


	#setta il repository corrente
	def setRepo(self, repoName):
		try:
			#verifico se esiste il repository altrimenti viene generata un'eccezione
			self.server.getRepo(repoName)
			#aggiorno il repository corrente
			self.setCurrRepo(repoName)
			#aggiorno la cartella di esecuzione
			repoDir = path.join(self.myRoot, repoName)
			self.setCurrPath(repoDir)
			print("> " + self.getCurrPath() + " : ")
		except:
			print("Il repository", repoName, "non esiste o non è stato mappato") 


	#setta il branch corrente
	def setBranch(self, branchName):
		try:
			#verifico se esiste il branch altrimenti viene generata un'eccezione
			self.server.getRepo(self.getCurrRepo()).getBranch(branchName)
			#aggiorno il branch corrente
			self.setCurrBranch(branchName)
			#aggiorno la cartella di esecuzione
			branchDir = path.join(self.myRoot, self.getCurrRepo(), branchName)
			self.setCurrPath(branchDir)
			print(">", self.getCurrPath(), ": ")
		except:
			print("Il branch", branchName, "non esiste o non è stato mappato")


	#setta il path di esecuzione
	def setCurrPath(self, path):
		self.currPath = path

	#setta il repository selezionato
	def setCurrRepo(self, repoName):
		self.currRepo = repoName

	#setta il branch selezionato
	def setCurrBranch(self, branchName):
		self.currBranch = branchName

	#setta il path di esecuzione
	def getCurrPath(self):
		return self.currPath

	#ritorna il repository selezionato
	def getCurrRepo(self):
		return self.currRepo

	#ritorna il branch selezionato
	def getCurrBranch(self):
		return self.currBranch


	###################################

	#esegue il comando "userInput"
	def menu(self, userInput):
	
		command = ""

		#costruisco una lista di comando e argomenti
		commandList = userInput.split()
		commandList.reverse()
		if(len(commandList) > 0):
			command = commandList.pop()
	
		#eseguo l'azione corrispondente al comando, default: "None"
		if (command == "exit")			: print("Programma terminato.", end="\n\n")
		elif (command == "repolist")	: self.showRepos()
		elif (command == "branchlist")	: self.showBranches()
		elif (command == "maprepo")		: self.mapRepository(commandList.pop()) 
		elif (command == "mapbranch")	: self.mapBranch(commandList.pop())
		elif (command == "delrepo")		: self.removeRepositoryMap(commandList.pop())
		elif (command == "delbranch")	: self.removeBranchMap(commandList.pop())
		elif (command == "setrepo")		: self.setRepo(commandList.pop())
		elif (command == "setbranch")	: self.setBranch(commandList.pop())
		else							: print("Valore non ammesso", end="\n\n")
	

		"""COMANDI:
		> exit
		> repolist
		> branchlist [repoName]
		> maprepo [repoName]
		> mapbranch [branchName]
		> delrepo [repoName]
		> delbranch [branchName]
		> setrepo [repoName]
		> setbranch [branchName]
		"""


	#esegue i comandi dell'utente fino al comando "exit"
	def runMenu(self):
		#eseguo i comandi dell'utente
		while True:
			print("> ", end="")
			userInput = input()
			self.menu(userInput)
		
			#il programma termina con il comando "exit"
			if(userInput == "exit"):
				break


	"""QUESTA DOVRA' ESSERE LA CLASSE CHE SI INTERFACCIA DIRETTAMENTE AL SERVER"""
	#TODO: comunicazione con il server e ftp