from flask import Flask, request, jsonify, render_template, send_from_directory
from pymongo import MongoClient
import json
import os

app = Flask(__name__)

# Connexion à la base de données MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['DGI']
collection = db['formations']

# Charger les données de formation depuis un fichier JSON et insérer dans MongoDB si la collection est vide
if collection.count_documents({}) == 0:
    with open('data/formation.json', encoding='utf-8') as f:
        data = json.load(f)
        collection.insert_many(data["formations"])
        greeting_message = data["greeting"]
else:
    # Récupérer le message de salutation à partir du fichier JSON
    with open('data/formation.json', encoding='utf-8') as f:
        data = json.load(f)
        greeting_message = data["greeting"] 

goodbye_message = "Au revoir humain !"
choose_formation_message = "Veuillez choisir le numéro de formation que vous cherchez !"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message'].strip().lower()
    response = handle_message(user_message)
    return jsonify({"response": response})

@app.route('/download/<string:pdf_name>')
def download_pdf(pdf_name):
    try:
        return send_from_directory('pdfs', pdf_name, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "Le fichier PDF demandé est introuvable."}), 404

def handle_message(message):
    if message == "salut":
        return greet_user()
    elif message == "affiche moi les formations disponibles":
        return list_formations()
    elif message.isdigit():
        return show_formation_by_number(int(message))
    elif "merci" in message:
        return goodbye_message
    else:
        return find_formation(message)

def greet_user():
    return greeting_message

def list_formations():
    formations = collection.find()
    response = "<div class='formations-list'>"
    response += "<b>Formations disponibles :</b><br>"
    for index, formation in enumerate(formations, start=1):
        response += f"{index}. {formation['formation']}<br>"
    response += "</div>"
    response += f"<p>{choose_formation_message}</p>"
    return response

def show_formation_by_number(number):
    formations = list(collection.find())
    if 1 <= number <= len(formations):
        return format_formation_detail(formations[number - 1])
    else:
        return "Le numéro de formation est invalide. Veuillez entrer un numéro valide."

def find_formation(query):
    matching_formations = collection.find({"formation": {"$regex": query, "$options": "i"}})
    response = ""
    for formation in matching_formations:
        response += format_formation_detail(formation)
    if response:
        return response
    return "Aucune formation ne correspond à votre recherche."

def format_formation_detail(formation):
    pdf_button = (
        f"<div class='pdf-download'>"
        f"<a href='/download/{formation['pdf']}' class='btn-download'>"
        f"<i class='fas fa-file-pdf'></i> <i class='fas fa-download'></i> Télécharger la brochure</a>"
        f"</div>"
    )
    return (f"<div class='formation-detail'>"
            f"<h2>{formation['formation']}</h2>"
            f"<p><b>Description:</b> {formation['description']}</p>"
            f"<div class='formation-info'>"
            f"<div><b>Durée:</b> {formation['duration']}</div>"
            f"<div><b>Email:</b> {formation['email']}</div>"
            f"<div><b>Téléphone:</b> {formation['phone']}</div>"
            f"<div><b>Régime:</b> {formation['regime']}</div>"
            f"</div>"
            f"{pdf_button}</div>")

if __name__ == '__main__':
    app.run(debug=True)
