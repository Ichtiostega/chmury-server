import flask
from flask_cors import CORS
from neo4j import GraphDatabase
app = flask.Flask(__name__)
CORS(app)

class Connector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_instruments(self):
        with self.driver.session() as session:
            result = session.run("MATCH (n:u7kocierz)-[:manufacturer]->(m:u7kocierz) RETURN n AS instrument, m AS producer")
            out = {'instruments': []}
            for record in result:
                out['instruments'].append({'name': record['instrument']['name'], 'price': record['instrument']['price'], 'manufacturer': record['producer']['name']})
            return out

    def suggest_instruments(self, type, min, max):
        with self.driver.session() as session:
            result = session.run('MATCH (o)<-[:manufacturer]-(n)-[r:of_type]->(m) WHERE m.name=$type AND n.price >= $min AND n.price <= $max RETURN n AS instrument, o AS producer', type=type, min=min, max=max)
            out = {'suggested instruments': []}
            for record in result:
                out['instruments'].append({'name': record['instrument']['name'], 'price': record['instrument']['price'], 'manufacturer': record['producer']['name']})
            return out

    def instrument_producers(self, type):
        with self.driver.session() as session:
            result = session.run('MATCH (n:u7kocierz)<-[:manufacturer]-()-[:of_type]->(m:u7kocierz) WHERE m.name=$type RETURN DISTINCT n as producer', type=type)
            out = {type + ' producers': []}
            for record in result:
                out[type + ' producers'].append({'name': record['producer']['name']})
            return out


c = Connector('bolt://149.156.109.37:7687', 'u7kocierz', '293170')


@app.route('/instruments', methods=['GET'])
def instruments():
    response = flask.jsonify(c.get_instruments())
    return response

@app.route('/instruments/suggestions/<string:type>/<int:min>/<int:max>', methods=['GET'])
def instruments_suggestions(type, min, max):
    response = flask.jsonify(c.suggest_instruments(type, min, max))
    return response

@app.route('/instruments/producers/<string:type>', methods=['GET'])
def instruments_producers(type):
    response = flask.jsonify(c.instrument_producers(type))
    return response

@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
