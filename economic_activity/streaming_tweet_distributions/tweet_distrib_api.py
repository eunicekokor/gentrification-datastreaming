import flask
import redis
import collections

app = flask.Flask(__name__)
conn = redis.Redis()

def buildHistogram():
    '''
    Returns unnormalized histogram of tweet events in each neighborhood
    '''
    keys = conn.keys()
    values = conn.mget(keys)
    c = collections.Counter(values)
    return {k:v for k,v in c.items()}

@app.route("/distrib")
def distribution():
    '''
    Returns unnormalized distribution of tweet events in each neighborhood
    '''
    dist = buildHistogram()
    return flask.jsonify(**dist)

if __name__ == "__main__":
    app.run()
