const express = require('express');
const mysql = require('mysql');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// MySQL connection
const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: '',
  database: 'studentmanagement'
});

db.connect(err => {
  if (err) {
    console.error('Database connection failed:', err);
    return;
  }
  console.log('MySQL Connected!');
});

// Test route
app.get('/', (req, res) => {
  res.send('Backend is running');
});

// LOGIN Route
app.post('/login', (req, res) => {
  const { username, password } = req.body;

  db.query(
    'SELECT * FROM guards WHERE username = ? AND password = ?',
    [username, password],
    (err, results) => {
      if (err) return res.status(500).json({ success: false, message: 'Database error' });

      if (results.length > 0) {
        res.json({ success: true, message: 'Login successful' });
      } else {
        res.json({ success: false, message: 'Invalid credentials' });
      }
    }
  );
});

// REGISTER Route
app.post('/register', (req, res) => {
  const { username, password } = req.body;

  db.query(
    'INSERT INTO guards (username, password) VALUES (?, ?)',
    [username, password],
    (err, result) => {
      if (err) {
        if (err.code === 'ER_DUP_ENTRY') {
          return res.json({ success: false, message: 'Username already exists' });
        }
        return res.status(500).json({ success: false, message: 'Registration failed' });
      }

      res.json({ success: true, message: 'Registered successfully' });
    }
  );
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
