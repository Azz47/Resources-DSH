import fs from 'node:fs';

const file = 'D:/Resources/DSH/_probe/catalogs/dsh-plugin-shop-catalog/package/v1/plugins.58c8672fc03c76240314cf13230a844331e19529635c52f4be539ed29387eb6f.json';
const data = JSON.parse(fs.readFileSync(file, 'utf8'));

const shape = (v, depth = 0) => {
  if (Array.isArray(v)) return `array(${v.length}) of ${v.length ? shape(v[0], depth + 1) : '?'}`;
  if (v && typeof v === 'object') return `{${Object.keys(v).slice(0, 14).join(',')}}`;
  return typeof v;
};

console.log('top-level:', Array.isArray(data) ? `array(${data.length})` : Object.keys(data).join(','));
const arr = Array.isArray(data) ? data : (data.plugins || data.items || data.entries);
console.log('entry shape:', shape(arr?.[0]));
console.log('sample:', JSON.stringify(arr?.[0], null, 1).slice(0, 700));
