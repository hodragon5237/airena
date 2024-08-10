import google.generativeai as genai
import os
import traceback
import json
import time
import re
from google.auth import credentials
from google.oauth2 import service_account
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# # 현재 파일의 디렉토리 경로
# base_dir = os.path.dirname(os.path.abspath(__file__))

# # 서비스 계정 키 파일 경로 설정
# service_account_file = os.path.join(base_dir, 'serviceAccountKey.json')

# # 서비스 계정 자격 증명 생성
# credentials = service_account.Credentials.from_service_account_file(
#     service_account_file,
#     scopes=['https://www.googleapis.com/auth/cloud-platform']
# )

# # 환경 변수로 서비스 계정 키 파일 경로 설정
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_file

# 환경 변수에서 API 키 가져오기
api_key = os.getenv("GEMINI_API_KEY")

# Gemini API 구성
genai.configure(api_key=api_key)

# PROBLEM_PROMPTS = {
#     "beginner": """
#     Create a Python beginner level problem with the following criteria:
#     1. Use only basic Python syntax without any libraries.
#     2. The problem should be a fill-in-the-blank question.
#     3. Include a short problem description, the code with a blank, and the correct answer.
#     4. The problem should focus on basic concepts like variables, if statements, or simple loops.

#     Format:
#     Description: [Problem description]
#     Code:
#     [Code with _____ for the blank]
#     Answer: [Correct answer for the blank]
#     """,
    
#     "elementary": """
#     Create a Python elementary level problem with the following criteria:
#     1. Use basic Python syntax and standard libraries.
#     2. The problem should be a fill-in-the-blank question.
#     3. Include a short problem description, the code with a blank, and the correct answer.
#     4. The problem should involve concepts like list manipulation, string operations, or basic file I/O.

#     Format:
#     Description: [Problem description]
#     Code:
#     [Code with _____ for the blank]
#     Answer: [Correct answer for the blank]
#     """,
    
#     "intermediate": """
#     Create a Python intermediate level problem with the following criteria:
#     1. The problem should be a fill-in-the-blank question.
#     2. Include concepts like working with APIs, data processing, or simple algorithms.
#     3. Use standard libraries if necessary.

#     Format:
#     Description: [Problem description]
#     Code:
#     [Code with _____ for the blank]
#     Answer: [Correct answer for the blank]
#     """,
    
#     "advanced": """
#     Create a Python advanced level problem focused on code refactoring with the following criteria:
#     1. Provide a working but poorly written Python code snippet.
#     2. Ask the user to refactor the code to improve its quality and adhere to PEP 8 guidelines.
#     3. The refactored code should have at least 50% compliance with PEP 8.
#     4. Include the original code, a description of what needs to be improved, and key points to consider in the refactoring.

#     Format:
#     Description: [Problem description and what needs to be improved]
#     Code:
#     [Poorly written code snippet]
#     Key Points:
#     - [Point 1]
#     - [Point 2]
#     - [Point 3]
#     Answer: [General guidelines for the expected refactored code]
#     """,
    
#     "expert": """
#     Create a Python expert level problem with the following criteria:
#     1. The problem should involve implementing a complex algorithm or data structure.
#     2. The solution should require advanced Python knowledge and problem-solving skills.
#     3. Include a detailed problem description and any constraints.
#     4. The problem should be challenging but solvable within a web-based coding environment.

#     Format:
#     Description: [Detailed problem description]
#     Code:
#     [Provide a code template or starting point for the solution]
#     Key Points:
#     - [Key concept or skill 1]
#     - [Key concept or skill 2]
#     - [Key concept or skill 3]
#     Answer: [Brief description of the expected solution approach]

#     Ensure all sections are present and clearly labeled. The problem should focus on advanced Python concepts and real-world applications, while being suitable for implementation in a web-based code editor.
#     """
# }

