const express = require('express');
const { asyncHandler } = require('../utils/http');
const requireAdmin = require('../middlewares/auth');

module.exports = (controller) => {
    const router = express.Router();
    router.get('/admin/financial-report', requireAdmin, asyncHandler(controller.financialReport));
    return router;
};
