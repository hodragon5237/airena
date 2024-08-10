(function() {
    function initHamburgerMenu() {
        const hamburgerButton = document.getElementById('hamburger-button');
        const messagesContainer = document.querySelector('.messages');
        
        if (hamburgerButton && messagesContainer) {
            hamburgerButton.addEventListener('click', () => {
                messagesContainer.classList.toggle('active');
                hamburgerButton.classList.toggle('active');
            });
        } else {
            console.error('Hamburger button or messages container not found');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHamburgerMenu);
    } else {
        initHamburgerMenu();
    }
})();

document.addEventListener('DOMContentLoaded', () => {
    const problemContainer = document.getElementById('problem-container');
    const userInput = document.getElementById('user-input');
    const submitButton = document.getElementById('submit-answer');
    const resultContainer = document.querySelector('.chat[data-chat="result"]');
    const introContainer = document.querySelector('.chat[data-chat="intro"]');
    const stageProblemContainer = document.getElementById('stage-problem-container');
    const homeButton = document.getElementById('homeButton');
    const logoutButton = document.getElementById('logoutButton');
    const studyRoomContainer = document.getElementById('study-room-container');

    homeButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    logoutButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/logout', { method: 'POST' });
            if (response.ok) {
                window.location.href = '/';
            } else {
                throw new Error('Logout failed');
            }
        } catch (error) {
            console.error('Error during logout:', error);
            alert('로그아웃 중 오류가 발생했습니다. 다시 시도해 주세요.');
        }
    });

    // 다크 모드 토글 기능 추가
    const toggleDarkMode = document.getElementById('toggle-dark-mode');
    if (toggleDarkMode) {
        toggleDarkMode.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
        });
    }

    // 포커스 가능한 요소들을 선택합니다.
    const focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

    // 페이지 내의 모든 포커스 가능한 요소를 가져옵니다.
    const focusableContent = document.querySelectorAll(focusableElements);

    // 첫 번째와 마지막 포커스 가능한 요소를 저장합니다.
    const firstFocusableElement = focusableContent[0];
    const lastFocusableElement = focusableContent[focusableContent.length - 1];

    // 키보드 이벤트 리스너를 추가합니다.
    document.addEventListener('keydown', function(e) {
        // ESC 키를 누르면 모달을 닫습니다 (모달이 있다고 가정).
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal');
            if (modal && modal.style.display !== 'none') {
                modal.style.display = 'none';
            }
        }

        // Tab 키 네비게이션
        if (e.key === 'Tab') {
            // Shift + Tab
            if (e.shiftKey) {
                if (document.activeElement === firstFocusableElement) {
                    lastFocusableElement.focus();
                    e.preventDefault();
                }
            // Tab
            } else {
                if (document.activeElement === lastFocusableElement) {
                    firstFocusableElement.focus();
                    e.preventDefault();
                }
            }
        }
    });

    // 포커스 가능한 요소들에 aria-label 추가
    focusableContent.forEach(element => {
        if (!element.getAttribute('aria-label')) {
            element.setAttribute('aria-label', element.innerText || element.value || '버튼');
        }
    });

    // 메인 컨텐츠로 바로 이동하는 스킵 링크 추가
    const skipLink = document.createElement('a');
    skipLink.innerText = '메인 컨텐츠로 건너뛰기';
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link class="sr-only"';
    document.body.insertBefore(skipLink, document.body.firstChild);

    // 메인 컨텐츠에 id 추가 (index.html 파일에서 메인 컨텐츠 요소에 id="main-content" 추가 필요)
    const mainContent = document.querySelector('.middle');
    if (mainContent) {
        mainContent.id = 'main-content';
    }

    let currentProblem = 0;
    let totalProblems = 0;

    function setActiveChat(chatId) {
        document.querySelectorAll('.chat').forEach(chat => {
            chat.classList.remove('active-chat');
        });
        const activeChat = document.querySelector(`.chat[data-chat="${chatId}"]`);
        if (activeChat) {
            activeChat.classList.add('active-chat');
        }
        
        document.querySelectorAll('.person').forEach(person => {
            person.classList.remove('active');
        });
        const activePerson = document.querySelector(`.person[data-chat="${chatId}"]`);
        if (activePerson) {
            activePerson.classList.add('active');
        }

        // 채팅 입력창 초기화
        const userInput = document.getElementById('user-input');
        const submitButton = document.getElementById('submit-answer');
        
        // 모든 탭에서 입력창과 제출 버튼을 표시합니다
        userInput.style.display = 'block';
        submitButton.style.display = 'block';
        
        // 입력창 내용 초기화
        userInput.value = '';
        
        // 객관식 옵션 초기화 (만약 있다면)
        document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
    }

    async function submitIntroQuestion() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        if (!message) return;
 
        const introContent = document.getElementById('intro-content');
        introContent.innerHTML += `
            <div class="bubble me">
                <p>${message}</p>
            </div>
        `;
 
        try {
            const response = await fetch('/intro_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            });
            const data = await response.json();
            
            introContent.innerHTML += `
                <div class="bubble you">
                    <p>${data.message}</p>
                </div>
            `;
        } catch (error) {
            console.error("Error submitting intro question:", error);
        }
 
        userInput.value = '';
        introContent.scrollTop = introContent.scrollHeight;
    }

    async function startStudyRoom() {
        console.log('startStudyRoom called');
        showLoading();
        try {
            const response = await fetch('/start_study_room', { method: 'POST' });
            const data = await response.json();
            if (response.ok) {
                const studyRoomContainer = document.getElementById('study-room-container');
                studyRoomContainer.innerHTML = `
                    <div class="bubble you">
                        <p>${data.message}</p>
                    </div>
                `;
                studyRoomContainer.scrollTop = studyRoomContainer.scrollHeight;
                setActiveChat('study_room');
            } else {
                throw new Error(data.error || 'Failed to start study room');
            }
        } catch (error) {
            console.error("Error starting study room:", error);
            if (error.message === 'User not authenticated') {
                handleSessionExpired();
            } else {
                alert('스터디룸을 시작하는 중 오류가 발생했습니다. 다시 시도해 주세요.');
            }
        } finally {
            hideLoading();
        }
    }

    function loadIntroduction() {
        const introContent = document.getElementById('intro-content');
        introContent.innerHTML = `
            <div class="bubble you">
                <h2>Welcome, welcome to AIrena!</h2>
                <p>AIrena is an AI-powered programming learning and assessment platform.</p>
                <h3>Start:</h3>
                <ol>
                    <li>Level Test: Start by taking the 'Level Test' to assess your current skills.</li>
                    <li>Learning Stage: Improve your skills by solving problems of varying difficulty in the Learning Stage.</li>
                    <li>Study Room: Learn concepts and ask questions in the Study Room with an AI tutor.</li>
                    <li>Weekly Competition: Join the 'Weekly Competition' to compete against other users.</li>
                </ol>
                <p>Click on each menu to access its features. Happy learning!</p>
                <p>Hi! Welcome to AIrena. What information do you need?</p>
            </div>
        `;
    }
    
    async function submitStudyAnswer() {
        const userInput = document.getElementById('user-input');
        const answer = userInput.value.trim();
        
        if (!answer) {
            alert('Please provide an answer before submitting.');
            return;
        }
        
        try {
            const response = await fetch('/submit_study_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ answer: answer }),
            });
            
            const result = await response.json();
            
            const studyRoomContainer = document.getElementById('study-room-container');
            studyRoomContainer.innerHTML += `
                <div class="bubble me">
                    <p>${answer}</p>
                </div>
                <div class="bubble you">
                    ${formatMessage(result.message)}
                </div>
            `;
            studyRoomContainer.scrollTop = studyRoomContainer.scrollHeight;
            
            userInput.value = '';

            Prism.highlightAll();
        } catch (error) {
            console.error("Error submitting study answer:", error);
            alert('An error occurred while submitting your answer. Please try again.');
        }
    }

    function formatMessage(message) {
        const codeRegex = /```(\w+)?\s*([\s\S]*?)```/g;
        let formattedMessage = message.replace('<br>', /\n/g);
        formattedMessage = formattedMessage.replace(codeRegex, (match, language, code) => {
            language = language || 'plaintext';
            return `<pre><code class="language-${language}">${escapeHtml(code)}</code></pre>`;
        });
        return formattedMessage;
    }
    
    function escapeHtml(unsafe) {
        return unsafe
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }

    document.querySelectorAll('.person').forEach(person => {
        person.addEventListener('click', async () => {
            const chatId = person.getAttribute('data-chat');
            setActiveChat(chatId);
            if (chatId === 'level_test') {
                startLevelTest();
            } else if (chatId === 'profile') {
                loadProfile();
            } else if (chatId === 'stage') {
                startStage();
            } else if (chatId === 'study_room') {
                startStudyRoom();
            }
        });
    });

    async function startLevelTest() {
        showLoading();
        try {
            const subjectRadios = document.querySelectorAll('input[name="subject"]');
            let selectedSubject = 'Python'; // 기본값 설정
            for (const radio of subjectRadios) {
                if (radio.checked) {
                    selectedSubject = radio.value;
                    break;
                }
            }
            hideLoading();
            const response = await fetch('/start_level_test', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ subject: selectedSubject })
            });
            if (response.status === 401) {
                alert('You need to be logged in to start the level test. Please log in and try again.');
                window.location.href = '/login';
                return;
            }
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            totalProblems = data.total_problems;
            currentProblem = 0;
            problemContainer.innerHTML = ''; // 문제 컨테이너 초기화
            loadProblem();
        } catch (error) {
            console.error("Error starting level test:", error);
            alert('An error occurred while starting the level test. Please try again.');
        } 
        await refreshSession();
    }

    async function loadProfile() {
        const leaderboardLoading = document.getElementById('leaderboard-loading');
        leaderboardLoading.style.display = 'none'; // 로딩 애니메이션 숨김
        showLoading();
        try {
            const response = await fetch('/profile');
            // if (!response.ok) {
            //     throw new Error('Failed to fetch profile data');
            // }
            const data = await response.json();
            
            let profileHtml = `
                <div class="bubble you">
                    <h2>Profile</h2>
                    <p><strong>Name:</strong> ${data.name}</p>
                    <p><strong>Email:</strong> ${data.email}</p>
                    <p><strong>Current Skill Level:</strong> ${data.skill_level}</p>
                    <p><strong>Last Level Test Date:</strong> ${data.last_test_date}</p>
                    <p><strong>Last Level Test Score:</strong> ${data.last_test_score}</p>
                </div>
            `;
            
            const profileContainer = document.querySelector('.chat[data-chat="profile"]');
            if (profileContainer) {
                profileContainer.innerHTML = profileHtml;
            } else {
                console.error("Profile container not found");
            }
        } catch (error) {
            console.error("Error loading profile:", error);
            alert('An error occurred while loading your profile. Please try again.');
        } finally {
            hideLoading();
        }
        await refreshSession();
    }

    async function loadProblem() {
        if (currentProblem >= totalProblems) {
            showResult();
            return;
        }

        // showLoading();
        const leaderboardLoading = document.getElementById('leaderboard-loading');
        leaderboardLoading.style.display = 'block'; // 로딩 애니메이션 표시
        try {
            const response = await fetch('/get_problem');
            const problem = await response.json();
            
            if (problem.error) {
                console.error("Error loading problem:", problem.error);
                alert('An error occurred while loading the problem. Please try again.');
                return;
            }
    
            currentProblem++;
            let bubbleHtml = `
                <div class="bubble you">
                    <h4>Problem ${currentProblem} of ${totalProblems}</h4>
                    <p>${problem.description}</p>
            `;

            if (problem.original_code && problem.refactored_code) {
                // Advanced or Expert level problem
                bubbleHtml += `
                    <h4>Original Code:</h4>
                        <pre><code class="language-python">${escapeHtml(problem.original_code)}</code></pre>
                    <h4>Refactored Code (Fill in the blank):</h4>
                        <pre><code class="language-python">${escapeHtml(problem.refactored_code)}</code></pre>
                `;
            } else if (problem.code) {
                // Other levels
                bubbleHtml += `
                    <h4>Code:</h4>
                        <pre><code class="language-python">${escapeHtml(problem.code)}</code></pre>
                `;
            }
    
            if (problem.options) {
                bubbleHtml += `<div class="options">`;
                for (const [key, value] of Object.entries(problem.options)) {
                    bubbleHtml += `<button class="option-btn" data-option="${key}">${key}: ${value}</button>`;
                }
                bubbleHtml += `</div>`;
            }
            
            bubbleHtml += `</div>`;
            
            problemContainer.innerHTML += bubbleHtml;
        
            userInput.style.display = problem.options ? 'none' : 'block';
            userInput.value = '';
            
            problemContainer.scrollTop = problemContainer.scrollHeight;
    
            if (problem.options) {
                document.querySelectorAll('.option-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
                        this.classList.add('selected');
                    });
                });
            }
            Prism.highlightAll();
        } catch (error) {
            console.error("Error loading problem:", error);
            alert('An error occurred while loading the problem. Please try again.');
        } finally {
            const leaderboardLoading = document.getElementById('leaderboard-loading');
            leaderboardLoading.style.display = 'none'; // 로딩 애니메이션 숨김
            // hideLoading();
        }
        await refreshSession();
    }

    async function submitAnswer() {
        const selectedOption = document.querySelector('.option-btn.selected');
        let answer;
        if (selectedOption) {
            answer = selectedOption.getAttribute('data-option');
        } else {
            answer = userInput.value.trim();
        }
        
        if (!answer) {
            alert('Please provide an answer before submitting.');
            return;
        }
        
        try {
            const response = await fetch('/submit_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ answer: answer }),
            });
            
            const result = await response.json();
            
            let feedbackHtml = `
                <div class="bubble me">
                    <p>Your answer: ${answer}</p>
                </div>
                <div class="bubble you">
                    <p>${result.is_correct ? 'Correct!' : 'Incorrect.'} ${result.feedback}</p>
                </div>
            `;
            
            problemContainer.innerHTML += feedbackHtml;
            problemContainer.scrollTop = problemContainer.scrollHeight;
            
            // Reset the input and selected option
            userInput.value = '';
            document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
            
            if (result.current_problem < totalProblems) {
                loadProblem();
            } else {
                showResult();
            }
        } catch (error) {
            console.error("Error submitting answer:", error);
            alert('An error occurred while submitting your answer. Please try again.');
        }
    }

    function setActiveMenu(menuId) {
        const menuItems = document.querySelectorAll('.person');
        menuItems.forEach(item => item.classList.remove('active'));
        const activeMenu = document.querySelector(`.person[data-chat="${menuId}"]`);
        if (activeMenu) {
            activeMenu.classList.add('active');
        }
    }

    async function startStage() {
        showLoading();
        try {
            const skillLevelResponse = await fetch('/get_current_skill_level');
            const skillLevelData = await skillLevelResponse.json();
            const userSkillLevel = skillLevelData.skill_level || 'beginner';

            const response = await fetch('/start_stage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ skill_level: userSkillLevel.toLowerCase() }) // 예시로 'beginner' 사용
            });
            const data = await response.json();
            totalProblems = data.total_problems;
            currentProblem = 0;
            sessionStorage.setItem('current_stage_problem', currentProblem); // 세션에 current_stage_problem 설정
            loadStageProblem();
        } catch (error) {
            console.error("Error starting stage:", error);
            alert('An error occurred while starting the stage. Please try again.');
        } finally {
            hideLoading();
        }
    }

    async function loadStageProblem() {
        if (currentProblem >= totalProblems) {
            showStageResult();
            return;
        }
    
        // showLoading();
        const leaderboardLoading = document.getElementById('leaderboard-loading');
        leaderboardLoading.style.display = 'block'; // 로딩 애니메이션 표시
        try {
            const response = await fetch('/get_problem');
            const problem = await response.json();
            
            if (problem.error) {
                console.error("Error loading problem:", problem.error);
                alert('An error occurred while loading the problem. Please try again.');
                return;
            }
    
            currentProblem++;
            sessionStorage.setItem('current_stage_problem', currentProblem);
            sessionStorage.setItem('current_stage_problem_description', JSON.stringify(problem));
            let bubbleHtml = `
                <div class="bubble you">
                    <h4>Problem ${currentProblem} of ${totalProblems}</h4>
                    <p>${problem.description}</p>
            `;
    
            if (problem.original_code && problem.refactored_code) {
                bubbleHtml += `
                    <h4>Original Code:</h4>
                    <pre><code class="language-python">${Prism.highlight(problem.original_code, Prism.languages.python, 'python')}</code></pre>
                    <h4>Refactored Code (Fill in the blank):</h4>
                    <pre><code class="language-python">${Prism.highlight(problem.refactored_code, Prism.languages.python, 'python')}</code></pre>
                `;
            } else if (problem.code) {
                bubbleHtml += `
                    <h4>Code:</h4>
                    <pre><code class="language-python">${Prism.highlight(problem.code, Prism.languages.python, 'python')}</code></pre>
                `;
            }
    
            if (problem.options) {
                bubbleHtml += `<div class="options">`;
                for (const [key, value] of Object.entries(problem.options)) {
                    bubbleHtml += `<button class="option-btn" data-option="${key}">${key}: ${value}</button>`;
                }
                bubbleHtml += `</div>`;
            }
            
            bubbleHtml += `</div>`;
            stageProblemContainer.innerHTML += bubbleHtml;
            stageProblemContainer.scrollTop = stageProblemContainer.scrollHeight;

            // Prism 초기화를 위한 setTimeout 추가
            setTimeout(() => {
                if (typeof Prism !== 'undefined') {
                    Prism.highlightAll();
                } else {
                    console.error('Prism is not defined');
                }
            }, 0);
    
            // 객관식 문제인 경우 입력 창을 숨기고, 주관식 문제인 경우 보이게 함
            userInput.style.display = problem.options ? 'none' : 'block';
    
            // 객관식 문제에 대한 이벤트 리스너 추가
            if (problem.options) {
                document.querySelectorAll('.option-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
                        this.classList.add('selected');
                    });
                });
            }
        } catch (error) {
            console.error("Error loading problem:", error);
            alert('An error occurred while loading the problem. Please try again.');
        } finally {
            const leaderboardLoading = document.getElementById('leaderboard-loading');
            leaderboardLoading.style.display = 'none'; // 로딩 애니메이션 숨김
            // hideLoading();
        }
    }

    async function submitStageAnswer() {
        const selectedOption = document.querySelector('.option-btn.selected');
        let answer;
        if (selectedOption) {
            answer = selectedOption.getAttribute('data-option');
        } else {
            answer = userInput.value.trim();
        }
        
        if (!answer) {
            alert('답변을 제출하기 전에 답을 입력하거나 선택해주세요.');
            return;
        }
        
        try {
            const response = await fetch('/submit_stage_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ answer: answer }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            let feedbackHtml = `
                <div class="bubble me">
                    <p>Your answer: ${answer}</p>
                </div>
                <div class="bubble you">
                    <p>${result.is_correct ? 'Correct!' : 'Incorrect.'} ${result.feedback}</p>
                </div>
            `;
            
            stageProblemContainer.innerHTML += feedbackHtml;
            stageProblemContainer.scrollTop = stageProblemContainer.scrollHeight;
            
            // 입력 및 선택된 옵션 초기화
            userInput.value = '';
            document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
            
            if (result.current_problem <= result.total_problems) {
                loadStageProblem();
            } else {
                await showStageResult();
            }
        } catch (error) {
            console.error("Error submitting answer:", error);
            alert('An error occurred. Please try again later.');
        }
        await refreshSession();
    }

    async function showStageResult() {
        try {
            const response = await fetch('/complete_stage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            const result = await response.json();
            
            if (result.error) {
                alert(result.error);
                return;
            }
            
            const resultMessage = `
                <div class="bubble you">
                    <h3>Stage Result</h3>
                    <p>XP Earned: ${result.xp_earned}</p>
                </div>
            `;
            
            stageProblemContainer.innerHTML += resultMessage;
            stageProblemContainer.scrollTop = stageProblemContainer.scrollHeight;
        } catch (error) {
            console.error("Error completing stage:", error);
            alert('An error occurred while completing the stage. Please try again.');
        }
        await refreshSession();
    }

    async function saveTestResult() {
        try {
            const response = await fetch('/save_result', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (response.ok) {
                console.log('Test result saved successfully', data.result_id);
                // 여기서 result_id를 사용하여 추가 작업을 수행할 수 있습니다.
            } else {
                console.error('Failed to save test result:', data.error);
            }
        } catch (error) {
            console.error('Error saving test result:', error);
        }
    }

    const leaderboardMenuItem = document.querySelector('.person[data-chat="leaderboard"]');
    if (leaderboardMenuItem) {
        leaderboardMenuItem.addEventListener('click', () => {
            setActiveChat('leaderboard');
            showLeaderboard();
        });
    }

    async function showLeaderboard() {
        try {
            showLoading();

            const currentUserSkillLevel = await getCurrentUserSkillLevel();
            const leaderboardContainer = document.getElementById('leaderboard-container');
            leaderboardContainer.innerHTML = `
                <div class="leaderboard">
                    <header>
                        <h1>Weekly Competition</h1>
                        <div class="week-selector">
                            <button id="prev-week" class="week-button">Previous Week</button>
                            <span id="current-week" class="week-date">Current Week</span>
                            <button id="next-week" class="week-button">Next Week</button>
                        </div>
                        <nav id="skill-tabs">
                            <a href="javascript:void(0);" class="skill-tab" data-skill="Beginner">Beginner</a>
                            <a href="javascript:void(0);" class="skill-tab" data-skill="Elementary">Elementary</a>
                            <a href="javascript:void(0);" class="skill-tab" data-skill="Intermediate">Intermediate</a>
                            <a href="javascript:void(0);" class="skill-tab" data-skill="Advanced">Advanced</a>
                            <a href="javascript:void(0);" class="skill-tab" data-skill="Expert">Expert</a>
                        </nav>
                        <select id="skill-tab-dropdown" class="skill-tab-dropdown">
                            <option value="Beginner">Beginner</option>
                            <option value="Elementary">Elementary</option>
                            <option value="Intermediate">Intermediate</option>
                            <option value="Advanced">Advanced</option>
                            <option value="Expert">Expert</option>
                        </select>
                    </header>
                    <table>
                        <thead>
                            <tr>
                                <th class="rank">Rank</th>
                                <th class="nick">Nickname</th>
                                <th class="xp">XP</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            `;
    
            const skillTabs = document.querySelectorAll('.skill-tab');
            let currentWeek = 0;
    
            async function updateLeaderboard(skill, week) {
                try {
                    // showLoading();  // 로딩 애니메이션 시작
                    const leaderboardLoading = document.getElementById('leaderboard-loading');
                    leaderboardLoading.style.display = 'block'; // 로딩 애니메이션 표시
                    const response = await fetch(`/get_weekly_leaderboard?skill_level=${skill}&week=${week}`);
                    const data = await response.json();
                    const tbody = leaderboardContainer.querySelector('tbody');
                    tbody.innerHTML = '';
                    data.leaderboard.forEach((user, index) => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td class="rank">${index + 1}${user.trophy ? ` ${user.trophy}` : ''}</td>
                            <td class="nick">${user.name}</td>
                            <td class="xp">${user.xp}</td>
                        `;
                        if (user.email === data.current_user_email) {
                            row.classList.add('current-user');
                        }
                        tbody.appendChild(row);
                    });
                    document.getElementById('current-week').textContent = `${data.start_date} - ${data.end_date}`;
                } catch (error) {
                    console.error("리더보드 업데이트 중 오류 발생:", error);
                    alert('리더보드를 업데이트하는 중 오류가 발생했습니다. 다시 시도해 주세요.');
                } finally {
                    // hideLoading();  // 로딩 애니메이션 종료
                    const leaderboardLoading = document.getElementById('leaderboard-loading');
                    leaderboardLoading.style.display = 'none'; // 로딩 애니메이션 숨김
                }
            }
    
            skillTabs.forEach(tab => {
                tab.addEventListener('click', async () => {
                    skillTabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    await updateLeaderboard(tab.dataset.skill, currentWeek);
                });
            });

            const skillTabDropdown = document.getElementById('skill-tab-dropdown');
            skillTabDropdown.value = currentUserSkillLevel; // 현재 사용자 레벨로 기본값 설정

            skillTabDropdown.addEventListener('change', async () => {
                const selectedSkill = skillTabDropdown.value;
                await updateLeaderboard(selectedSkill, currentWeek);
            });
            
            document.getElementById('prev-week').addEventListener('click', async () => {
                currentWeek++;
                await updateLeaderboard(document.querySelector('.skill-tab.active').dataset.skill, currentWeek);
            });
            
            document.getElementById('next-week').addEventListener('click', async () => {
                if (currentWeek > 0) {
                    currentWeek--;
                    await updateLeaderboard(document.querySelector('.skill-tab.active').dataset.skill, currentWeek);
                }
            });
    
            const initialTab = Array.from(skillTabs).find(tab => tab.dataset.skill.toLowerCase() === currentUserSkillLevel.toLowerCase()) || skillTabs[0];
            initialTab.classList.add('active');
            updateLeaderboard(initialTab.dataset.skill, currentWeek);
            
        } catch (error) {
            console.error("리더보드 로딩 중 오류 발생:", error);
            alert('리더보드를 불러오는 중 오류가 발생했습니다. 다시 시도해 주세요.');
        } finally {
            hideLoading();
        }
    }

    async function getCurrentUserSkillLevel() {
        try {
            const response = await fetch('/get_current_skill_level');
            const data = await response.json();
            return data.skill_level;
        } catch (error) {
            console.error("Error getting current user skill level:", error);
            return 'beginner';
        }
    }

    async function showResult() {
        try {
            await saveTestResult();  // 여기에 saveTestResult() 호출 추가
            const response = await fetch('/get_result');
            const result = await response.json();
            
            const resultMessage = `
                <div class="bubble you">
                    <h3>Level Test Result</h3>
                    <p>Correct Answers: ${result.correct_answers} / ${result.total_problems}</p>
                    <p>Your Skill Level: ${result.skill_level}</p>
                </div>
            `;
            
            problemContainer.innerHTML += resultMessage;
            problemContainer.scrollTop = problemContainer.scrollHeight;
        } catch (error) {
            console.error("Error getting result:", error);
            alert('An error occurred while fetching your result. Please try again.');
        }
    }

    submitButton.addEventListener('click', () => {
        const activeChat = document.querySelector('.chat.active-chat').getAttribute('data-chat');
        if (activeChat === 'level_test') {
            submitAnswer();
        } else if (activeChat === 'stage') {
            submitStageAnswer();
        } else if (activeChat === 'study_room') {
            submitStudyAnswer();
        } else if (activeChat === 'intro') {
            submitIntroQuestion();
        } 
    });
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const activeChat = document.querySelector('.chat.active-chat').getAttribute('data-chat');
            if (activeChat === 'level_test') {
                submitAnswer();
            } else if (activeChat === 'stage') {
                submitStageAnswer();
            } else if (activeChat === 'study_room') {
                submitStudyAnswer();
            } else if (activeChat === 'intro') {
                submitIntroQuestion();
            }
        }
    });

    function showLoading() {
        console.log('showLoading called');
        document.querySelector('.loading-overlay').classList.add('show');
    }
    
    function hideLoading() {
        console.log('hideLoading called');
        document.querySelector('.loading-overlay').classList.remove('show');
    }

    function handleSessionExpired() {
        alert('세션이 만료되었습니다. 다시 로그인해주세요.');
        window.location.href = '/';
    }

    async function refreshSession() {
        try {
            await fetch('/refresh_session', { method: 'POST' });
        } catch (error) {
            console.error('Error refreshing session:', error);
        }
    }

    const introMenuItem = document.querySelector('.person[data-chat="intro"]');
    introMenuItem.addEventListener('click', loadIntroduction);

    // 페이지 로드 시 자동으로 Introduction 표시
    loadIntroduction();
});