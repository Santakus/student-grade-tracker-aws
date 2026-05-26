require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// ==========================================
// DATABASE CONNECTION
// ==========================================
const pool = new Pool({
    host: process.env.RDS_HOSTNAME || 'localhost',
    port: process.env.RDS_PORT || 5432,
    database: process.env.RDS_DB_NAME || 'gradetracker',
    user: process.env.RDS_USERNAME || 'postgres',
    password: process.env.RDS_PASSWORD || 'password',
    ssl: process.env.RDS_HOSTNAME ? { rejectUnauthorized: false } : false
});

// ==========================================
// MIDDLEWARE
// ==========================================
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// ==========================================
// DATABASE INITIALIZATION
// ==========================================
async function initializeDatabase() {
    const client = await pool.connect();
    try {
        await client.query(`
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        `);
        await client.query(`
            CREATE TABLE IF NOT EXISTS grades (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                subject VARCHAR(100) NOT NULL,
                score DECIMAL(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
                grade_letter VARCHAR(2),
                semester VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        `);
        console.log('Database tables initialized successfully.');
    } catch (err) {
        console.error('Database initialization error:', err.message);
    } finally {
        client.release();
    }
}

// Helper: Calculate letter grade
function getLetterGrade(score) {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
}

// ==========================================
// ROUTES
// ==========================================

// Home / Dashboard
app.get('/', async (req, res) => {
    try {
        const studentsResult = await pool.query('SELECT COUNT(*) as count FROM students');
        const gradesResult = await pool.query('SELECT COUNT(*) as count FROM grades');
        const avgResult = await pool.query('SELECT COALESCE(AVG(score), 0) as average FROM grades');
        const topStudents = await pool.query(`
            SELECT s.first_name, s.last_name, ROUND(AVG(g.score), 1) as avg_score
            FROM students s
            JOIN grades g ON s.id = g.student_id
            GROUP BY s.id, s.first_name, s.last_name
            ORDER BY avg_score DESC
            LIMIT 5
        `);

        const gradeDistribution = await pool.query(`
            SELECT grade_letter, COUNT(*) as count
            FROM grades
            GROUP BY grade_letter
            ORDER BY grade_letter
        `);

        res.render('dashboard', {
            totalStudents: studentsResult.rows[0].count,
            totalGrades: gradesResult.rows[0].count,
            classAverage: parseFloat(avgResult.rows[0].average).toFixed(1),
            topStudents: topStudents.rows,
            gradeDistribution: gradeDistribution.rows
        });
    } catch (err) {
        console.error(err);
        res.render('error', { message: 'Failed to load dashboard' });
    }
});

// List all students
app.get('/students', async (req, res) => {
    try {
        const result = await pool.query(`
            SELECT s.*, COALESCE(ROUND(AVG(g.score), 1), 0) as avg_score, COUNT(g.id) as grade_count
            FROM students s
            LEFT JOIN grades g ON s.id = g.student_id
            GROUP BY s.id
            ORDER BY s.last_name, s.first_name
        `);
        res.render('students', { students: result.rows });
    } catch (err) {
        console.error(err);
        res.render('error', { message: 'Failed to load students' });
    }
});

// Add student form
app.get('/students/new', (req, res) => {
    res.render('student-form', { student: null, error: null });
});

// Create student
app.post('/students', async (req, res) => {
    const { first_name, last_name, email } = req.body;
    try {
        await pool.query(
            'INSERT INTO students (first_name, last_name, email) VALUES ($1, $2, $3)',
            [first_name, last_name, email]
        );
        res.redirect('/students');
    } catch (err) {
        console.error(err);
        const errorMsg = err.code === '23505' ? 'A student with this email already exists.' : 'Failed to add student.';
        res.render('student-form', { student: req.body, error: errorMsg });
    }
});

// View student details + grades
app.get('/students/:id', async (req, res) => {
    try {
        const student = await pool.query('SELECT * FROM students WHERE id = $1', [req.params.id]);
        if (student.rows.length === 0) return res.render('error', { message: 'Student not found' });

        const grades = await pool.query(
            'SELECT * FROM grades WHERE student_id = $1 ORDER BY semester DESC, subject ASC',
            [req.params.id]
        );
        const avg = await pool.query(
            'SELECT COALESCE(AVG(score), 0) as average FROM grades WHERE student_id = $1',
            [req.params.id]
        );

        res.render('student-detail', {
            student: student.rows[0],
            grades: grades.rows,
            average: parseFloat(avg.rows[0].average).toFixed(1)
        });
    } catch (err) {
        console.error(err);
        res.render('error', { message: 'Failed to load student details' });
    }
});

// Delete student
app.post('/students/:id/delete', async (req, res) => {
    try {
        await pool.query('DELETE FROM students WHERE id = $1', [req.params.id]);
        res.redirect('/students');
    } catch (err) {
        console.error(err);
        res.render('error', { message: 'Failed to delete student' });
    }
});

// Add grade form
app.get('/students/:id/grades/new', async (req, res) => {
    try {
        const student = await pool.query('SELECT * FROM students WHERE id = $1', [req.params.id]);
        if (student.rows.length === 0) return res.render('error', { message: 'Student not found' });
        res.render('grade-form', { student: student.rows[0], error: null });
    } catch (err) {
        console.error(err);
        res.render('error', { message: 'Failed to load form' });
    }
});

// Create grade
app.post('/students/:id/grades', async (req, res) => {
    const { subject, score, semester } = req.body;
    const numScore = parseFloat(score);
    const letterGrade = getLetterGrade(numScore);

    try {
        await pool.query(
            'INSERT INTO grades (student_id, subject, score, grade_letter, semester) VALUES ($1, $2, $3, $4, $5)',
            [req.params.id, subject, numScore, letterGrade, semester]
        );
        res.redirect(`/students/${req.params.id}`);
    } catch (err) {
        console.error(err);
        const student = await pool.query('SELECT * FROM students WHERE id = $1', [req.params.id]);
        res.render('grade-form', { student: student.rows[0], error: 'Failed to add grade. Score must be 0-100.' });
    }
});

// Health check endpoint (for Elastic Beanstalk)
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// ==========================================
// START SERVER
// ==========================================
initializeDatabase().then(() => {
    app.listen(PORT, () => {
        console.log(`Student Grade Tracker running on port ${PORT}`);
    });
});
