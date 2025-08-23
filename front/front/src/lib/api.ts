import DOMPurify from 'dompurify';

var sanitise = DOMPurify.sanitize;

export function send(query: string): any{
    let q: string = sanitise(query);
    console.log("POST: ", q);
    return {"query": query};
}