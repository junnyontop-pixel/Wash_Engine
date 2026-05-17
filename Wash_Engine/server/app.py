from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import jwt
import datetime

app = Flask(__name__)

# 프론트엔드 브라우저에서 포트가 달라도 요청을 보낼 수 있도록 CORS 허용
# (예: 프론트엔드가 Live Server 5500포트면 Flask 5000포트와 통신 가능하게 해줌)
CORS(app) 

SECRET_KEY = "wash_engine_secret_key_dash_dash" # JWT 토큰 암호화 키

# DB 연결을 편하게 하기 위한 헬퍼 함수
def get_db_connection():
    conn = sqlite3.connect('wash_engine.db')
    conn.row_factory = sqlite3.Row # 결과를 딕셔너리 형태로 편하게 가져오기 위함
    return conn

# 데이터베이스 테이블 초기화
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. 유저 테이블 (아이디는 고유값)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # 2. 프로젝트 테이블 (유저 외래키 연결)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            code TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# 앱 실행 시 DB 초기화
init_db()

# --- JWT 토큰에서 유저 ID를 뽑아내는 인증 함수 ---
def get_user_from_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(" ")[1]
    try:
        # 토큰 복호화
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data['user_id']
    except jwt.ExpiredSignatureError:
        return "EXPIRED" # 토큰 만료
    except jwt.InvalidTokenError:
        return None # 잘못된 토큰

# --- 1. 회원가입 API ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "아이디와 비밀번호를 모두 입력해주세요."}), 400
        
    # 비밀번호 안전하게 해싱(암호화)
    hashed_password = generate_password_hash(password)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        return jsonify({"message": "회원가입이 완료되었습니다!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "이미 존재하는 아이디입니다."}), 400
    finally:
        conn.close()

# --- 2. 로그인 API (성공 시 JWT 토큰 발급) ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    # 유저가 존재하고 비밀번호 해시값이 일치하는지 확인
    if user and check_password_hash(user['password'], password):
        # 24시간 동안 유효한 토큰 생성
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "token": token,
            "username": user['username'],
            "message": "로그인 성공!"
        }), 200
    
    return jsonify({"message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401

# --- 3. 특정 유저의 프로젝트 목록 불러오기 API (GET) ---
@app.route('/api/projects', methods=['GET'])
def get_projects():
    user_id = get_user_from_token()
    if user_id == "EXPIRED":
        return jsonify({"message": "세션이 만료되었습니다. 다시 로그인해주세요."}), 401
    if not user_id:
        return jsonify({"message": "로그인이 필요한 서비스입니다."}), 401
        
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM projects WHERE user_id = ? ORDER BY date DESC', (user_id,)).fetchall()
    conn.close()
    
    # 결과를 JSON 배열 형태로 변환
    projects_list = []
    for row in rows:
        projects_list.append({
            "id": row['id'],
            "title": row['title'],
            "date": row['date'],
            "code": row['code']
        })
        
    return jsonify(projects_list), 200

# --- 4. 새 프로젝트 추가 API (POST) ---
@app.route('/api/projects', methods=['POST'])
def add_project():
    user_id = get_user_from_token()
    if user_id == "EXPIRED" or not user_id:
        return jsonify({"message": "인증에 실패했습니다."}), 401
        
    data = request.json
    p_id = data.get('id')
    title = data.get('title')
    date = data.get('date')
    code = data.get('code')
    
    if not p_id or not title:
        return jsonify({"message": "올바른 프로젝트 데이터가 아닙니다."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO projects (id, title, date, code, user_id) VALUES (?, ?, ?, ?, ?)', 
                       (p_id, title, date, code, user_id))
        conn.commit()
        return jsonify({"message": "프로젝트가 성공적으로 생성되었습니다."}), 201
    except sqlite3.Error as e:
        return jsonify({"message": f"DB 에러: {str(e)}"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    # 5000번 포트에서 디버그 모드로 실행
    app.run(port=5000, debug=True)