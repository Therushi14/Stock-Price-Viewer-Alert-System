const sqlite3 = require('sqlite3').verbose();

// Initialize SQLite database
const db = new sqlite3.Database(':memory:');

// Create alerts table
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      symbol TEXT NOT NULL,
      threshold REAL NOT NULL,
      email TEXT NOT NULL
    )
  `);
});

module.exports = db;
