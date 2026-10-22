// Probe download mirrors with HEAD only (no body transfer).
const urls = [
  'https://registry.npmmirror.com/-/binary/git-for-windows/v2.56.0.windows.2/PortableGit-2.56.0.2-64-bit.7z.exe',
  'https://registry.npmmirror.com/-/binary/git-for-windows/',
  'https://www.7-zip.org/a/7z2301-x64.exe',
  'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
  'https://mirrors.tuna.tsinghua.edu.cn/',
  'https://codeload.github.com/BtbN/FFmpeg-Builds/tar.gz/refs/heads/master',
];
for (const u of urls) {
  const t0 = Date.now();
  try {
    const ctl = AbortSignal.timeout(20000);
    let r = await fetch(u, { method: 'HEAD', redirect: 'follow', signal: ctl });
    if (r.status === 405 || r.status === 501) r = await fetch(u, { method: 'GET', headers: { Range: 'bytes=0-0' }, redirect: 'follow', signal: ctl });
    const len = r.headers.get('content-length');
    console.log(`${String(r.status).padEnd(4)} ${((Date.now() - t0) / 1000).toFixed(1)}s  ${len ? (Number(len) / 1048576).toFixed(1) + ' MB' : '-'}  ${u}`);
  } catch (e) {
    console.log(`ERR  ${((Date.now() - t0) / 1000).toFixed(1)}s  ${e.cause?.code || e.name}  ${u}`);
  }
}