PROBLEM_PROMPTS = {
    "beginner": """
    Create a Python beginner-level fill-in-the-blank question based on the following criteria
    1. use only basic functions built into Python.
    2. the problem should have only one blank.
    3. focus on solving simple, basic grammar or algorithms.
    4. make sure the problem has a clear and unambiguous solution.
    5. The problem description should clearly and precisely state what you need to enter.
    6. provide context for the problem and explain why this knowledge is useful.
    7. End your description with “What code should be in the blank?”.

    Return the question in the following JSON format:
    {
        "description": "Clear, concise, friendly problem description with context, ending with a question",
        "code": "Code, including _____ in the blank",
        "answer": "The correct answer to the blank"
    }

    Example:
    {
        "description": "In Python, string manipulation is a crucial skill for text processing. One common task is to convert all characters in a string to uppercase. This is useful for standardizing text input or creating headings. The upper() method can be used for this purpose. Given a variable text containing a string, how would you convert it to all uppercase? What code should be in the blank?",
        "code": "text = "Hello, World!"\nuppercase_text = text._____",
        "answer": "upper()"
    }
    """,
    
    "beginner_multiple_choice": """
    Create a Python beginner-level multiple-choice question based on the following criteria
    1. focus on basic concepts or simple operations using basic functions built into Python.
    2. make sure all options are clearly related to the given problem.
    3. Ensure that the question has a clear and single correct answer.
    4. provide a brief explanation of why each option is the correct or incorrect answer.
    5. Include real-world usage scenarios in the question or options.
    6. The question description should clearly and accurately describe what is required to be entered.
    7. provide context for the question and explain why this knowledge is useful.

    Return the problem in the following JSON format:
    {
        "description": "A clear and concise description of the problem, A specific multiple choice question about the selected library",
        "options": {
            "A": "Option A",
            "B": "Option B",
            "C": "Option C",
            "D": "Option D"
        },
        "answer": "Correct option letter (A, B, C, or D)",
        "explanation": "Brief explanation for each option"
    }

    Example:
    {
        "description": "String manipulation is a fundamental skill in Python, especially when working with user input or processing text data. One common task is to remove whitespace from the beginning and end of a string. This is particularly useful when validating or cleaning user input, such as in web forms or data processing pipelines. Which built-in string method would you use to remove leading and trailing whitespace from a string?",
        "options": {
            "A": "string.strip()",
            "B": "string.trim()",
            "C": "string.clean()",
            "D": "string.remove_whitespace()"
        },
        "answer": "A",
        "explanation": "A: strip() is the correct method to remove leading and trailing whitespace from a string in Python.\nB: trim() is not a built-in Python string method, but it's used for similar purposes in some other programming languages.\nC: clean() is not a built-in Python string method. It might be confused with methods from third-party libraries.\nD: remove_whitespace() is not a built-in Python string method. While its name is descriptive, it's not a standard Python function."
    }
    """,
    
    "intermediate": """
    Create a Python intermediate level fill-in-the-blank problem focusing on django, flask, beautifulsoup4, selenium, or requests with the following criteria:
    1. Use intermediate-level functions or concepts from the specified libraries.
    2. The problem should have only one blank to fill.
    3. Focus on web development, scraping, or API interaction tasks.
    4. Ensure the problem has a clear, unambiguous solution.
    5. The description should clearly state what needs to be filled in.
    6. Provide a realistic programming scenario for the problem.
    7. End the description with 'What code should be in the blank?'

    Return the problem in the following JSON format:
    {
        "description": "Clear, concise, friendly problem description with a realistic scenario, ending with the question",
        "code": "Code with _____ for the blank",
        "answer": "Exact correct answer for the blank"
    }

    Example:
    {
        "description": "You're building a web scraping application to gather product information from an e-commerce website. You've successfully loaded the HTML content of a product page into a BeautifulSoup object called 'soup'. Now, you need to extract all the product titles from the page. Each product title is contained within an <h2> tag with the class 'product-title'. To efficiently select all these elements at once, you need to use an appropriate BeautifulSoup method. This method should return a list of all matching elements, allowing you to easily iterate over them and extract the text content later. What code should be in the blank?",
        "code": "product_titles = soup._____("h2", class_="product-title")",
        "answer": "find_all"
    }
    """,
    
    "intermediate_multiple_choice": """
    Create a Python intermediate level multiple-choice problem focusing on django, flask, beautifulsoup4, selenium, or requests with the following criteria:
    1. Focus on intermediate-level concepts or operations using these libraries.
    2. Ensure all options are valid syntax or concepts directly related to the chosen library.
    3. The question should have only one clear, correct answer.
    4. Provide a brief explanation for why each option is correct or incorrect.
    5. Include a practical scenario or use case in the question.
    6. Ensure the question is specific and unambiguous.
    7. provide context for the question and explain why this knowledge is useful.

    Return the problem in the following JSON format:
    {
        "description": "A clear and concise description of the problem, A specific multiple choice question about the selected library",
        "options": {
            "A": "Option A",
            "B": "Option B",
            "C": "Option C",
            "D": "Option D"
        },
        "answer": "Correct option letter (A, B, C, or D)",
        "explanation": "Brief explanation for each option"
    }

    Example:
    {
        "description": "You're developing a Flask web application that needs to handle user authentication. You want to implement a feature that restricts access to certain routes, allowing only authenticated users to view them. Which Flask extension provides a convenient way to manage user sessions and implement authentication in your application?",
        "options": {
            "A": "Flask-Session",
            "B": "Flask-Login",
            "C": "Flask-Security",
            "D": "Flask-User"
        },
        "answer": "B",
        "explanation": "A: Flask-Session is used for server-side session management, but doesn't directly handle authentication.\nB: Flask-Login is the correct answer. It provides user session management for Flask, handling tasks like logging in, logging out, and remembering users' sessions.\nC: Flask-Security is a more comprehensive extension that includes authentication, but it's often considered overkill for basic auth needs and is built on top of Flask-Login.\nD: Flask-User is a user management extension that includes authentication, but it's more complex and feature-rich than typically needed for basic authentication tasks."
    }
    """,
    
    "advanced": """
    Create a Python advanced level fill-in-the-blank problem focusing on advanced usage of numpy, pandas, matplotlib, seaborn, django, flask, beautifulsoup4, selenium, or requests with the following criteria:
    1. Use advanced functions, optimizations, or best practices from the specified libraries.
    2. The problem should involve refactoring or optimizing existing code.
    3. Replace only one space in the specific part of the code that needs improvement (_____).
    4. Include a clear description of what needs to be improved and why it's important.
    5. Provide specific key points to consider for the improvement.
    6. Ensure the problem has a clear goal and criteria for successful refactoring.
    7. End the description with 'What code should be in the blank to improve this function?'

    Return the problem in the following JSON format:
    {
        "description": "Clear problem description and what needs to be improved, ending with the question",
        "original_code": "Python code snippet that needs optimization",
        "refactored_code": "Optimized version of the code with _____ for the blank, ensuring the blank is actually present",
        "answer": "Correct code to fill in the blank",
        "key_points": [
            "Key point 1",
            "Key point 2",
            "Key point 3"
        ]
    }
    """ ,
    
    "advanced_multiple_choice": """
    Create a Python advanced level multiple-choice problem focusing on advanced concepts of numpy, pandas, matplotlib, seaborn, django, flask, beautifulsoup4, selenium, or requests with the following criteria:
    1. Focus on advanced-level concepts, optimizations, or best practices using these libraries.
    2. Provide a complex scenario or code snippet as the basis for the question.
    3. Ensure all options are plausible and require deep understanding of the chosen library to differentiate.
    4. The question should have only one clear, correct answer, but it should require advanced knowledge to identify.
    5. Provide a comprehensive explanation for why each option is correct or incorrect, including potential trade-offs or considerations.
    6. Ensure the question is specific and unambiguous.
    7. provide context for the question and explain why this knowledge is useful.

    Return the problem in the following JSON format:
    {
        "description": "Detailed scenario or code snippet using the chosen library, Specific multiple-choice question based on the complex scenario",
        "options": {
            "A": "Option A",
            "B": "Option B",
            "C": "Option C",
            "D": "Option D"
        },
        "answer": "Correct option letter (A, B, C, or D)",
        "explanation": "Comprehensive explanation for each option, including trade-offs and considerations"
    }

    Example:
    {
        "description": "You're working on a large-scale data analysis project using pandas. You have a DataFrame 'df' with millions of rows and hundreds of columns. One of your tasks is to calculate the correlation between all pairs of numerical columns. Your current implementation is as follows:\n\ndef calculate_correlations(df):\n    numeric_cols = df.select_dtypes(include=[np.number]).columns\n    correlations = {}\n    for col1 in numeric_cols:\n        for col2 in numeric_cols:\n            if col1 != col2:\n                correlations[(col1, col2)] = df[col1].corr(df[col2])\n    return correlations\n\nHowever, this function is extremely slow for your large dataset. Which of the following approaches would be the most efficient way to optimize this function?",
        "options": {
        "A": "Use numpy's corrcoef function instead of pandas' corr method",
        "B": "Implement parallel processing using Python's multiprocessing library",
        "C": "Use pandas' built-in corr() method on the entire DataFrame",
        "D": "Use Dask DataFrame for out-of-core computation"
        },
        "answer": "C",
        "explanation": "A: While numpy's corrcoef is generally faster than element-wise correlation calculation, it still requires manual looping over columns and doesn't take full advantage of pandas' optimizations.\n\nB: Parallel processing could potentially speed up the computation, but it introduces complexity and may not be necessary if we can use pandas' built-in optimizations. It's also not as straightforward to implement with shared memory issues.\n\nC: This is the correct answer. Pandas' corr() method is highly optimized for DataFrame operations and can compute the correlation matrix for all numerical columns in a single operation. It uses efficient C implementations under the hood and is designed to work well with large datasets.\n\nD: Dask is excellent for out-of-core computations when dealing with datasets larger than memory, but it introduces additional complexity and dependencies. For datasets that fit in memory, pandas' built-in methods are usually faster and simpler to use. Dask would be a good choice if the dataset doesn't fit in memory.\n\nUsing pandas' built-in corr() method is the most efficient and straightforward solution for this scenario. It leverages pandas' internal optimizations and vectorized operations, making it significantly faster than the original implementation. This approach also simplifies the code, making it more readable and maintainable."
    }
    """,
    
    "expert": """
    Create a Python expert level fill-in-the-blank problem focusing on advanced usage and optimization of numpy, pandas, matplotlib, seaborn, django, flask, beautifulsoup4, selenium, or requests.
    1. The problem involves implementing a complex algorithm or optimization using Python-specific features and the chosen library.
    2. The original code provided is working but inefficient or suboptimal.
    3. The refactored code should have a clear improvement over the original code.
    4. Replace only one space in the specific part of the refactored code that needs improvement (_____).
    5. The description includes detailed requirements and constraints, focusing on the library's advanced capabilities.
    6. The explanation should clearly state why the optimization is better and how it improves performance.
    7. The key points consider specific improvements, focusing on expert-level techniques.

    Do not include any explanation or additional text outside the JSON object.
    Respond ONLY with a JSON object in the following format, and nothing else:
    {
        "description": "Detailed problem description with clear requirements and constraints specific to the chosen library, ending with the question 'What code should be in the blank to optimize this implementation?'",
        "original_code": "Python code snippet that needs optimization",
        "refactored_code": "Optimized version of the code with _____ for the blank, ensuring the blank is actually present",
        "answer": "Correct code to fill in the blank",
        "explanation": "Detailed explanation of why this optimization is better, including performance considerations",
        "key_points": [
            "Key concept or skill 1",
            "Key concept or skill 2",
            "Key concept or skill 3"
        ]
    }
    """,
    
    "expert_multiple_choice": """
    Create a Python expert level multiple-choice problem focusing on advanced usage of numpy, pandas, matplotlib, seaborn, django, flask, beautifulsoup4, selenium, or requests with the following criteria:
    1. Focus on expert-level concepts, optimizations, or architectural decisions using these libraries.
    2. Provide a complex scenario, algorithm description, or system architecture as the basis for the question.
    3. Ensure all options are highly plausible and require deep understanding of the chosen library to differentiate.
    4. The question should have only one clear, correct answer, but it should require expert knowledge to identify.
    5. Provide a comprehensive explanation for why each option is correct or incorrect, including potential trade-offs or considerations specific to the library.
    6. Ensure the question is specific and unambiguous.
    7. Include practical, real-world applications or performance considerations in the scenario.

    Return the problem in the following JSON format:
    {
        "description": "Detailed scenario, algorithm description, or system architecture using the chosen library ,Specific multiple-choice question based on the complex scenario",
        "options": {
            "A": "Option A",
            "B": "Option B",
            "C": "Option C",
            "D": "Option D"
        },
        "answer": "Correct option letter (A, B, C, or D)",
        "explanation": "Comprehensive explanation for each option, including library-specific trade-offs and considerations"
    }

    Example:
    {
        "description": "You're developing a high-performance web scraping system using Scrapy and Selenium for a large-scale e-commerce price comparison service. The system needs to scrape millions of product pages daily from various websites, some of which heavily rely on JavaScript for content rendering. The current implementation uses a combination of Scrapy for static content and Selenium for JavaScript-rendered content. However, the system is facing performance issues, especially with JavaScript-heavy sites, and struggles to handle the increasing volume of pages. You need to optimize the architecture to improve scraping speed, reduce resource usage, and enhance scalability. Which of the following approaches would be the most effective solution for this scenario?",
        "options": {
            "A": "Implement a hybrid approach using Scrapy with Splash for JavaScript rendering, and use Redis for distributed scheduling and duplication filtering",
            "B": "Switch entirely to Selenium with a headless browser, utilizing a pool of browser instances managed by a custom load balancer",
            "C": "Use Scrapy with playwright-scrapy integration for JavaScript rendering, combined with ScrapyD for distributed scraping",
            "D": "Implement a custom asynchronous scraping framework using aiohttp and pyppeteer, with distributed task queue using Celery"
        },
        "answer": "C",
        "explanation": "A: While this approach can be effective, Splash has limitations in handling complex JavaScript and may struggle with some modern websites. Redis for scheduling is good, but it doesn't address the core issue of JavaScript rendering performance.\n\nB: Switching entirely to Selenium would solve JavaScript rendering issues but at a significant cost to performance and resource usage. Selenium is generally slower and more resource-intensive than specialized scraping tools.\n\nC: This is the most effective solution. Scrapy is highly efficient for scraping, and the playwright-scrapy integration provides powerful JavaScript rendering capabilities that can handle modern web technologies. ScrapyD allows for easy distribution of scraping tasks across multiple machines, addressing scalability. This combination offers the best balance of performance, capability, and scalability.\n\nD: While this custom solution could be powerful, it requires significant development and maintenance effort. It may not leverage the optimizations and features already present in established frameworks like Scrapy, potentially leading to reinventing the wheel."
    }
    """,

    "elementary": """
    Create a Python elementary level fill-in-the-blank problem focusing on basic usage of numpy, pandas, matplotlib, or seaborn with the following criteria:
    1. Use basic functions from the specified libraries.
    2. The problem should have only one blank to fill.
    3. Focus on simple data manipulation or visualization tasks.
    4. Ensure the problem has a clear, unambiguous solution.
    5. The description should clearly state what needs to be filled in.
    6. Provide context for the problem, explaining why this knowledge is useful.
    7. End the description with 'What code should be in the blank?'

    Return the problem in the following JSON format:
    {
        "description": "Clear, concise, friendly problem description with context, ending with the question",
        "code": "Code with _____ for the blank",
        "answer": "Exact correct answer for the blank"
    }

    Example:
    {
        "description": "Pandas is a powerful library for data manipulation in Python. One of its most fundamental operations is reading data from CSV files, which is crucial for data analysis tasks. Suppose you have a CSV file named 'sales_data.csv' containing information about product sales. To start analyzing this data, you first need to load it into a pandas DataFrame. This allows you to work with the data in a structured format, making it easier to perform calculations, filter information, or create visualizations. What code should go in the blank?",
        "code": "import pandas as pd\n\nsales_df = pd._____("sales_data.csv")",
        "answer": "read_csv"
    }
    """,
    
    "elementary_multiple_choice": """
    Create a Python elementary level multiple-choice problem focusing on basic concepts of numpy, pandas, matplotlib, or seaborn with the following criteria:
    1. Focus on fundamental concepts or simple operations using these libraries.
    2. Ensure all options are clearly related to the chosen library.
    3. The question should have only one clear, correct answer.
    4. Provide a brief explanation for why each option is correct or incorrect.
    5. Include real-world usage scenarios in the question or options.
    6. The question description should clearly and accurately describe what is required to be entered.
    7. provide context for the question and explain why this knowledge is useful.

    Respond ONLY with a valid JSON object in the following format, and nothing else:
    {
        "description": "Clear and concise problem description, Specific multiple-choice question about the chosen library",
        "options": {
            "A": "Option A",
            "B": "Option B",
            "C": "Option C",
            "D": "Option D"
        },
        "answer": "Correct option letter (A, B, C, or D)",
        "explanation": "Brief explanation for each option"
    }

    Example:
    {
        "description": "description": "Matplotlib is a popular library for creating visualizations in Python. When working with data analysis or scientific computing, it's often necessary to create line plots to show trends over time or relationships between variables. In a financial analysis scenario, you want to create a simple line plot to visualize stock prices over time. Which Matplotlib function would you use to create a basic line plot?",
        "options": {
            "A": "plt.scatter()",
            "B": "plt.bar()",
            "C": "plt.plot()",
            "D": "plt.hist()"
        },
        "answer": "C",
        "explanation": "A: plt.scatter() is used for scatter plots, not line plots. It's useful for showing the relationship between two variables but doesn't connect points with lines.\nB: plt.bar() creates bar charts, which are better for comparing discrete categories rather than continuous data like stock prices over time.\nC: plt.plot() is the correct function for creating line plots, ideal for visualizing trends in continuous data such as stock prices over time.\nD: plt.hist() generates histograms, which are used to show the distribution of a dataset, not for tracking changes over time."
    }
    """,
}

