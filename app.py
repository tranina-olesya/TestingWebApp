from flask import Flask, render_template, request, g, redirect, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import *
from sqlalchemy import func, sql
from enum import Enum
from forms import *
from __init__ import *


class QuestionsTypes(Enum):
    INPUT_ANSWER = 'INPUT_ANSWER'
    ONE_ANSWER = 'ONE_ANSWER'
    MANY_ANSWERS = 'MANY_ANSWERS'


@app.before_request
def before_request():
    g.user = current_user
    g.id = 0 if not g.user.is_authenticated else g.user.id


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(login=form.login.data.lower()).first()
        if user is None:
            flash("Неверное имя пользователя!")
        elif form.password.data == user.password:
            next = request.args.get('next')
            login_user(user)
        else:
            flash('Неверный пароль!')

    user = {'login': g.user.login if g.user.is_authenticated else 0,
            'full_name': g.user.first_name + ' ' + g.user.last_name if g.user.is_authenticated else 0}
    return render_template('main_page.html', form=form, logged_in=g.user.is_authenticated, user=user, subjects=list(Subjects.query.all()))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(login = form.login.data).first()
        if user is None:
            role = ROLE_USER
            user = Users(login=form.login.data, first_name=form.first_name.data, last_name=form.last_name.data, password=form.password.data, role=role)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/')
    return render_template("register.html", form=form)


@app.route('/subjects')
@login_required
def subjects():
    subjects = []
    for s in Subjects.query.all():
        tests = Tests.query.filter_by(subject_id=s.id)
        tests_count= len(list(tests))
        completed_tests_count = len(list(Attempt.query.with_entities(Attempt.test_id, Attempt.user_id).filter(Attempt.test_id.in_(t.id for t in tests), Attempt.user_id.is_(g.user.id)).distinct()))
        progress = round(completed_tests_count/tests_count*100) if tests_count > 0 else 0
        subjects.append({**vars(s), 'tests_count': tests_count, 'completed_tests_count': completed_tests_count, 'progress': progress})
    return render_template('subjects.html', subjects=subjects)


@app.route('/attempt', methods=['GET', 'POST'])
@login_required
def attempt():
    if request.method == 'POST':
        score = 0
        at = Attempt(test_id=int(request.values['test_id']), user_id=g.user.id, score=sql.null())
        db.session.add(at)
        at_id = db.session.query(func.max(Attempt.id)).first()[0]
        b = request.form
        for k in b:
            question = Questions.query.get(k)
            if question.question_type == QuestionsTypes.MANY_ANSWERS.value:
                answers = []
                for e in b.getlist(k):
                    ca = ChosenAnswers(attempt_id=at_id, question_id=k, answer_id=int(e))
                    answers.append(ca)
                    db.session.add(ca)
                cor_answers = list(ans.answer_id for ans in CorrectAnswers.query.filter_by(question_id=k))

                if len(cor_answers) == len(answers) and all((ans.answer_id in cor_answers)for ans in answers):
                    score += 1
            elif question.question_type == QuestionsTypes.ONE_ANSWER.value:
                ca = ChosenAnswers(attempt_id=at_id, question_id=k, answer_id=int(b[k]), answer_text=sql.null())
                db.session.add(ca)
                if CorrectAnswers.query.filter_by(question_id=k).first().answer_id == ca.answer_id:
                    score += 1
            else:
                ca = ChosenAnswers(attempt_id=at_id, question_id=k, answer_text=b[k].lower(), answer_id=sql.null())
                db.session.add(ca)
                cor_answer = AnswerChoices.query.get(CorrectAnswers.query.filter_by(question_id=k).first().answer_id)
                if cor_answer.answer_text == b[k]:
                    score += 1
        at.score = score
        #db.session.update(attempt)
        db.session.commit()
        return redirect("/attempts_view?test_id=" + request.values['test_id'])
    t = []

    for q in Questions.query.filter_by(test_id=request.values['test_id']):
        t.append({**vars(q), 'answers': tuple(AnswerChoices.query.filter_by(question_id=q.id))})
        #t.append({'id': q.id, 'question_text': q.question_text, 'question_type': q.question_type, 'answers': tuple(AnswerChoices.query.filter_by(question_id=q.id))})
    return render_template('attempt.html', questions=t, subjects=list(Subjects.query.all()), test=Tests.query.get(int(request.values['test_id'])).name)


@app.route('/attempts_view')
@login_required
def attempts_view():
    test_id = int(request.values['test_id'])
    attempts = list(Attempt.query.filter_by(test_id=test_id, user_id=g.user.id))
    attempts_count = len(attempts)
    questions_count = len(list(Questions.query.filter_by(test_id=test_id)))
    max_score = list(Attempt.query.with_entities(Attempt.test_id, Attempt.user_id, Attempt.score).group_by(Attempt.test_id, Attempt.user_id).filter_by(test_id=test_id, user_id=g.user.id).having(func.max(Attempt.score)))[0][2] / questions_count * 100 if attempts_count else 0
    attempts = list({**vars(att), 'percent_score': round(att.score / questions_count * 100)} for att in attempts)
    return render_template("attempts_view.html",
                           subjects=list(Subjects.query.all()), max_score=round(max_score),
                           test=Tests.query.get(test_id), attempts=attempts,
                           attempts_count=len(list(attempts)), question_number=questions_count)


@app.route('/attempt_view')
@login_required
def attempt_view():
    t = []
    attempt = list(Attempt.query.filter_by(id=request.values['attempt_id'], user_id=g.user.id))
    if not len(attempt):
        return redirect('/subjects')
    attempt = attempt[0]
    chosen_answers = tuple(ChosenAnswers.query.filter_by(attempt_id=attempt.id))
    for q in Questions.query.filter_by(test_id=attempt.test_id):
        answers = []
        for ans in AnswerChoices.query.filter_by(question_id=q.id):
            if Questions.query.get(ans.question_id).question_type == QuestionsTypes.INPUT_ANSWER.value:
                chosen = list(filter(lambda x: x.question_id == ans.question_id, chosen_answers))[0].answer_text
            else:
                chosen = ans.id in (a.answer_id for a in chosen_answers)
            answers.append({**vars(ans), 'chosen': chosen})
        t.append({**vars(q), 'answers': answers})
         #t.append({'id': q.id, 'question_text': q.question_text, 'question_type': q.question_type, 'answers': tuple(AnswerChoices.query.filter_by(question_id=q.id))})
    return render_template('attempt_view.html', questions=t, subjects=list(Subjects.query.all()), test=Tests.query.get(Attempt.query.get(int(request.values['attempt_id'])).id))


@app.route('/tests_view')
@login_required
def tests_view():
    result = []
    for t in Tests.query.filter_by(subject_id=request.values['subject_id']):
        attempts_count = len(list(Attempt.query.filter_by(test_id=t.id, user_id=g.user.id)))
        questions_count = len(list(Questions.query.filter_by(test_id=t.id)))
        max_score = list(Attempt.query.with_entities(Attempt.test_id, Attempt.user_id, Attempt.score).group_by(Attempt.test_id, Attempt.user_id).filter_by(test_id=t.id, user_id=g.user.id).having(func.max(Attempt.score)))[0][2] / questions_count * 100 if attempts_count else 0
        result.append({**vars(t), 'max_score': round(max_score), 'attempts_count': attempts_count})
    return render_template('tests_view.html', tests=result, subjects=list(Subjects.query.all()), subject=Subjects.query.get(request.values['subject_id']))


if __name__ == '__main__':
    app.run(debug=True)
