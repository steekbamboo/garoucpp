from flask import Flask, render_template, request, session
import sqlite3
app = Flask(__name__)
app.secret_key = 'tamere'


def checkDatabase():
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM ext""")
    rows = cursor.fetchall()
    db.close()
    moment = rows[0][0]

    roles = {}
    votes = {}
    vivants = []
    villageois = []
    loups = []
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM users""")
    rows = cursor.fetchall()
    db.close()
    for row in rows:
        roles[row[1]] = row[3]
        votes[row[1]] = row[4]
        if row[3] is not None:
            vivants.append(row[1])
            if row[3] != 'loup':
                villageois.append(row[1])
            else:
                loups.append(row[1])
    if moment == 'voteVillage':

        cibles = {}
        for a in vivants:
            cibles[a] = 0
        i = 0
        for a in roles:
            if roles[a] is not None:
                if votes[a] is not None:
                    cibles[votes[a]] += 1
                    i += 1
        if i == len(vivants):
            choisi = max(cibles, key=cibles.get)
            db = sqlite3.connect('users.db')
            cursor = db.cursor()
            cursor.execute("""UPDATE users SET role = NULL WHERE username = ?""", (choisi,))
            cursor.execute("""UPDATE users SET vote = NULL""")
            db.commit()
            db.close()
            db = sqlite3.connect('users.db')
            cursor = db.cursor()
            cursor.execute("""UPDATE ext SET moment = "loups" """)
            cursor.execute("""UPDATE ext SET lastDead = ? """, (choisi,))
            cursor.execute("""UPDATE ext SET causeDeath = "le vote du village" """)
            cursor.execute("""UPDATE ext SET roleDeath = ? """, (roles[choisi],))
            db.commit()
            db.close()
    if moment == 'loups':
        cibles = {}
        for a in villageois:
            cibles[a] = 0
        i = 0
        for a in loups:
            if votes[a] is not None:
                cibles[votes[a]] += 1
                i += 1
        if i == len(loups):
            choisi = max(cibles, key=cibles.get)
            db = sqlite3.connect('users.db')
            cursor = db.cursor()
            cursor.execute("""UPDATE users SET role = NULL WHERE username = ?""", (choisi,))
            cursor.execute("""UPDATE users SET vote = NULL""")
            db.commit()
            db.close()
            db = sqlite3.connect('users.db')
            cursor = db.cursor()
            cursor.execute("""UPDATE ext SET moment = "voteVillage" """)
            cursor.execute("""UPDATE ext SET lastDead = ? """, (choisi,))
            cursor.execute("""UPDATE ext SET causeDeath = "les loups" """)
            cursor.execute("""UPDATE ext SET roleDeath = ? """, (roles[choisi],))
            db.commit()
            db.close()


@app.route('/login', methods=['GET', 'POST'])
def form():
    try:
        session.pop('username', None)
        session.pop('password', None)
    except:
        None
    return render_template('form.html', message='Connectez vous', type='connection')


@app.route('/signin', methods=['GET', 'POST'])
def formSignIn():
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM ext""")
    rows = cursor.fetchall()
    db.close()
    moment = rows[0][0]

    if moment == 'start':
        return render_template('form.html', message='Inscrivez vous', type='inscription')
    else:
        return render_template('partieEnCours.html')


@app.route('/voteAll', methods=['GET', 'POST'])
def voteAll():
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM users""")
    rows = cursor.fetchall()
    db.close()
    vivants = []
    loups = []
    for row in rows:
        if row[3] is not None:
            vivants.append(row[1])
        if row[3] == 'loup':
            loups.append(row[1])
    if session['username'] in loups:
        for i in range(len(vivants)):
            if vivants[i] in loups:
                vivants[i] = vivants[i] + " (loup garou)"
    return render_template('choix.html', vivants=vivants, nomduser=session['username'])


@app.route('/connection', methods=['GET', 'POST'])
def hello():
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM ext""")
    rows = cursor.fetchall()
    db.close()
    moment = rows[0][0]
    rip = (rows[0][1], rows[0][2], rows[0][3])
    try:
        nomduser = session['username']
        motdepasse = session['password']
    except:
        try:
            nomduser = request.form['say']
            motdepasse = request.form['to']
            session['username'] = request.form['say']
            session['password'] = request.form['to']
        except:
            return render_template('form.html', message='Connectez vous', type='connection')
    users = {}
    roles = {}
    votes = {}
    vivants = []
    loups = []
    morts = []
    villageois = []
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM users""")
    rows = cursor.fetchall()
    db.close()
    for row in rows:
        users[row[1]] = row[2]
        roles[row[1]] = row[3]
        votes[row[1]] = row[4]
        if row[3] is not None:
            vivants.append(row[1])
        if row[3] == 'loup':
            loups.append(row[1])
        if row[3] == 'villageois':
            villageois.append(row[1])
        if row[3] is None:
            morts.append(row[1])
    personnes = users.keys()
    if nomduser in personnes:
        if motdepasse == users[nomduser]:
            if moment == 'start':
                return render_template('lounge.html', nomduser=nomduser, users=personnes)
            else:
                if loups == []:
                    for a in roles:
                        if roles[a] is None:
                            roles[a] = "Mort"
                    return render_template('win.html', camp="villageois", roles=roles, rip=rip)
                elif villageois == []:
                    for a in roles:
                        if roles[a] is None:
                            roles[a] = "Mort"
                    return render_template('win.html', camp="loups", roles=roles, rip=rip)
                else:
                    if moment == 'voteVillage':
                        votesVivants = {}
                        for g in vivants:
                            if votes[g] is None:
                                votesVivants[g] = "N'a pas encore voté"
                            else:
                                votesVivants[g] = votes[g]
                        if nomduser in vivants:
                            return render_template('voteVillage.html', message="C'est le jour - tout le monde participe !", nomduser=nomduser, users=votesVivants, morts=morts, rip=rip)
                        else:
                            return render_template('voteVillage.html', message="Vous êtes mort - vous ne pouvez pas voter.", nomduser=nomduser, users=votesVivants, morts=morts, rip=rip)
                    elif moment == 'loups':
                        if roles[nomduser] == 'villageois':
                            return render_template('wait.html', nomduser=nomduser, vivants=vivants, morts=morts, rip=rip, moment=moment)
                        if roles[nomduser] == 'loup':
                            votesLoups = {}
                            for g in loups:
                                if votes[g] is None:
                                    votesLoups[g] = "N'a pas encore voté"
                                else:
                                    votesLoups[g] = votes[g]
                            return render_template('loungeGarous.html', nomduser=nomduser, users=votesLoups, vivants=vivants, morts=morts, rip=rip)
                        else:
                            return render_template('mort.html', nomduser=nomduser, vivants=vivants, morts=morts, rip=rip, moment=moment)
        else:
            try:
                session.pop('username', None)
                session.pop('password', None)
            except:
                None
            return render_template('form.html', message='Mot de passe incorrect', type='connection')
    else:
        return render_template('form.html', message='Utilisateur incorrect', type='connection')


