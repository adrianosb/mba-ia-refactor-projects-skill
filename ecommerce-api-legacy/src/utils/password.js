const crypto = require('crypto');

// Hash com salt via scrypt (built-in do Node, sem dependência externa).
// Formato armazenado: "<salt>:<derived>".
const KEYLEN = 64;

function hash(pwd) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(String(pwd), salt, KEYLEN).toString('hex');
    return `${salt}:${derived}`;
}

function verify(pwd, stored) {
    if (!stored || !stored.includes(':')) return false;
    const [salt, derived] = stored.split(':');
    const test = crypto.scryptSync(String(pwd), salt, KEYLEN).toString('hex');
    const a = Buffer.from(derived, 'hex');
    const b = Buffer.from(test, 'hex');
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

module.exports = { hash, verify };
