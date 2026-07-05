// Erro com status HTTP para as falhas de negócio (400/404) e wrapper que
// encaminha rejeições de handlers async para o middleware de erro.

class HttpError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

const asyncHandler = (fn) => (req, res, next) =>
    Promise.resolve(fn(req, res, next)).catch(next);

module.exports = { HttpError, asyncHandler };
