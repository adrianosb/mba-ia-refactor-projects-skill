// Logger estruturado simples. Nunca receber cartão, senha ou segredo como meta.

const line = (level, msg, meta = {}) =>
    JSON.stringify({ ts: new Date().toISOString(), level, msg, ...meta });

module.exports = {
    info: (msg, meta) => console.log(line('info', msg, meta)),
    warn: (msg, meta) => console.warn(line('warn', msg, meta)),
    error: (msg, meta) => console.error(line('error', msg, meta)),
};
