from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from fpdf import FPDF

# --- Configuration ---
app = Flask(__name__)
# Configuration CORS plus explicite pour autoriser toutes les origines sur les routes /api/
CORS(app, resources={r"/api/*": {"origins": "*"}})

# NOUVEAU: Route pour servir le fichier index.html
from flask import send_from_directory
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html') # Assurez-vous que index.html est dans le même dossier que app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gestion.db' # Nom de votre base de données
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modèles de base de données (Database Models) ---

# Modèle Clie nt (probablement déjà existant)
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

# NOUVEAU: Modèle pour la Main d'oeuvre
class MainDoeuvre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150), nullable=False, unique=True)
    taux_horaire = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# NOUVEAU: Modèles pour la Facturation
class Facture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_facture = db.Column(db.String(50), unique=True, nullable=False)
    date_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    informations_complementaires = db.Column(db.Text, nullable=True)
    total_ht = db.Column(db.Float, nullable=False, default=0.0)
    total_ttc = db.Column(db.Float, nullable=False, default=0.0)
    
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref=db.backref('factures', lazy=True))
    
    lignes = db.relationship('FactureLigne', backref='facture', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'numero_facture': self.numero_facture,
            'date_creation': self.date_creation.isoformat(),
            'client_id': self.client_id,
            'client': self.client.to_dict(),
            'lignes': [ligne.to_dict() for ligne in self.lignes],
            'total_ht': self.total_ht,
            'total_ttc': self.total_ttc
        }

class FactureLigne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    quantite = db.Column(db.Float, nullable=False, default=1)
    prix_unitaire_ht = db.Column(db.Float, nullable=False)
    
    facture_id = db.Column(db.Integer, db.ForeignKey('facture.id'), nullable=False)
    piece_id = db.Column(db.Integer, db.ForeignKey('piece.id'), nullable=True) # Nullable for labor
    piece = db.relationship('Piece')

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'quantite': self.quantite,
            'prix_unitaire_ht': self.prix_unitaire_ht,
            'piece_id': self.piece_id
        }
# Modèle pour le Planning
class Planning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    work_description = db.Column(db.Text, nullable=False)
    technician_name = db.Column(db.String(100))
    car_registration = db.Column(db.String(20))
    
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = db.relationship('Client', backref=db.backref('planning_events', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'start_datetime': self.start_datetime.isoformat(),
            'work_description': self.work_description,
            'technician_name': self.technician_name,
            'car_registration': self.car_registration,
            'client_id': self.client_id,
            'client': self.client.to_dict() # Inclut les détails du client
        }

# NOUVEAU: Modèle pour les Fournisseurs
class Fournisseur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    contact_person = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adresse = db.Column(db.String(200))
    delai_livraison_moyen = db.Column(db.Integer) # Délai en jours

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# NOUVEAU: Modèle pour les Remises Fournisseur
class RemiseFournisseur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('fournisseur.id'), nullable=False)
    piece_category = db.Column(db.String(100), nullable=False) # Ex: "Moteur", "Freinage", "Carrosserie"
    remise_pourcentage = db.Column(db.Float, nullable=False)

    fournisseur = db.relationship('Fournisseur', backref=db.backref('remises', lazy=True))

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

@app.route('/api/clients/search', methods=['GET', 'POST'])
def search_clients_unified():
    if request.method == 'GET':
        # Recherche rapide pour le formulaire de facture
        search_term = request.args.get('q', '')
        if not search_term or len(search_term) < 2:
            return jsonify([])
        clients = Client.query.filter(Client.nom.ilike(f'%{search_term}%')).limit(10).all()
        return jsonify([client.to_dict() for client in clients])
    
    if request.method == 'POST':
        # Recherche détaillée depuis l'onglet "Clients"
        data = request.get_json()
        query = Client.query
        nom = data.get('nom')
        prenom = data.get('prenom')
        code_postal = data.get('code_postal')
        if nom:
            query = query.filter(Client.nom.ilike(f'%{nom}%'))
        if prenom:
            query = query.filter(Client.prenom.ilike(f'%{prenom}%'))
        if code_postal:
            query = query.filter(Client.code_postal.ilike(f'%{code_postal}%'))
        clients = query.all()
        return jsonify({'clients': [client.to_dict() for client in clients]})

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    # Récupère le client par son ID, ou renvoie une erreur 404 s'il n'existe pas.
    client = Client.query.get_or_404(client_id)

    # Vérification de sécurité : ne pas supprimer un client s'il a des factures associées.
    # La relation `client.factures` nous permet de vérifier cela facilement.
    if client.factures:
        # Renvoie une erreur claire au frontend avec le statut 400 (Bad Request).
        return jsonify({'message': 'Impossible de supprimer ce client, il est lié à des factures existantes.'}), 400

    db.session.delete(client)
    db.session.commit()
    return jsonify({'message': 'Client supprimé avec succès!'})

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

