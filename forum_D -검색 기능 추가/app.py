from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL 연동하는 부분
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'ahj740429^^' 
app.config['MYSQL_DB'] = 'forum'
mysql = MySQL(app)

# /를 입력했을 때, 즉 기본 페이지 부분
@app.route('/', methods=['GET', 'POST'])
def index():
    search_type = request.form.get('search_type', 'all')
    search_query = request.form.get('search_query', '')

    cur = mysql.connection.cursor()
    
    #검색 조건 설정하는 부분
    if search_type == 'title':
        cur.execute(f"SELECT * FROM topics WHERE title LIKE '%{search_query}%'")
    elif search_type == 'body':
        cur.execute(f"SELECT * FROM topics WHERE body LIKE '%{search_query}%'")
    elif search_type == 'all':
        cur.execute(f"SELECT * FROM topics WHERE title LIKE '%{search_query}%' OR body LIKE '%{search_query}%'")

    else:
        cur.execute("SELECT * FROM topics")
        
    posts = cur.fetchall()
    cur.close()
    return render_template('index.html', posts=posts, search_query=search_query, search_type=search_type)

# Route to add a new post
@app.route('/add', methods=['POST'])
def add_post():
    title = request.form['title']
    body = request.form['body']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO topics (title, body) VALUES (%s, %s)", (title, body))
    mysql.connection.commit()
    cur.close()
    flash('Post added successfully!')
    return redirect(url_for('index'))

# Route to delete a post
@app.route('/delete/<int:id>', methods=['POST'])
def delete_post(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM topics WHERE id = %s", [id])
    mysql.connection.commit()
    cur.close()
    flash('Post deleted successfully!')
    return redirect(url_for('index'))

# Route to show the edit form for a post
@app.route('/edit/<int:id>', methods=['GET'])
def edit_post(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM topics WHERE id = %s", [id])
    post = cur.fetchone()
    cur.close()
    return render_template('edit.html', post=post)

# Route to update the post
@app.route('/update/<int:id>', methods=['POST'])
def update_post(id):
    title = request.form['title']
    body = request.form['body']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE topics SET title = %s, body = %s WHERE id = %s", (title, body, id))
    mysql.connection.commit()
    cur.close()
    flash('Post updated successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
