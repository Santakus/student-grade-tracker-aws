import os
import pymysql
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
import socket

app = Flask(__name__)

# ==========================================
# DATABASE CONNECTION
# ==========================================
def get_db():
    """Create a database connection."""
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD', 'password'),
        database=os.environ.get('DB_NAME', 'statusdashboard'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def init_db():
    """Initialize database tables."""
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS status_updates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    team_name VARCHAR(100) NOT NULL,
                    project VARCHAR(200) NOT NULL,
                    status ENUM('on_track', 'at_risk', 'blocked', 'completed') DEFAULT 'on_track',
                    message TEXT NOT NULL,
                    author VARCHAR(100) NOT NULL,
                    instance_id VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS milestones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project VARCHAR(200) NOT NULL,
                    title VARCHAR(300) NOT NULL,
                    due_date DATE NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database init error: {e}")


# ==========================================
# ROUTES
# ==========================================

@app.route('/')
def dashboard():
    """Main dashboard showing all status updates and stats."""
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM status_updates ORDER BY created_at DESC LIMIT 20')
            updates = cursor.fetchall()

            cursor.execute('SELECT status, COUNT(*) as count FROM status_updates GROUP BY status')
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}

            cursor.execute('SELECT COUNT(DISTINCT team_name) as count FROM status_updates')
            team_count = cursor.fetchone()['count']

            cursor.execute('SELECT * FROM milestones ORDER BY due_date ASC LIMIT 10')
            milestones = cursor.fetchall()
        conn.close()

        instance_id = socket.gethostname()

        return render_template('dashboard.html',
                               updates=updates,
                               status_counts=status_counts,
                               team_count=team_count,
                               milestones=milestones,
                               instance_id=instance_id)
    except Exception as e:
        return render_template('error.html', message=str(e))


@app.route('/update', methods=['GET', 'POST'])
def post_update():
    """Post a new status update."""
    if request.method == 'POST':
        try:
            conn = get_db()
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO status_updates (team_name, project, status, message, author, instance_id) VALUES (%s, %s, %s, %s, %s, %s)',
                    (request.form['team_name'], request.form['project'],
                     request.form['status'], request.form['message'],
                     request.form['author'], socket.gethostname())
                )
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('error.html', message=str(e))

    return render_template('update_form.html')


@app.route('/milestone', methods=['GET', 'POST'])
def add_milestone():
    """Add a new project milestone."""
    if request.method == 'POST':
        try:
            conn = get_db()
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO milestones (project, title, due_date) VALUES (%s, %s, %s)',
                    (request.form['project'], request.form['title'], request.form['due_date'])
                )
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('error.html', message=str(e))

    return render_template('milestone_form.html')


@app.route('/health')
def health_check():
    """Health check endpoint for ALB."""
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1')
        conn.close()
        return jsonify({
            'status': 'healthy',
            'instance': socket.gethostname(),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ==========================================
# MAIN
# ==========================================
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80)
