const { HttpError } = require('../utils/http');

module.exports = ({ users }) => ({
    async remove(req, res) {
        const removed = await users.deleteCascade(req.params.id);
        if (!removed) throw new HttpError(404, 'Usuário não encontrado');
        res.status(200).json({ msg: 'Usuário e vínculos removidos' });
    },
});