def clean_json_string(json_str):
    # 제어 문자 제거
    json_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_str)
    # JSON 객체의 시작과 끝 부분만 추출
    match = re.search(r'\{.*\}', json_str, re.DOTALL)
    if match:
        json_str = match.group()
        # 줄바꿈 문자를 \\n으로 대체
        json_str = json_str.replace('\n', '\\n').replace('\r', '')
        # 연속된 공백 제거 (줄바꿈 제외)
        json_str = re.sub(r'(?<!\\n)\s+', ' ', json_str)
        return json_str
    return ''

# def clean_json_string(json_str):
#     # 제어 문자 제거
#     json_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_str)
#     # JSON 객체의 시작과 끝 부분만 추출
#     match = re.search(r'\{.*\}', json_str, re.DOTALL)
#     if match:
#         json_str = match.group()
#         # 줄바꿈 문자를 공백으로 대체
#         json_str = json_str.replace('\n', ' ').replace('\r', ' ')
#         # 연속된 공백 제거
#         json_str = re.sub(r'\s+', ' ', json_str)
#         # 쉼표 뒤에 공백이 없는 경우 공백 추가
#         json_str = re.sub(r',(?=\S)', ', ', json_str)
#         # 콜론 뒤에 공백이 없는 경우 공백 추가
#         json_str = re.sub(r':(?=\S)', ': ', json_str)
#         return json_str
#     return ''

