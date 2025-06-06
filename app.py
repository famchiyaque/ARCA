from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'secret'  # Use a better one in production

current_presentation_state = {'section': 'intro'}

with open('questions.json') as f:
    QUESTIONS = json.load(f)

# -- Database Helper --
def get_db():
    conn = sqlite3.connect('survey.db')
    conn.row_factory = sqlite3.Row
    return conn

# -- Routes --

@app.route("/")
def presentation():
    if current_presentation_state['section'] == 'show_results':
        return redirect("/show_results")
    return render_template("presentation.html")

@app.route("/get_presentation_state")
def get_presentation_state():
    return jsonify(current_presentation_state)

@app.route("/set_presentation", methods=["POST"])
def set_presentation():
    global current_presentation_state
    section = request.form.get("section")
    if section:
        current_presentation_state['section'] = section
    return redirect("/admin")


@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        name = request.form['name']
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name) VALUES (?)", (name,))
        user_id = cur.lastrowid
        conn.commit()
        conn.close()
        session['user_id'] = user_id
        return redirect(url_for('question', number=1))
    return render_template('start.html')

@app.route('/question/<int:number>', methods=['GET'])
def question(number):
    if number > len(QUESTIONS):
        return redirect(url_for('waiting', number='end'))
    question = QUESTIONS[number - 1]
    return render_template('question.html', question=question, scenario_number=number)

@app.route('/answer', methods=['POST'])
def answer():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('start'))

    number = int(request.form['scenario_number'])
    answer_index = int(request.form['answer'])  # this will be the index of the selected option
    question = QUESTIONS[number - 1]
    selected_option = question['options'][answer_index]
    resource_delta = selected_option.get('resourceDelta', 0)

    print(user_id)
    print(number)
    print(answer_index)
    print(selected_option)
    print(resource_delta)

    conn = get_db()
    cur = conn.cursor()

    # Save the answer (store the option index as answer)
    cur.execute("INSERT INTO answers (user_id, question_number, answer) VALUES (?, ?, ?)",
                (user_id, number, str(answer_index)))

    # Update resources
    if resource_delta > 0:
        cur.execute("UPDATE users SET resources = resources - ? WHERE id = ?", (resource_delta, user_id))

    conn.commit()
    conn.close()

    if number >= len(QUESTIONS):
        return redirect(url_for('waiting', number='end'))
    else:
        return redirect(url_for('waiting', number=number))


# @app.route('/answer', methods=['POST'])
# def answer():
#     user_id = session.get('user_id')
#     print(user_id)
#     if user_id is None:
#         return redirect(url_for('start'))

#     number = int(request.form['scenario_number'])
#     answer = request.form['answer']
#     print(number)
#     print(answer)

#     conn = get_db()
#     conn.execute("INSERT INTO answers (user_id, question_number, answer) VALUES (?, ?, ?)",
#                  (user_id, number, answer))
#     conn.commit()
#     conn.close()

#     if number >= len(QUESTIONS):
#         return redirect(url_for('waiting', number='end'))
#     else:
#         return redirect(url_for('waiting', number=number))

# @app.route('/waiting/<number>')
# def waiting(number):
#     if number == 'end':
#         return render_template('waiting.html', scenario_number="End of Questions")
#     return render_template('waiting.html', scenario_number=number)

@app.route('/waiting/<number>')
def waiting(number):
    if number != 'end':
        number = int(number)
    return render_template('waiting.html', scenario_number=number)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/reset_database', methods=['POST'])
def reset_db():
    conn = sqlite3.connect('survey.db')
    c = conn.cursor()

    c.execute("DELETE FROM users;")
    c.execute("DELETE FROM answers;")

    conn.commit()
    conn.close()
    return render_template('admin.html')

@app.route('/admin/show_results')
def show_results():
    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    total_resources = 0
    results = []

    for user in users:
        total_resources += user["resources"]
        answers = conn.execute(
            "SELECT question_number, answer FROM answers WHERE user_id=? ORDER BY question_number",
            (user['id'],)
        ).fetchall()
        user_answers = [(QUESTIONS[a['question_number'] - 1], a['answer']) for a in answers]
        results.append({
            "name": user["name"],
            "resources": user["resources"],
            "answers": user_answers
        })

    avg_resources = total_resources / len(users) if users else 0

    return render_template('results.html', users=results, avg_resources=avg_resources)


# @app.route('/admin/show_results')
# def show_results():
#     conn = get_db()
#     users = conn.execute("SELECT * FROM users").fetchall()
#     results = []
#     for user in users:
#         answers = conn.execute(
#             "SELECT question_number, answer FROM answers WHERE user_id=? ORDER BY question_number",
#             (user['id'],)
#         ).fetchall()
#         user_answers = [(QUESTIONS[a['question_number'] - 1], a['answer']) for a in answers]
#         # Simple verdict logic: if 3+ yes, success
#         yes_count = sum(1 for _, a in user_answers if a == "yes")
#         verdict = "SUCCESS" if yes_count >= 3 else "FAILURE"
#         results.append({
#             "name": user["name"],
#             "verdict": verdict,
#             "answers": user_answers
#         })
#     return render_template('results.html', users=results)
