const config = require('../config');

// Auth mínima para rotas admin/destrutivas: Bearer token comparado com o env.
module.exports = function requireAdmin(req, res, next) {
    const header = req.headers.authorization || '';
    const token = header.startsWith('Bearer ') ? header.slice(7) : null;
    if (!token || token !== config.adminToken) {
        return res.status(401).json({ error: 'unauthorized' });
    }
    next();
};
