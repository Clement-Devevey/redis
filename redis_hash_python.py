import redis
from pprint import pprint
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Fonctions qui permettent d'effectuer des actions lorsqu'un élément du combobox est selectionné (cliqué)
def callbackComboAffectable(event):
	i = 0
	for key, value in appels[comboAffectable.current()].items():
		if(i!=5):
			entry[i].delete(0, tk.END)
			entry[i].insert(0, value)
		i=i+1

def callbackComboOperateur(event):
	entry[5].delete(0, tk.END)
	entry[5].insert(0, operateurs[comboOperateur.current()]["identifiant"])
	text.delete(1.0, tk.END)
	text.insert(1.0, "Voici vos appels :\n")
	for i in range (r.hlen("appels")):
		if(json.loads(r.hvals("appels")[i])["operateur"] == operateurs[comboOperateur.current()]["identifiant"]):

			json_val = json.loads(r.hvals("appels")[i])
			
			for k in json_val:
				print(k, json_val[k])
				text.insert(tk.END, '{} = {}\n'.format(k,json_val[k]))
			text.insert(tk.END, "-----------------\n")

	

def callbackCreate():
	if(entry[0].get() == "" or entry[1].get() == "" or entry[3].get() == ""):
		tk.messagebox.showwarning(title="Erreur création appel", message="Vous devez remplir les cases 1,2 et 4 minimum")
		return
	# check si un appel a déjà l'identifiant
	if(r.hexists("appels", entry[0].get())):
		tk.messagebox.showwarning(title="Erreur création appel", message="Identifiant déjà existant.")
		return
	r.hset('appels', entry[0].get() , "{ \"identifiant\": \""+entry[0].get()+"\", \"heure_appel\": \""+entry[1].get()+"\", \"numero_origine\": \""+entry[2].get()+"\", \"statut\": \""+entry[3].get()+"\", \"durée\": \""+entry[4].get()+"\", \"operateur\": \""+entry[5].get()+"\", \"description\": \""+entry[6].get()+"\" }")
	tk.messagebox.showinfo(title="Création appel", message="Appel bien créé")

def callbackTake():
	if(comboAffectable.current()==-1 or comboOperateur.current()==-1):
		tk.messagebox.showwarning(title="Erreur lors de la prise d'appel", message="Vous devez sélectionner un appel et un opérateur")
		return

	r.hdel('appels', entry[0].get())
	r.hset('appels', entry[0].get(), "{ \"identifiant\": \""+entry[0].get()+"\", \"heure_appel\": \""+entry[1].get()+"\", \"numero_origine\": \""+entry[2].get()+"\", \"statut\": \""+"en cours"+"\", \"durée\": \""+entry[4].get()+"\", \"operateur\": \""+entry[5].get()+"\", \"description\": \""+entry[6].get()+"\" }")
	


# Fonctions qui permettent de refresh les éléments dans les combobox à chaque fois que l'utilisateur ouvre le menu déroulant
def changeAffectable():
	appels.clear()
	appel_affectable = []
	for i in range (r.hlen("appels")):
		if(json.loads(r.hvals("appels")[i])["statut"] != "en cours" and json.loads(r.hvals("appels")[i])["statut"] != "terminé"):
			appel_affectable.append(json.loads(r.hvals("appels")[i])["identifiant"]+"-"+json.loads(r.hvals("appels")[i])["statut"])
			appels.append(json.loads(r.hvals("appels")[i]))

	comboAffectable["values"] = appel_affectable

def changeOperateur():
	operateurs.clear()
	operateur_temp = []
	for i in range (r.hlen("operateurs")):
		operateur_temp.append(json.loads(r.hvals("operateurs")[i])["prenom"]+" "+json.loads(r.hvals("operateurs")[i])["nom"])
		operateurs.append(json.loads(r.hvals("operateurs")[i]))

	comboOperateur["values"] = operateur_temp



r = redis.Redis(db=4)
appels = []
operateurs = []

#appels = r.lrange("appels",0,-1)
#operateurs = r.lrange("operateurs",0,-1)


app = tk.Tk() 
app.geometry('1200x800')
app.title("Call center")
text = tk.Text(app)

text.grid(column=2, row=20)

#Setting labels
labelTop = tk.Label(app, text = "Appels affectables :")
labelTop.grid(column=0, row=0)

labelOperateur = tk.Label(app, text = "Qui êtes-vous ? :")
labelOperateur.grid(column=2, row=0)

#Setting comboboxes
comboAffectable = ttk.Combobox(app, postcommand=changeAffectable)
comboAffectable.grid(column=0, row=1, ipadx = 10)
comboAffectable.bind("<<ComboboxSelected>>", callbackComboAffectable)

comboOperateur = ttk.Combobox(app, postcommand=changeOperateur)
comboOperateur.grid(column=2, row=1, ipadx = 10)
comboOperateur.bind("<<ComboboxSelected>>", callbackComboOperateur)


# Setting label + entries to print all the json datas (APPELS)
i = 0
entry = []
myString = []
for key in (json.loads(r.hvals("appels")[0]).keys()):
	i=i+1
	labelTop = tk.Label(app, text = key)
	labelTop.grid(column=0, row=i+1, sticky=tk.E)
	resultString=tk.StringVar()
	myString.append(resultString)
	entry.append(tk.Entry(app, width=20, textvariable=myString))
	entry[i-1].grid(column=1, row=i+1, padx=10)


# Buttons

create = tk.Button(app, text = 'Créer appel', command=callbackCreate)
create.grid(column=0, row=entry[-1].grid_info()['row']+1, pady=10, sticky=tk.E)

take = tk.Button(app, text = "prendre l'appel", command=callbackTake)
take.grid(column=1, row=entry[-1].grid_info()['row']+1, pady=10, sticky=tk.W)

app.mainloop()
