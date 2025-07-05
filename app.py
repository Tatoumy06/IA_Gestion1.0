from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

# Initialise l'application Flask
app = Flask(__name__, static_folder='.', static_url_path='')
# Permettre les requêtes cross-origin si besoin (API séparée)
CORS(app)

# Configuration de la base SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'gestion.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class RepairOrder(db.Model):
    __tablename__ = 'repair_orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'vehicle_model': self.vehicle_model,
            'license_plate': self.license_plate,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Technician(db.Model):
    __tablename__ = 'technicians'
    __table_args__ = {'extend_existing': True}

    id                = db.Column(db.Integer,   primary_key=True)
    nom               = db.Column(db.String(100), nullable=False)
    prenom            = db.Column(db.String(100), nullable=False)
    adresse           = db.Column(db.String(200))
    code_postal       = db.Column(db.String(20))
    ville             = db.Column(db.String(100))
    date_naissance    = db.Column(db.Date)
    email             = db.Column(db.String(120))
    telephone         = db.Column(db.String(20))
    numero_technicien = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'adresse': self.adresse,
            'code_postal': self.code_postal,
            'ville': self.ville,
            'date_naissance': self.date_naissance.isoformat() if self.date_naissance else None,
            'email': self.email,
            'telephone': self.telephone,
            'numero_technicien': self.numero_technicien
        }

# Route principale : sert le fichier index.html
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# API GET : récupérer tous les ordres
@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = RepairOrder.query.order_by(RepairOrder.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

# API POST JSON : créer un ordre via fetch
@app.route('/api/orders', methods=['POST'])
def create_order_api():
    data = request.get_json() or {}
    try:
        order = RepairOrder(
            customer_name=data['customer_name'],
            vehicle_model=data['vehicle_model'],
            license_plate=data['license_plate'],
            description=data['description']
        )
        db.session.add(order)
        db.session.commit()
        return jsonify(order.to_dict()), 201
    except KeyError:
        return jsonify({'error': 'Champs manquants'}), 400

# Route POST formulaire : route de secours pour formulaire HTML classique
@app.route('/orders', methods=['POST'])
def create_order_form():
    customer_name = request.form.get('customer_name')
    vehicle_model = request.form.get('vehicle_model')
    license_plate = request.form.get('license_plate')
    description = request.form.get('description')
    if not all([customer_name, vehicle_model, license_plate, description]):
        return "Tous les champs sont requis", 400
    order = RepairOrder(
        customer_name=customer_name,
        vehicle_model=vehicle_model,
        license_plate=license_plate,
        description=description
    )
    db.session.add(order)
    db.session.commit()
    return redirect(url_for('serve_index'))

# Création des tables dans le contexte de l'application avant de démarrer
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=8000)
