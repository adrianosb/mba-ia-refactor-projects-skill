module.exports = (db) => ({
    create(userId, courseId) {
        return db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
    },
});
