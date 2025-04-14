const { contextBridge, ipcRenderer } = require('electron');

// 안전한 노출을 위한 API
contextBridge.exposeInMainWorld('electron', {
  // 앱 정보
  app: {
    getVersion: () => ipcRenderer.invoke('get-app-version'),
    quit: () => ipcRenderer.send('app-quit'),
  },
  
  // 파일 시스템
  fs: {
    checkNasPath: (path) => ipcRenderer.invoke('check-nas-path', path),
  },
  
  // 시스템 정보
  system: {
    getPlatform: () => process.platform,
    getArch: () => process.arch,
  },
}); 