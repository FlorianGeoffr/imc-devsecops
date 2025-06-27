# Projet DevSecOps

## Calcul IMC, CI/CD sécurisé et scan de vulnérabilités

Nom de l’étudiant : Florian GEOFFRENET
Date : 27/06/2025

---

## 1. Présentation du projet

### Objectifs pédagogiques

Ce projet vise à initier les étudiants à la démarche DevSecOps au travers d’une application simple de calcul d’IMC, incluant :

·        Le développement Python/Flask avec connexion à une base de données MySQL.

·        La création et la gestion de conteneurs Docker.

·        La mise en place d’un pipeline CI/CD via GitHub Actions.

·        L’intégration de la sécurité avec les outils Trivy (scan d’image) et Snyk (scan de dépendances).

·        Le déploiement automatique sur DockerHub.

### Architecture DevSecOps

### ![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXcRy3_r88Ac-UGa2xi-7D6xUwp8HUW_Lb52Qce8L7slOzFdZgsw1709JYF7cwqt9_qKKLiLSrdynOzPeNWTBbAjcmuz0Gcy8Ukf63T5wxitlfiDTJVs41LK_DIEv-XMhXAOT24Zgg?key=ZBr-y8wXccpo_dxFQNeMow)

---

## 2. Développement de l’application

### Code de l’application Flask (app/app.py)

| from flaskimportFlask, request, jsonify<br />importmysql.connector<br /><br />app = Flask(__name__)<br /><br />def get_db_connection():<br /> returnmysql.connector.connect(<br />host="db",<br />user="root",<br />password="root",<br />database="imc_db"<br />)<br /><br />@app.route('/')<br />defhome():<br /> return "Bienvenue dans l'application de calcul IMC !"<br /><br />@app.route('/imc', methods=['POST'])<br />def calcul_imc():<br />data = request.get_json()<br />poids = data.get("poids")<br />taille = data.get("taille")<br /><br /> if notpoidsor nottaille:<br /> returnjsonify({"error":"Poids et taille requis"}),400<br /><br />imc = round(poids / (taille **2),2)<br /><br />conn = get_db_connection()<br /> cursor= conn.cursor()<br /> cursor.execute("INSERT INTO imc_values (poids, taille, imc) VALUES (%s, %s, %s)", (poids, taille, imc))<br />conn.commit()<br /> cursor.close()<br />conn.close()<br /><br /> returnjsonify({"IMC": imc}),200<br /><br />if__name__ =="__main__":<br />app.run(host='0.0.0.0', port=5000) |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

### Connexion à MySQL

Connexion via le connecteur mysql-connector-python, hébergée dans un conteneur db MySQL séparé.

### Fichier app/requirements.txt

| flask<br />mysql-connector-python |
| ------------------------------- |

### Structure des fichiers

| imc-devsecops/<br />├── app/<br />│   ├── app.py<br />│   ├── requirements.txt<br />│   └── Dockerfile<br />├── db/<br />│   ├── init.sql<br />│   └── Dockerfile<br />├── .github/workflows/ci-cd.yml<br />├── docker-compose.yml<br />└── README.md |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

---

## 3. Conteneurisation avec Docker

### Dockerfile (app)

| FROMpython:3.11-slim<br />WORKDIR/app<br />COPY. .<br />RUNpip install --no-cache-dir -r requirements.txt<br />EXPOSE 5000<br />CMD["python","app.py"] |
| ------------------------------------------------------------------------------------------------------------------------------------ |

### Dockerfile (db)

| FROMmysql:8.0<br />ENVMYSQL_ROOT_PASSWORD=root<br />ENVMYSQL_DATABASE=imc_db<br />COPYinit.sql /docker-entrypoint-initdb.d/ |
| ----------------------------------------------------------------------------------------------------------------- |

### Script SQL db/init.sql

| CREATE DATABASE IF NOT EXISTSimc_db;<br />USEimc_db;<br /><br />CREATE TABLE IF NOT EXISTSimc_values (<br /> id INTAUTO_INCREMENT PRIMARYKEY,<br />poidsFLOAT,<br />tailleFLOAT,<br />imcFLOAT<br />); |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |

### Docker Compose (optionnel pour tests locaux)

Permet de lancer les deux conteneurs ensemble avec un réseau commun.

| version:'3.8'<br /> services:<br /> web:<br />  build: ./app<br />  ports:<br />  -"5000:5000"<br />  depends_on:<br />  - db<br /> db:<br />  build: ./db<br />  environment:<br />  MYSQL_ROOT_PASSWORD: root<br />  MYSQL_DATABASE: imc_db<br />  ports:<br />  -"3306:3306" |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

