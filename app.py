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

    @staticmethod
    def _checked_add(login, k, v, session):
        res0 = session.run("MATCH (n:user:u7kocierz) WHERE n.name=$login RETURN n AS x", login=login)
        record = res0.single()
        if not record:
            session.run("CREATE (n:user:u7kocierz {name:$login})", login=login)

        res1 = session.run("MATCH (n:"+k+":u7kocierz) WHERE n.name=$v RETURN n AS x", v=v)
        record = res1.single()
        if not record:
            session.run("CREATE (n:"+k+":u7kocierz {name:$v})", k=k, v=v)
        
        res2 = session.run("MATCH (m:user:u7kocierz)-[r:likes]->(n:"+k+":u7kocierz) WHERE n.name=$v AND m.name=$login RETURN r AS x", v=v, login=login)
        record = res2.single()
        if not record:
            session.run("MATCH (m:user:u7kocierz),(n:"+k+":u7kocierz) WHERE n.name=$v AND m.name=$login CREATE (m)-[r:likes]->(n)", v=v, login=login)


    def get_instruments(self):
        with self.driver.session() as session:
            result = session.run("MATCH (n:u7kocierz)<-[:manufactures]-(m:u7kocierz) RETURN n AS instrument, m AS producer")
            out = {'instruments': []}
            for record in result:
                out['instruments'].append({'name': record['instrument']['name'], 'price': record['instrument']['price'], 'manufacturer': record['producer']['name']})
            return out
    
    def save_preferences(self, login, data):
        with self.driver.session() as session:
            for k, v in data.items():
                self._checked_add(login, k, v, session)

    def get_suggestion(self, login, min, max):
        print(login, min, max)
        with self.driver.session() as session:
            result = session.run("MATCH (n:user:u7kocierz)-[:likes]->()-[]->(m:instrument:u7kocierz) WHERE n.name=$login AND m.price>=$min AND m.price<=$max RETURN DISTINCT m AS instrument, count(m) AS c ORDER BY c DESC LIMIT 1", login=login, min=min, max=max)
            record = result.single()
            if record:
                return {'Recommended instrument': [{'name': record['instrument']['name'], 'price': record['instrument']['price']}]}
            else:
                return {'Recommended instrument': [{'name': 'None available', 'price': 0}]}

    def instrument_producers(self, type):
        with self.driver.session() as session:
            result = session.run('MATCH (n:u7kocierz)-[:manufactures]->()<-[:subtype]-(m:u7kocierz) WHERE m.name=$type RETURN DISTINCT n as producer', type=type)
            out = {type + ' producers': []}
            for record in result:
                out[type + ' producers'].append({'name': record['producer']['name']})
            return out

    def instrument_popularity(self):
        with self.driver.session() as session:
            result = session.run('MATCH (n)-[r:plays]->(m) RETURN m AS instrument, count(m) AS amount')
            out = {'Instrument popularity': []}
            for record in result:
                out['Instrument popularity'].append({'name': record['instrument']['name'], 'amount': record['amount']})
            return out

    def instrument_type_cost(self, type, min, max):
        with self.driver.session() as session:
            result = session.run('MATCH (m:u7kocierz)-[:subtype]->(n:u7kocierz) WHERE n.price>=$min AND n.price<=$max AND m.name=$type RETURN n AS instrument', type=type, min=min, max=max)
            out = {'Available instruments': []}
            for record in result:
                out['Available instruments'].append({'name': record['instrument']['name'], 'price': record['instrument']['price']})
            return out

c = Connector('bolt://149.156.109.37:7687', 'u7kocierz', '293170')


@app.route('/instruments', methods=['GET'])
def instruments():
    response = flask.jsonify(c.get_instruments())
    return response

@app.route('/preferences/<string:login>', methods=['POST'])
def preferences(login):
    body = flask.request.json
    response = flask.jsonify(c.save_preferences(login, body))
    return response

@app.route('/suggestion/<string:login>/<int:min>/<int:max>', methods=['GET'])
def suggestion(login, min, max):
    response = flask.jsonify(c.get_suggestion(login, min, max))
    return response


@app.route('/instruments/producers/<string:type>', methods=['GET'])
def instruments_producers(type):
    response = flask.jsonify(c.instrument_producers(type))
    return response

@app.route('/instruments/popularity', methods=['GET'])
def instruments_popularity():
    response = flask.jsonify(c.instrument_popularity())
    return response

@app.route('/instruments/<string:type>/<int:min>/<int:max>', methods=['GET'])
def instrument_type_cost(type, min, max):
    response = flask.jsonify(c.instrument_type_cost(type, min, max))
    return response

@app.route('/')
def index():
    return "<h1>You requested in the wrong neighborhood friend!</h1>"

if __name__ == '__main__':
    app.run(threaded=True, port=5000)

