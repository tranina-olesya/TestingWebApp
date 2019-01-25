from __init__ import db
from config import ROLE_ADMIN, ROLE_USER
from __init__ import lm
from flask_login import UserMixin


@lm.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password = db.Column(db.String(128))
    role = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "Id: {}, Login: {}, Role: {}".format(self.id, self.login, self.role)


class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return "Id: {}, Name: {}".format(self.id, self.name)


class Tests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    name = db.Column(db.String)

    def __repr__(self):
        return "Id: {}, Subject: {}, Name: {}".format(self.id, self.subject_id, self.name)


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))
    question_text = db.Column(db.String)
    question_type = db.Column(db.String)
    
    def __repr__(self):
        return "Id: {}, Test: {}, Text: {}, Type: {}".format(self.id, self.test_id, self.question_text, self.question_type)
    

class Attempt(db.Model):
    __tablename__ = 'attempts'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.Integer)

    def __repr__(self):
        return "Id: {}, Test: {}, User: {}".format(self.id, self.test_id, self.user_id)


class AnswerChoices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_text = db.Column(db.String)
    
    def __repr__(self):
        return "Id: {}, Question: {}, Answer: {}".format(self.id, self.question_id, self.answer_text)
    

class ChosenAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer_choices.id'))
    answer_text = db.Column(db.String)

    def __repr__(self):
        return "Id: {}, Question: {}, Attempt: {}, Answer: {}, Text: {}".format(self.id, self.question_id, self.attempt_id, self.answer_id, self.answer_text)


class CorrectAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey('answer_choices.id'))

    def __repr__(self):
        return "Id: {}, Question: {}, Answer: {}".format(self.id, self.question_id, self.answer_text)
