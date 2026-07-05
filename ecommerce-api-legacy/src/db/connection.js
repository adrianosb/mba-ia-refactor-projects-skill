const sqlite3 = require('sqlite3').verbose();

// Envelope da API callback-based do sqlite3 em Promises + helper de transação.
class Database {
    constructor(dbPath) {
        this.db = new sqlite3.Database(dbPath);
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.run(sql, params, function (err) {
                if (err) return reject(err);
                resolve(this); // expõe lastID e changes
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        });
    }

    async transaction(work) {
        await this.run('BEGIN');
        try {
            const result = await work();
            await this.run('COMMIT');
            return result;
        } catch (err) {
            await this.run('ROLLBACK');
            throw err;
        }
    }
}

module.exports = Database;
