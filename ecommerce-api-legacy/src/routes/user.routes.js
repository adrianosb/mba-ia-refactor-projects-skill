const express = require('express');
const { asyncHandler } = require('../utils/http');
const requireAdmin = require('../middlewares/auth');

module.exports = (controller) => {
    const router = express.Router();
    router.delete('/users/:id', requireAdmin, asyncHandler(controller.remove));
    return router;
};
