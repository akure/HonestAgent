import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

const sort = (v) => Array.isArray(v) ? v.map(sort) : v && typeof v === "object" ? Object.fromEntries(Object.keys(v).sort().map(k => [k, sort(v[k])])) : v;
const parse = (v) => { const m = /^(\d+)\.(\d+)$/.exec(v); if (!m) throw Error("ProtocolError"); return [+m[1], +m[2]]; };
const negotiate = (p, major, minor) => { const c = p.map(parse).filter(([m, n]) => m === major && n <= minor).sort((a, b) => b[1] - a[1]); if (!c.length) throw Error("ProtocolError"); return `${c[0][0]}.${c[0][1]}`; };
const extension = (n, c) => { if (!/^x-[a-z0-9][a-z0-9.-]*:[a-z][a-z0-9.-]{0,63}$/.test(n) || !["informational", "restrictive", "security_relevant"].includes(c)) throw Error("ProtocolError"); return c; };
const hash = (intent) => createHash("sha256").update(JSON.stringify(sort({ contract_version: "cx0", destination: "local", ...intent }))).digest("hex");
const one = (x) => { try { let value; if (x.operation === "parse_version") value = parse(x.value).join("."); else if (x.operation === "negotiate_version") value = negotiate(x.peer_versions, x.supported_major, x.supported_minor); else if (x.operation === "validate_extension") value = extension(x.name, x.classification); else if (x.operation === "intent_hash") value = hash(x.intent); else throw Error("ConformanceError"); return { id: x.id, status: "PASS", value }; } catch (e) { return { id: x.id, status: "ERROR", error: e.message }; } };
const manifest = JSON.parse(await readFile(process.argv[2], "utf8"));
if (manifest.suite !== "honestagent.control.v1") throw Error("ConformanceError");
const results = manifest.cases.map(x => { const actual = one(x), expected = x.expected; const conformant = actual.status === expected.status && ((expected.status === "ERROR" && actual.error === expected.error) || (expected.status === "PASS" && (!expected.value || actual.value === expected.value) && (!expected.not_equal_to || actual.value !== expected.not_equal_to))); return { ...actual, expected, conformant }; });
const result = { suite: manifest.suite, suite_version: manifest.suite_version, profile: manifest.profile, passed: results.filter(x => x.conformant).length, failed: results.filter(x => !x.conformant).length, conformant: results.every(x => x.conformant), results };
console.log(JSON.stringify(result, null, 2));
process.exitCode = result.conformant ? 0 : 1;