# Route unifiée pour la recherche de pièces
@app.route('/api/pieces/search', methods=['GET', 'POST'])
def search_pieces_unified():
    if request.method == 'GET':
        # Recherche rapide pour le formulaire de facture
        search_term = request.args.get('q', '')
        if not search_term or len(search_term) < 2:
            return jsonify([])
        
        # Recherche dans la désignation ou la référence
        pieces = Piece.query.filter(
            or_(
                Piece.designation.ilike(f'%{search_term}%'),
                Piece.ref.ilike(f'%{search_term}%')
            )
        ).limit(10).all()
        return jsonify([piece.to_dict() for piece in pieces])

    if request.method == 'POST':
        # Recherche détaillée depuis l'onglet "Pièces"
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

# --- NOUVEAU: Routes pour la Main d'oeuvre ---

@app.route('/api/maindoeuvre', methods=['POST'])
def add_maindoeuvre():
    data = request.get_json()
    if not data or not data.get('description') or data.get('taux_horaire') is None:
        return jsonify({'message': 'Les champs description et taux horaire sont requis'}), 400
    try:
        taux_horaire = float(data['taux_horaire'])
    except (ValueError, TypeError):
        return jsonify({'message': 'Le taux horaire doit être un nombre valide'}), 400
    
    new_item = MainDoeuvre(
        description=data['description'],
        taux_horaire=taux_horaire
    )
    db.session.add(new_item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Renvoie une erreur claire si la description est déjà utilisée (contrainte "unique")
        return jsonify({'message': 'Erreur : cette description de main d\'oeuvre existe déjà.'}), 409

    return jsonify({'message': 'Type de main d\'oeuvre ajouté avec succès!', 'maindoeuvre': new_item.to_dict()}), 201

@app.route('/api/maindoeuvre/search', methods=['POST'])
def search_maindoeuvre():
    data = request.get_json()
    query = MainDoeuvre.query
    description = data.get('description')
    if description:
        query = query.filter(MainDoeuvre.description.ilike(f'%{description}%'))
    items = query.all()
    return jsonify({'maindoeuvre': [item.to_dict() for item in items]})

@app.route('/api/maindoeuvre/<int:item_id>', methods=['PUT'])
def update_maindoeuvre(item_id):
    item = MainDoeuvre.query.get_or_404(item_id)
    data = request.get_json()
    if not data or not data.get('description') or data.get('taux_horaire') is None:
        return jsonify({'message': 'Les champs description et taux horaire sont requis'}), 400
    
    try:
        taux_horaire = float(data['taux_horaire'])
    except (ValueError, TypeError):
        return jsonify({'message': 'Le taux horaire doit être un nombre valide'}), 400

    # Vérifie si la nouvelle description existe déjà pour un autre item
    existing_item = MainDoeuvre.query.filter(MainDoeuvre.description == data['description'], MainDoeuvre.id != item_id).first()
    if existing_item:
        return jsonify({'message': 'Erreur : cette description de main d\'oeuvre existe déjà.'}), 409

    item.description = data['description']
    item.taux_horaire = taux_horaire
    db.session.commit()
    return jsonify({'message': 'Type de main d\'oeuvre mis à jour avec succès!', 'maindoeuvre': item.to_dict()})

@app.route('/api/maindoeuvre/<int:item_id>', methods=['DELETE'])
def delete_maindoeuvre(item_id):
    item = MainDoeuvre.query.get_or_404(item_id)
    
    # Sécurité : Vérifie si ce type de main d'oeuvre est utilisé dans des factures
    usage_count = FactureLigne.query.filter_by(description=item.description).count()
    if usage_count > 0:
        return jsonify({'message': f'Impossible de supprimer "{item.description}", car il est utilisé dans {usage_count} facture(s).'}), 400

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Type de main d\'oeuvre supprimé avec succès!'})
# --- Routes pour les Factures ---

