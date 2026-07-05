const { HttpError } = require('../utils/http');
const config = require('../config');
const password = require('../utils/password');
const logger = require('../utils/logger');

// Regra do checkout: valida, decide o pagamento e persiste tudo numa transação.
module.exports = ({ db, users, courses, enrollments, payments, audits }) => ({
    async checkout({ usr, eml, pwd, cid, cc }) {
        if (!usr || !eml || !cid || !cc) throw new HttpError(400, 'Bad Request');

        const course = await courses.findActiveById(cid);
        if (!course) throw new HttpError(404, 'Curso não encontrado');

        const status = String(cc).startsWith(config.approvedCardPrefix) ? 'PAID' : 'DENIED';
        logger.info('checkout.payment', { course_id: cid, status }); // sem cartão nem chave do gateway
        if (status === 'DENIED') throw new HttpError(400, 'Pagamento recusado');

        return db.transaction(async () => {
            const existing = await users.findByEmail(eml);
            let userId;
            if (!existing) {
                const created = await users.create({
                    name: usr,
                    email: eml,
                    pass: password.hash(pwd || '123456'),
                });
                userId = created.lastID;
            } else {
                userId = existing.id;
            }

            const enrollment = await enrollments.create(userId, cid);
            const enrollmentId = enrollment.lastID;
            await payments.create(enrollmentId, course.price, status);
            await audits.log(`Checkout curso ${cid} por ${userId}`);
            return enrollmentId;
        });
    },
});