@app.route('/inscription', methods=['GET', 'POST'])
def helloConnection():
    users = {}
    global nomduser
    nomduser = request.form['say']
    motdepasse = request.form['to']
    if nomduser != '':
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM users""")
        rows = cursor.fetchall()
        for row in rows:
            users[row[1]] = row[2]
        if nomduser in users.keys():
            return render_template('form.html', message="Nom d'utilisateur déjà pris", type='inscription')
        else:
            cursor.execute("""INSERT INTO users(id, username, password) VALUES(NULL, ?, ?)""", (nomduser, motdepasse))
            db.commit()
            db.close()
            try:
                session.pop('username', None)
                session.pop('password', None)
            except:
                None
            return(render_template("succes.html", choix="inscription de " + nomduser))
    else:
        return render_template('form.html', message='Mot de passe ou utilisateur vide', type='inscription')


@app.route('/', methods=['GET', 'POST'])
def accueil():
    return render_template('home.html')


@app.route('/choix', methods=['GET', 'POST'])
def choix():
    roles = {}
    votes = {}
    cibles = []
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM users""")
    rows = cursor.fetchall()
    db.close()
    for row in rows:
        roles[row[1]] = row[3]
        votes[row[1]] = row[4]
        if row[3] is not None:
            if row[3] != 'loup':
                cibles.append(row[1])
    try:
        if request.form['ok'] == 'Voter pour tuer un villageois':
            return render_template('choix.html', vivants=cibles, nomduser=session['username'])
        else:
            return(render_template("home.html"))
    except:
        return(render_template("home.html"))


@app.route('/succes', methods=['POST'])
def succes():
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("""UPDATE users SET vote = ? WHERE username = ?""", (request.form['nom'], session['username']))
    db.commit()
    db.close()
    checkDatabase()
    return(render_template("succes.html", choix="tuer " + request.form['nom']))


@app.route('/controle', methods=['POST', 'GET'])
def adminisration():
    return render_template('adminAuth.html')


@app.route('/administration', methods=['POST', 'GET'])
def admin():
    if request.form['mdp'] == 'qsdf':
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM ext""")
        rows = cursor.fetchall()
        db.close()
        moment = rows[0][0]
        users = {}
        roles = {}
        votes = {}
        vivants = []
        loups = []
        morts = []
        villageois = []
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute("""SELECT * FROM users""")
        rows = cursor.fetchall()
        db.close()
        for row in rows:
            users[row[1]] = row[2]
            roles[row[1]] = row[3]
            votes[row[1]] = row[4]
            if row[3] is not None:
                vivants.append(row[1])
            if row[3] == 'loup':
                loups.append(row[1])
            if row[3] == 'villageois':
                villageois.append(row[1])
            if row[3] is None:
                morts.append(row[1])
        personnes = users.keys()
        if request.form['hi'] == "Observer la partie":
            return(render_template('admin.html', moment=moment, users=users, roles=roles, votes=votes))
        elif request.form['hi'] == "Ouvrir les inscriptions":
            db = sqlite3.connect('users.db')
            cursor = db.cursor()
            cursor.execute("""UPDATE ext SET moment = "start" """)
            cursor.execute("""UPDATE ext SET lastDead = NULL """)
            cursor.execute("""UPDATE ext SET causeDeath = NULL """)
            cursor.execute("""UPDATE ext SET roleDeath = NULL """)
            cursor.execute("""DELETE FROM users""")
            db.commit()
            db.close()
            return("Done")
        elif request.form['hi'] == "Commencer une partie":
            nombre = len(users)
            if nombre < 8:
                nombregarous = 1
            elif nombre >= 8 and nombre < 12:
                nombregarous = 2
            elif nombre > 12:
                nombregarous = 3
            elif nombre > 18:
                nombregarous = 4
            import random
            definirGarous = random.sample(list(users), nombregarous)
            db = sqlite3.connect('users.db')
            cursor = db.cursor()
            cursor.execute("""UPDATE ext SET moment = "loups" """)
            for a in definirGarous:
                cursor.execute("""UPDATE users SET role = "loup" WHERE username = ?""", (a,))
            cursor.execute("""UPDATE users SET role = "villageois" WHERE role is NULL""")
            db.commit()
            db.close()
            return("Done")



if __name__ == "__main__":
    app.run()
