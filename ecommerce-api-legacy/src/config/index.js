const fs = require('fs');
const path = require('path');

// Carrega o .env, se existir, sem depender de nenhum pacote externo.
const envPath = path.resolve(__dirname, '../../.env');
if (fs.existsSync(envPath)) {
    for (const raw of fs.readFileSync(envPath, 'utf8').split('\n')) {
        const line = raw.trim();
        if (!line || line.startsWith('#')) continue;
        const idx = line.indexOf('=');
        if (idx === -1) continue;
        const key = line.slice(0, idx).trim();
        const value = line.slice(idx + 1).trim();
        if (!(key in process.env)) process.env[key] = value;
    }
}

module.exports = {
    port: Number(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    adminToken: process.env.ADMIN_TOKEN || 'dev-admin-token',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    approvedCardPrefix: process.env.APPROVED_CARD_PREFIX || '4',
};
