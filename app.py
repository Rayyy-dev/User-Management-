"""
User Registration System - REST API
A Flask-based REST API for user registration with PostgreSQL database.

Endpoints:
- POST   /api/users      - Register a new user
- GET    /api/users      - List all users
- GET    /api/users/<id> - Get user by ID
- DELETE /api/users/<id> - Delete user by ID
- GET    /health         - Health check endpoint
"""

import os
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash
from email_validator import validate_email, EmailNotValidError
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Database configuration from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://admin:secretpassword@localhost:5432/userdb')


def get_db_connection():
    """Create and return a database connection."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


def validate_user_input(data):
    """Validate user registration input data."""
    errors = []

    # Check required fields
    if not data.get('username'):
        errors.append('Username is required')
    elif len(data['username']) < 3:
        errors.append('Username must be at least 3 characters long')
    elif len(data['username']) > 50:
        errors.append('Username must be less than 50 characters')
    elif not re.match(r'^[a-zA-Z0-9_]+$', data['username']):
        errors.append('Username can only contain letters, numbers, and underscores')

    if not data.get('email'):
        errors.append('Email is required')
    else:
        try:
            # check_deliverability=False skips DNS check (for testing/demo purposes)
            validate_email(data['email'], check_deliverability=False)
        except EmailNotValidError as e:
            errors.append(f'Invalid email: {str(e)}')

    if not data.get('password'):
        errors.append('Password is required')
    elif len(data['password']) < 6:
        errors.append('Password must be at least 6 characters long')

    return errors


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with UI."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) as count FROM users')
        user_count = cur.fetchone()['count']
        cur.execute('SELECT version()')
        pg_version = cur.fetchone()['version'].split(',')[0]
        cur.close()
        conn.close()
        status = 'healthy'
        db_status = 'connected'
        error = None
    except Exception as e:
        status = 'unhealthy'
        db_status = 'disconnected'
        error = str(e)
        user_count = 0
        pg_version = 'N/A'

    # Check if JSON is requested
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'status': status,
            'database': db_status,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if status == 'healthy' else 503

    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Health</title>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'DM Sans', system-ui, sans-serif;
                background: #f5f5f7;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }}
            .container {{
                width: 100%;
                max-width: 480px;
            }}
            .card {{
                background: #fff;
                border-radius: 20px;
                border: 1px solid #e8e8ed;
                overflow: hidden;
            }}
            .header {{
                padding: 32px 32px 24px;
                text-align: center;
                border-bottom: 1px solid #f5f5f7;
            }}
            .status-icon {{
                width: 72px;
                height: 72px;
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 32px;
            }}
            .status-icon.healthy {{
                background: #d1fae5;
            }}
            .status-icon.unhealthy {{
                background: #fee2e2;
            }}
            .header h1 {{
                font-size: 24px;
                font-weight: 700;
                color: #1d1d1f;
                margin-bottom: 8px;
            }}
            .header .status {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: 15px;
                font-weight: 600;
            }}
            .status.healthy {{ color: #059669; }}
            .status.unhealthy {{ color: #dc2626; }}
            .status::before {{
                content: '';
                width: 10px;
                height: 10px;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            .status.healthy::before {{ background: #10b981; }}
            .status.unhealthy::before {{ background: #ef4444; }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            .metrics {{
                padding: 24px 32px;
            }}
            .metric {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 0;
                border-bottom: 1px solid #f5f5f7;
            }}
            .metric:last-child {{ border-bottom: none; }}
            .metric-label {{
                font-size: 14px;
                color: #6e6e73;
            }}
            .metric-value {{
                font-size: 14px;
                font-weight: 600;
                color: #1d1d1f;
            }}
            .metric-value.success {{ color: #059669; }}
            .metric-value.error {{ color: #dc2626; }}
            .footer {{
                padding: 20px 32px;
                background: #fafafa;
                border-top: 1px solid #f5f5f7;
                text-align: center;
            }}
            .footer a {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                color: #1d1d1f;
                text-decoration: none;
                background: #fff;
                border: 1px solid #e8e8ed;
                border-radius: 10px;
                transition: all 0.2s;
            }}
            .footer a:hover {{
                background: #f5f5f7;
            }}
            .timestamp {{
                margin-top: 16px;
                font-size: 12px;
                color: #a1a1a6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="header">
                    <div class="status-icon {status}">
                        {"✓" if status == "healthy" else "✕"}
                    </div>
                    <h1>System Health</h1>
                    <span class="status {status}">
                        {"All Systems Operational" if status == "healthy" else "System Degraded"}
                    </span>
                </div>
                <div class="metrics">
                    <div class="metric">
                        <span class="metric-label">API Status</span>
                        <span class="metric-value success">Running</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Database</span>
                        <span class="metric-value {"success" if db_status == "connected" else "error"}">{db_status.title()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">PostgreSQL</span>
                        <span class="metric-value">{pg_version}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Users</span>
                        <span class="metric-value">{user_count}</span>
                    </div>
                    {f'<div class="metric"><span class="metric-label">Error</span><span class="metric-value error">{error}</span></div>' if error else ''}
                </div>
                <div class="footer">
                    <a href="/">← Back to Dashboard</a>
                    <div class="timestamp">Last checked: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    return html, 200 if status == 'healthy' else 503


# Register a new user
@app.route('/api/users', methods=['POST'])
def register_user():
    """Register a new user with username, email, and password."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate input
        errors = validate_user_input(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400

        # Hash the password
        password_hash = generate_password_hash(data['password'])

        # Insert user into database
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            '''INSERT INTO users (username, email, password_hash)
               VALUES (%s, %s, %s)
               RETURNING id, username, email, created_at''',
            (data['username'], data['email'].lower(), password_hash)
        )

        new_user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'email': new_user['email'],
                'created_at': new_user['created_at'].isoformat()
            }
        }), 201

    except psycopg2.IntegrityError as e:
        if 'username' in str(e):
            return jsonify({'error': 'Username already exists'}), 409
        elif 'email' in str(e):
            return jsonify({'error': 'Email already exists'}), 409
        return jsonify({'error': 'Database integrity error'}), 409
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# List all users
@app.route('/api/users', methods=['GET'])
def list_users():
    """Get a list of all registered users."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT id, username, email, created_at FROM users ORDER BY created_at DESC')
        users = cur.fetchall()

        cur.close()
        conn.close()

        # Format datetime for JSON response
        users_list = []
        for user in users:
            users_list.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'].isoformat()
            })

        return jsonify({
            'users': users_list,
            'count': len(users_list)
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Get user by ID
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by their ID."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT id, username, email, created_at FROM users WHERE id = %s',
            (user_id,)
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'].isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# Delete user by ID
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user by their ID."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user exists
        cur.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()

        if not user:
            cur.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404

        # Delete the user
        cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'message': f'User with ID {user_id} deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


# HTML Template - Clean Modern UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Users</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'DM Sans', system-ui, sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
            min-height: 100vh;
        }

        .app {
            max-width: 1200px;
            margin: 0 auto;
            padding: 48px 24px;
        }

        /* Nav */
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 48px;
        }

        .logo {
            font-size: 20px;
            font-weight: 700;
            color: #1d1d1f;
        }

        .nav-links {
            display: flex;
            gap: 8px;
        }

        .nav-link {
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
            color: #6e6e73;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.2s;
        }

        .nav-link:hover { background: #e8e8ed; color: #1d1d1f; }
        .nav-link.active { background: #1d1d1f; color: #fff; }

        /* Hero */
        .hero {
            text-align: center;
            margin-bottom: 64px;
        }

        .hero h1 {
            font-size: 48px;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin-bottom: 16px;
            background: linear-gradient(135deg, #1d1d1f 0%, #6e6e73 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: 18px;
            color: #6e6e73;
        }

        /* Main Grid */
        .main-grid {
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 32px;
        }

        @media (max-width: 900px) {
            .main-grid { grid-template-columns: 1fr; }
        }

        /* Card */
        .card {
            background: #fff;
            border-radius: 20px;
            border: 1px solid #e8e8ed;
        }

        .card-head {
            padding: 24px 28px 20px;
            border-bottom: 1px solid #f5f5f7;
        }

        .card-head h2 {
            font-size: 16px;
            font-weight: 600;
            color: #1d1d1f;
        }

        .card-body {
            padding: 28px;
        }

        /* Form */
        .field {
            margin-bottom: 20px;
        }

        .field label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 8px;
        }

        .field input {
            width: 100%;
            padding: 14px 16px;
            font-size: 15px;
            font-family: inherit;
            border: 1px solid #d2d2d7;
            border-radius: 12px;
            background: #fff;
            color: #1d1d1f;
            transition: all 0.2s;
        }

        .field input::placeholder { color: #a1a1a6; }
        .field input:focus {
            outline: none;
            border-color: #0071e3;
            box-shadow: 0 0 0 4px rgba(0,113,227,0.1);
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 14px 28px;
            font-size: 15px;
            font-weight: 600;
            font-family: inherit;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-primary {
            width: 100%;
            background: #0071e3;
            color: #fff;
        }

        .btn-primary:hover { background: #0077ed; }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

        .btn-secondary {
            background: #f5f5f7;
            color: #1d1d1f;
        }

        .btn-secondary:hover { background: #e8e8ed; }

        .btn-delete {
            padding: 8px 14px;
            font-size: 13px;
            background: #fff;
            color: #ff3b30;
            border: 1px solid #ffcdd2;
        }

        .btn-delete:hover { background: #fff5f5; }

        /* Table */
        .users-card .card-body { padding: 0; }

        .users-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 28px;
            border-bottom: 1px solid #f5f5f7;
        }

        .users-header h2 {
            font-size: 16px;
            font-weight: 600;
        }

        .users-count {
            font-size: 13px;
            color: #6e6e73;
            background: #f5f5f7;
            padding: 6px 12px;
            border-radius: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            text-align: left;
            padding: 14px 28px;
            font-size: 12px;
            font-weight: 600;
            color: #6e6e73;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: #fafafa;
            border-bottom: 1px solid #f5f5f7;
        }

        td {
            padding: 18px 28px;
            font-size: 14px;
            border-bottom: 1px solid #f5f5f7;
        }

        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #fafafa; }

        .user-row {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .user-avatar {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: #f5f5f7;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
            color: #6e6e73;
        }

        .user-details strong {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #1d1d1f;
        }

        .user-details span {
            font-size: 13px;
            color: #6e6e73;
        }

        .status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            font-weight: 500;
            color: #34c759;
        }

        .status::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #34c759;
            border-radius: 50%;
        }

        .date { color: #6e6e73; }

        /* Empty */
        .empty {
            padding: 64px 28px;
            text-align: center;
        }

        .empty-icon {
            width: 64px;
            height: 64px;
            margin: 0 auto 20px;
            background: #f5f5f7;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }

        .empty h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .empty p {
            font-size: 14px;
            color: #6e6e73;
        }

        /* Toast */
        .toast-container {
            position: fixed;
            bottom: 32px;
            right: 32px;
            z-index: 1000;
        }

        .toast {
            padding: 16px 24px;
            background: #1d1d1f;
            color: #fff;
            border-radius: 14px;
            font-size: 14px;
            font-weight: 500;
            animation: slideUp 0.3s ease;
        }

        .toast.error { background: #ff3b30; }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Loading */
        .loading {
            padding: 48px;
            text-align: center;
        }

        .spinner {
            width: 32px;
            height: 32px;
            border: 3px solid #e8e8ed;
            border-top-color: #0071e3;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        /* Footer */
        .footer {
            margin-top: 64px;
            padding-top: 32px;
            border-top: 1px solid #e8e8ed;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            color: #6e6e73;
        }

        .footer a {
            color: #0071e3;
            text-decoration: none;
        }

        .footer a:hover { text-decoration: underline; }

        .api-links {
            display: flex;
            gap: 24px;
        }
    </style>
</head>
<body>
    <div class="app">
        <nav class="nav">
            <div class="logo">UserSystem</div>
            <div class="nav-links">
                <a href="/" class="nav-link active">Dashboard</a>
                <a href="/health" class="nav-link">Health</a>
                <a href="http://localhost:8080" target="_blank" class="nav-link">Database</a>
            </div>
        </nav>

        <div class="hero">
            <h1>User Management</h1>
            <p>Register and manage users with ease</p>
        </div>

        <div class="main-grid">
            <div class="card">
                <div class="card-head">
                    <h2>Add New User</h2>
                </div>
                <div class="card-body">
                    <form id="registerForm">
                        <div class="field">
                            <label>Username</label>
                            <input type="text" id="username" placeholder="Enter username" required>
                        </div>
                        <div class="field">
                            <label>Email</label>
                            <input type="email" id="email" placeholder="Enter email" required>
                        </div>
                        <div class="field">
                            <label>Password</label>
                            <input type="password" id="password" placeholder="Min 6 characters" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Create User</button>
                    </form>
                </div>
            </div>

            <div class="card users-card">
                <div class="users-header">
                    <h2>Users</h2>
                    <span class="users-count" id="userCount">0 users</span>
                </div>
                <div id="usersList">
                    <div class="loading"><div class="spinner"></div></div>
                </div>
            </div>
        </div>

        <footer class="footer">
            <span>Built with Flask + PostgreSQL + Docker</span>
            <div class="api-links">
                <a href="/api/users">GET /api/users</a>
                <a href="/api">API Info</a>
                <a href="/health">Health Check</a>
            </div>
        </footer>
    </div>

    <div class="toast-container" id="toast"></div>

    <script>
        const toast = (msg, error = false) => {
            const el = document.getElementById('toast');
            el.innerHTML = `<div class="toast${error ? ' error' : ''}">${msg}</div>`;
            setTimeout(() => el.innerHTML = '', 3000);
        };

        const loadUsers = async () => {
            const el = document.getElementById('usersList');
            el.innerHTML = '<div class="loading"><div class="spinner"></div></div>';

            try {
                const res = await fetch('/api/users');
                const data = await res.json();

                document.getElementById('userCount').textContent =
                    data.count === 1 ? '1 user' : `${data.count} users`;

                if (!data.users.length) {
                    el.innerHTML = `
                        <div class="empty">
                            <div class="empty-icon">+</div>
                            <h3>No users yet</h3>
                            <p>Create your first user to get started</p>
                        </div>`;
                    return;
                }

                el.innerHTML = `
                    <table>
                        <thead><tr><th>User</th><th>Status</th><th>Joined</th><th></th></tr></thead>
                        <tbody>
                            ${data.users.map(u => `
                                <tr>
                                    <td>
                                        <div class="user-row">
                                            <div class="user-avatar">${u.username.slice(0,2).toUpperCase()}</div>
                                            <div class="user-details">
                                                <strong>${u.username}</strong>
                                                <span>${u.email}</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td><span class="status">Active</span></td>
                                    <td class="date">${new Date(u.created_at).toLocaleDateString('en-US', {month:'short',day:'numeric',year:'numeric'})}</td>
                                    <td><button class="btn btn-delete" onclick="deleteUser(${u.id})">Remove</button></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>`;
            } catch (e) {
                el.innerHTML = '<div class="empty"><h3>Error loading users</h3></div>';
            }
        };

        const deleteUser = async (id) => {
            if (!confirm('Delete this user?')) return;
            try {
                const res = await fetch(`/api/users/${id}`, {method:'DELETE'});
                if (res.ok) { toast('User deleted'); loadUsers(); }
                else toast('Failed to delete', true);
            } catch { toast('Error', true); }
        };

        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            btn.disabled = true;
            btn.textContent = 'Creating...';

            try {
                const res = await fetch('/api/users', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: document.getElementById('username').value,
                        email: document.getElementById('email').value,
                        password: document.getElementById('password').value
                    })
                });
                const data = await res.json();

                if (res.ok) {
                    toast(`User ${data.user.username} created`);
                    e.target.reset();
                    loadUsers();
                } else {
                    toast(data.details?.join(', ') || data.error, true);
                }
            } catch { toast('Error creating user', true); }
            finally { btn.disabled = false; btn.textContent = 'Create User'; }
        });

        loadUsers();
    </script>
</body>
</html>
'''


# Root endpoint - HTML Frontend
@app.route('/', methods=['GET'])
def root():
    """Serve the HTML frontend."""
    return render_template_string(HTML_TEMPLATE)


# API info endpoint
@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint."""
    return jsonify({
        'name': 'User Registration System API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/users': 'Register a new user',
            'GET /api/users': 'List all users',
            'GET /api/users/<id>': 'Get user by ID',
            'DELETE /api/users/<id>': 'Delete user by ID',
            'GET /health': 'Health check'
        }
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
