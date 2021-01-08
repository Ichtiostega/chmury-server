from flask import Flask
from neo4j import GraphDatabase
app = Flask(__name__)

class Connector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_instruments(self):
        with self.driver.session() as session:
            instruments = session.write_transaction(self._get_instrument)
            retuer instruments

    @staticmethod
    def _get_instrument(tx):
        result = tx.run("MATCH (n:Instrument) RETURN n LIMIT 25")
        return result.single()[0]

c = Connector()


@app.route('/instruments', methods=['GET'])
def instruments():
    return c.get_instruments()

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
