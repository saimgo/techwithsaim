from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
import sqlite3
from forms import PostForm, RegistrationForm, UserLoginForm, AdminLoginForm
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
import sqlite3
import io
import sympy as sp
import re
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'saim2024@stella'

# Define the upload folder
UPLOAD_FOLDER = 'C:\\Users\\SAIM\\Documents\\User_Datas'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row
    return conn

#Math solver
# Example validation function for expressions
def validate_expression(expression):
    # Ensure expression only contains allowed characters
    if not re.match(r'^[\w\s\.\*\+\-\^\/\(\)\[\]\{\}\,\=;]*$', expression):
        raise ValueError("Invalid characters in expression.")
    return expression

def is_logged_in():
    return 'user_id' in session

def is_admin_logged_in():
    return session.get('admin_id') is not None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash('You are logged in!You have to log out to register a new account.')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        form.image.data.save(filepath)

        conn = get_db_connection()
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        conn.execute('INSERT INTO registrations (name, phone, email, school, image, password) VALUES (?, ?, ?, ?, ?, ?)',
                     (form.name.data, form.phone.data, form.email.data, form.school.data, filepath, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/get_image/<int:user_id>')
def get_image(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM registrations WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return send_file(io.BytesIO(user['image']), mimetype='image/jpeg')
    
@app.route('/profile', methods=['GET', 'POST'])
def user_profile():
    if 'user_id' not in session:
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))

    form = RegistrationForm()
    
    if form.validate_on_submit():
        print("Form validated and submitted")
        print(f"Form data: name={form.name.data}, phone={form.phone.data}, school={form.school.data}")
        
        try:
            conn = get_db_connection()
            conn.execute('UPDATE registrations SET name = ?, phone = ?, school = ? WHERE id = ?', 
                         (form.name.data, form.phone.data, form.school.data, session['user_id']))
            conn.commit()
            conn.close()

            flash('Your profile has been updated successfully.', 'success')
            return redirect(url_for('user_profile'))
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')
    else:
        if request.method == 'POST':
            print(f"Form validation failed with errors: {form.errors}")
        else:
            print("Form not submitted")

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM registrations WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    form.name.data = user['name']
    form.phone.data = user['phone']
    form.email.data = user['email']
    form.school.data = user['school']

    image_path = user['image']
    image_filename = os.path.basename(image_path)

    return render_template('user_profile.html', form=form, user=user, image_filename=image_filename)


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    form = UserLoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM registrations WHERE email = ?', (form.email.data,)).fetchone()
        conn.close()
        if user and (user['password'], form.password.data):
            session['user_id'] = user['id']
            flash('User login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    elif 'admin_id' in session:
        flash('You already logged in as admin!')
        return redirect(url_for('home'))
    elif 'user_id' in session:
        flash('You already logged in as user!')
        return redirect(url_for('home'))
    


    return render_template('login.html', form=form)
    
    


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    form = AdminLoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM admins WHERE email = ?', (form.email.data,)).fetchone()
        conn.close()
        if user and (user['password'], form.password.data):
            session['admin_id'] = user['id']
            flash('Admin login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    elif 'admin_id' in session:
        flash('You already logged in as admin!')
        return redirect(url_for('home'))
    elif 'user_id' in session:
        flash('You already logged in as user!')
        return redirect(url_for('home'))
    return render_template('admin_login.html', form=form)
    
    
@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    if 'admin_id' not in session:
        flash('You are not authorized for this page!')
        return redirect(url_for('login'))
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('dashboard.html', posts=posts)

    

@app.route('/logout')
def logout():
   
    session.pop('user_id', None)
    # session.pop('admin_id', None)
    if (session.pop('admin_id', None)) :
        return redirect(url_for('admin_login'))
    else:
        flash('You are not logged in yet!Log in.')
        return redirect(url_for('login'))


@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    form = PostForm()
    if form.validate_on_submit():
        author_name = request.form.get('author')
        category = form.category.data
        conn = get_db_connection()
        conn.execute('INSERT INTO posts (title, content, author, category) VALUES (?, ?, ?, ?)',
                     (form.title.data, form.content.data, author_name, category))
        conn.commit()
        conn.close()
        return redirect(url_for('new_post'))
    return render_template('add_post.html', form=form)

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'admin_id' not in session:
        flash('You are not authorized for this action!')
        return redirect(url_for('home'))
    if session.get('admin_id'):
        conn = get_db_connection()
        post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
        conn.close()
        form = PostForm()
        if form.validate_on_submit():
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (form.title.data, form.content.data, post_id))
            conn.commit()
            conn.close()
            return redirect(url_for('home'))
        elif request.method == 'GET':
            form.title.data = post['title']
            form.content.data = post['content']
        return render_template('edit_post.html', form=form)
    else:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('home'))

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if session.get('admin_id'):
        conn = get_db_connection()
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('home'))

