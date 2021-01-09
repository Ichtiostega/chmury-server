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
    def _gen_suggest_query(type, genres = [], producers = [], musicians = [], min=None, max=None):
        args = {'type': type}
        args['query'] = 'MATCH (n:Type:u7kocierz)<-[]-(m:Instrument)-[]->(o:Genre:u7kocierz),(p:Musician:u7kocierz)<-[]-(m:Instrument)-[]->(q:Company) WHERE n.name=$type'
        for i, genre in enumerate(genres):
            args['genre'+str(i)] = genre
            if i==0:
                args['query'] += ' AND '
                args['query'] += '(o.name=$genre'+str(i)
            else:
                args['query'] += ' OR o.name=$genre'+str(i)
            if i==(len(genres)-1):
                args['query'] += ')'
        for i, producer in enumerate(producers):
            args['producer'+str(i)] = producer
            if i==0:
                args['query'] += ' AND '
                args['query'] += '(q.name=$producer'+str(i)
            else:
                args['query'] += ' OR q.name=$producer'+str(i)
            if i==(len(producers)-1):
                args['query'] += ')'
        for i, musician in enumerate(musicians):
            args['musician'+str(i)] = musician
            if i==0:
                args['query'] += ' AND '
                args['query'] += '(p.name=$musician'+str(i)
            else:
                args['query'] += ' OR p.name=$musician'+str(i)
            if i==(len(musicians)-1):
                args['query'] += ')'
        if min:
            args['query'] += ' AND m.price>=$min'
            args['min'] = min
        if max:
            args['query'] += ' AND m.price<=$max'
            args['max'] = max
        args['query'] += ' RETURN m AS instrument, n AS type, o AS genre, p AS musician, q AS producer'
        print(args)
        return args





    def get_instruments(self):
        with self.driver.session() as session:
            result = session.run("MATCH (n:u7kocierz)-[:manufacturer]->(m:u7kocierz) RETURN n AS instrument, m AS producer")
            out = {'instruments': []}
            for record in result:
                out['instruments'].append({'name': record['instrument']['name'], 'price': record['instrument']['price'], 'manufacturer': record['producer']['name']})
            return out

    def suggest_instruments(self, type, genres = [], producers = [], musicians = [], min=None, max=None):
        with self.driver.session() as session:
            print(type, genres, producers, musicians, min, max)
            result = session.run(**self._gen_suggest_query(type, genres, producers, musicians, min, max))
            out = {'suggested instruments': []}
            for record in result:
                out['suggested instruments'].append({'name': record['instrument']['name'], 'price': record['instrument']['price'], 'manufacturer': record['producer']['name']})
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

@app.route('/instruments/suggestions/<string:type>', methods=['POST'])
def instruments_suggestions(type):
    body = flask.request.json
    print(type, body)
    response = flask.jsonify(c.suggest_instruments(type, **body))
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
    # print(c.suggest_instruments('Guitar', ['Rock', 'Punk'], ['Fender', 'Gibson'], ['David Gilmour', 'Jimmy Page'], 1000, 3000))
