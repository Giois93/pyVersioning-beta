import os
import os.path as path
import time
import datetime
import shutil
import filecmp
import uti
from uti import PENDING_FILE
from uti import CHANGESET_FILE
from uti import LAST_RUN_FILE
from Server import Server

class Client:
	
	myRoot = ""
	currPath = ""
	currRepo = ""
	currBranch = ""
	server = None

	def __init__(self, server):
		self.myRoot = "C:\my\myclient"
		self.server = server

		#chiedo all'utente se desidera impostare l'ultimo percorso usato
		if (uti.askQuestion("Impostare l'ultimo percorso aperto?")):
			try:
				#setto il repository se memorizzato nel file
				self.setCurrRepo(uti.readFileByTag("last_repo", self.getLastRunFile())[0])
			except:
				print("Impossibile effettuare l'operazione richiesta")
				self.setCurrPath(self.myRoot)

			try:
				#setto il branch se memorizzato nel file
				self.setCurrBranch(uti.readFileByTag("last_branch", self.getLastRunFile())[0])
			except:
				pass
		else:
			self.setCurrPath(self.myRoot)


	#esegue i comandi dell'utente fino al comando "exit"
	def runMenu(self):
		#eseguo i comandi dell'utente
		while True:
			print("> ", end="")
			userInput = input()
			self.menu(userInput)
		
			#il programma termina con il comando "exit"
			if (userInput == "exit"):
				break


	#esegue il comando "userInput"
	def menu(self, userInput):

		#costruisco una lista di comando e argomenti
		commandList = userInput.split()
		commandList.reverse()

		#eseguo il comando
		try:
			try:
				command = commandList.pop()
			except:
				print("Valore non ammesso", end="\n\n")

			if (command == "exit"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				#memorizzo gli ultimi repo/branch settati
				uti.writeFileByTag("last_repo", self.getCurrRepo(), self.getLastRunFile())
				uti.writeFileByTag("last_branch", self.getCurrBranch(), self.getLastRunFile())
				print("Programma terminato.", end="\n\n")
			
			elif (command == "clear"):
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				os.system("cls")

			elif (command == "currdir"):
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				print("> {}".format(uti.getPathForPrint(self.getCurrPath())))

			elif (command == "repolist"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				self.showRepos() 
			
			elif (command == "branchlist"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				self.showBranches()

			elif (command == "maprepo"): 
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				self.mapRepository(commandList.pop()) 

			elif (command == "mapbranch"): 
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				self.mapBranch(commandList.pop())

			elif (command == "delrepo"): 
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				self.removeRepositoryMap(commandList.pop())

			elif (command == "delbranch"):
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				self.removeBranchMap(commandList.pop())

			elif (command == "setrepo"):
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				self.setRepo(commandList.pop())

			elif (command == "setbranch"): 
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				self.setBranch(commandList.pop())

			elif (command == "history"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.showHistory()

			elif (command == "getlatest"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.getLatestVersion() 

			elif (command == "getspecific"):
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.getSpecificVersion(int(commandList.pop()))

			elif (command == "pending"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.printPendingChanges()

			elif (command == "commit"): 
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.commitOne(commandList.pop())

			elif (command == "commitall"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.commitAll()

			elif (command == "undo"): 
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.undoFile(commandList.pop())

			elif (command == "undoall"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.undoAll()
			
			elif (command == "compare"):
				if (len(commandList) != 1):
					raise Exception("Parametri errati")
				elif(not self.getCurrRepo()):
					raise Exception("Nessun repository settato")
				elif(not self.getCurrBranch()):
					raise Exception("Nessun branch settato")
				self.compare(commandList.pop())
			
			elif (command == "help"): 
				if (len(commandList) != 0):
					raise Exception("Parametri errati")
				self.printHelp()

			else: 
				print("Valore non ammesso", end="\n\n")

		except Exception as ex:
			print(ex, end="\n\n")


	#mostra la lista dei repository presenti sul server
	def showRepos(self):
		print("\nRepositories sul server di MyVersion")
	
		for repo in self.server.showRepos():
			#ottengo la cartella del repository
			repoDir = path.join(self.myRoot, repo)
			#verifico che la cartella esista in locale
			if (path.isdir(repoDir)):
				print("- {} ({})".format(repo, "mapped"))
			else:
				print("- {}".format(repo))
		print()


	#mostra la lista dei branch presenti sul server
	def showBranches(self):
		print("\nBranches sul repository {}:".format(self.getCurrRepo()))
		for branch in self.server.showBranches(self.getCurrRepo()):
			#ottengo la cartella del branch
			branchdir = path.join(self.myRoot, self.getCurrRepo(), branch)
			#verifico che la cartella esista in locale
			if (path.isdir(branchdir)):
				print("- {} ({})".format(branch, "mapped"))
			else:
				print("- {}".format(branch))
		print()


	#mostra la lista dei changeset presenti in questo branch
	def showHistory(self):
		print("\nChangeset del branch {}:".format(self.getCurrBranch()))
		for changeSet in self.getCurrBranchOnServer().getChangesetList():
			print("- {}".format(changeSet))
		print()


	#mappa il repository nella cartella del client
	def mapRepository(self, repoName):

		#ottengo il path del repository
		clientDir = path.join(self.myRoot, repoName)

		#chiedo all'utente se sovrascrivere la cartella
		if (uti.askAndRemoveDir(clientDir, askOverride=True)):
			#mappo il repository nella cartella del client
			try:
				#se il repository esiste sul server, creo una cartella sul client
				#altrimenti viene generata un'eccezione
				self.server.existsRepo(repoName)
				os.makedirs(clientDir)
				print("Repository mappato in:", clientDir, end = "\n\n")
				
				#setto anche il repository mappato come repository corrente di default
				self.setRepo(repoName)
			except:
				raise Exception("Repository non trovato", end = "\n\n")


	#mappa il branch nella cartella del client
	def mapBranch(self, branchName):

		#ottengo il path del branch
		clientDir = path.join(self.myRoot, self.getCurrRepo(), branchName)

		#chiedo all'utente se sovrascrivere la cartella
		if (uti.askAndRemoveDir(clientDir, askOverride=True)):
			#mappo il branch nella cartella del client
			try:
				#se il branch esiste sul server, creo il branch sul client
				#altrimenti viene generata un'eccezione
				#scarico anche la LatestVersion di default
				self.server.mapBranch(self.getCurrRepo(), branchName, clientDir)
				print("Branch mappato in:", clientDir, end = "\n\n")
				
				#setto anche il branch mappato come branch corrente di default
				self.setBranch(branchName)
			except:
				raise Exception("Branch non trovato")


	#rimuove la cartella del repo sul client
	def removeRepositoryMap(self, repoName):
		repodir = path.join(self.myRoot, repoName)
		if (path.isdir(repodir)):
			uti.askAndRemoveDir(repodir)
			if (self.getCurrRepo() == repoName):
				self.setCurrRepo("")
				self.setCurrBranch("")
		else:
			raise Exception("Repository {} non presente".format(repoName))


	#rimuove la cartella del branch sul client
	def removeBranchMap(self, branchName):
		branchdir = path.join(self.myRoot, self.getCurrRepo(), branchName)
		if (path.isdir(branchdir)):
			uti.askAndRemoveDir(branchdir)
			if (self.getCurrBranch() == branchName):
				self.setCurrBranch("")
		else:
			raise Exception("Branch {} non presente".format(branchName))


	#setta il repository corrente
	def setRepo(self, repoName):
		#ottengo la cartella del repository
		repoDir = path.join(self.myRoot, repoName)
		#verifico che la cartella esista
		if (path.isdir(repoDir) == False):
			raise Exception("Il repository", repoName, "non esiste o non è stato mappato")

		#aggiorno il repository corrente
		self.setCurrRepo(repoName)
		self.setCurrBranch("")
			
		print("> {}".format(uti.getPathForPrint(self.getCurrPath())), end="\n\n")


	#setta il branch corrente
	def setBranch(self, branchName):
		#ottengo la cartella del branch
		branchDir = path.join(self.myRoot, self.getCurrRepo(), branchName)
		#verifico che la cartella locale esista
		if (path.isdir(branchDir) == False):
			raise Exception("Il branch", branchName, "non esiste o non è stato mappato", end="\n\n")
			
		#aggiorno il branch corrente
		self.setCurrBranch(branchName)
			
		print("> {}".format(uti.getPathForPrint(self.getCurrPath())), end="\n\n")


	#scarica l'ultima versione e la copia nella cartella del branch
	def getLatestVersion(self):
		#chiedo all'utente se sovrascrivere la cartella
		if (uti.askAndRemoveDir(self.getCurrPath(), ask=False)):
			#prendo la latestVersion da Repository e Branch corrente
			self.getCurrBranchOnServer().getLatestVersion(self.getCurrPath())
			uti.writeFileByTag("last_changeset", self.getCurrBranchOnServer().getLastChangesetNum(), self.getPendingFile())
			print("Versione locale aggiornata con successo", end="\n\n")

	
	#scarica una versione specifica (identificata dal numero di changeset) e la copia nella cartella del branch
	def getSpecificVersion(self, changesetNum):
		#chiedo all'utente se sovrascrivere la cartella
		if (uti.askAndRemoveDir(self.getCurrPath(), ask=False)):
			#prendo la versione specifica da Repository e Branch corrente con il numero di changeset passato
			self.getCurrBranchOnServer().getSpecificVersion(changesetNum, self.getCurrPath())
			uti.writeFileByTag("last_changeset", changesetNum, self.getPendingFile())
			print("Versione locale aggiornata con successo", end="\n\n")


	#stampa una lista dei file modificati in locale con data di ultima modifica
	def printPendingChanges(self):
		#scorro tutti i file nella lista dei pending
		pendingList = self.getPendingChanges()
		if (len(pendingList) == 0):
			raise Exception("Nessun file in modifica.")
		else:
			print("Lista dei file in modifica:")
			for file in pendingList:
				#prendo la data di ultima modifica del file
				date = datetime.datetime.fromtimestamp(path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
				#stampo file e data ultima modifica
				print("{} - {}".format(file.replace(self.getCurrPath(), ""), date))
			print()

	
	#ritorna una lista dei file modificati in locale
	def getPendingChanges(self):
		#rimuovo il file dei pending vecchio
		if (path.isfile(self.getPendingFile())):
			try:
				#memorizzo il changeset originale
				originalChangeset = int(uti.readFileByTag("last_changeset", self.getPendingFile())[0])
				#rimuovo il file
				os.remove(self.getPendingFile())
				#scrivo il file e ci copio il changeset originale
				uti.writeFileByTag("last_changeset", originalChangeset, self.getPendingFile())
			except:
				raise Exception("Errore: file {} corrotto o non presente".format(PENDING_FILE))

		#prendo la cartella corrente dal client
		localRoot = self.getCurrPath()

		#prendo la cartella corrente dal server
		serverBranch = self.getCurrBranchOnServer().branchDir

		#scorro tutti i file della cartella
		for dirPath, dirNames, files in os.walk(localRoot):
			for fileName in files:
				if (fileName != PENDING_FILE):
					localFile = path.join(dirPath, fileName)
					try:
						#cerco sul server il file corrispondente al localFile 
						#(cerco sempre a partire dall'ultima versione così da segnalare anche file vecchi)
						serverFile = self.findFileOnServer(localFile, serverBranch)
				
						#confronto le date di ultima modifica dei file
						#se il file locale è stato modificato va aggiunto ai pending
						localDate = path.getmtime(localFile)
						serverDate = path.getmtime(serverFile)

						if (int(path.getmtime(localFile)) > int(path.getmtime(serverFile))):
							if (filecmp.cmp(localFile, serverFile) == False):
								self.addPendingFile(localFile)
						elif(int(path.getmtime(localFile)) < int(path.getmtime(serverFile))):
							if (filecmp.cmp(localFile, serverFile) == False):
								self.addPendingFile(localFile)

					except:		
						#se il file non viene trovato nel server vuol dire che è stato aggiunto in locale
						self.addPendingFile(localFile)
		
		#ritorno la lista dei pendig
		return self.getPendingList()


	#aggiunge il file alla lista dei pending
	def addPendingFile(self, file):
		uti.writeFile("file={}".format(file), self.getPendingFile())


	#rimuove il file alla lista dei pending
	def delPendingFile(self, file):
		#prendo la stringa di tutto il file
		fileStr = uti.readFile(self.getPendingFile())
		#rimuovo il file dalla lista dei pending
		fileStr.replace("file={}\n".format(file), "")
		#sovrascrivo il file
		uti.writeFile(fileStr, self.getPendingFile(), True)


	#legge il file dei pending e ritorna una lista 
	def getPendingList(self):
		try:
			return uti.readFileByTag("file", self.getPendingFile())
		except:
			return ()


	#crea un nuovo changeset con le modifiche del solo file in input
	def commitOne(self, fileName):

		#creo una cartella temporanea
		tmpDir = path.join(self.getCurrPath(), "tmp")
		
		#prendo il file corrente dai pending
		try:
			file = self.findFileInPending(fileName)
		except:
			raise
		
		#aggiunto i file da committare nella cartella temporanea
		self.addForCommit(file, tmpDir)
		
		#effettuo il commit
		print("Inserire un commento: ")
		comment = input()
		self.doCommit(tmpDir, comment)
		self.delPendingFile(file)
		print("File: {} aggiornato con successo.".format(fileName), end="\n\n")


	#crea un nuovo changeset con le modifiche dei file in pending
	def commitAll(self):

		#creo una cartella temporanea
		tmpDir = path.join(self.getCurrPath(), "tmp")
		if (path.isdir(tmpDir)):
			shutil.rmtree(tmpDir)

		#scorro tutti i file nella lista dei pending
		pendingList = self.getPendingChanges()
		if (len(pendingList) == 0):
			raise Exception("Nessun file in modifica.")

		#aggiungo ai pending tutti i file diversi dalla versione del server
		for file in pendingList:
			self.addForCommit(file, tmpDir)

		#effettuo il commit
		print("Inserire un commento: ")
		comment = input()
		self.doCommit(tmpDir, comment)

		print("Modifiche inviate con successo.", end="\n\n")

		#chiedo all'utente se desidera anche aggiornare la versione locale
		if (uti.askQuestion("Scaricare ultima versione?")):
			self.getLatestVersion()


	#aggiunge un file alla cartella temporanea dei file da committare
	def addForCommit(self, file, tmpDir):
		#copio il file nella cartella temporanea (creo le cartelle se non presenti)
		#prendo il path del file da copiare
		tmpFileDir = path.dirname(file.replace(self.getCurrPath(), tmpDir))
		#se non esiste creo il percorso
		if (path.isdir(tmpFileDir) == False):
			os.makedirs(tmpFileDir)

		#copio il file
		shutil.copy2(file, tmpFileDir)
		

	#effettua il commit dei file contenuti in "sourceDir" su un nuovo changeset
	def doCommit(self, sourceDir, comment):
		#creo un nuovo changeset in cui copiare la cartella temporanea
		changesetNum = self.getCurrBranchOnServer().addChangeset(sourceDir, comment)

		#rimuovo la cartella temporanea
		if (path.isdir(sourceDir)):
			shutil.rmtree(sourceDir)
		
		uti.writeFileByTag("last_changeset", changesetNum, self.getPendingFile())


	#annulla le modifiche sul file e riporta la versione a quella del server
	def undoFile(self, file):
		if (uti.askQuestion("Questo comando annullerà le modifiche sul file {}, sei sicuro?".format(file))):
			#prendo il file corrispondente dal server e lo sovrascrivo al file locale
			try:
				filePath = self.findFileInPending(file)
				try:
					originalChangeset = int(uti.readFileByTag("last_changeset", self.getPendingFile())[0])
					serverFile = self.findFileOnServer(filePath, self.getCurrBranchOnServer().branchDir, originalChangeset)
					shutil.copy2(serverFile, path.dirname(filePath))
				except:
					#se il file non è presente sul server era in add sul client, quindi va semplicemente rimosso
					os.remove(file)
				print("Modifiche annullate.", end="\n\n")
			except:
				print("File non trovato.", end="\n\n")
				self.printPendingChanges()


	#annulla tutte le modifiche e riporta la versione a quella del server
	def undoAll(self):
		if (uti.askQuestion("Questo comando cancellerà tutti i pending, sei sicuro?")):
			print("Modifiche annullate.", end="\n\n")
			self.getSpecificVersion(int(uti.readFileByTag("last_changeset", self.getPendingFile())[0]))
		

	#effettua il merge del file in pending con il file sul server
	def compare(self, localFile):
		try:
			pendingFile = self.findFileInPending(localFile)
			try:
				serverFile = self.findFileOnServer(pendingFile, self.getCurrBranchOnServer().branchDir)
				print ("".join(uti.diff(serverFile, pendingFile)))
			except Exception as e:
				print(e)
		except:
			print("File non presente in pending", end="\n\n")
			self.printPendingChanges()


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
			  "> compare [file] - effettua un confronto fra il file \"file\" e la versione del server",
			  "> clear - pulisce il terminale",
			  "> help - stampa la guida", sep="\n", end="\n\n")


	#setta il path di esecuzione
	def setCurrPath(self, path):
		self.currPath = path


	#setta il repository selezionato
	def setCurrRepo(self, repoName):
		self.currRepo = repoName
		self.setCurrPath(path.join(self.myRoot, repoName))


	#setta il branch selezionato
	def setCurrBranch(self, branchName):
		self.currBranch = branchName
		self.setCurrPath(path.join(self.myRoot, self.getCurrRepo(), branchName))


	#ritorna il path di esecuzione
	def getCurrPath(self):
		return self.currPath


	#ritorna il repository selezionato
	def getCurrRepo(self):
		return self.currRepo


	#ritorna il branch selezionato
	def getCurrBranch(self):
		return self.currBranch


	#ritorna il file dei pending nel branch corrente
	def getPendingFile(self):
		return path.join(self.getCurrPath(), PENDING_FILE)

	
	#ritorna il file dell'ultimo run
	def getLastRunFile(self):
		return path.join(self.myRoot, LAST_RUN_FILE)


	#ritorna il repository del server corrispondente a quello corrente
		"""TODO: DA SPOSTARE NEL SERVER - usare oggetti del server"""
	def getCurrRepoOnServer(self):
		return self.server.getRepo(self.getCurrRepo())


	#ritorna il branch del server corrispondente a quello corrente
		"""TODO: DA SPOSTARE NEL SERVER - usare oggetti del server"""
	def getCurrBranchOnServer(self):
		return self.server.getRepo(self.getCurrRepo()).getBranch(self.getCurrBranch())


	#ritorna il percorso del file sul server, il file viene cercato a partire da branchDir
	def findFileOnServer(self, localFile, branchDir, startChangeset=None): 
		#TODO: dovrei fare una copia locale del file e ritornare il suo path per il confronto
		return self.server.findFile(self.getCurrRepo(), self.getCurrBranch(), localFile.replace("{}\\".format(self.getCurrPath()), ""), startChangeset)

	
	"""NOTA: non ammette 2 file con lo stesso nome"""
	#cerca il file "fileName" frai pending
	def findFileInPending(self, fileName):
		for pendingFile in self.getPendingChanges():
			if (path.basename(pendingFile) == fileName):
				return pendingFile

		raise Exception("File non trovato in pending")