def generate_single_problem(level, max_attempts=3):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = PROBLEM_PROMPTS.get(level, "")
    
    if not prompt:
        print(f"Error: Invalid level '{level}'. Available levels: {', '.join(PROBLEM_PROMPTS.keys())}")
        return create_default_problem(level)

    for attempt in range(max_attempts):
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            print(f"Raw response for {level} (Attempt {attempt + 1}):\n{response_text}\n")

            # 응답을 받은 후 1초 대기
            time.sleep(1)

            # JSON 형식 검증 및 수정
            # try:
            #     cleaned_response = clean_json_string(response_text)
            #     if not cleaned_response:
            #         raise ValueError("No valid JSON object found in the response")

            #     problem_json = json.loads(cleaned_response)
            # except json.JSONDecodeError as e:
            #     print(f"JSON Decode Error: {str(e)}")
            #     print(f"Problematic JSON string: {cleaned_response}")
            #     # JSON 파싱 실패 시 기본 문제로 대체
            #     return create_default_problem(level)
            try:
                cleaned_response = clean_json_string(response_text)
                if not cleaned_response:
                    raise ValueError("No valid JSON object found in the response")

                problem_json = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {str(e)}")
                print(f"Problematic JSON string: {cleaned_response}")
                raise  # 이 예외를 상위로 전파하여 더 자세한 오류 정보를 얻을 수 있습니다.

            # 레벨에 따라 필요한 키 확인
            if '_multiple_choice' in level:
                required_keys = ["description", "options", "answer", "explanation"]
            elif level in ['advanced', 'expert']:
                required_keys = ["description", "original_code", "refactored_code", "answer"]
            else:
                required_keys = ["description", "code", "answer"]

            if not all(key in problem_json for key in required_keys):
                missing_keys = [key for key in required_keys if key not in problem_json]
                raise ValueError(f"Missing required keys: {', '.join(missing_keys)}")

            # 코드에 Blank가 있는지 확인 (multiple choice가 아닌 경우에만)
            if '_multiple_choice' not in level:
                if level in ['advanced', 'expert']:
                    if 'original_code' not in problem_json or 'refactored_code' not in problem_json:
                        raise ValueError("Missing original_code or refactored_code for advanced/expert level")
                    if '_____' not in problem_json['refactored_code']:
                        raise ValueError("No blank found in the refactored code")
                else:
                    if 'code' not in problem_json:
                        raise ValueError("Missing code for non-advanced/expert level")
                    if '_____' not in problem_json['code']:
                        raise ValueError("No blank found in the code")

            problem_json['level'] = level
            return problem_json

        except Exception as e:
            print(f"Error in attempt {attempt + 1}: {str(e)}")
            if 'response_text' in locals():
                print(f"Problematic response:\n{response_text}")
            if attempt < max_attempts - 1:
                print("Retrying...")
                time.sleep(2)
            else:
                print(f"Max attempts reached. Falling back to default problem for {level}.")
                return create_default_problem(level)

    # 이 부분은 실행되지 않겠지만, 안전을 위해 남겨둡니다.
    print(f"Unexpected error. Falling back to default problem for {level}.")
    return create_default_problem(level)