@app.route('/list/posts')
def list_posts():
    if 'admin_id' not in session:

        flash('You are not authorized to view this page.', 'danger')
        return redirect(url_for('home'))
    if not session.get('admin_id'):
        flash('You are not authorized to view this page.', 'danger')
        return redirect(url_for('home'))
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('list_posts.html', posts=posts)

@app.route('/category/<string:category>')
def category_posts(category):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts WHERE category = ?', (category,)).fetchall()
    conn.close()
    return render_template('category_posts.html', posts=posts, category=category)

@app.route('/', methods=['GET'])
def home():
    conn = get_db_connection()
    search_query = request.args.get('q')
    per_page = 12

    if search_query:
        # Handle search query
        query = "SELECT COUNT(*) FROM posts WHERE title LIKE ? OR content LIKE ?"
        total_posts = conn.execute(query, (f'%{search_query}%', f'%{search_query}%')).fetchone()[0]
    else:
        # Get total number of posts
        query = 'SELECT COUNT(*) FROM posts'
        total_posts = conn.execute(query).fetchone()[0]

    total_pages = (total_posts + per_page - 1) // per_page
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    if search_query:
        # Fetch posts for search query
        query = "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?"
        posts = conn.execute(query, (f'%{search_query}%', f'%{search_query}%', per_page, offset)).fetchall()
        conn.close()
        return render_template('search.html', posts=posts, query=search_query, page=page, total_pages=total_pages)
    else:
        # Fetch posts for home page
        posts = conn.execute('SELECT * FROM posts ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
        conn.close()
        return render_template('home.html', posts=posts, page=page, total_pages=total_pages)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        conn.execute('INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)', (name, email, message))
        conn.commit()
        conn.close()

        flash('Your message has been sent successfully!', 'success')

    return render_template('contact.html')



@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    conn = get_db_connection()

    if request.method == 'POST':
        if 'comment' in request.form:
            # Handle new comment submission
            name = request.form['name']
            comment_text = request.form['comment']

            conn.execute('''
                INSERT INTO comments (post_id, name, text) VALUES (?, ?, ?)
            ''', (post_id, name, comment_text))

            conn.commit()

        elif 'reply' in request.form:
            # Handle new reply submission
            comment_id = request.form['comment_id']
            name = request.form['name']
            reply_text = request.form['reply']

            conn.execute('''
                INSERT INTO replies (comment_id, name, text) VALUES (?, ?, ?)
            ''', (comment_id, name, reply_text))

            conn.commit()

        return redirect(url_for('post', post_id=post_id))

    # Fetch the main post details
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()

    # Fetch comments associated with the post
    comments = conn.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY timestamp ASC', (post_id,)).fetchall()

    # Fetch replies associated with each comment
    comment_replies = {}
    for comment in comments:
        replies = conn.execute('SELECT * FROM replies WHERE comment_id = ? ORDER BY timestamp ASC', (comment['id'],)).fetchall()
        comment_replies[comment['id']] = replies

    conn.close()

    return render_template('post.html', post=post, comments=comments, comment_replies=comment_replies)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))  # Ensure the user is an admin

    conn = get_db_connection()
    conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()

    post_id = request.form['post_id']
    return redirect(url_for('post', post_id=post_id))

@app.route('/delete_reply/<int:reply_id>', methods=['POST'])
def delete_reply(reply_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))  # Ensure the user is an admin

    conn = get_db_connection()
    conn.execute('DELETE FROM replies WHERE id = ?', (reply_id,))
    conn.commit()
    conn.close()

    post_id = request.form['post_id']
    return redirect(url_for('post', post_id=post_id))

