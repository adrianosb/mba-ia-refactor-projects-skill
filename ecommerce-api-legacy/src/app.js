const express = require('express');
const config = require('./config');
const logger = require('./utils/logger');
const Database = require('./db/connection');
const seed = require('./db/seed');

const userModel = require('./models/user.model');
const courseModel = require('./models/course.model');
const enrollmentModel = require('./models/enrollment.model');
const paymentModel = require('./models/payment.model');
const auditModel = require('./models/audit.model');
const reportModel = require('./models/report.model');

const buildCheckoutService = require('./services/checkout.service');
const buildReportService = require('./services/report.service');

const buildCheckoutController = require('./controllers/checkout.controller');
const buildReportController = require('./controllers/report.controller');
const buildUserController = require('./controllers/user.controller');

const checkoutRoutes = require('./routes/checkout.routes');
const reportRoutes = require('./routes/report.routes');
const userRoutes = require('./routes/user.routes');

const errorHandler = require('./middlewares/errorHandler');

// Composition root: só faz o wiring das dependências, sem lógica.
async function buildApp() {
    const db = new Database(config.dbPath);
    await seed(db);

    const users = userModel(db);
    const courses = courseModel(db);
    const enrollments = enrollmentModel(db);
    const payments = paymentModel(db);
    const audits = auditModel(db);
    const reports = reportModel(db);

    const checkoutService = buildCheckoutService({ db, users, courses, enrollments, payments, audits });
    const reportService = buildReportService({ reports });

    const checkoutController = buildCheckoutController({ checkoutService });
    const reportController = buildReportController({ reportService });
    const userController = buildUserController({ users });

    const app = express();
    app.use(express.json());

    app.use('/api', checkoutRoutes(checkoutController));
    app.use('/api', reportRoutes(reportController));
    app.use('/api', userRoutes(userController));

    app.use(errorHandler);
    return { app, db };
}

if (require.main === module) {
    buildApp()
        .then(({ app }) => app.listen(config.port, () => logger.info('server.started', { port: config.port })))
        .catch((err) => {
            logger.error('boot_failed', { message: err.message });
            process.exit(1);
        });
}

module.exports = buildApp;
