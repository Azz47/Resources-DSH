// Read the Electron fuse wire embedded in an executable.
//   node exe_fuses.js <path-to-exe>
const fs = require('fs');
const p = process.argv[2];
const b = fs.readFileSync(p);
const sentinel = Buffer.from('dL7pKGdnNz796PbbjQWNKmHXBZaB9tsX');
const i = b.indexOf(sentinel);
console.log('exe        :', p);
console.log('bytes      :', b.length);
console.log('sentinel at:', i);
if (i < 0) { console.log('no fuse wire found'); process.exit(1); }
const off = i + sentinel.length;
const version = b[off], count = b[off + 1];
console.log('wire ver   :', version, '| fuse count:', count);
const names = ['RunAsNode', 'EnableCookieEncryption', 'EnableNodeOptionsEnvironmentVariable',
  'EnableNodeCliInspectArguments', 'EnableEmbeddedAsarIntegrityValidation', 'OnlyLoadAppFromAsar',
  'LoadBrowserProcessSpecificV8Snapshot', 'GrantFileProtocolExtraPrivileges'];
for (let k = 0; k < count; k++) {
  const v = b[off + 2 + k];
  const label = v === 0x30 ? '0 (disabled)' : v === 0x31 ? '1 (ENABLED)' : '0x' + v.toString(16);
  console.log('  fuse[' + (k + 1) + '] ' + (names[k] || ('unknown' + k)).padEnd(42) + ' = ' + label);
}