def create_default_problem(level):
    if '_multiple_choice' in level:
        return {
            "level": level,
            "description": "Let's test your basic Python knowledge with a simple multiple-choice question.",
            "question": "In Python, which of the following is used to define a function?",
            "options": {
                "A": "func",
                "B": "define",
                "C": "def",
                "D": "function"
            },
            "answer": "C",
            "explanation": "A: Incorrect, 'func' is not a Python keyword. B: Incorrect, 'define' is not used to define functions in Python. C: Correct! 'def' is the keyword used to define functions in Python. D: Incorrect, while 'function' describes what we're creating, it's not the keyword used to define one."
        }
    elif 'beginner' in level:
        return {
            "level": level,
            "description": "Let's practice using the print function in Python. The print function is used to output text to the console.",
            "code": "# Complete the code to print 'Hello, World!' to the console\n_____('Hello, World!')",
            "answer": "print"
        }
    elif 'elementary' in level:
        return {
            "level": level,
            "description": "Let's work with lists in Python. We'll create a list and then access one of its elements.",
            "code": "# Create a list of fruits and access the second item\nfruits = ['apple', 'banana', 'cherry']\nsecond_fruit = fruits[_____]  # Remember, Python uses 0-based indexing\nprint(second_fruit)",
            "answer": "1"
        }
    elif 'intermediate' in level:
        return {
            "level": level,
            "description": "Let's practice using a dictionary in Python. We'll create a dictionary and then access one of its values.",
            "code": "# Create a dictionary of country capitals and access the capital of France\ncapitals = {'USA': 'Washington D.C.', 'France': 'Paris', 'Japan': 'Tokyo'}\nfrance_capital = capitals[_____]\nprint(france_capital)",
            "answer": "'France'"
        }
    elif 'advanced' in level:
        return {
            "level": level,
            "description": "Let's work with list comprehensions in Python. We'll create a list of squares of even numbers from 0 to 9.",
            "code": "# Create a list of squares of even numbers from 0 to 9 using a list comprehension\nsquares = [x**2 for x in range(10) _____]\nprint(squares)",
            "answer": "if x % 2 == 0"
        }
    else:  # expert level
        return {
            "level": level,
            "description": "Let's practice with decorators in Python. We'll create a simple decorator that measures the execution time of a function.",
            "code": "import time\n\ndef timing_decorator(func):\n    def wrapper(*args, **kwargs):\n        start_time = time.time()\n        result = _____  # Call the original function here\n        end_time = time.time()\n        print(f'{func.__name__} took {end_time - start_time:.2f} seconds to execute')\n        return result\n    return wrapper\n\n@timing_decorator\ndef slow_function():\n    time.sleep(1)\n    print('Function executed')\n\nslow_function()",
            "answer": "func(*args, **kwargs)"
        }