---

## 

## 4. Pipeline CI/CD

### Fichier .github/workflows/ci-cd.yml

| name: CI/CD Pipeline<br /><br />on:<br />push:<br />branches: [ "main" ]<br /><br />jobs:<br />build:<br />runs-on: ubuntu-latest<br /><br />steps:<br />- uses: actions/checkout@v3<br /><br />- uses: docker/setup-buildx-action@v2<br /><br />- uses: docker/login-action@v2<br />with:<br />username: ${{ secrets.DOCKERHUB_USERNAME }}<br />password: ${{ secrets.DOCKERHUB_TOKEN }}<br /><br />- uses: docker/build-push-action@v5<br />with:<br />context: ./app<br />push: true<br />tags: ${{ secrets.DOCKERHUB_USERNAME }}/imc-web:latest<br /><br />- uses: docker/build-push-action@v5<br />with:<br />context: ./db<br />push: true<br />tags: ${{ secrets.DOCKERHUB_USERNAME }}/imc-db:latest<br /><br />- name: Scan image with Trivy<br />uses: aquasecurity/trivy-action@master<br />with:<br />image-ref: ${{ secrets.DOCKERHUB_USERNAME }}/imc-web:latest<br /><br />- name: Scan image with Trivy<br />uses: aquasecurity/trivy-action@master<br />with:<br />image-ref: ${{ secrets.DOCKERHUB_USERNAME }}/imc-db:latest<br /><br />- name: Set up Python<br />uses: actions/setup-python@v4<br />with:<br />python-version: 3.11<br /><br />- name: Install Python dependencies<br />run: pip install -r app/requirements.txt<br /><br />- name: Download Snyk CLI<br />run: \|<br />curl -Lo snyk https://static.snyk.io/cli/latest/snyk-linux<br />chmod +x snyk<br />mv snyk /usr/local/bin/<br /><br />- name: Authenticate with Snyk<br />run: snyk auth ${{ secrets.SNYK_TOKEN }}<br /><br />- name: Scan dependencies with Snyk<br />run: snyk test --file=app/requirements.txt --project-name=imc-web |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

### Logs GitHub Actions

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXf_B_SlSDthKLKtiO9MtUUQsWEPbEvv_C9_qGznQOm-WIOXcDECJyOhT3ua7f-opFhJqY6J3cmdx1QVKhqZ5VzODOnRxybpHHpZDNi-RSk0AMfnREsaVXt19R5K-ajvL38KWcS29g?key=ZBr-y8wXccpo_dxFQNeMow)

---

## 

## 5. Sécurité DevSecOps

### Trivy (scan image Docker)

Outil open-source intégré au pipeline pour identifier les CVE dans les layers de l’image Docker.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfih0WE_LdP64NEEkJwa0jXDE1wdCo1X7if-76IOzJZ9N4lcTUtIi8E1jbrhNHMj3WcZF6IMMRS5coeUahiru-qaTRX2jIIpIonS3QFbLziHoka8kYnjYTStx7-hmXGrTwzcf-E?key=ZBr-y8wXccpo_dxFQNeMow)

### Snyk (scan de dépendances Python)

Permet d’analyser les vulnérabilités dans requirements.txt, directement dans GitHub Actions.![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXclBJBbCjPZiOqau_wL_IhwEsefxEp2rp4SPAXlCAomB-1Ba1QR8pbuAsJbtLFl4tcDvPnrT2_zjFFM9cLVgmqS2PjN7gEuNKpe6ECYXtJH7GqaTPFfmMsoiyIdSpaJaUl5I8VE?key=ZBr-y8wXccpo_dxFQNeMow)

---

## 

## 6. Publication DockerHub

Les images suivantes sont automatiquement publiées grâce au pipeline :

·        imc-web:latest

·        imc-db:latest

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXde6iEJexlKtqiN1LebmQOBXHN7PI378T_VSJGAcyuOP_QUo25EeTeNDbOmb3cI6muKMMHzt1TA--yb6VbhD_dS1zWn5rdGASL9WgN0bm-S7QG9DlFTVJhyFErUiiKohsqlG89W9w?key=ZBr-y8wXccpo_dxFQNeMow)

---

## 7. Tests & Exemples

### Test via Postman

Requête POST : http://localhost:5000/imc
 Corps JSON :

| {<br /> "poids":70,<br /> "taille":1.75<br />} |
| ------------------------------------ |

Réponse attendue :

| {<br /> "IMC":22.86<br />} |
| -------------------- |

![image](https://github.com/user-attachments/assets/3d6edb7a-5251-42e1-8d07-7ebd36443e90)

---
