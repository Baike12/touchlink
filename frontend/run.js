#!/usr/bin/env node
const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 获取项目根目录
const getProjectRoot = () => {
  // 当前文件所在目录
  const currentDir = __dirname;
  // 向上一级目录即为项目根目录 (frontend -> root)
  return path.resolve(currentDir, '..');
};

// 项目根目录
const PROJECT_ROOT = getProjectRoot();

// 确保日志目录存在
const logDir = path.join(PROJECT_ROOT, 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// 日志文件路径
const logFile = path.join(logDir, 'frontend.log');
const logStream = fs.createWriteStream(logFile, { flags: 'w' });

// 杀掉占用指定端口的进程
function killProcessOnPort(port) {
  try {
    console.log(`检查端口 ${port} 是否被占用...`);
    
    // 在macOS上查找占用端口的进程
    const command = `lsof -i :${port} -t`;
    
    try {
      const pid = execSync(command).toString().trim();
      if (pid) {
        // 可能有多个PID，按行分割
        const pids = pid.split('\n');
        for (const p of pids) {
          if (p.trim()) {
            console.log(`发现进程 ${p} 占用了端口 ${port}，正在杀掉...`);
            try {
              execSync(`kill -9 ${p}`);
              console.log(`已杀掉进程 ${p}`);
            } catch (killError) {
              console.error(`杀掉进程 ${p} 失败: ${killError.message}`);
            }
          }
        }
        return true;
      }
    } catch (error) {
      // 如果没有进程占用该端口，lsof命令会返回非零退出码
      console.log(`没有进程占用端口 ${port}`);
    }
    return false;
  } catch (error) {
    console.error(`检查端口占用时出错: ${error.message}`);
    return false;
  }
}

// 杀掉占用3000-3003端口的所有进程
const portsToCheck = [3000, 3001, 3002, 3003];
let needWait = false;

for (const port of portsToCheck) {
  if (killProcessOnPort(port)) {
    needWait = true;
  }
}

// 如果杀掉了进程，等待一段时间确保端口已经释放
if (needWait) {
  console.log('等待端口释放...');
  execSync('sleep 2');
}

// 再次检查3000端口是否已释放
let portIsAvailable = true;
try {
  execSync('lsof -i :3000 -t');
  console.error('警告：端口3000仍然被占用，可能无法正常启动前端服务');
  portIsAvailable = false;
} catch (error) {
  // 如果命令失败，说明端口已经释放，这是我们期望的结果
  console.log('端口3000已释放，可以启动前端服务');
}

// 如果端口仍然被占用，尝试强制杀掉所有相关进程
if (!portIsAvailable) {
  console.log('尝试强制杀掉所有Node.js进程...');
  try {
    execSync('pkill -9 node');
    console.log('已杀掉所有Node.js进程');
    // 再等待一段时间
    execSync('sleep 2');
  } catch (error) {
    console.log('没有找到Node.js进程');
  }
}

console.log(`启动前端，日志将写入: ${logFile}`);

// 保存进程ID到文件
const pidFile = path.join(logDir, 'frontend.pid');
const savePid = (pid) => {
  fs.writeFileSync(pidFile, pid.toString());
  console.log(`前端进程ID已保存到: ${pidFile}`);
};

// 启动前端开发服务器，指定端口为3000，并强制使用该端口
const process = spawn('npm', ['run', 'dev', '--', '--port', '3000', '--strictPort'], {
  cwd: __dirname,
  stdio: ['ignore', 'pipe', 'pipe']
});

// 保存进程ID
savePid(process.pid);

// 将输出重定向到日志文件
process.stdout.pipe(logStream);
process.stderr.pipe(logStream);

// 监听进程退出
process.on('exit', (code) => {
  console.log(`前端进程已退出，退出码: ${code}`);
  console.log(`请查看日志文件: ${logFile}`);
});

// 监听CTRL+C
process.on('SIGINT', () => {
  console.log('接收到中断信号，正在关闭前端...');
  process.kill();
}); 