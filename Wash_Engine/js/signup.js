// 1. 사용할 DOM 요소들 가져오기
const signupForm = document.getElementById('signup-form');
const usernameInput = document.getElementById('username');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');

const API_URL = "http://localhost:5000/api/signup";

// 2. 폼 제출(Submit) 이벤트 리스너 등록
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault(); // 무조건 리프레시되는 기본 동작 방지

    // 3. 입력 필드에서 값 추출
    const username = usernameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // [참고] 앞서 만든 Flask 백엔드는 현재 username과 password만 받도록 설계되어 있어.
    // 만약 이메일도 DB에 저장하고 싶다면 나중에 Flask의 users 테이블에 email 컬럼을 추가하면 돼!
    const signupData = {
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
            body: JSON.stringify(signupData)
        });

        const result = await response.json();

        // 5. 서버 응답 결과에 따른 처리 가이드
        if (response.ok) {
            alert(result.message || '회원가입 성공!');
            // 성공 시 로그인 페이지나 메인화면으로 이동시키는 로직 공간
            // location.href = 'login.html';
        } else {
            // 에러 메시지 처리 (예: 이미 존재하는 아이디 등)
            alert(`가입 실패: ${result.message}`);
        }

    } catch (error) {
        console.error('서버 통신 중 에러 발생:', error);
        alert('서버와 연결할 수 없습니다. 백엔드가 켜져 있는지 확인해 주세요.');
    }
});