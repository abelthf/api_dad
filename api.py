import os
from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '../data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH

db = SQLAlchemy(app)


class ValidationError(ValueError):
    """Simple validacion de error"""
    pass


class Customer(db.Model):
    """Clase que define al consumidor"""
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    def get_url(self):
        """Obtiene el url del cliente."""
        return url_for('get_customer', id=self.id, _external=True)

    def export_data(self):
        """Exporta la data almacenada."""
        return {
            'self_url': self.get_url(),
            'name': self.name
        }

    def import_data(self, data):
        """Importa data definida en el uri."""
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Cliente no valido: missing' + e.args[0])
        return self

@app.route('/customers/', methods=['GET'])
def get_customers():
    """Obtiene todos los clientes almacenados en la db."""
    return jsonify({
        'customers': [customer.get_url() for customer in Customer.query.all()]
        })

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    """Obtiene el cliente en funcion al id indicado."""
    return jsonify(Customer.query.get_or_404(id).export_data())

@app.route('/customers/', methods=['POST'])
def new_customer():
    """Crea un nuevo cliente."""
    customer = Customer()
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({}), 201, {'Location': customer.get_url()}

app.route('/customers/<int:id>', methods=['PUT'])
def edit_customer(id):
    """Edita los datos de un cliente en funcion al id."""
    customer = Customer.query.get_or_404(id)
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
