/**
 * Linting/update script: parses search_box.svelte template, infers DOM structure
 * and z-order, then rewrites the "DOM structure" comment block accordingly.
 *
 * Run from repo root: node front/scripts/update-search-box-dom-comment.js
 * Or from front/: node scripts/update-search-box-dom-comment.js
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SEARCH_BOX_PATH = path.join(__dirname, "..", "src", "lib", "search_box.svelte");

// Short descriptions keyed by id (optional; used when no preceding comment is found)
const DEFAULT_DESCRIPTIONS = {
  "input_box": "relative container",
  "search_box": "top: visible text field",
  "base-layer": "bottom: black base",
  "back-glow": "dark glow",
  "white-glow": "blue-tinted shadow",
  "back-cursor-light": "outer cursor highlight (white, z-30)",
  "inner_cursor_light": "inner cursor highlight (yellow)",
  "inner_light_mask": "clipping mask",
  "inner_light_highlight": "draggable yellow spot",
};

/**
 * Extract z-index from a string (Tailwind z-N or !z-N).
 * @param {string} s
 * @returns {number | null}
 */
function extractZ(s) {
  if (!s) return null;
  const m = s.match(/(?:^|[\s"'])(?:!)?z-(\d+)(?:\s|$|["')])/);
  return m ? parseInt(m[1], 10) : null;
}

/**
 * Get the template section only (markup between </script> and <style> or {#snippet}).
 * @param {string} content
 * @returns {string}
 */
function getTemplateSection(content) {
  const afterScript = content.indexOf("</script>");
  if (afterScript === -1) return "";
  let start = content.indexOf("\n", afterScript) + 1;
  const snippetStart = content.indexOf("{#snippet", afterScript);
  const styleStart = content.indexOf("<style>", afterScript);
  let end = content.length;
  if (snippetStart !== -1) end = Math.min(end, snippetStart);
  if (styleStart !== -1) end = Math.min(end, styleStart);
  return content.slice(start, end);
}

/**
 * Extract the #input_box block (from opening <div id="input_box" to matching closing </div>).
 * @param {string} template
 * @returns {string}
 */
function getInputBoxBlock(template) {
  const inputBoxStart = template.indexOf('<div id="input_box"');
  if (inputBoxStart === -1) return "";
  let depth = 0;
  let i = inputBoxStart;
  while (i < template.length) {
    const open = template.indexOf("<div", i);
    const close = template.indexOf("</div>", i);
    const openInput = template.indexOf("<input", i);
    if (close !== -1 && (open === -1 || close < open) && (openInput === -1 || close < openInput)) {
      depth--;
      if (depth === 0) return template.slice(inputBoxStart, close + "</div>".length);
      i = close + "</div>".length;
      continue;
    }
    if (open !== -1 && (close === -1 || open < close)) {
      depth++;
      i = open + "<div".length;
      continue;
    }
    if (openInput !== -1 && (close === -1 || openInput < close)) {
      depth++;
      i = openInput + "<input".length;
      continue;
    }
    break;
  }
  return "";
}

const INPUT_BOX_SENTINEL = { isInputBoxRoot: true };

/**
 * Parse the input_box block into direct children of #input_box (id, z, tag, children, description).
 * The first <div id="input_box"> is the container; we only collect its direct children.
 */
function parseInputBoxBlock(block) {
  const lines = block.split(/\r?\n/);
  const nodes = [];
  const stack = []; // [ INPUT_BOX_SENTINEL, ...element nodes ]
  let i = 0;
  let inBlockComment = false;

  function pushNode(node) {
    const parent = stack[stack.length - 1];
    if (parent === INPUT_BOX_SENTINEL) {
      nodes.push(node);
    } else {
      parent.children.push(node);
    }
  }

  function getNextCommentLine() {
    let j = i - 1;
    while (j >= 0) {
      const line = lines[j].trim();
      if (line.startsWith("<!--") && line.endsWith("-->")) {
        const inner = line.slice(4, -3).trim();
        const dash = inner.indexOf("—");
        const colon = inner.indexOf(":");
        const idx = dash !== -1 ? dash : (colon !== -1 ? colon : -1);
        if (idx !== -1) return inner.slice(idx + (dash !== -1 ? 1 : 1)).trim();
        return inner;
      }
      if (line && !line.startsWith("<!--")) break;
      j--;
    }
    return null;
  }

  /** Read lines from startLine until we see ">" (full opening tag may span lines). */
  function readAheadUntilTagEnd(startLine, maxLines = 20) {
    let chunk = "";
    for (let k = startLine; k < Math.min(lines.length, startLine + maxLines); k++) {
      chunk += lines[k] + "\n";
      if (chunk.includes(">")) return chunk;
    }
    return chunk;
  }

  function readAheadForZ(startLine, maxLines = 18) {
    let chunk = "";
    for (let k = startLine; k < Math.min(lines.length, startLine + maxLines); k++) {
      chunk += lines[k] + "\n";
      const z = extractZ(chunk);
      if (z !== null) return z;
      if (chunk.includes("</div>") && !chunk.includes("<div")) break;
      if (chunk.includes(">") && lines[k].trim().startsWith("</")) break;
    }
    return null;
  }

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed.includes("<!--") && !trimmed.includes("-->")) inBlockComment = true;
    if (inBlockComment) {
      if (trimmed.includes("-->")) inBlockComment = false;
      i++;
      continue;
    }

    // Opening tag that might span lines: get full tag for id / input_box check
    const openDiv = trimmed.startsWith("<div");
    const openInput = trimmed.startsWith("<input");
    if (openDiv || openInput) {
      const tagChunk = readAheadUntilTagEnd(i);
      const isInputBox = /id\s*=\s*["']input_box["']/.test(tagChunk);
      if (openDiv && isInputBox) {
        stack.push(INPUT_BOX_SENTINEL);
        i++;
        continue;
      }
      const idInTag = tagChunk.match(/\bid\s*=\s*["']([^"']+)["']/);
      if (idInTag) {
        const id = idInTag[1];
        const z = readAheadForZ(i);
        const desc = getNextCommentLine() || DEFAULT_DESCRIPTIONS[id] || "";
        const node = {
          id,
          z,
          tag: openInput ? "input" : "div",
          children: [],
          description: desc || undefined,
        };
        pushNode(node);
        if (openDiv) stack.push(node);
        i++;
        continue;
      }
      if (openDiv && !tagChunk.includes("id=")) {
        const z = readAheadForZ(i);
        if (z !== null && stack.length) {
          const parent = stack[stack.length - 1];
          if (parent !== INPUT_BOX_SENTINEL && parent.z == null) parent.z = z;
        }
        stack.push({ id: null, z, tag: "div", children: [] });
        i++;
        continue;
      }
    }

    // {@render div("id", ...) — id may be on same or next line
    if (trimmed.includes("@render") && trimmed.includes("div")) {
      const renderChunk = readAheadUntilTagEnd(i, 8);
      const renderMatch = renderChunk.match(/\{\s*@render\s+div\s*\(\s*["']([^"']+)["']/);
      if (renderMatch) {
        const id = renderMatch[1];
        const z = readAheadForZ(i);
        const desc = getNextCommentLine() || DEFAULT_DESCRIPTIONS[id] || "";
        const node = { id, z, tag: "div", children: [], description: desc || undefined };
        pushNode(node);
        i++;
        continue;
      }
    }

    if (trimmed.includes("</div>")) {
      const count = (trimmed.match(/<\/div>/g) || []).length;
      for (let n = 0; n < count && stack.length; n++) stack.pop();
      i++;
      continue;
    }

    i++;
  }

  return nodes;
}

/**
 * Effective z for ordering: own z or max of descendants.
 * @param {{ z: number | null, children: Array }} node
 * @returns {number}
 */
function effectiveZ(node) {
  if (node.z != null) return node.z;
  if (node.children && node.children.length) {
    return Math.max(...node.children.map(effectiveZ));
  }
  return 0;
}

/**
 * Sort direct children of input_box by effective z (ascending = bottom to top in comment).
 */
function sortByZ(nodes) {
  return [...nodes].sort((a, b) => effectiveZ(a) - effectiveZ(b));
}

/**
 * Format a single line for the tree (with optional description).
 * @param {{ id: string | null, tag: string, z: number | null, description?: string }} node
 * @param {boolean} isLast
 * @param {string} prefix
 */
function formatLine(node, isLast, prefix) {
  const id = node.id || "(anonymous)";
  const tag = node.tag === "input" ? " input" : "";
  const zPart = node.z != null ? ` (z-${node.z})` : "";
  const desc = node.description ? ` — ${node.description}` : "";
  const branch = isLast ? "└── " : "├── ";
  const displayId = id.startsWith("inner_") || id === "base-layer" || id === "back-glow" || id === "white-glow" ? id : `#${id}`;
  return `${prefix}${branch}${displayId}${tag}${zPart}${desc}`;
}

/**
 * Build tree lines (direct children in z-order, then children of each with subtree).
 * @param {{ id?: string, z?: number, tag: string, children: Array, description?: string }[]} nodes
 * @param {string} prefix
 * @returns {string[]}
 */
function buildTreeLines(nodes, prefix = "") {
  const sorted = sortByZ(nodes);
  const lines = [];
  sorted.forEach((node, idx) => {
    const isLast = idx === sorted.length - 1;
    const childPrefix = prefix + (isLast ? "    " : "│   ");
    lines.push(formatLine(node, isLast && !node.children.length, prefix));
    if (node.children && node.children.length) {
      node.children.forEach((child, cIdx) => {
        const cLast = cIdx === node.children.length - 1;
        lines.push(formatLine(child, cLast, childPrefix));
      });
    }
  });
  return lines;
}

/**
 * Generate the full DOM structure comment block.
 */
function generateComment(nodes) {
  const header = [
    "  DOM structure (stacking order, bottom to top):",
    "  #input_box (relative container)",
  ];
  const treeLines = buildTreeLines(nodes);
  const body = treeLines.map((l) => "  " + l);
  return "<!--\n" + header.join("\n") + "\n" + body.join("\n") + "\n-->";
}

/**
 * Replace the existing DOM structure comment in content with the new one.
 * Matches the block that contains "DOM structure (stacking order" and ends with "-->".
 */
function replaceComment(content, newComment) {
  const marker = "DOM structure (stacking order";
  const markerIdx = content.indexOf(marker);
  if (markerIdx === -1) {
    throw new Error("DOM structure comment block not found in file");
  }
  const start = content.lastIndexOf("<!--", markerIdx);
  if (start === -1) {
    throw new Error("DOM structure comment block not found in file");
  }
  const end = content.indexOf("-->", markerIdx);
  if (end === -1) {
    throw new Error("DOM structure comment block not found in file");
  }
  const endAfter = end + "-->".length;
  return content.slice(0, start) + newComment + content.slice(endAfter);
}

function main() {
  const content = fs.readFileSync(SEARCH_BOX_PATH, "utf8");
  const template = getTemplateSection(content);
  const block = getInputBoxBlock(template);
  if (!block) {
    console.error("Could not find #input_box block in template.");
    process.exit(1);
  }
  const nodes = parseInputBoxBlock(block);
  const newComment = generateComment(nodes);
  const updated = replaceComment(content, newComment);
  fs.writeFileSync(SEARCH_BOX_PATH, updated, "utf8");
  console.log("Updated DOM structure comment in", SEARCH_BOX_PATH);
}

main();