@app.route('/api/factures', methods=['POST'])
def create_facture():
    data = request.get_json()

    if not data or not data.get('client_id') or not data.get('lignes'):
        return jsonify({'message': 'Données de facture incomplètes'}), 400

    # Validation : Vérifier que le client existe
    client = Client.query.get(data.get('client_id'))
    if not client:
        return jsonify({'message': f"Erreur : Le client avec l'ID {data.get('client_id')} n'a pas été trouvé."}), 404

    # Calcul des totaux côté serveur pour la sécurité
    total_ht = sum(float(ligne['quantite']) * float(ligne['prix_unitaire_ht']) for ligne in data['lignes'])
    total_ttc = total_ht * 1.20 # En supposant une TVA de 20%

    nouvelle_facture = Facture(
        numero_facture=data['numero_facture'],
        client_id=data['client_id'],
        informations_complementaires=data.get('informations_complementaires'),
        total_ht=total_ht,
        total_ttc=total_ttc
    )

    for ligne_data in data['lignes']:
        nouvelle_ligne = FactureLigne(
            description=ligne_data['description'],
            quantite=float(ligne_data['quantite']),
            prix_unitaire_ht=float(ligne_data['prix_unitaire_ht']),
            piece_id=ligne_data.get('piece_id')
        )
        nouvelle_facture.lignes.append(nouvelle_ligne)

    db.session.add(nouvelle_facture)
    db.session.commit()

    return jsonify({'message': 'Facture sauvegardée avec succès!', 'facture': nouvelle_facture.to_dict()}), 201

@app.route('/api/factures/search', methods=['GET'])
def search_factures():
    search_term = request.args.get('q', '')
    # Log de débogage pour voir les termes de recherche dans la console Flask
    print(f"--- Recherche de factures avec le terme : '{search_term}'")

    if not search_term or len(search_term) < 2:
        return jsonify([])

    # Recherche par numéro de facture OU par nom/prénom du client associé
    query = Facture.query.join(Client).filter(
        or_(
            Facture.numero_facture.ilike(f'%{search_term}%'),
            Client.nom.ilike(f'%{search_term}%'),
            Client.prenom.ilike(f'%{search_term}%')
        )
    ).order_by(Facture.date_creation.desc())

    factures = query.limit(20).all() # On limite les résultats pour la performance

    # Log de débogage pour voir combien de résultats la requête a retournés
    print(f"--- Nombre de factures trouvées : {len(factures)}")

    return jsonify([facture.to_dict() for facture in factures])

