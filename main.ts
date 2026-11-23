import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entry program for the news-image-20261123 bounty.
// Copies the pre-rendered image ./entry.png into the output directory
// the harness reads (MAKEFUN_OUTPUT_DIR, or /output by default).

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const src = join(here, "entry.png");
const dest = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(src, dest);
console.log(`entry.png -> ${dest} (${statSync(dest).size} bytes)`);
