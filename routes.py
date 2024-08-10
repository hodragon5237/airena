from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore
from problem_handler import grade_answer, determine_skill_level
from gemini_api import generate_single_problem, continue_study_conversation, generate_study_room_intro, generate_intro_response
import random
from datetime import datetime, timedelta
from auth import login, callback, logout, refresh_token_if_needed
import re
from datetime import timedelta
from translations import get_translation
import os
import bleach
import logging
import json
import base64
from firebase_config import db

db = firestore.client()

main_bp = Blueprint('main', __name__)

def refresh_session():
    session.modified = True

@main_bp.route('/refresh_session', methods=['POST'])
def refresh_session_route():
    refresh_session()
    return jsonify({'message': 'Session refreshed'}), 200

@main_bp.route('/')
def index():
    refresh_token_if_needed()
    language = session.get('language', 'en')
    return render_template('main.html', logged_in='credentials' in session, get_translation=get_translation, language=language, RECAPTCHA_SITE_KEY=os.getenv('RECAPTCHA_SITE_KEY'))

@main_bp.route('/login', methods=['POST'])
def login_route():
    return login()

@main_bp.route('/auth/callback')
def callback_route():
    return callback()

@main_bp.route('/logout')
def logout_route():
    return logout()

@main_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@main_bp.route('/level_test')
def level_test():
    return render_template('index.html', RECAPTCHA_SITE_KEY=os.getenv('RECAPTCHA_SITE_KEY'))

@main_bp.route('/introduction')
def introduction():
    language = session.get('language', 'en')
    return render_template('index.html', RECAPTCHA_SITE_KEY=os.getenv('RECAPTCHA_SITE_KEY'))

@main_bp.route('/start_level_test', methods=['POST'])
def start_level_test():
    # session.clear()
    # session['google_id'] = request.form.get('google_id')
    # session['name'] = request.form.get('name')
    # session['email'] = request.form.get('email')
    
    problem_types = ['beginner', 'beginner_multiple_choice', 'elementary', 'elementary_multiple_choice', 
                     'intermediate', 'intermediate_multiple_choice', 'advanced', 'advanced_multiple_choice', 
                     'expert', 'expert_multiple_choice']
    session['levels'] = random.sample(problem_types, 10)
    session['current_problem'] = 0
    session['correct_answers'] = 0
    session['subject'] = request.json.get('subject', 'Python')
    return jsonify({'total_problems': len(session['levels'])})

