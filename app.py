from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# --- Configuration ---
app = Flask(__name__)
CORS(app)  # Permet à votre page web de communiquer avec le backend
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestion.db' # Nom de votre base de données
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modèles de base de données (Database Models) ---

# Modèle Client (probablement déjà existant)
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adresse = db.Column(db.String(200))
    code_postal = db.Column(db.String(10))
    ville = db.Column(db.String(80))
    pays = db.Column(db.String(80))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# NOUVEAU: Modèle pour les Pièces
class Piece(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(150), nullable=False)
    ref = db.Column(db.String(50), nullable=True, unique=True)
    prix_achat = db.Column(db.Float, nullable=True)
    prix_vente = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# --- Routes API ---

# Routes pour les clients (probablement déjà existantes)
@app.route('/api/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    new_client = Client(**data)
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'message': 'Client ajouté avec succès!'}), 201

@app.route('/api/clients/recherche', methods=['POST'])
def search_clients():
    # ... (votre logique de recherche de client ici) ...
    # Pour l'exemple, on retourne tous les clients
    clients = Client.query.all()
    return jsonify({'clients': [client.to_dict() for client in clients]})

# ... (vos autres routes pour les clients : PUT, DELETE) ...

# NOUVEAU: Route pour ajouter une pièce
@app.route('/api/pieces', methods=['POST'])
def add_piece():
    data = request.get_json()

    # Validation simple
    if not data or not 'designation' in data or not 'prix_vente' in data:
        return jsonify({'message': 'Les champs désignation et prix de vente sont requis'}), 400

    # Conversion des prix en nombres, avec gestion des erreurs
    try:
        # Utilise .get() pour éviter une erreur si la clé n'existe pas
        prix_achat = float(data.get('prix_achat')) if data.get('prix_achat') else None
        prix_vente = float(data['prix_vente'])
    except (ValueError, TypeError):
        return jsonify({'message': 'Les prix doivent être des nombres valides'}), 400

    new_piece = Piece(
        designation=data['designation'],
        ref=data.get('ref'),
        prix_achat=prix_achat,
        prix_vente=prix_vente
    )
    db.session.add(new_piece)
    db.session.commit()
    
    return jsonify({'message': 'Pièce ajoutée avec succès!', 'piece': new_piece.to_dict()}), 201

# NOUVEAU: Route pour rechercher une pièce
@app.route('/api/pieces/recherche', methods=['POST'])
def search_pieces():
    data = request.get_json()
    query = Piece.query

    designation = data.get('designation')
    ref = data.get('ref')

    if designation:
        query = query.filter(Piece.designation.ilike(f'%{designation}%'))
    
    if ref:
        query = query.filter(Piece.ref.ilike(f'%{ref}%'))

    pieces = query.all()
    return jsonify({'pieces': [piece.to_dict() for piece in pieces]})

# --- Initialisation ---
if __name__ == '__main__':
    # Crée les tables dans la base de données si elles n'existent pas
    with app.app_context():
        db.create_all()
    
    # Lance le serveur de développement
    app.run(debug=True, port=5000)