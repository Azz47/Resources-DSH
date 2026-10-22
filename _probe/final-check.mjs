import { readFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'

const P = 'C:\\Users\\Administrator\\.dsh\\profiles\\desktop'
const prof = JSON.parse(readFileSync(join(P, 'package.json'), 'utf8'))
const deps = prof.dependencies ?? {}
const bundles = prof.dsh?.profile?.bundles ?? []
const bundleText = bundles.join('\n')

const want = [
  'dsh-ppt-studio', 'dsh-craft-your-textbook', 'dsh-plugin-education',
  '@arcaneorion/dsh-teaching-board', 'dsh-mindmap', 'dsh-context',
  'dsh-better-sidebar', 'dsh-hotspots', 'dsh-image-generation', 'dshmarket',
  'dsh-todo-board', 'dsh-skill-mcp-manager',
  '@haoranwang0921/dsh-session-cleaner', '@michengai/dsh-archive-manager',
  'dsh-whale-widget', '@tt-a1i/archify-dsh',
]

const pad = (s, n) => String(s).padEnd(n)
console.log(pad('PACKAGE', 42) + pad('VERSION', 12) + pad('DEP', 6) + pad('BUNDLE', 8) + 'INSTALLED-DIR')
let bad = 0
for (const w of want) {
  const dir = join(P, 'node_modules', w)
  const pj = join(dir, 'package.json')
  let v = 'NOT-FOUND'
  if (existsSync(pj)) v = JSON.parse(readFileSync(pj, 'utf8')).version
  const inDep = Object.prototype.hasOwnProperty.call(deps, w)
  const inBun = bundleText.includes(w)
  if (!inDep || !inBun || v === 'NOT-FOUND') bad++
  console.log(pad(w, 42) + pad(v, 12) + pad(inDep ? 'yes' : 'NO', 6) + pad(inBun ? 'yes' : 'NO', 8) + (existsSync(dir) ? 'yes' : 'no'))
}
console.log('')
console.log('requested packages: ' + want.length)
console.log('any problem row:    ' + bad)
console.log('total dependencies: ' + Object.keys(deps).length)
console.log('total bundles:      ' + bundles.length)
console.log('')
console.log('--- dsh.profile.bundles ---')
for (const b of bundles) console.log('  ' + b)
