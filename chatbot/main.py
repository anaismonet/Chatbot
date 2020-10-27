from flask import Flask,Blueprint, render_template,request,redirect,url_for, session,current_app, send_file
import os
from . import database_user as db
from os.path import basename
import pickle
import pandas as pd
import json
from time import strftime
from datetime import datetime
from datetime import timedelta
import fnmatch
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

signed_in = False

messages = []
reponses = []
json_file = []
pseudo = ""

cwd = os.getcwd() + '/chatbot/'
filename = 'model.pkl'
with open(cwd + filename,'rb') as model :
        classifier = pickle.load(model)

def prediction_msg(msg, classifier = classifier) :
    temp = pd.DataFrame({'message' : [msg] })
    pred = classifier.predict(temp)
    return pred



@main.route('/')
@main.route('/login')
def login():
    return render_template('login.html')

@main.route('/signup')
def signin():
    return render_template('signup.html')

@main.route('/chatbot')
@login_required
def chat():
    global pseudo, json_file
    pseudo = current_user.pseudo 
    #ouverture JSON
    cwd = os.getcwd() + '/chatbot/static/'

    found = 0
    for filename in os.listdir(cwd) :
        if fnmatch.fnmatch(filename,"calendrier.json"):
            found = 1
            break

    print("found", found)
    if found == 0 :
        with open(cwd + "calendrier.json","w") as f :
                json.dump([],f)

    file = open(cwd + "calendrier.json", "r")
    json_file = json.load(file)
    file.close()

    print("json_file", json_file)
    return render_template('index.html', message = messages, reponse = reponses, pseudo = pseudo )

@main.route('/chatbot', methods=["GET"])
@login_required
def chat_back():
    return render_template('index.html', message = messages, reponse = reponses, pseudo = pseudo)

