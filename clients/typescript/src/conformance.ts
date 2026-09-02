import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

type Case = Record<string, any>;

function sorted(value: any): any {
  if (Array.isArray(value)) return value.map(sorted);
  if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map((key) => [key, sorted(value[key])]));
  return value;
}

function canonical(value: any): string { return JSON.stringify(sorted(value)); }
function parseVersion(value: string): [number, number] {
  const match = /^(\d+)\.(\d+)$/.exec(value);
  if (!match) throw new Error("ProtocolError");
  return [Number(match[1]), Number(match[2])];
}
function negotiate(peer: string[], major: number, minor: number): string {
  const compatible = peer.map(parseVersion).filter(([m, n]) => m === major && n <= minor);
  if (!compatible.length) throw new Error("ProtocolError");
  compatible.sort((a, b) => b[1] - a[1]);
  return `${compatible[0][0]}.${compatible[0][1]}`;
}
function extension(name: string, classification: string): string {
  if (!/^x-[a-z0-9][a-z0-9.-]*:[a-z][a-z0-9.-]{0,63}$/.test(name) || !["informational", "restrictive", "security_relevant"].includes(classification)) throw new Error("ProtocolError");
  return classification;
}
function intentHash(intent: Case): string {
  const payload = { contract_version: "cx0", destination: "local", ...intent };
  return createHash("sha256").update(canonical(payload), "utf8").digest("hex");
}
function runCase(item: Case): Case {
  try {
    let value: string | undefined;
    if (item.operation === "parse_version") value = parseVersion(item.value).join(".");
    else if (item.operation === "negotiate_version") value = negotiate(item.peer_versions, item.supported_major, item.supported_minor);
    else if (item.operation === "validate_extension") value = extension(item.name, item.classification);
    else if (item.operation === "intent_hash") value = intentHash(item.intent);
    else throw new Error("ConformanceError");
    return { id: item.id, status: "PASS", value };
  } catch (error) { return { id: item.id, status: "ERROR", error: (error as Error).message }; }
}

export async function runConformance(path: string): Promise<any> {
  const manifest = JSON.parse(await readFile(path, "utf8"));
  if (manifest.suite !== "honestagent.control.v1") throw new Error("ConformanceError");
  const results = manifest.cases.map((item: Case) => {
    const actual = runCase(item); const expected = item.expected;
    const matches = actual.status === expected.status && ((expected.status === "ERROR" && actual.error === expected.error) || (expected.status === "PASS" && ((!expected.value || actual.value === expected.value) && (!expected.not_equal_to || actual.value !== expected.not_equal_to))));
    return { ...actual, expected, conformant: matches };
  });
  return { suite: manifest.suite, suite_version: manifest.suite_version, profile: manifest.profile, passed: results.filter((r: Case) => r.conformant).length, failed: results.filter((r: Case) => !r.conformant).length, conformant: results.every((r: Case) => r.conformant), results };
}

if (process.argv[1]?.endsWith("conformance.js")) {
  runConformance(process.argv[2]).then((result) => { console.log(JSON.stringify(result, null, 2)); process.exitCode = result.conformant ? 0 : 1; }).catch((error) => { console.error(error.message); process.exitCode = 1; });
}
