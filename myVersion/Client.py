import os
import os.path as path
import time
import datetime
import shutil
import uti
from uti import PENDING_FILE
from uti import CHANGESET_FILE
from Server import Server

class Client:
	
	myRoot = ""
	currPath = ""
	currRepo = ""
	currBranch = ""
	server = None

	def __init__(self, server):
		self.myRoot = "C:/myClient"
		self.currPath = self.myRoot
		self.server = server


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


	#esegue il comando "userInput"
	def menu(self, userInput):

		#costruisco una lista di comando e argomenti
		commandList = userInput.split()
		commandList.reverse()

		#eseguo il comando
		try:
			command = commandList.pop()
		
			if (command == "exit"): 
				print("Programma terminato.", end="\n\n")

			elif (command == "repolist"): 
				if(len(commandList) != 0):
					raise Exception("Parametri errati")
				self.showRepos() 
			
			elif (command == "branchlist"): 
				if(len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				self.showBranches()

			elif (command == "maprepo"): 
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				self.mapRepository(commandList.pop()) 

			elif (command == "mapbranch"): 
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				self.mapBranch(commandList.pop())

			elif (command == "delrepo"): 
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				self.removeRepositoryMap(commandList.pop())

			elif (command == "delbranch"):
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				self.removeBranchMap(commandList.pop())

			elif (command == "setrepo"):
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				self.setRepo(commandList.pop())

			elif (command == "setbranch"): 
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				self.setBranch(commandList.pop())

			elif (command == "history"): 
				if(len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.showHistory()

			elif (command == "getlatest"): 
				if(len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.getLatestVersion() 

			elif (command == "getspecific"):
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.getSpecificVersion(int(commandList.pop()))

			elif (command == "pending"): 
				if(len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.printPendingChanges()

			elif (command == "commit"): 
				if(len(commandList) != 2):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.commit(commandList.pop(), commandList.pop())

			elif (command == "commitall"): 
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.commitAll(commandList.pop())

			elif (command == "undo"): 
				if(len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.undoFile(commandList.pop())

			elif (command == "undoall"): 
				if(len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.undoAll()

			elif (command == "help"): 
				if(len(commandList) != 0):
					raise Exception("Parametri errati")
				self.printHelp()

			else: 
				print("Valore non ammesso", end="\n\n")

		except Exception as ex:
			print("Errore:", ex)


	#mostra la lista dei repository presenti sul server
	def showRepos(self):
		print("\nRepositories sul server di MyVersion")
	
		for repo in self.server.showRepos():
			print("- " + repo)
		print()


	#mostra la lista dei branch presenti sul server
	def showBranches(self):
		print("\nBranches sul repository " + self.getCurrRepo() + ": ")
		for branch in self.server.showBranches(self.getCurrRepo()):
			print("- " + branch)
		print()


	#mostra la lista dei changeset presenti in questo branch
	def showHistory(self):
		print("\nChangeset del branch " + self.getCurrBranch() + ": ")
		for changeSet in self.getCurrBranchOnServer().getChangesetList():
			print("- " + changeSet)
		print()


	#mappa il repository nella cartella del client
	def mapRepository(self, repoName):

		#ottengo il path del repository
		clientDir = path.join(self.myRoot, repoName)

		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(clientDir, askOverride=True)):
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
		if(uti.askAndRemoveDir(clientDir, askOverride=True)):
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
			self.setCurrBranch("")
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
			self.getCurrRepoOnServer().getBranch(branchName)
			#aggiorno il branch corrente
			self.setCurrBranch(branchName)
			#aggiorno la cartella di esecuzione
			branchDir = path.join(self.myRoot, self.getCurrRepo(), branchName)
			self.setCurrPath(branchDir)
			print(">", self.getCurrPath(), ": ")
		except:
			print("Il branch", branchName, "non esiste o non è stato mappato")


	#scarica l'ultima versione e la copia nella cartella del branch
	def getLatestVersion(self):
		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(self.getCurrPath(), ask=False)):
			#prendo la latestVersion da Repository e Branch corrente
			self.getCurrBranchOnServer().getLatestVersion(self.getCurrPath())
			print("Versione locale aggiornata con successo", end="\n\n")
			uti.writeFile("last_changeset" + str(self.getCurrBranchOnServer().getLastChangesetNum()), self.getPendingFile())

	
	#scarica una versione specifica (identificata dal numero di changeset) e la copia nella cartella del branch
	def getSpecificVersion(self, changesetNum):
		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(self.getCurrPath(), ask=False)):
			#prendo la versione specifica da Repository e Branch corrente con il numero di changeset passato
			self.getCurrBranchOnServer().getSpecificVersion(changesetNum, self.getCurrPath())
			uti.writeFile("last_changeset" + str(changesetNum), self.getPendingFile())


	#stampa una lista dei file modificati in locale con data di ultima modifica
	def printPendingChanges(self):
		#scorro tutti i file nella lista dei pending
		pendingList = self.getPendingChanges()
		if(len(pendingList) == 0):
			print("Nessun file in modifica.", end="\n\n")
		else:
			for file in pendingList:
				#prendo la data di ultima modifica del file
				date = datetime.datetime.fromtimestamp(path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
				#stampo file e data ultima modifica
				print(file.replace(self.getCurrPath(), ""), date)
			print()

	
	#ritorna una lista dei file modificati in locale
	def getPendingChanges(self):
		#rimuovo il file dei pending vecchio
		if(path.isfile(self.getPendingFile())):
			try:
				#memorizzo il changeset originale
				originalChangeset = int(uti.readFileByTag("last_changeset", self.getPendingFile())[0])
				#rimuovo il file
				os.remove(self.getPendingFile())
				#scrivo il file e ci copio il changeset originale
				uti.writeFile("last_changeset" + str(originalChangeset), self.getPendingFile())
			except:
				raise Exception("Errore: file", PENDING_FILE, "corrotto o non presente")

		#prendo la cartella corrente dal client
		localRoot = self.getCurrPath()

		#prendo la cartella corrente dal server
		serverBranch = self.getCurrBranchOnServer().branchDir

		#scorro tutti i file della cartella
		for dirPath, dirNames, files in os.walk(localRoot):
			for fileName in files:
				if(fileName != PENDING_FILE):
					localFile = path.join(dirPath, fileName)
				
					try:
						#cerco sul server il file corrispondente al localFile
						serverFile = self.findFileOnServer(localFile, serverBranch)
				
						#confronto le date di ultima modifica dei file
						#se il file locale è stato modificato va aggiunto ai pending
						localDate = path.getmtime(localFile)
						serverDate = path.getmtime(serverFile)

						if((path.getmtime(localFile)) > path.getmtime(serverFile)):
							self.addPendingFile(localFile)
						elif((path.getmtime(localFile)) < path.getmtime(serverFile)):
							self.addPendingFile(localFile, older=True)

					except:		
						#se il file non viene trovato nel server vuol dire che è stato aggiunto in locale
						self.addPendingFile(localFile, addedFile=True)
		
		#ritorno la lista dei pendig
		return self.getPendingList()


	#aggiunge il file alla lista dei pending
	def addPendingFile(self, file, addedFile=False, older=False):

		info = ""
		if(addedFile):
			info += " add "
		if(older):
			info += " older "

		uti.writeFile("file: " + file + info, self.getPendingFile())


	#rimuove il file alla lista dei pending
	def delPendingFile(self, file):
		#prendo la stringa di tutto il file
		fileStr = uti.readFile(self.getPendingFile())
		#rimuovo il file dalla lista dei pending
		fileStr.replace("file: " + file + "\n", "")
		#sovrascrivo il file
		uti.writeFile(fileStr, self.getPendingFile(), True)


	#legge il file dei pending e ritorna una lista 
	def getPendingList(self):
		try:
			return uti.readFileByTag("file", self.getPendingFile())
		except:
			return ()


	#crea un nuovo changeset con le modifiche del solo file in input
	def commit(self, fileToCommit = None, comment = ""):
		#creo una cartella temporanea
		tmpDir = path.join(self.getCurrPath(), "tmp")

		#scorro tutti i file in pending
		for file in self.getPendingChanges():
			#se è stato specificato un file, effetto il commit solo di quello, altrimenti committo tutto
			if((fileToCommit == None) | (file == fileToCommit)):
				#copio il file nella cartella temporanea (creo le cartelle se non presenti)
				#prendo il path del file da copiare
				tmpFileDir = path.dirname(file.replace(self.getCurrPath(), tmpDir))
				#se non esiste creo il percorso
				if(path.isdir(tmpFileDir) == False):
					os.makedirs(tmpFileDir)

				#copio il file (con metadati)
				shutil.copy2(file, tmpFileDir)
		
		#creo un nuovo changeset in cui copiare la cartella temporanea
		self.getCurrBranchOnServer().addChangeset(tmpDir, comment)

		#rimuovo la cartella temporanea
		shutil.rmtree(tmpDir)
		
		print("Commit effettuato.")


	#crea un nuovo changeset con le modifiche dei file in pending
	def commitAll(self, comment):
		self.commit(comment = comment)

		#Chiedo all'utente se desidera anche aggiornare la versione locale
		while True:
			print("Scaricare ultima versione? (s/n): ")
			userInput = input()
			if(userInput == "s"):
				self.getLatestVersion()
				break
			elif(userInput == "n"):
				break

						
	#annulla le modifiche sul file e riporta la versione a quella del server
	def undoFile(self, file):
		while True:
			print("Questo comando annullerà le modifiche sul file", file, ", sei sicuro? (s/n) :")
			userInput = input()
			if(userInput == "s"):
				try:
					#prendo il file corrispondente dal server e lo sovrascrivo al file locale
					serverFile = self.findFileOnServer(file, self.getCurrBranchOnServer().branchDir, int(uti.readFileByTag("last_changeset", self.getPendingFile())[0]))
					shutil.copy2(serverFile, path.dirname(file))
				except:
					#se il file non è presente sul server era in add sul client, quindi va semplicemente rimosso
					os.remove(file)
				break
			elif(userInput == "n"):
				break

	
	#annulla tutte le modifiche e riporta la versione a quella del server
	def undoAll(self):
		while True:
			print("Questo comando cancellerà tutti i pending, sei sicuro? (s/n) :")
			userInput = input()
			if(userInput == "s"):
				self.getSpecificVersion(int(uti.readFileByTag("last_changeset", self.getPendingFile())[0]))
				break
			elif(userInput == "n"):
				break


	#stampa una lista di comandi con descrizione
	def printHelp(self):
		print("> exit - chiude il programma",
			  "> repolist - stampa la lista dei repositories presenti sul server",
			  "> branchlist - stampa una lista dei branchs presenti sul repository corrente sul server",
			  "> maprepo [repoName] - mappa il repository \"repoName\" nella macchina locale",
			  "> mapbranch [branchName] - mappa il branch \"branchName\" nella macchina locale",
			  "> delrepo [repoName] - elimina il repository \"repoName\" dalla macchina locale",
			  "> delbranch [branchName] - elimina il branch \"branchName\" dalla macchina locale",
			  "> setrepo [repoName] - imposta il repository \"repoName\" come repository corrente",
			  "> setbranch [branchName] - imposta il branch \"branchName\" come branch corrente",
			  "> history - stampa la lista dei changeset del branch corrente",
			  "> getlatest - scarica la versione più recente del branch corrente",
			  "> getspecific [changeset] - scarica la versione specificata in \"changeset\" del branch corrente",
			  "> pending - stampa una lista dei file modificati in locale",
			  "> commit [file] [comment] - effettua il commit del file \"file\" associando il commento \"comment\"",
			  "> commitall [comment] - effettua il commit di tutti i file in pending associando il commento \"comment\"",
			  "> undo [file] - annulla le modifiche sul file \"file\"",
			  "> undoall - annulla le modifiche su tutti i file in pending e scarica l'ultima versione",
			  "> help - stampa la guida", sep="\n")


	#setta il path di esecuzione
	def setCurrPath(self, path):
		self.currPath = path


	#setta il repository selezionato
	def setCurrRepo(self, repoName):
		self.currRepo = repoName


	#setta il branch selezionato
	def setCurrBranch(self, branchName):
		self.currBranch = branchName


	#ritorna il path di esecuzione
	def getCurrPath(self):
		return self.currPath

	#ritorna il file dei pending nel branch corrente
	def getPendingFile(self):
		return path.join(self.getCurrPath(), PENDING_FILE)


	#ritorna il repository selezionato
	def getCurrRepo(self):
		return self.currRepo


	#ritorna il branch selezionato
	def getCurrBranch(self):
		return self.currBranch


	#ritorna il repository del server corrispondente a quello corrente
	def getCurrRepoOnServer(self):
		return self.server.getRepo(self.getCurrRepo())


	#ritorna il branch del server corrispondente a quello corrente
	def getCurrBranchOnServer(self):
		return self.server.getRepo(self.getCurrRepo()).getBranch(self.getCurrBranch())


	#ritorna il percorso del file sul server, il file viene cercato a partire da branchDir
	def findFileOnServer(self, localFile, branchDir, startChangeset=None): 
		"""TODO: DA SPOSTARE NEL SERVER - usare oggetti del server"""

		#se non diversamente specificato, la ricerca parte dall'ultimo changeset
		if(startChangeset == None):
			startChangeset = self.getCurrBranchOnServer().getLastChangesetNum()

		#scorro tutti i changeset presenti nella cartella del branch a partire dal più recente
		for changeset in reversed(os.listdir(branchDir)):
			if(path.isdir(path.join(branchDir, changeset))):

				#non considero i changeset più recenti di quello di partenza
				if(int(changeset) > startChangeset): 
					continue

				#prendo la cartella del changeset precedente (più recente)
				prevChangesetDir = path.join(branchDir, str(int(changeset) + 1))

				#se il changeset precedente non esiste questo è il più recente
				if(path.isdir(prevChangesetDir)):
					#apro il file del changeset precedente
					prevChangesetTxt = path.join(prevChangesetDir, CHANGESET_FILE)
					
					#se l'ultimo changeset era un backup devo interrompere la ricerca
					if(int(uti.readFileByTag("is_backup", prevChangesetTxt)[0]) == 1):
						raise Exception("File non trovato")

				#ricavo la cartella del changeset corrente
				changesetDir = path.join(branchDir, changeset)

				#ricavo il path del file sul server
				serverFile = localFile.replace(self.getCurrPath(), changesetDir)
				
				#se il file esiste in questo branch interrompo la ricerca
				if(path.isfile(serverFile)):
					break

		return serverFile