def generate_study_room_intro(current_skill_level, next_skill_level):
    skill_levels = {
        'beginner': 'Beginners can use basic built-in Python functions to manipulate strings, work with simple data types, and implement basic algorithms. They can write clear and unambiguous code using simple loop and conditional structures. For example, they can convert strings to uppercase or perform basic list operations.',
        'elementary': 'At the elementary level, programmers can utilize basic functions from libraries like NumPy and Pandas to perform simple data manipulation tasks. They can import data from CSV files into Pandas DataFrames and use Matplotlib or Seaborn to create basic visualizations such as line plots or scatter plots. They understand fundamental data structures like DataFrames and can perform basic operations on them.',
        'intermediate': 'Intermediate programmers can work with web development frameworks like Django or Flask, and use libraries such as BeautifulSoup4, Selenium, or Requests for web scraping and API interactions. They can parse HTML structures, extract specific elements from web pages, and handle more complex data operations. They understand how to use framework extensions for tasks like user authentication in web applications.',
        'advanced': 'Advanced Python programmers can implement optimizations and best practices using libraries like NumPy, Pandas, Matplotlib, and Seaborn. They can refactor and optimize code for better performance, especially when dealing with large datasets. They understand concepts like vectorization in NumPy and Pandas, can use advanced library-specific methods efficiently, and are aware of performance implications when working with big data.',
        'expert': 'Expert-level Python programmers can design and implement complex algorithms and system architectures using advanced features of Python and specialized libraries. They have a deep understanding of library internals and can optimize code for high-performance scenarios involving millions of data points. They are proficient in advanced concepts like distributed computing, scalability, asynchronous programming, and multi-processing. Experts can evaluate and choose optimal solutions for complex, real-world scenarios, such as designing efficient web scraping systems or implementing high-performance data processing pipelines.'
    }

    prompt = f"""
    You are an AI tutor helping someone learn Python. The user's current skill level is '{current_skill_level}', 
    Your next target level is '{next_skill_level}'.

    Current level ({current_skill_level}) requirements:
    {skill_levels[current_skill_level]}

    Next level ({next_skill_level}) requirements:
    {skill_levels[next_skill_level]}

    To send a welcome message to users and help them improve from their current level to the next. 
    Provide 3-5 suggestions for what topics to learn. 
    Then ask the user which topic they'd like to start with.

    Keep your responses friendly and encouraging.
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def continue_study_conversation(user_input, conversation_history, current_skill_level, next_skill_level):
    skill_levels = {
        'beginner': 'Beginners can use basic built-in Python functions to manipulate strings, work with simple data types, and implement basic algorithms. They can write clear and unambiguous code using simple loop and conditional structures. For example, they can convert strings to uppercase or perform basic list operations.',
        'elementary': 'At the elementary level, programmers can utilize basic functions from libraries like NumPy and Pandas to perform simple data manipulation tasks. They can import data from CSV files into Pandas DataFrames and use Matplotlib or Seaborn to create basic visualizations such as line plots or scatter plots. They understand fundamental data structures like DataFrames and can perform basic operations on them.',
        'intermediate': 'Intermediate programmers can work with web development frameworks like Django or Flask, and use libraries such as BeautifulSoup4, Selenium, or Requests for web scraping and API interactions. They can parse HTML structures, extract specific elements from web pages, and handle more complex data operations. They understand how to use framework extensions for tasks like user authentication in web applications.',
        'advanced': 'Advanced Python programmers can implement optimizations and best practices using libraries like NumPy, Pandas, Matplotlib, and Seaborn. They can refactor and optimize code for better performance, especially when dealing with large datasets. They understand concepts like vectorization in NumPy and Pandas, can use advanced library-specific methods efficiently, and are aware of performance implications when working with big data.',
        'expert': 'Expert-level Python programmers can design and implement complex algorithms and system architectures using advanced features of Python and specialized libraries. They have a deep understanding of library internals and can optimize code for high-performance scenarios involving millions of data points. They are proficient in advanced concepts like distributed computing, scalability, asynchronous programming, and multi-processing. Experts can evaluate and choose optimal solutions for complex, real-world scenarios, such as designing efficient web scraping systems or implementing high-performance data processing pipelines.'
    }

    conversation_text = "\n".join([f"{'AI' if role == 'assistant' else 'User'}: {message}" for role, message in conversation_history])
    prompt = f"""
    You are an AI tutor helping someone learn Python. The user's current skill level is '{current_skill_level}', 
    Your next target level is '{next_skill_level}'.

    Current level ({current_skill_level}) requirements:
    {skill_levels[current_skill_level]}

    Next level ({next_skill_level}) requirements:
    {skill_levels[next_skill_level]}

    Previous conversation:
    {conversation_text}

    User's last input: {user_input}

    Respond appropriately to the user's input and help them learn. 
    Provide code examples or additional explanations when needed. 
    Always maintain a friendly and encouraging tone, and motivate users to advance to the next skill level. 
    motivate the user to improve to the next skill level.

    Your response:
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# def parse_problem(problem_text, level):
#     is_multiple_choice = '_multiple_choice' in level
#     sections = ["Description:", "Question:", "A)", "B)", "C)", "D)", "Answer:"] if is_multiple_choice else ["Description:", "Code:", "Answer:"]
    
