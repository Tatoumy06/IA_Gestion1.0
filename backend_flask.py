from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # autorise les requêtes du frontend local

# Initialiser la base de données SQLite
def init_db():
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT,
            telephone TEXT,
            email TEXT,
            adresse TEXT,
            code_postal TEXT,
            ville TEXT,
            pays TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Endpoint pour ajouter un nouveau client
@app.route("/api/clients", methods=["POST"])
def ajouter_client():
    data = request.get_json()
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (nom, prenom, telephone, email, adresse, code_postal, ville, pays)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["nom"],
        data["prenom"],
        data["telephone"],
        data["email"],
        data["adresse"],
        data["code_postal"],
        data["ville"],
        data["pays"]
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Client sauvegardé avec succès"})

# Endpoint pour rechercher un client
@app.route("/api/clients/recherche", methods=["POST"])
def rechercher_clients():
    data = request.get_json()
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()
    query = "SELECT * FROM clients WHERE 1=1"
    params = []
    if data.get("nom"):
        query += " AND nom LIKE ?"
        params.append(f"%{data['nom']}%")
    if data.get("prenom"):
        query += " AND prenom LIKE ?"
        params.append(f"%{data['prenom']}%")
    if data.get("code_postal"):
        query += " AND code_postal = ?"
        params.append(data['code_postal'])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    results = [
        {
            "id": row[0],
            "nom": row[1],
            "prenom": row[2],
            "telephone": row[3],
            "email": row[4],
            "adresse": row[5],
            "code_postal": row[6],
            "ville": row[7],
            "pays": row[8]
        } for row in rows
    ]
    return jsonify({"clients": results})

# Endpoint pour supprimer un client
@app.route("/api/clients/<int:id>", methods=["DELETE"])
def supprimer_client(id):
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Client supprimé avec succès"})

# Endpoint pour modifier un client
@app.route("/api/clients/<int:id>", methods=["PUT"])
def modifier_client(id):
    data = request.get_json()
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clients SET
            nom = ?,
            prenom = ?,
            telephone = ?,
            email = ?,
            adresse = ?,
            code_postal = ?,
            ville = ?,
            pays = ?
        WHERE id = ?
    """, (
        data["nom"],
        data["prenom"],
        data["telephone"],
        data["email"],
        data["adresse"],
        data["code_postal"],
        data["ville"],
        data["pays"],
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Client modifié avec succès"})

# Endpoint pour les pieces (préparation future)
@app.route("/api/pieces", methods=["GET"])
def gestion_pieces():
    return jsonify({"message": "Interface pièces prête"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)


