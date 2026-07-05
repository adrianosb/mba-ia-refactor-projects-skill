// Acesso a dados de usuário. Só queries parametrizadas e o DTO público.
module.exports = (db) => ({
    findByEmail(email) {
        return db.get('SELECT * FROM users WHERE email = ?', [email]);
    },

    findById(id) {
        return db.get('SELECT * FROM users WHERE id = ?', [id]);
    },

    create({ name, email, pass }) {
        return db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, pass]);
    },

    // Remove o usuário e seus vínculos numa transação, evitando registros órfãos.
    deleteCascade(id) {
        return db.transaction(async () => {
            await db.run(
                'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
                [id]
            );
            await db.run('DELETE FROM enrollments WHERE user_id = ?', [id]);
            const res = await db.run('DELETE FROM users WHERE id = ?', [id]);
            return res.changes;
        });
    },

    // Nunca expor o campo pass na resposta.
    toPublic(row) {
        if (!row) return null;
        return { id: row.id, name: row.name, email: row.email };
    },
});
