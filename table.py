import sqlite3

def create_tables():
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            school TEXT NOT NULL,
            image TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            post_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY,
            comment_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comment_id) REFERENCES comments (id)
        )
    ''')

    
    

    # Add initial admin user
    admin_email = 'admin@admin.com'
    admin_password = 'adminpassword'
    cursor.execute('''
        INSERT OR IGNORE INTO admins (email, password) VALUES (?, ?)
    ''', (admin_email, admin_password))

    # Add initial user
    user_name = 'Jhon Doe'
    user_phone = '+88019XXXXXXXX'
    user_email = 'user@user.com
    user_school = 'X College'
    user_image = '/src/saim.jpg'
    user_password = 'userpassword'
    cursor.execute('''
        INSERT OR IGNORE INTO registrations (name, phone, email, school, image, password) VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_name, user_phone, user_email, user_school, user_image, user_password))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