@app.route('/api/factures/<int:facture_id>/pdf')
def generate_facture_pdf(facture_id):
    facture = Facture.query.get_or_404(facture_id)

    # FONCTION CRUCIALE: Nettoie le texte pour fpdf2 en forçant l'encodage latin-1
    # et en remplaçant les caractères non supportés pour éviter les crashs.
    def sanitize_text(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, sanitize_text(f'Facture N°: {facture.numero_facture}'), 0, 1, 'C')
            self.set_font('Arial', '', 10)
            self.cell(0, 10, sanitize_text(f"Date: {facture.date_creation.strftime('%d/%m/%Y')}"), 0, 1, 'C')
            self.ln(20)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, sanitize_text(f'Page {self.page_no()}'), 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()

    # Informations du client
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, sanitize_text('Client:'), 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 6, sanitize_text(f"{facture.client.prenom} {facture.client.nom}"), 0, 1, 'L')
    pdf.cell(0, 6, sanitize_text(f"{facture.client.adresse}"), 0, 1, 'L')
    pdf.cell(0, 6, sanitize_text(f"{facture.client.code_postal} {facture.client.ville}"), 0, 1, 'L')
    pdf.ln(10)

    # Tableau des lignes de facture
    pdf.set_font('Arial', 'B', 11)
    col_width = [110, 25, 45] # Description, Quantité, Prix Unitaire HT
    pdf.cell(col_width[0], 8, sanitize_text('Description'), 1, 0, 'C')
    pdf.cell(col_width[1], 8, sanitize_text('Qté'), 1, 0, 'C')
    pdf.cell(col_width[2], 8, sanitize_text('Prix U. HT'), 1, 1, 'C')

    pdf.set_font('Arial', '', 10)
    for ligne in facture.lignes:
        pdf.cell(col_width[0], 8, sanitize_text(ligne.description), 1)
        pdf.cell(col_width[1], 8, sanitize_text(ligne.quantite), 1, 0, 'C')
        pdf.cell(col_width[2], 8, sanitize_text(f"{ligne.prix_unitaire_ht:.2f} EUR"), 1, 1, 'R')

    # Totaux
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(135, 8, sanitize_text('Total HT:'), 0, 0, 'R')
    pdf.cell(45, 8, sanitize_text(f"{facture.total_ht:.2f} EUR"), 1, 1, 'R')
    pdf.cell(135, 8, sanitize_text('Total TTC (TVA 20%):'), 0, 0, 'R')
    pdf.cell(45, 8, sanitize_text(f"{facture.total_ttc:.2f} EUR"), 1, 1, 'R')

    # Solution robuste pour gérer les incohérences de type de retour de fpdf2
    pdf_output = pdf.output(dest='B')
    
    # S'assurer que la sortie est bien en bytes, sinon l'encoder.
    # fpdf2 utilise l'encodage 'latin-1' en interne pour ses sorties string.
    if isinstance(pdf_output, str):
        pdf_bytes = pdf_output.encode('latin-1')
    else:
        pdf_bytes = pdf_output

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={'Content-Disposition': f'attachment;filename=facture_{facture.numero_facture}.pdf'}
    )
# Routes pour le Planning ---

@app.route('/api/planning', methods=['GET'])
def get_planning_events(): # MODIFIÉ pour filtrer par date
    """
    Récupère les événements du planning, filtrés par date de début et de fin si spécifiées.
    Paramètres GET: start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)
    """
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = Planning.query
    if start_date_str:
        query = query.filter(Planning.start_datetime >= datetime.fromisoformat(start_date_str))
    if end_date_str:
        # Ajouter un jour pour inclure toute la journée de fin
        query = query.filter(Planning.start_datetime < datetime.fromisoformat(end_date_str) + timedelta(days=1))
    
    events = query.order_by(Planning.start_datetime.asc()).all()
    return jsonify([event.to_dict() for event in events])

@app.route('/api/planning', methods=['POST'])
def create_planning_event():
    """Crée un nouvel événement dans le planning."""
    data = request.get_json()
    if not all(k in data for k in ['client_id', 'start_datetime', 'work_description']):
        return jsonify({'message': 'Données manquantes (client_id, start_datetime, work_description requis)'}), 400

    client = Client.query.get(data['client_id'])
    if not client:
        return jsonify({'message': 'Client non trouvé'}), 404

    try:
        # Convertit la date du format ISO (envoyé par JS) en objet datetime Python
        start_dt = datetime.fromisoformat(data['start_datetime'])
    except (ValueError, TypeError):
        return jsonify({'message': 'Format de date invalide. Utilisez le format ISO 8601.'}), 400

    new_event = Planning(
        client_id=data['client_id'],
        start_datetime=start_dt,
        work_description=data['work_description'],
        technician_name=data.get('technician_name'),
        car_registration=data.get('car_registration')
    )
    db.session.add(new_event)
    db.session.commit()

    return jsonify({'message': 'Intervention planifiée avec succès!', 'event': new_event.to_dict()}), 201

# --- NOUVEAU: Routes pour les Fournisseurs ---

@app.route('/api/fournisseurs', methods=['GET'])
def get_fournisseurs():
    search_term = request.args.get('q', '')
    query = Fournisseur.query
    if search_term:
        query = query.filter(Fournisseur.nom.ilike(f'%{search_term}%'))
    fournisseurs = query.order_by(Fournisseur.nom.asc()).all()
    return jsonify([f.to_dict() for f in fournisseurs])

