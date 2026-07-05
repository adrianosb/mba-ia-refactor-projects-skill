module.exports = ({ reportService }) => ({
    async financialReport(req, res) {
        const report = await reportService.financialReport();
        res.status(200).json(report);
    },
});