@app.route('/block_user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))  # Ensure the user is an admin

    conn = get_db_connection()
    conn.execute('UPDATE users SET blocked = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    post_id = request.form['post_id']
    return redirect(url_for('post', post_id=post_id))



#Math solver main codes
@app.route('/math_solver')
def math_solver():
    if 'admin_id' in session:
        return render_template('math_solver.html')

    if 'user_id' not in session:
        flash('You must be logged in to access this feature.', 'warning')
        return redirect(url_for('login'))
        
    return render_template('math_solver.html')

@app.route('/solve', methods=['POST'])
def solve():

    # return render_template('index.html')
    try:
        operation = request.form['operation']
        expression = request.form['expression']
        variable = request.form.get('variable', 'x')
        var = sp.symbols(variable)
        
        # Validate expression
        expression = validate_expression(expression)
        
        if operation == 'solve':
            solutions = sp.solve(expression, var)
            result = format_solutions(solutions)
        
        elif operation == 'differentiate':
            derivative = sp.diff(expression, var)
            result = sp.pretty(derivative, use_unicode=False)
        
        elif operation == 'integrate':
            integral = sp.integrate(expression, var)
            result = sp.pretty(integral, use_unicode=False)
            result = str(result)  # Convert SymPy expression to string
        
        elif operation == 'simplify':
            simplified_expr = sp.simplify(expression)
            result = sp.pretty(simplified_expr, use_unicode=False)
        
        elif operation == 'diff_eq':
            y = sp.Function('y')(var)
            diff_eq = sp.Eq(sp.diff(y, var, 2) - y, 0)
            solutions = sp.dsolve(diff_eq)
            result = format_solution(solutions)
        
        elif operation == 'matrix':
            matrix = sp.Matrix(eval(expression))
            matrix_operation = request.form['matrix_operation']
            if matrix_operation == 'inverse':
                result = sp.pretty(matrix.inv(), use_unicode=False)
            elif matrix_operation == 'determinant':
                result = sp.pretty(matrix.det(), use_unicode=False)
            elif matrix_operation == 'eigenvalues':
                result = sp.pretty(matrix.eigenvals(), use_unicode=False)
            else:
                result = 'Invalid matrix operation'
        
        elif operation == 'limit':
            limit_value = request.form.get('limit_value', '0')
            limit = sp.limit(expression, var, limit_value)
            result = sp.pretty(limit, use_unicode=False)
        
        elif operation == 'series':
            series_order = int(request.form.get('series_order', '6'))
            series_expansion = sp.series(expression, var, n=series_order).removeO()
            result = sp.pretty(series_expansion, use_unicode=False)
        
        elif operation == 'sys_eq':
            # Split equations by ';' and remove any leading/trailing whitespace
            equations = [eq.strip() for eq in expression.split(';')]
            system_eqs = [sp.sympify(eq) for eq in equations]

            solutions = sp.linsolve(system_eqs, var)
            result = format_solution(solutions)
        
        elif operation == 'taylor_series':
            taylor_order = int(request.form.get('taylor_order', '4'))
            taylor_series = sp.series(expression, var, n=taylor_order).removeO()
            result = sp.pretty(taylor_series, use_unicode=False)
        
        elif operation == 'partial_fraction':
            partial_frac = sp.apart(expression, var)
            result = sp.pretty(partial_frac, use_unicode=False)
        
        elif operation == 'surface_integral':
            # Perform surface integral
            a1, b1 = float(request.form.get('a1', '0')), float(request.form.get('b1', '1'))
            a2, b2 = float(request.form.get('a2', '0')), float(request.form.get('b2', '1'))
            surface_integral = sp.integrate(expression, (var[0], a1, b1), (var[1], a2, b2))
            result = sp.pretty(surface_integral, use_unicode=False)
        
        elif operation == 'line_integral':
            # Perform line integral
            a, b = float(request.form.get('a', '0')), float(request.form.get('b', '1'))
            line_integral = sp.integrate(expression, (var, a, b))
            result = sp.pretty(line_integral, use_unicode=False)
        
        elif operation == 'volume_integral':
            # Perform volume integral
            a1, b1 = float(request.form.get('a1', '0')), float(request.form.get('b1', '1'))
            a2, b2 = float(request.form.get('a2', '0')), float(request.form.get('b2', '1'))
            a3, b3 = float(request.form.get('a3', '0')), float(request.form.get('b3', '1'))
            volume_integral = sp.integrate(expression, (var[0], a1, b1), (var[1], a2, b2), (var[2], a3, b3))
            result = sp.pretty(volume_integral, use_unicode=False)
        
        elif operation == 'parametric_surface':
            # Calculate area of parametric surface
            t = sp.symbols('t')
            x = sp.Function('x')(t)
            y = sp.Function('y')(t)
            z = sp.Function('z')(t)
            surface_expr = (x, y, z)
            area = sp.integrate(sp.sqrt(sum(sp.diff(s, t)**2 for s in surface_expr)), (t, a, b))
            result = sp.pretty(area, use_unicode=False)
        
        elif operation == 'gradient':
            # Calculate gradient of a scalar field
            gradient = sp.Matrix([sp.diff(expression, var) for var in var])
            result = sp.pretty(gradient, use_unicode=False)
        
        elif operation == 'divergence':
            # Calculate divergence of a vector field
            divergence = sum(sp.diff(expression[i], var[i]) for i in range(len(var)))
            result = sp.pretty(divergence, use_unicode=False)
        
        elif operation == 'curl':
            # Calculate curl of a vector field
            curl = sp.Matrix([
                sp.diff(expression[2], var[1]) - sp.diff(expression[1], var[2]),
                sp.diff(expression[0], var[2]) - sp.diff(expression[2], var[0]),
                sp.diff(expression[1], var[0]) - sp.diff(expression[0], var[1])
            ])
            result = sp.pretty(curl, use_unicode=False)
        
        else:
            result = 'Invalid operation'
        
        return render_template('result.html', operation=operation, expression=expression, result=result)
        # return render_template('index.html')
    except ValueError as ve:
        error_message = f"ValueError: {str(ve)}"
        return render_template('error.html', error_message=error_message)
    
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return render_template('error.html', error_message=error_message)




def format_solutions(solutions):
    if isinstance(solutions, list):
        return ', '.join([str(sol) for sol in solutions])
    else:
        return str(solutions)

def format_solution(solution):
    if isinstance(solution, sp.Eq):
        return f"{solution.lhs} = {solution.rhs}"
    else:
        return str(solution)

#Math solver main codes
@app.route('/pallindrome')
def pallindrome():
    if 'admin_id' in session:
        return render_template('pallindrome.html')

    if 'user_id' not in session:
        flash('You must be logged in to access this feature.', 'warning')
        return redirect(url_for('login'))
        
    return render_template('pallindrome.html')


@app.route('/pallindrome_result', methods=['POST'])
def palli_check():
    inputs = request.form['inputs'].lower()
    # if inputs == inputs[:-1]:
    #     x = print("This is a pallindrome.")
    # else:
    #     x = print("This is not a pallindrome.")
    return render_template('pallindrome_result.html', inputs=inputs)


@app.route('/age')
def age():
    if 'admin_id' in session:
        return render_template('age_calc.html')
    if 'user_id' not in session:
        flash('You have to logged in to access this feature!', 'warning')
        return redirect(url_for('login'))
    return render_template('age.html')


@app.route('/age_calc', methods=['POST'])
def age_calc():
    year = int(request.form['year'])
    month = int(request.form['month'])
    day = int(request.form['day'])
    
    current_date = datetime.now()
    birth_date = datetime(year, month, day)

    # Calculate difference between current date and birth date
    delta = current_date - birth_date

    # Calculate years, months, and days
    age_years = current_date.year - birth_date.year
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age_years -= 1

    age_months = current_date.month - birth_date.month
    if current_date.day < birth_date.day:
        age_months -= 1
    if age_months < 0:
        age_months += 12

    age_days = (current_date - birth_date.replace(year=current_date.year, month=current_date.month)).days
    if age_days < 0:
        previous_month = current_date.month - 1 if current_date.month > 1 else 12
        previous_year = current_date.year if current_date.month > 1 else current_date.year - 1
        previous_month_date = datetime(previous_year, previous_month, birth_date.day)
        age_days = (current_date - previous_month_date).days
    
    age_weeks = delta.days // 7
    remaining_days = delta.days % 7

    # Calculate hours, minutes, and seconds
    age_hours = delta.total_seconds() // 3600
    age_minutes = delta.total_seconds() // 60
    age_seconds = delta.total_seconds()

    return render_template(
        'age_calc.html', 
        year=year, month=month, day=day,
        age_years=age_years, age_months=age_months, age_days=age_days, age_weeks=age_weeks,
        age_hours=int(age_hours), age_minutes=int(age_minutes), age_seconds=int(age_seconds)
    )

if __name__ == '__main__':
    app.run(debug=True)

