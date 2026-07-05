const { hash } = require('../utils/password');

// Cria o schema e carrega os dados iniciais no boot (mesmos dados do legado,
// mas a senha do seed agora entra com hash).
async function seed(db) {
    await db.run('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
    await db.run('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await db.run('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await db.run('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await db.run('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

    await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        'Leonan', 'leonan@fullcycle.com.br', hash('123'),
    ]);
    await db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)', [
        'Clean Architecture', 997.0, 'Docker', 497.0,
    ]);
    await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.0, 'PAID')");
}

module.exports = seed;
