import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):  # Given by workshop exercise
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs

  --DONE

  '''

    CORS(app, resources={"/": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow

  --DONE

  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.

  DONE

  '''
    @app.route('/categories')
    def get_categoties():
        all_categories = Category.query.all()
        categories = {}
        for category in all_categories:
            categories[category.id] = category.type
        return jsonify({
            'success': True,
            'categories': categories
        })
    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.

  DONE

  '''

    @app.route('/questions')
    def get_questions_with_pagination():
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)
        all_categories = Category.query.all()
        categories = {}
        for category in all_categories:
            categories[category.id] = category.type
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': categories
        })
    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.

  DONE

  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_quesions': len(Question.query.all())
            })
        except:
            abort(422)

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.

  DONE

  '''

    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        add_new_question = Question(
            question=new_question, answer=new_answer, difficulty=difficulty, category=category)
        add_new_question.insert()

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'created': add_new_question.id,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
        })

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.

  DONE

  '''

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        selection = Question.query.order_by(
            Question.id).filter(Question.question.ilike('%{}%'.format(search_term)))

        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'searched_questions': len(selection.all())
        })

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.

  DONE

  '''

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        category = Category.query.filter(
            Category.id == category_id).one_or_none()
        selection = Question.query.filter(
            Question.category == category.id).all()

        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection)
        })
    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

    @app.route('/quizzes', methods=['POST'])
    def play_the_quiz():
        body = request.get_json()
        category = body['quiz_category']['id']
        print(category)
        previous_questions = body['previous_questions']
        if(category == 0):
            current_category = Question.query.all()
        else:
            current_category = Question.query.filter(
                Question.category == category).all()
        print(current_category)
        answered_question = False
        current_question = random.choice(current_category).format()
        if current_question['id'] in previous_questions:
            answered_question = True
        while answered_question:
            current_question = random.choice(current_category).format()
            if(len(previous_questions) == len(current_category)):
                return jsonify({
                    'success': True,
                    'message': "game over"
                }), 200
        print(current_question)
        print(previous_questions)
        return jsonify({
            'success': True,
            'question': current_question
        })

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  
  --DONE
  
  '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app
