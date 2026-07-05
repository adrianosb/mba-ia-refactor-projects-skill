module.exports = (db) => ({
    // Uma query com JOIN no lugar dos loops aninhados do relatório legado (N+1).
    financialRows() {
        return db.all(
            `SELECT c.id    AS course_id,
                    c.title AS course,
                    e.id    AS enrollment_id,
                    u.name  AS student,
                    p.amount AS amount,
                    p.status AS status
               FROM courses c
               LEFT JOIN enrollments e ON e.course_id = c.id
               LEFT JOIN users u       ON u.id = e.user_id
               LEFT JOIN payments p    ON p.enrollment_id = e.id
              ORDER BY c.id, e.id`,
            []
        );
    },
});
