const { spawn, execSync } = require('child_process');

// Start live-server
const server = spawn('npx', ['live-server', 'base-v2', '--open=/Base.html'], {
  stdio: 'inherit',
  shell: true,
});

console.log('live-server started. Auto-pulling every 5s...\n');

// Auto-pull every 5 seconds
setInterval(() => {
  try {
    const out = execSync('git pull origin main', { encoding: 'utf8' });
    if (!out.includes('Already up to date')) {
      console.log('[auto-pull]', out.trim());
    }
  } catch (e) {
    // silently ignore network blips
  }
}, 5000);

process.on('SIGINT', () => { server.kill(); process.exit(); });
