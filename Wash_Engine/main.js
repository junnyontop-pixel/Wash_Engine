const addProjectBtn = document.getElementById('add-project');
const API_URL = "http://localhost:5000/api";

addProjectBtn.addEventListener('click', async () => {
    console.log('프로젝트 추가 버튼이 클릭되었습니다!');
    
    // 1. 로그인 상태 확인 (로컬 스토리지에 토큰이 있는지 검사)
    const token = localStorage.getItem('wash_token');
    if (!token) {
        alert('로그인이 필요한 서비스입니다.');
        // 나중에 로그인 모달을 띄우거나 로그인 페이지로 이동시키는 로직 추가
        location.href = './pages/login.html'; // 로그인 페이지로 이동
        return;
    }

    // 2. 유저에게 프로젝트 이름 입력받기
    const title = prompt('새 프로젝트의 이름을 입력하세요:');
    if (!title || !title.trim()) return;

    // 3. 서버에 보낼 새 프로젝트 데이터 구성
    const today = new Date().toISOString().split('T')[0];
    const projectId = 'p_' + Date.now(); // 고유 ID 생성

    const newProjectData = {
        id: projectId,
        title: title.trim(),
        date: today,
        code: `# ${title.trim()}\n@Player\n  on: start\n    speed = 5\n\n  on: tick\n    move: right, speed`
    };

    try {
        // 4. Flask 백엔드에 프로젝트 생성 요청 (POST)
        const response = await fetch(`${API_URL}/projects`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newProjectData)
        });

        if (response.ok) {
            // 5. 서버에 저장이 성공하면, 생성된 프로젝트 ID를 가지고 에디터로 이동!
            location.href = `editor.html?id=${projectId}`;
        } else {
            const errorData = await response.json();
            alert(`프로젝트 생성 실패: ${errorData.message}`);
        }
    } catch (error) {
        console.error('서버 통신 에러:', error);
        alert('서버와 연결할 수 없습니다.');
    }
});