from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="db",
        user="root",
        password="root",
        database="imc_db"
    )

@app.route('/')
def home():
    return "Bienvenue dans l'application de calcul IMC !"

@app.route('/imc', methods=['POST'])
def calcul_imc():
    data = request.get_json()
    poids = data.get("poids")
    taille = data.get("taille")

    if not poids or not taille:
        return jsonify({"error": "Poids et taille requis"}), 400

    imc = round(poids / (taille ** 2), 2)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO imc_values (poids, taille, imc) VALUES (%s, %s, %s)", (poids, taille, imc))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"IMC": imc}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
