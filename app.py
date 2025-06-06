from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'secret'  # Use a better one in production

current_presentation_state = {'section': 'intro'}
pointsDomo = 0
pointsFuera = 0

with open('questions.json', encoding='utf-8') as f:
    QUESTIONS = json.load(f)

with open('waitings.json', encoding='utf-8') as f:
    WAITINGS = json.load(f)

# -- Routes --

@app.route("/")
def presentation():
    global pointsDomo, pointsFuera
    if current_presentation_state['section'] == 'show_results':
        return render_template('results.html', pointsDomo=pointsDomo, pointsFuera=pointsFuera)
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

@app.route('/start', methods=['GET'])
def start():
    return render_template('start.html')

@app.route('/question/<int:number>', methods=['GET'])
def question(number):    
    if number > len(QUESTIONS):
        return redirect(url_for('waiting', number='end'))
    question = QUESTIONS[number - 1]
    return render_template('question.html', question=question, scenario_number=number)

@app.route('/answer', methods=['POST'])
def answer():
    global pointsDomo, pointsFuera

    number = int(request.form['scenario_number'])
    answer_index = int(request.form['answer'])  # this will be the index of the selected option
    question = QUESTIONS[number - 1]
    selected_option = question['options'][answer_index]
    alignment = selected_option['alignment']

    if alignment == 'Domo':
        pointsDomo += 1
    elif alignment == 'Fuera':
        pointsFuera += 1

    if number >= len(QUESTIONS):
        return redirect(url_for('waiting', number=5))
    else:
        return redirect(url_for('waiting', number=number))
    
def isReset():
    global pointsFuera, pointsDomo

    if pointsFuera == 0 and pointsDomo == 0:
        return True
    else:
        return False


@app.route('/waiting/<number>')
def waiting(number):
    if isReset():
        return render_template('start.html')

    if number != 'end':
        number = int(number)
    waiting = WAITINGS[number - 1]
    return render_template('waiting.html', waiting=waiting, scenario_number=number)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/reset_sim', methods=['GET'])
def reset_db():
    global pointsDomo, pointsFuera
    pointsDomo = 0
    pointsFuera = 0
    current_presentation_state['section'] = 'intro'
    return render_template('admin.html')

@app.route('/end_sim', methods=['GET'])
def end_sim():
    current_presentation_state['section'] = 'show_results'
    return redirect(url_for('admin'))

@app.route('/show_results')
def show_results():
    global pointsDomo, pointsFuera

    if pointsDomo == 0 and pointsFuera == 0:
        return redirect(url_for('presentation'))

    return render_template('results.html', pointsDomo=pointsDomo, pointsFuera=pointsFuera)
