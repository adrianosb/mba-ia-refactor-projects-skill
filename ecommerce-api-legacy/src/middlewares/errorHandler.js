const logger = require('../utils/logger');

// Erros de negócio (com status) mantêm a mensagem original; o resto vira 500 genérico.
// eslint-disable-next-line no-unused-vars
module.exports = function errorHandler(err, req, res, next) {
    if (err.status) return res.status(err.status).send(err.message);
    logger.error('unhandled_error', { message: err.message });
    res.status(500).json({ error: 'internal error' });
};
