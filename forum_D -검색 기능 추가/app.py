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

# 허용된 파일 확장자 확인(허용된 확장자를 가지는 파일만 업로드 가능)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'docx'}

# 인덱스 라우트 및 검색 기능
@app.route('/', methods=['GET', 'POST'])
def index():
    search_type = request.form.get('search_type', 'all')
    search_query = request.form.get('search_query', '')
    posts = []  # 초기화하여 빈 리스트로 설정
    
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

# 새 글 작성 라우트
@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO topics (title, body) VALUES (%s, %s)", (title, body))
        mysql.connection.commit()
        cur.close()
        flash('새 글이 추가되었습니다!')
        return redirect(url_for('index'))
    return render_template('add.html')

# 회원가입 라우트
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        name = request.form['name']
        school = request.form['school']

        # 사용자 등록
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (user_id, password, name, school) VALUES (%s, %s, %s, %s)", 
                    (user_id, password, name, school))
        mysql.connection.commit()
        cur.close()
        flash('회원가입이 완료되었습니다!')
        return redirect(url_for('login'))
    return render_template('회원가입.html')

# 로그인 라우트
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s AND password = %s", (user_id, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['user_id'] = user['user_id']
            flash('로그인 성공!')
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다.')
    return render_template('login.html')

# 로그아웃 라우트
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('로그아웃되었습니다.')
    return redirect(url_for('index'))

# 내 프로필 수정 라우트
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        school = request.form['school']
        cur.execute("UPDATE users SET name = %s, school = %s WHERE user_id = %s", (name, school, user_id))
        mysql.connection.commit()
        flash('프로필이 수정되었습니다.')
    
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    # 템플릿 파일 이름을 'profile.html'로 수정
    return render_template('profile.html', user=user)

# 다른 회원 프로필 보기 라우트
@app.route('/view_profile/<string:user_id>')
def view_profile(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    # 템플릿 파일 이름을 'view-profile.html'로 수정
    return render_template('view-profile.html', user=user)

# 게시글 수정 라우트
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        cur.execute("UPDATE topics SET title = %s, body = %s WHERE id = %s", (title, body, post_id))
        mysql.connection.commit()
        cur.close()
        flash('게시글이 수정되었습니다.')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM topics WHERE id = %s", (post_id,))
    post = cur.fetchone()
    cur.close()
    return render_template('edit.html', post=post)

# 게시글 삭제
@app.route('/delete/<int:id>', methods=['POST'])
def delete_post(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM topics WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('게시글이 삭제되었습니다.')
    return redirect(url_for('index'))

# 파일 다운로드
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ID 찾기
@app.route('/find_id', methods=['GET', 'POST'])
def find_id():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user:
            flash(f"ID는 {user['id']}입니다.")
        else:
            flash('해당 이메일로 등록된 사용자가 없습니다.')
    return render_template('find-id.html')

# 비밀번호 찾기
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        user_id = request.form['user_id']
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
        mysql.connection.commit()
        cur.close()
        flash(f"새 비밀번호는 {new_password}입니다. 로그인 후 비밀번호를 변경해주세요.")
    return render_template('find-passwd.html')

if __name__ == '__main__':
    app.run(debug=True)