#     problem_dict = {section.strip(':)'): '' for section in sections}
#     current_section = None

#     for line in problem_text.split('\n'):
#         line = line.strip()
#         if line.startswith('##') or line.startswith('**'):
#             potential_section = line.lstrip('#').lstrip('*').strip()
#             if potential_section in problem_dict:
#                 current_section = potential_section
#         elif any(section.lower() in line.lower() for section in sections):
#             current_section = next(s.strip(':)') for s in sections if s.lower() in line.lower())
#         elif current_section:
#             problem_dict[current_section] += line + '\n'

#     # 빈 줄 제거 및 앞뒤 공백 제거
#     problem_dict = {k: v.strip() for k, v in problem_dict.items() if v.strip()}

#     # 모든 섹션이 있는지 확인
#     missing_sections = [s.strip(':)') for s in sections if s.strip(':)') not in problem_dict]
#     if missing_sections:
#         print(f"Missing sections for {level}: {', '.join(missing_sections)}")
#         return None

#     if is_multiple_choice:
#         return {
#             'level': level,
#             'description': problem_dict.get('Description', ''),
#             'question': problem_dict.get('Question', ''),
#             'options': {
#                 'A': problem_dict.get('A', ''),
#                 'B': problem_dict.get('B', ''),
#                 'C': problem_dict.get('C', ''),
#                 'D': problem_dict.get('D', '')
#             },
#             'answer': problem_dict.get('Answer', '')
#         }
#     else:
#         return {
#             'level': level,
#             'description': problem_dict.get('Description', ''),
#             'code': problem_dict.get('Code', ''),
#             'answer': problem_dict.get('Answer', '')
#         }