@main.route('/chatbot', methods=["POST"])
@login_required
def chat_msg():
    global messages, reponses
    message = request.form.get("message_input")
    date = datetime.now()
    msg_day = date.isoweekday()
    time = date.strftime("%m/%d/%Y %H:%M:%S")
    day = date.strftime("%m/%d/%Y")
    msg_hour = date.hour
    msg_min = date.minute
    messages.append(message)

    attente = prediction_msg(message, classifier)

    if attente[0] == 'autre':
        reponses.append('Je ne suis pas capable de répondre à votre demande')
    else :
        #récupération du nombre de pages
        list_pages = message.split("pages", 1)
        list_pages_bis = list_pages[0].split()
        nb_pages = list_pages_bis[-1]

        #récupération du nom du document
        list_doc = message.split("doc", 1)
        list_doc_bis = list_doc[1].split()
        print(list_doc_bis)
        if list_doc_bis[0] == 'ument' :
            nom_doc = list_doc_bis[1]
        else :
            nom_doc = 'doc' + list_doc_bis[0]

        #calcul timing
        pages = int(nb_pages)


        while True : 
            br = False
            if len(json_file) == 0:
                print("Le json file est vide")
                start = time
                break
            else:
                print("Le json file n'est pas vide")
                print("nom du dernier objet", json_file[-1]['titre'])
                # Cas 1 : on vérifie entre l'heure actuelle et 19:00:00 si on peut imprimer notre nombre de pages et on vérifie si heure actuelle est bien < 19:00:00
                if (datetime.strptime(day + " 19:00:00", "%m/%d/%Y %H:%M:%S") -  date).seconds > pages and datetime.strptime(day + " 19:00:00", "%m/%d/%Y %H:%M:%S") > date :
                    print("Je remplis les conditions du cas 1")
                    late = datetime.strptime(json_file[-1]["end"], "%m/%d/%Y %H:%M:%S")
                    print("Je suis le dernier élément du fichier calendrier.json", late)

                    #Sous cas 1 : si aujourd'hui et le dernier élément du json ont le même jour
                    if (date - late).days == -1:
                        print("Je remplis les conditions du sous cas 1 : date et late sont le même jour")

                        #Sous sous cas 1 : on vérifie si entre le dernier élément et 19:00:00 il y a le temps d'imprimer nos pages et si late est < à 19:00:00
                        if (datetime.strptime(day + " 19:00:00", "%m/%d/%Y %H:%M:%S") -  late).seconds > pages and datetime.strptime(late.strftime("%m/%d/%Y") + " 19:00:00", "%m/%d/%Y %H:%M:%S") > late :
                            print("Je remplis les conditions du sous sous cas 1")
                            start = max(date, late).strftime("%m/%d/%Y %H:%M:%S")
                            print("start", start)
                            break

                        #Sous sous cas 2 : 
                        else:
                            print("je remplis sous sous cas 2")
                            day_after = late.day +1
                            print("day_after", day_after)
                            try:
                                start = date.replace(day = day_after, hour = 7, minute = 0, second = 0, microsecond = 0 ).strftime("%m/%d/%Y %H:%M:%S")
                                break
                            except ValueError:
                                start = date.replace(day = 1, month = date.month +1, hour = 7, minute = 0, second = 0, microsecond = 0 ).strftime("%m/%d/%Y %H:%M:%S")
                                break
                    # Sous cas 2 : 
                    else:
                        print("Je suis dans le cas 2")
                        for i in range(len(json_file), 0, -1):
                            print("elem numéro ", i)
                            elem = datetime.strptime(json_file[i-1]['end'], "%m/%d/%Y %H:%M:%S")
                            print("elem du cas 2", elem)
                            if (elem.day == date.day):
                                if (elem - elem.replace(hour = 19, minute = 00, second = 00)).seconds > pages:
                                    start = elem.strftime("%m/%d/%Y %H:%M:%S")
                                    br = True
                                    break
                                else :
                                    date = late
                                    day = late.strftime("%m/%d/%Y")
                                    print("Ce n'est pas la même jour")
                                    break
                        if br:           
                            break
                # Cas 2
                else:
                    late = datetime.strptime(json_file[-1]["end"], "%m/%d/%Y %H:%M:%S")
                    print("late du Cas 2", late)
                    print("date du Cas 2", date)
                    # 2.1
                    if (date - late).days == 0:
                        print('dif ', (date - late).days)
                        day_after = date.day +1
                        try:
                            print("2.1 premier try ")
                            start = date.replace(day = day_after, hour = 7, minute = 0, second = 0, microsecond = 0 ).strftime("%m/%d/%Y %H:%M:%S")
                            print("date 2.1 premier try", start)
                            break
                        except ValueError:
                            print("2.1 valueError")
                            start = date.replace(day = 1, month = date.month +1, hour = 7, minute = 0, second = 0, microsecond = 0 ).strftime("%m/%d/%Y %H:%M:%S")
                            print("start 2.1 value Error", start)
                            break
                    #2.2
                    else:
                        #2.2.1
                        if (datetime.strptime(late.strftime("%m/%d/%Y") + " 19:00:00", "%m/%d/%Y %H:%M:%S") -  late).seconds > pages and datetime.strptime(late.strftime("%m/%d/%Y") + " 19:00:00", "%m/%d/%Y %H:%M:%S") > late :
                            start = late.strftime("%m/%d/%Y %H:%M:%S")
                            print("start 2.2.1", start)
                            break
                        #2.2.2
                        else:
                            day_after = late.day +1
                            start = late.replace(day = day_after, hour = 7, minute = 0, second = 0, microsecond = 0 ).strftime("%m/%d/%Y %H:%M:%S")
                            print("start 2.2.2", start)
                            break


        start = datetime.strptime(start, "%m/%d/%Y %H:%M:%S")
        # fin de semaine
        if start.isoweekday() == 7:
            try:
                start = start.replace(day = start.day + 1)
                print("fin de semaine dimanche try", start)
            except ValueError:
                start = start.replace(day = 1, month = start.month +1)
                print("fin de semaine dimanche except", start)
        if start.isoweekday() == 6:
            try:
                start = start.replace(day = start.day + 1)
                print("fin de semaine samedi start premier try:", start)
                try:
                    start = start.replace(day = start.day + 1)
                    print("fin de semaine samedi start deuxième try:", start)
                except ValueError:
                    start = start.replace(day = 1, month = start.month +1)
                    print("fin de semaine samedi start valueerror dans le premier try:", start)
                
            except ValueError:
                start = start.replace(day = 2, month = start.month +1)
                print("fin de semaine samedi start valueerror:", start)

        start = start.strftime("%m/%d/%Y %H:%M:%S")
        end = datetime.strptime(start, "%m/%d/%Y %H:%M:%S") + timedelta(seconds = pages)
    
            
        #Update json
        object = {}
        object['titre'] = nom_doc
        object['utilisateur'] = pseudo
        object['start'] = start
        object['end'] = end.strftime("%m/%d/%Y %H:%M:%S")
        object['jour'] = datetime.strptime(start, "%m/%d/%Y %H:%M:%S").isoweekday()
        object['pages'] = pages

        json_file.append(object)

        #ecriture JSON
        print(json_file)
        cwd = os.getcwd() + '/chatbot/static/'
        file = open(cwd + "calendrier.json", "w")
        json.dump(json_file, file)
        file.close()

        #envoie message de réponse
        reponses.append("Je lance l'impresion du document " + nom_doc + " de " + nb_pages + "pages")
    return render_template('index.html', message = messages, reponse = reponses, pseudo = pseudo)


@main.route('/calendrier', methods=['POST','GET'])
def calendrier():
    week = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi']
    return render_template('calendrier.html', json = json_file, week = week)

if __name__ == "__main__":
    main.run(debug = True)