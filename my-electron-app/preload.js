const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  startPython: (command) => ipcRenderer.send('start-python', command),
  onPythonData: (callback) => ipcRenderer.on('python-data', (event, data) => callback(data)),
  onPythonStatus: (callback) => ipcRenderer.on('python-status', (event, status) => callback(status)),
  receiveRelicsData: (callback) => ipcRenderer.on('relics-data', (event, data) => callback(data))
});
