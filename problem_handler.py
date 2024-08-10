import ast
import pycodestyle
from gemini_api import evaluate_code

def check_syntax(code):
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error on line {e.lineno}: {e.text}"

def check_pep8(code, compliance_level):
    style_guide = pycodestyle.StyleGuide(quiet=True)
    result = style_guide.check_files([code])
    total_errors = result.total_errors
    total_lines = len(code.splitlines())
    compliance = 1 - (total_errors / total_lines)
    return compliance >= compliance_level

def grade_answer(user_answer, problem_description, level):
    if not user_answer or not isinstance(user_answer, str):
        return False, "No answer provided or invalid answer format. Please enter a solution."

    if '_multiple_choice' in level:
        if not problem_description or not isinstance(problem_description, dict):
            return False, "Invalid problem description for multiple-choice question."
        correct_answer = problem_description.get('answer')
        if not correct_answer:
            return False, "Correct answer not found in problem description."
        is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
        if is_correct:
            feedback = "Correct!"
        else:
            explanation = problem_description.get('explanation', '')
            feedback = f"Incorrect. The correct answer is {correct_answer}. {explanation}"
        return is_correct, feedback
    else:
        # 주관식 문제 처리
        correct_answer = problem_description.get('answer', '').strip()
        user_answer = user_answer.strip()

        if correct_answer.lower() == user_answer.lower():
            return True, "Correct!"
        else:
            return False, f"Incorrect. The correct answer is: {correct_answer}"

    # 이 부분은 더 이상 필요하지 않습니다.
    # evaluation = evaluate_code(user_answer, level, problem_description)
    # is_correct = evaluation.lower().startswith("correct:")
    # return is_correct, evaluation

def determine_skill_level(correct_answers):
    if correct_answers >= 9:
        return "Expert"
    elif correct_answers >= 7:
        return "Advanced"
    elif correct_answers >= 5:
        return "Intermediate"
    elif correct_answers >= 3:
        return "Elementary"
    else:
        return "Beginner"