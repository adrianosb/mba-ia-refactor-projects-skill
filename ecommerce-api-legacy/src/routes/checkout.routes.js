const express = require('express');
const { asyncHandler } = require('../utils/http');

module.exports = (controller) => {
    const router = express.Router();
    router.post('/checkout', asyncHandler(controller.create));
    return router;
};
