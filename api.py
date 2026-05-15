from flask import Flask, jsonify
import database as db

app = Flask(__name__)

@app.route("/data")
def data():
    return jsonify(db.dohvati_podatke())


@app.route("/status")
def status():
    return jsonify({"system": "AEGIS GRID active"})