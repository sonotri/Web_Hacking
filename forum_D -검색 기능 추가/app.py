from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL 설정 부분
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'ahj740429^^'
app.config['MYSQL_DB'] = 'forum'
mysql = MySQL(app)

# 파일 업로드 설정
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용된 파일 확장자 확인
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'docx'}

# 인덱스 라우트는 로그인 화면으로 리디렉션
@app.route('/')
def home():
    return redirect(url_for('login'))

# 로그인 라우트
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            print("Fetched user:", user) 
        except Exception as e:
            print("Error fetching user:", e)  
            flash("오류 발생: 로그인 중 문제가 생겼습니다.")
            return redirect(url_for('login'))
        finally:
            cur.close()
        
        if user and check_password_hash(user[2], password):  
            session['user_id'] = user[0]  
            session['name'] = user[1]  
            session['school'] = user[3]  
            flash('로그인 성공!')
            return redirect(url_for('index'))  # 로그인 성공 시 게시판 화면으로 이동
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다.')
    return render_template('login.html')

# 로그아웃 라우트
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('로그아웃되었습니다.')
    return redirect(url_for('login'))

# 게시판 화면
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))
    
    search_type = request.form.get('search_type', 'all')
    search_query = request.form.get('search_query', '')
    posts = []

    cur = mysql.connection.cursor()
    try:
        if search_type == 'title':
            cur.execute("SELECT * FROM topics WHERE title LIKE %s", (f"%{search_query}%",))
        elif search_type == 'body':
            cur.execute("SELECT * FROM topics WHERE body LIKE %s", (f"%{search_query}%",))
        else:
            cur.execute("SELECT * FROM topics WHERE title LIKE %s OR body LIKE %s", (f"%{search_query}%", f"%{search_query}%"))
        
        posts = cur.fetchall()
    except Exception as e:
        flash(f"오류 발생: {str(e)}")
    finally:
        cur.close()

    return render_template('index.html', posts=posts)

# 내 프로필 보기 라우트
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))

    user = {
        'user_id': session.get('user_id'),
        'name': session.get('name'),
        'school': session.get('school')
    }

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        school = request.form['school']
        cur.execute("UPDATE users SET name = %s, school = %s WHERE user_id = %s", (name, school, user['user_id']))
        mysql.connection.commit()
        session['name'] = name  # 업데이트된 정보를 세션에도 저장
        session['school'] = school
        flash('프로필이 수정되었습니다.')

    cur.close()
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
