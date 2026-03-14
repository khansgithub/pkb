import postgres from 'postgres'

export type SnippetCode = {
    id: number;
    code: string | null;
};

export type SnippetsDb = {
    id: number;
    snippetIndex: number | null; // References SnippetCode.id
    metadata: string | null;
    metadataAi: string | null;
};

async function main(){
    const sql = postgres({
        host: "127.0.0.1",
        port: 5432,
        onnotice: () => {}, // disable PostgreSQL NOTICE/INFO logging
    }); // will use psql environment variables
    
    const x = await sql<SnippetCode[]>`SELECT * FROM snippetCode`;
    const y = x[0] as SnippetCode;
    console.log(y.code);
    console.log(x.length);
    await sql.end();
}

await main();

// export default sql