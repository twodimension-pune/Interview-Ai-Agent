from flask import Flask, render_template, request, redirect, session, url_for
from openai_utils import ask_question, evaluate_answer
from evaluation import generate_pdf_report
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['username']
        return redirect(url_for('select_profile'))
    return render_template('login.html')

@app.route('/select_profile', methods=['GET', 'POST'])
def select_profile():
    if request.method == 'POST':
        session['profile'] = request.form['profile']
        session['score_total'] = 0
        session['questions_answered'] = 0
        session['hr_score'] = 0
        session['hr_questions_answered'] = 0
        session['asked_tech'] = []
        session['asked_hr'] = []

        if session['profile'] == 'technical':
            return redirect(url_for('interview'))
        elif session['profile'] == 'hr':
            return redirect(url_for('hr_round'))
        else:
            return redirect(url_for('interview'))
    return render_template('select_profile.html')

@app.route('/interview', methods=['GET', 'POST'])
def interview():
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        feedback, score = evaluate_answer(question, answer)

        session['score_total'] += score
        session['questions_answered'] += 1

        if session['questions_answered'] >= 5:
            avg_score = session['score_total'] / 5
            if session.get('profile') == 'both':
                if avg_score >= 6:
                    return redirect(url_for('hr_round'))
                else:
                    session['result'] = 'Fail'
                    generate_pdf_report(session['user'], 'Technical + HR', 'Fail', session['score_total'], 0)
                    return redirect(url_for('result'))
            else:
                session['result'] = 'Pass' if avg_score >= 6 else 'Fail'
                generate_pdf_report(session['user'], 'Technical Only', session['result'], session['score_total'])
                return redirect(url_for('result'))

        question = ask_question('tech', session)
        return render_template("interview.html", question=question, feedback=feedback)
    else:
        question = ask_question('tech', session)
        return render_template("interview.html", question=question)

@app.route('/hr', methods=['GET', 'POST'])
def hr_round():
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        feedback, score = evaluate_answer(question, answer)

        session['hr_score'] += score
        session['hr_questions_answered'] += 1

        if session['hr_questions_answered'] >= 3:
            avg_hr_score = session['hr_score'] / 3
            session['result'] = 'Pass' if avg_hr_score >= 6 else 'Fail'
            generate_pdf_report(session['user'], 'Technical + HR', session['result'], session['score_total'], session['hr_score'])
            return redirect(url_for('result'))

        question = ask_question('hr', session)
        return render_template("interview.html", question=question, feedback=feedback)
    else:
        question = ask_question('hr', session)
        return render_template("interview.html", question=question)

@app.route('/result')
def result():
    profile = session.get('profile', 'technical')
    return render_template("result.html", result=session.get('result'), profile=profile)

if __name__ == '__main__':
    app.run(debug=True)
