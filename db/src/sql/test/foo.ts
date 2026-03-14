import * as readline from 'readline';
import * as fs from 'fs/promises';
import { createDb } from '../../db';
import { seed } from '../../seed';

// Top-level file name variables
const CREATE_DB_SQL_PATH = new URL('./createDb.sql', import.meta.url).pathname;
const TEST_SQL_PATH = new URL('./test.sql', import.meta.url).pathname;
const FUNCTIONS_SQL_PATH = new URL('./functions.sql', import.meta.url).pathname;
const SEED_DB_SQL_PATH = new URL('./seedDb.sql', import.meta.url).pathname;
const db = await createDb();
let seeded = false;

async function loadFunctions() {
    return await fs.readFile(new URL(FUNCTIONS_SQL_PATH, import.meta.url), 'utf-8');
}

async function buildDb() {
    const createDbSql = await fs.readFile(new URL(CREATE_DB_SQL_PATH, import.meta.url), 'utf-8');
    if (!createDbSql.trim()) {
        console.log('[createDb.sql is empty]');
        return;
    }
    await db.exec(createDbSql);
    console.log('[createDb.sql executed]');
}

async function seedDb({custom}: {custom?: boolean}) {
    if (custom) {
        const seedDbSql = await fs.readFile(new URL(SEED_DB_SQL_PATH, import.meta.url), 'utf-8');
        if (!seedDbSql.trim()) {
            console.log('[seedDb.sql is empty]');
            return;
        }
        await db.exec(seedDbSql);
        console.log('[seedDb.sql executed]');
    }
    else {
        await seed(db);
    }

}

async function setupDb() {
    await buildDb();
    if (!seeded) {
        await seedDb({custom: false});
        seeded = true;
    }
}

async function runTestSql() {
    try {
        const sqlContent = await fs.readFile(new URL(TEST_SQL_PATH, import.meta.url), 'utf-8');
        if (!sqlContent.trim()) {
            console.log('[test.sql is empty]');
            return;
        }
        console.log(
            '[running test.sql]:',
            sqlContent
                .split('\n')
                .filter(line => !line.trim().startsWith('--'))
                .join('\n')
        );
        const result = await db.exec(sqlContent);
        console.log('───────────────[ Results ]───────────────');
        console.log(JSON.stringify(result[0]!.rows, null, 2));
    } catch (err) {
        console.error('Error running test.sql:', err);
    }
}

async function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    let running = true;

    // Cleanly handle SIGINT (Ctrl+C)
    process.on('SIGINT', async () => {
        running = false;
        rl.close();
        await db.close();
        console.log('\nClosing database. Exiting.');
        process.exit(0);
    });

    await setupDb();
    await runTestSql();
    await loadFunctions();

    while (running) {
        await new Promise<void>((resolve) => {
            rl.question('Press Enter to re-run setup_debug_db.sql and test.sql or Ctrl+C to exit: ', async (_answer) => {
                console.clear();

                await loadFunctions();
                await runTestSql();
                resolve();
            });
        });
    }
    await db.close();
}

await main();