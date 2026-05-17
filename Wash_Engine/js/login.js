// dom 요소들 가져오기
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

const API_URL = "http://localhost:5000/api/login";

// 2. 폼 제출(Submit) 이벤트 리스너 등록
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // 무조건 리프레시되는 기본 동작 방지

    // 3. 입력 필드에서 값 추출
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    const loginData = {
        username: username,
        password: password
    };

    try {
        // 4. Flask 백엔드로 비동기 POST 요청 전송
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        const result = await response.json();

        // 5. 서버 응답 결과에 따른 처리 가이드
        if (response.ok) {
            alert(result.message || '로그인 성공!');

            localStorage.setItem('wash_token', result.token);

            // 성공 시 메인화면으로 이동시키는 로직 공간
            location.href = '../index.html';
        } else {
            // 에러 메시지 처리 (예: 이미 존재하는 아이디 등)
            alert(`로그인 실패: ${result.message}`);
        }

    } catch (error) {
        console.error('서버 통신 중 에러 발생:', error);
        alert('서버와 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해 주세요.');
    }
});