@app.route('/api/fournisseurs', methods=['POST'])
def add_fournisseur():
    data = request.get_json()
    
    # Validation plus robuste pour éviter les crashs si le JSON est invalide ou vide
    if not isinstance(data, dict):
        return jsonify({'message': 'Données JSON invalides ou vides fournies'}), 400
    if not data.get('nom'):
        return jsonify({'message': 'Le nom du fournisseur est requis'}), 400
    
    if Fournisseur.query.filter_by(nom=data['nom']).first():
        return jsonify({'message': 'Un fournisseur avec ce nom existe déjà'}), 409

    new_fournisseur = Fournisseur(
        nom=data['nom'],
        contact_person=data.get('contact_person'),
        telephone=data.get('telephone'),
        email=data.get('email'),
        adresse=data.get('adresse'),
        delai_livraison_moyen=data.get('delai_livraison_moyen')
    )
    db.session.add(new_fournisseur)
    db.session.commit()
    return jsonify({'message': 'Fournisseur ajouté avec succès!', 'fournisseur': new_fournisseur.to_dict()}), 201

@app.route('/api/fournisseurs/<int:fournisseur_id>', methods=['GET'])
def get_fournisseur(fournisseur_id):
    fournisseur = Fournisseur.query.get_or_404(fournisseur_id)
    return jsonify(fournisseur.to_dict())

@app.route('/api/fournisseurs/<int:fournisseur_id>', methods=['PUT'])
def update_fournisseur(fournisseur_id):
    fournisseur = Fournisseur.query.get_or_404(fournisseur_id)
    data = request.get_json()

    # Validation plus robuste pour éviter les crashs
    if not isinstance(data, dict):
        return jsonify({'message': 'Données JSON invalides ou vides fournies'}), 400

    # Validation robuste : Vérifier la présence du nom et son unicité
    new_nom = data.get('nom')
    if not new_nom:
        return jsonify({'message': 'Le nom du fournisseur est requis'}), 400

    if Fournisseur.query.filter(Fournisseur.nom == new_nom, Fournisseur.id != fournisseur_id).first():
        return jsonify({'message': 'Un autre fournisseur avec ce nom existe déjà'}), 409

    fournisseur.nom = new_nom
    fournisseur.contact_person = data.get('contact_person', fournisseur.contact_person)
    fournisseur.telephone = data.get('telephone', fournisseur.telephone)
    fournisseur.email = data.get('email', fournisseur.email)
    fournisseur.adresse = data.get('adresse', fournisseur.adresse)
    fournisseur.delai_livraison_moyen = data.get('delai_livraison_moyen', fournisseur.delai_livraison_moyen)
    db.session.commit()
    return jsonify({'message': 'Fournisseur mis à jour avec succès!', 'fournisseur': fournisseur.to_dict()})

@app.route('/api/fournisseurs/<int:fournisseur_id>', methods=['DELETE'])
def delete_fournisseur(fournisseur_id):
    fournisseur = Fournisseur.query.get_or_404(fournisseur_id)
    db.session.delete(fournisseur)
    db.session.commit()
    return jsonify({'message': 'Fournisseur supprimé avec succès!'})

# --- NOUVEAU: Routes pour les Remises Fournisseur ---

@app.route('/api/fournisseurs/<int:fournisseur_id>/remises', methods=['GET'])
def get_fournisseur_remises(fournisseur_id):
    remises = RemiseFournisseur.query.filter_by(fournisseur_id=fournisseur_id).all()
    return jsonify([r.to_dict() for r in remises])

@app.route('/api/fournisseurs/<int:fournisseur_id>/remises', methods=['POST'])
def add_fournisseur_remise(fournisseur_id):
    data = request.get_json()
    if not all(k in data for k in ['piece_category', 'remise_pourcentage']):
        return jsonify({'message': 'Catégorie de pièce et pourcentage de remise sont requis'}), 400
    new_remise = RemiseFournisseur(fournisseur_id=fournisseur_id, **data)
    db.session.add(new_remise)
    db.session.commit()
    return jsonify({'message': 'Remise ajoutée avec succès!', 'remise': new_remise.to_dict()}), 201

# --- Initialisation ---
if __name__ == '__main__':
    # Crée les tables dans la base de données si elles n'existent pas
    with app.app_context():
        db.create_all()
    
    # Lance le serveur de développement
    app.run(debug=True, host='127.0.0.1', port=8000) # L'application sera accessible depuis d'autres machines sur le réseau
