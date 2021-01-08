from flask import Flask
from neo4j import GraphDatabase
app = Flask(__name__)

# class Connector:
#     def __init__(self, uri, user, password):
#         self.driver = GraphDatabase.driver(uri, auth=(user, password))

#     def close(self):
#         self.driver.close()

#     def get_instruments(self):
#         with self.driver.session() as session:
#             instruments = session.write_transaction(self._get_instrument)
#             return instruments

#     @staticmethod
#     def _get_instrument(tx):
#         result = tx.run("MATCH (n:Instrument) RETURN n LIMIT 25")
#         return result.single()[0]

# c = Connector()


# @app.route('/instruments', methods=['GET'])
# def instruments():
#     return c.get_instruments()

@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
