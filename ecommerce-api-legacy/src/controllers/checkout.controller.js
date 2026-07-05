module.exports = ({ checkoutService }) => ({
    async create(req, res) {
        const enrollmentId = await checkoutService.checkout({
            usr: req.body.usr,
            eml: req.body.eml,
            pwd: req.body.pwd,
            cid: req.body.c_id,
            cc: req.body.card,
        });
        res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    },
});
