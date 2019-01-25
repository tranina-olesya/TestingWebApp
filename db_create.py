from sqlalchemy import Column, Integer, String, Date, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///testing.db',echo=True, encoding='utf-8')
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String, nullable=False)
    role = Column(Integer, nullable=False)

    def __init__(self, login, first_name, last_name, password, role=0):
        self.login = login
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.role = role

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s', '%s', '%s')>" % (self.login, self.first_name, self.last_name, self.date_of_birth, self.password, self.role)


class Subjects(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Subject('%s')>" % self.name


class Tests(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    name = Column(String, nullable=False)

    def __init__(self, subject_id, name):
        self.subject_id = subject_id
        self.name = name

    def __repr__(self):
        return "<Test('%s', '%s')>" % (self.subject_id, self.name)


class Questions(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    question_text = Column(String, nullable=False)
    question_type = Column(String, nullable=False)

    def __init__(self, test_id, question_text, question_type):
        self.test_id = test_id
        self.question_text = question_text
        self.question_type = question_type

    def __repr__(self):
        return "<Questions('%s', '%s', '%s')>" % (self.test_id, self.question_text, self.question_type)


class Attempt(Base):
    __tablename__ = 'attempts'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    score = Column(Integer)

    def __init__(self, test_id, user_id, score, number):
        self.test_id = test_id
        self.user_id = user_id
        self.score = score

    def __repr__(self):
        return "<TestResults('%s', '%s', '%s')>" % (self.test_id, self.user_id, self.score)


class AnswerChoices(Base):
    __tablename__ = 'answer_choices'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer_text = Column(String, nullable=False)

    def __init__(self, question_id, answer_text):
        self.question_id = question_id
        self.answer_text = answer_text

    def __repr__(self):
        return "<AnswerChoices('%s', '%s')>" % (self.question_id, self.answer_text)


class ChosenAnswers(Base):
    __tablename__ = 'chosen_answers'
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey('attempts.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_id = Column(Integer, ForeignKey('answer_choices.id'))
    answer_text = Column(String)

    def __init__(self, attempt_id, question_id, answer_id, answer_text):
        self.attempt_id = attempt_id
        self.question_id = question_id
        self.answer_id = answer_id
        self.answer_text = answer_text

    def __repr__(self):
        return "<ChosenAnswers('%s', '%s', '%s', '%s')>" % (self.attempt_id, self.question_id, self.answer_id, self.answer_text)


class CorrectAnswers(Base):
    __tablename__ = 'correct_answers'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_id = Column(Integer, ForeignKey('answer_choices.id'))

    def __init__(self, question_id, answer_id):
        self.question_id = question_id
        self.answer_id = answer_id

    def __repr__(self):
        return "<CorrectAnswers('%s', '%s')>" % (self.question_id, self.answer_id)


Base.metadata.create_all(engine)