document.addEventListener('DOMContentLoaded', function() {
    const googleBtn = document.querySelector('#googleLoginBtn');
    if (googleBtn) {
        googleBtn.addEventListener('click', function(event) {
            event.preventDefault(); // 기본 동작 방지
            grecaptcha.ready(function() {
                grecaptcha.execute('{{ RECAPTCHA_SITE_KEY }}', {action: 'login'}).then(function(token) {
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = '/login'; // 로그인 경로
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'g-recaptcha-response';
                    input.value = token;
                    form.appendChild(input);
                    document.body.appendChild(form);
                    form.submit(); // 폼 제출
                });
            });
        });
    } else {
        console.error('Google login button not found');
    }
});