@main_bp.route('/get_problem', methods=['GET'])
def get_problem():
    try:
        levels = session.get('levels', [])
        current_problem = session.get('current_problem', 0)
        
        if current_problem < len(levels):
            level = levels[current_problem]
            problem = generate_single_problem(level)
            
            if 'error' in problem:
                return jsonify(problem), 500
            else:
                problem.pop('level', None)
                session['current_problem_description'] = problem
                return jsonify(problem)
        else:
            return jsonify({'error': 'No more problems'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.before_request
def check_session():
    if 'google_id' in session:
        refresh_token_if_needed()
    elif request.endpoint not in ['main.login_route', 'main.callback_route', 'main.index']:
        return redirect(url_for('main.index'))  # 세션이 만료되면 main으로 리다이렉트

@main_bp.route('/start_study_room', methods=['POST'])
def start_study_room():
    google_id = session.get('google_id')
    if not google_id:
        return jsonify({'error': 'User not authenticated'}), 401

    user_ref = db.collection('users').document(google_id)
    user_data = user_ref.get().to_dict()

    if not user_data:
        return jsonify({'error': 'User data not found'}), 404

    last_level_test = user_data.get('level_test_results', [])
    if last_level_test:
        last_level_test_id = last_level_test[-1]
        last_level_test_ref = db.collection('level_test_results').document(last_level_test_id)
        last_level_test_data = last_level_test_ref.get().to_dict()
        current_skill_level = last_level_test_data.get('skill_level', 'beginner').lower()
    else:
        current_skill_level = 'beginner'

    next_skill_level = get_next_skill_level(current_skill_level)
    session['study_context'] = {
        'current_skill_level': current_skill_level,
        'next_skill_level': next_skill_level,
        'conversation': []
    }
    initial_message = generate_study_room_intro(current_skill_level, next_skill_level)
    session['study_context']['conversation'].append(('assistant', initial_message))
    return jsonify({'message': initial_message})

@main_bp.route('/submit_study_answer', methods=['POST'])
def submit_study_answer():
    data = request.json
    answer = bleach.clean(data.get('answer', ''))
    if len(answer) > 1000:  # 예시 길이 제한
        return jsonify({'error': 'Answer too long'}), 400
    study_context = session.get('study_context', {})
    if 'conversation' not in study_context:
        study_context['conversation'] = []
    study_context['conversation'].append(('user', answer))
    
    google_id = session.get('google_id')
    if not google_id:
        return jsonify({'error': 'User not authenticated'}), 401

    user_ref = db.collection('users').document(google_id)
    user_data = user_ref.get().to_dict()

    if not user_data:
        return jsonify({'error': 'User data not found'}), 404

    last_level_test = user_data.get('level_test_results', [])
    if last_level_test:
        last_level_test_id = last_level_test[-1]
        last_level_test_ref = db.collection('level_test_results').document(last_level_test_id)
        last_level_test_data = last_level_test_ref.get().to_dict()
        current_skill_level = last_level_test_data.get('skill_level', 'beginner').lower()
    else:
        current_skill_level = 'beginner'
    
    next_skill_level = get_next_skill_level(current_skill_level)
    
    response = continue_study_conversation(answer, study_context['conversation'], current_skill_level, next_skill_level)
    formatted_response = format_response(response)
    study_context['conversation'].append(('assistant', formatted_response))
    session['study_context'] = study_context
    
    return jsonify({'message': formatted_response})

def format_response(response):
    # 볼드 처리
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)
    # 줄바꿈 처리
    formatted = formatted.replace('<br>', '\n')
    return formatted

def evaluate_study_answer(answer, topic):
    # 이 함수는 사용자의 답변을 평가합니다.
    # 실제 구현에서는 더 복잡한 로직이 필요할 수 있습니다.
    return f"Thank you for your answer. Here's some feedback on the topic of {topic['topic']}..."

@main_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    user_answer = bleach.clean(data.get('answer', ''))
    if len(user_answer) > 1000:  # 예시 길이 제한
        return jsonify({'error': 'Answer too long'}), 400
    level = session['levels'][session['current_problem'] - 1]
    problem_description = session.get('current_problem_description')

    if user_answer is None:
        return jsonify({
            'is_correct': False,
            'feedback': 'No answer provided. Please enter a solution.',
            'current_problem': session['current_problem'],
            'total_problems': len(session['levels'])
        })

    is_correct, feedback = grade_answer(user_answer, problem_description, level)

    if is_correct:
        session['correct_answers'] += 1

    session['current_problem'] += 1

    return jsonify({
        'is_correct': is_correct,
        'feedback': feedback,
        'current_problem': session['current_problem'],
        'total_problems': len(session['levels'])
    })

@main_bp.route('/save_result', methods=['POST'])
def save_result():
    if 'google_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        correct_answers = session.get('correct_answers', 0)
        total_problems = len(session.get('levels', []))
        skill_level = determine_skill_level(correct_answers)

        test_result = {
            'date': datetime.now().isoformat(),
            'subject': session.get('subject', 'Python'),
            'score': correct_answers,
            'total_problems': total_problems,
            'skill_level': skill_level,
            'user_id': session['google_id'],
            'user_name': session.get('name', 'Unknown'),
            'user_email': session.get('email', 'Unknown')
        }

        result_ref = db.collection('level_test_results').document()
        result_ref.set(test_result)

        user_ref = db.collection('users').document(session['google_id'])
        user_ref.set({
            'email': session.get('email', 'Unknown'),
            'name': session.get('name', 'Unknown'),
            'level_test_results': firestore.ArrayUnion([result_ref.id])
        }, merge=True)

        return jsonify({'message': 'Result saved successfully', 'result_id': result_ref.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/get_result', methods=['GET'])
def get_result():
    try:
        correct_answers = session.get('correct_answers', 0)
        total_problems = len(session.get('levels', []))
        skill_level = determine_skill_level(correct_answers)
        
        return jsonify({
            'correct_answers': correct_answers,
            'total_problems': total_problems,
            'skill_level': skill_level
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({'message': 'Session reset successfully'})

# @main_bp.route('/profile', methods=['POST'])
# def update_profile():
#     data = request.json
#     uid = data.get('uid')
#     profile_data = data.get('profile')
#     try:
#         save_user_profile(uid, profile_data)
#         return jsonify({'message': 'Profile updated successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @main_bp.route('/profile/<uid>', methods=['GET'])
# def get_profile(uid):
#     try:
#         profile = get_user_profile(uid)
#         if profile:
#             return jsonify(profile), 200
#         else:
#             return jsonify({'error': 'Profile not found'}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @main_bp.route('/upload_profile_image', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image file'}), 400
#     image_file = request.files['image']
#     uid = request.form.get('uid')
#     try:
#         image_url = upload_profile_image(uid, image_file)
#         return jsonify({'image_url': image_url}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

@main_bp.route('/get_current_skill_level', methods=['GET'])
def get_current_skill_level():
    if 'google_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        refresh_session()
        user_ref = db.collection('users').document(session['google_id'])
        user_data = user_ref.get().to_dict()

        if user_data is None:
            return jsonify({'error': 'User data not found'}), 404

        last_level_test = user_data.get('level_test_results', [])
        if last_level_test:
            last_level_test_id = last_level_test[-1]
            last_level_test_ref = db.collection('level_test_results').document(last_level_test_id)
            last_level_test_data = last_level_test_ref.get().to_dict()
            return jsonify({'skill_level': last_level_test_data.get('skill_level', 'beginner')})
        return jsonify({'skill_level': 'beginner'})
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve user data: ' + str(e)}), 500

@main_bp.route('/start_stage', methods=['POST'])
def start_stage():
    if 'google_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401
    
    google_id = session.get('google_id')
    name = session.get('name')
    email = session.get('email')
    
    # session.clear()
    
    # session['google_id'] = google_id
    # session['name'] = name
    # session['email'] = email
    
    user_skill_level = request.json.get('skill_level', 'beginner')
    problem_types = {
        'beginner': ['beginner', 'beginner_multiple_choice'],
        'elementary': ['elementary', 'elementary_multiple_choice'],
        'intermediate': ['intermediate', 'intermediate_multiple_choice'],
        'advanced': ['advanced', 'advanced_multiple_choice'],
        'expert': ['expert', 'expert_multiple_choice']
    }
    
    available_problems = problem_types.get(user_skill_level, problem_types['beginner'])
    session['levels'] = random.sample(available_problems, min(4, len(available_problems)))
    session['levels'].extend(random.sample(available_problems, min(4, len(available_problems))))
    session['levels'].extend(random.sample(problem_types.get(get_next_skill_level(user_skill_level), problem_types['beginner']), 1))
    session['current_problem'] = 0
    session['stage_correct_answers'] = 0
    session['stage_incorrect_problems'] = []
    session['subject'] = request.json.get('subject', 'Python')

    return jsonify({'total_problems': len(session['levels'])})

@main_bp.route('/submit_stage_answer', methods=['POST'])
def submit_stage_answer():
    data = request.json
    user_answer = data.get('answer')
    current_problem = session.get('current_problem', 1)
    level = session['levels'][session['current_problem'] - 1]
    problem_description = session.get('current_problem_description')
    
    if user_answer is None:
        return jsonify({
            'is_correct': False,
            'feedback': 'No answer provided. Please enter a solution.',
            'current_problem': current_problem,
            'total_problems': len(session['levels'])
        })
    
    is_correct, feedback = grade_answer(user_answer, problem_description, level)
    
    if is_correct:
        session['stage_correct_answers'] = session.get('stage_correct_answers', 0) + 1
    else:
        session['stage_incorrect_problems'] = session.get('stage_incorrect_problems', [])
        session['stage_incorrect_problems'].append({
            'problem': problem_description,
            'level': level,
            'user_answer': user_answer
        })
    
    session['current_problem'] = current_problem + 1
    
    return jsonify({
        'is_correct': is_correct,
        'feedback': feedback,
        'current_problem': session['current_problem'],
        'total_problems': len(session['levels'])
    })

@main_bp.route('/complete_stage', methods=['POST'])
def complete_stage():
    if 'google_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        user_ref = db.collection('users').document(session['google_id'])
        user_data = user_ref.get().to_dict()
        # user_data = user_ref.get().to_dict()
        # current_xp = user_data.get('xp', 0)
        new_xp = session.get('stage_correct_answers', 0) * 10

        # 현재 사용자의 skill level 가져오기
        last_level_test = user_data.get('level_test_results', [])
        if last_level_test:
            last_level_test_id = last_level_test[-1]
            last_level_test_ref = db.collection('level_test_results').document(last_level_test_id)
            last_level_test_data = last_level_test_ref.get().to_dict()
            current_skill_level = last_level_test_data.get('skill_level', 'beginner')
        else:
            current_skill_level = 'beginner'
        
        stage_result = {
            'date': datetime.now().isoformat(),
            'XP': new_xp,
            'user_id': session['google_id'],
            'user_name': session.get('name', 'Unknown'),
            'user_email': session.get('email', 'Unknown'),
            'skill_level': current_skill_level  # 현재 skill level 추가
        }
        
        result_ref = db.collection('learning_stage_results').document()
        result_ref.set(stage_result)

        user_ref.set({
            'email': session.get('email', 'Unknown'),
            'name': session.get('name', 'Unknown'),
            'learning_stage_results': firestore.ArrayUnion([result_ref.id])
        }, merge=True)

        return jsonify({
            'message': 'Stage completed successfully',
            'result_id': result_ref.id,
            'xp_earned': new_xp,
            'skill_level': current_skill_level  # 응답에 skill level 추가
            }), 200
    except Exception as e:
        logging.error(f"Error in complete_stage: {str(e)}")
        return jsonify({'error': 'An internal error occurred'}), 500

@main_bp.route('/intro_chat', methods=['POST'])
def intro_chat():
    user_input = request.json.get('message')
    response = generate_intro_response(user_input)
    return jsonify({'message': response})

@main_bp.route('/get_weekly_leaderboard', methods=['GET'])
def get_weekly_leaderboard():
    try:
        skill_level = request.args.get('skill_level', 'Beginner')
        week = int(request.args.get('week', 0))
        current_user_email = session.get('email', '')

        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday() + 7 * week)
        end_of_week = start_of_week + timedelta(days=6)

        leaderboard = []
        users = db.collection('users').get()

        for user in users:
            user_data = user.to_dict()
            if user_data:
                learning_stage_results = user_data.get('learning_stage_results', [])
                total_xp = 0

                for result_id in learning_stage_results:
                    result = db.collection('learning_stage_results').document(result_id).get().to_dict()
                    if result and result.get('skill_level') == skill_level:
                        result_date = datetime.fromisoformat(result.get('date').replace('Z', '+00:00')).date()
                        if start_of_week.date() <= result_date <= end_of_week.date():
                            total_xp += result.get('XP', 0)

                if total_xp > 0:
                    leaderboard.append({
                        'name': user_data.get('name', 'Unknown'),
                        'email': user_data.get('email', 'Unknown'),
                        'xp': total_xp
                    })

        leaderboard = sorted(leaderboard, key=lambda x: x['xp'], reverse=True)
        
        top_10 = leaderboard[:10]
        for i, user in enumerate(top_10[:3]):
            user['trophy'] = ['🥇', '🥈', '🥉'][i]

        current_user_rank = next((index + 1 for index, user in enumerate(leaderboard) if user['email'] == current_user_email), None)
        current_user_data = next((user for user in leaderboard if user['email'] == current_user_email), None)

        response_data = {
            'week': week,
            'start_date': start_of_week.strftime('%Y-%m-%d'),
            'end_date': end_of_week.strftime('%Y-%m-%d'),
            'leaderboard': top_10,
            'current_user_email': current_user_email
        }

        if current_user_data:
            if current_user_rank > 10:
                response_data['current_user'] = {
                    'rank': current_user_rank,
                    'name': current_user_data['name'],
                    'xp': current_user_data['xp']
                }

        return jsonify(response_data)
    except Exception as e:
        print(f"get_weekly_leaderboard에서 오류 발생: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@main_bp.route('/profile')
def get_profile():
    # if 'google_id' not in session:
    #     return jsonify({'error': 'User not authenticated'}), 401

    if 'google_id' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        refresh_session()
        user_ref = db.collection('users').document(session['google_id'])
        user_data = user_ref.get().to_dict()

        if not user_data:
            return jsonify({'error': 'User data not found'}), 404

        # 마지막 레벨 테스트 결과 가져오기
        last_level_test = user_data.get('level_test_results', [])
        last_test_data = {}
        if last_level_test:
            last_level_test_id = last_level_test[-1]
            last_level_test_ref = db.collection('level_test_results').document(last_level_test_id)
            last_test_data = last_level_test_ref.get().to_dict()

        profile_data = {
            'name': user_data.get('name', 'Unknown'),
            'email': user_data.get('email', 'Unknown'),
            'skill_level': last_test_data.get('skill_level', 'Not available'),
            'last_test_date': last_test_data.get('date', 'Not available'),
            'last_test_score': f"{last_test_data.get('score', 0)}/{last_test_data.get('total_problems', 0)}",
        }

        return jsonify(profile_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_next_skill_level(current_skill_level):
    skill_levels = ['beginner', 'elementary', 'intermediate', 'advanced', 'expert']
    current_skill_level = current_skill_level.lower()  # 소문자로 변환
    try:
        current_index = skill_levels.index(current_skill_level)
        next_index = min(current_index + 1, len(skill_levels) - 1)
        return skill_levels[next_index]
    except ValueError:
        print(f"Warning: Unknown skill level '{current_skill_level}'. Defaulting to 'beginner'.")
        return 'beginner'

class User:
    def __init__(self, uid):
        self.uid = uid

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.uid

    # @staticmethod
    # def get(user_id):
    #     # Firebase에서 사용자 정보를 가져오는 로직
    #     try:
    #         user = auth.get_user(user_id)
    #         return User(user.uid)
    #     except:
    #         return None