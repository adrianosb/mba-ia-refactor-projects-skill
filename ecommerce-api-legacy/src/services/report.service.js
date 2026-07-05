// Monta o relatório financeiro agrupando as linhas do JOIN em memória.
// Mantém o mesmo shape do legado: [{ course, revenue, students: [{ student, paid }] }].
module.exports = ({ reports }) => ({
    async financialReport() {
        const rows = await reports.financialRows();
        const byCourse = new Map();

        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, { course: row.course, revenue: 0, students: [] });
            }
            const bucket = byCourse.get(row.course_id);
            if (row.enrollment_id != null) {
                if (row.status === 'PAID') bucket.revenue += row.amount;
                bucket.students.push({ student: row.student || 'Unknown', paid: row.amount || 0 });
            }
        }

        return [...byCourse.values()];
    },
});