def generate_intro_response(user_input):
    prompt = f"""
    You are an AI assistant for AIrena, an AI-powered programming learning platform. Here's some information about AIrena:

    - AIrena is a combination of competitive programs to learn AI and programming.
    - It offers programming languages like Python, Java, and JavaScript, as well as domain-based skill-building programs and challenges in AI modeling, data analytics, and software architecture.
    - Currently, only Python is available, with programming languages like Java and JavaScript and domains like AI modeling, data analytics, and software architecture coming in the future.
    - Users can improve their programming skills through AI-generated challenges and feedback.
    - Features include conversational training with level tests and generative AI, a learning stage that builds skills by solving missions like a game, and weekly competitions.
    - The level test is a 10-question test, with questions for each level. After solving these questions, your level is determined. Your level can change each time you take the test, and you can retake it as you build your skillset.
    - In the Study Room, a generative AI will recommend what you should study based on your level and actually teach you. You can study by asking questions in a conversational format.
    - In the LEARNING STAGE, you can earn experience points by taking quizzes as they are given to you. Each problem you solve is worth 10 XP. This experience leads to a weekly competition.
    - The Weekly Competition is renewed every week. Medal badges are awarded on-screen for first through third place. If you've been working hard, you'll be able to climb the leaderboards, earning honors and boosting your skills.
    - In Profile, you can view your recent level test history.
    - AIrena is a generative AI-based programming and AX empowerment platform. Here, anyone can freely interact with generative AI to improve their skills.
    - What's more, AIrena is constantly expanding. In the future, we'll be covering a variety of programming languages and domains, and we'll be offering exciting courses with a variety of new features.

    User question: {user_input}

    Provide a friendly and informative response to the user's question about AIrena.
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def evaluate_code(code, level, problem_description):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Evaluate the following Python code for {level} level:
    
    Problem Description:
    {problem_description}
    
    User's Code:
    {code}
    
    Please provide a detailed assessment covering:
    1. Correctness of the solution (Does it solve the problem correctly?)
    2. Code quality and style
    3. Efficiency and performance considerations
    4. Any potential improvements or alternative approaches
    
    Conclude with a clear statement of whether the solution is CORRECT or INCORRECT.
    Your conclusion must start with either "CORRECT:" or "INCORRECT:" followed by a brief explanation.
    """
    response = model.generate_content(prompt)
    return response.text

def test_gemini_connection():
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, World!")
        print("Gemini API test successful. Response:", response.text)
        return True
    except Exception as e:
        print("Gemini API test failed:", str(e))
        return False

# app.py의 시작 부분에 다음 코드 추가
if not test_gemini_connection():
    print("Warning: Gemini API connection failed. Please check your API key and internet connection.")