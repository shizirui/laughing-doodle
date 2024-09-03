const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const { createBrotliCompress } = require('zlib');
const fs = require('fs');

let pythonProcess = null;
let isRunning = false;
let mainWindow;
let buffer = '';  // 用于累积输入数据
const pauseFilePath = path.join(__dirname, './src/pause.flag');


function startPython() {
  pythonProcess = spawn('python', ['-u','./src/check.py']);
  isRunning = true;
  
  pythonProcess.stdout.setEncoding('utf8');
  pythonProcess.stderr.setEncoding('utf8');

  pythonProcess.stdout.on('data', (data) => {
    buffer += data.toString();  // 累积输入数据
    let boundary = buffer.indexOf('\n');  // 假设每个JSON对象以换行符结束

    while (boundary !== -1) {
      let jsonString = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 1);

      try {
        const jsonData = JSON.parse(jsonString);
        mainWindow.webContents.send('python-data', jsonData);
      } catch (err) {
        console.error('Error parsing JSON from Python script:', err);
      }

      boundary = buffer.indexOf('\n');  // 查找下一个换行符
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python error: ${data.toString()}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    isRunning = false;
    mainWindow.webContents.send('python-status', 'stopped');
  });
}

// function stopPython() {
//   if (pythonProcess) {
//     pythonProcess.kill();
//     pythonProcess = null;
//     isRunning = false;
//     mainWindow.webContents.send('python-status', 'stopped');
//   }
// }

ipcMain.on('start-python', async (event, command) => {
  if (command === 'start') {
    fs.writeFileSync(pauseFilePath,'');
    return 'running';
  } else if (command === 'stop') {
    if (fs.existsSync(pauseFilePath)) {
      fs.unlinkSync(pauseFilePath);
    }
    return 'stopped';
  }
  return 'invalid';
});

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: true,
    },
  });
  mainWindow.loadFile('index.html');
};

function readsetting(){
  fs.readFile('relics.json', 'utf-8', (err, data) => {
    if (err) {
      console.error('读取文件失败', err);
      return;
    }
    const relics = JSON.parse(data);
    mainWindow.webContents.on('did-finish-load', () => {
      mainWindow.webContents.send('relics-data', relics);
    });
  });
}

function readcharacter(){
  fs.readFile('','utf-8',(err,data) => {
    if(err){
      
    }
  })
}

app.whenReady().then(() => {
  createWindow();
  startPython();
  readsetting();
  
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
    if(fs.existsSync(pauseFilePath))
      fs.unlinkSync(pauseFilePath)
  }
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
