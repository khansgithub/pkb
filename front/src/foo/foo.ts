import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const filename = "merged_gists.json"
const test_filename = "merged_gists.test.json"

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const jsonPath = path.join(__dirname, "data", filename);
const testJsonPath = path.join(__dirname, "data", test_filename);

const json = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
const testJson = JSON.parse(fs.readFileSync(testJsonPath, "utf8"));


function main() {
    // const r = buildRows(testJson as Section1[]);
    const r = buildRows(json as Section1[]);
    // Sort 'r' based on the value of a property, e.g., by 'title'
    r.sort((a, b) => {
        if (a.path < b.path) return -1;
        if (a.path > b.path) return 1;
        return 0;
    });
    console.log(JSON.stringify(r, null, 2));
}


main();

