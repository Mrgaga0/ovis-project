const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const fs = require('fs');

// 메인 윈도우 변수 (전역)
let mainWindow;

// 개발 환경에서 DevTools 설치
if (isDev) {
  const { default: installExtension, REACT_DEVELOPER_TOOLS, REDUX_DEVTOOLS } = require('electron-devtools-installer');
  
  app.whenReady().then(() => {
    installExtension(REACT_DEVELOPER_TOOLS)
      .then((name) => console.log(`설치 완료: ${name}`))
      .catch((err) => console.log('설치 실패:', err));
      
    installExtension(REDUX_DEVTOOLS)
      .then((name) => console.log(`설치 완료: ${name}`))
      .catch((err) => console.log('설치 실패:', err));
  });
}

// 앱 설정
function createWindow() {
  // 메인 윈도우 생성
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, isDev ? '../public/icon.png' : 'icon.png'),
    show: false, // 준비될 때까지 숨김
  });

  // 로드할 URL (개발/프로덕션 모드에 따라 다름)
  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  // URL 로드
  mainWindow.loadURL(startUrl);

  // 개발자 도구 (개발 모드에서만)
  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  // 윈도우가 준비되면 표시
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 윈도우가 닫히면 메인 윈도우 참조 제거
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Electron 앱이 준비되면 윈도우 생성
app.whenReady().then(createWindow);

// 모든 윈도우가 닫히면 앱 종료 (macOS 제외)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// macOS에서 앱 아이콘 클릭 시 윈도우 재생성
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC 통신 설정 (렌더러 프로세스와 통신)
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

// NAS 경로 확인 (예시 함수)
ipcMain.handle('check-nas-path', async (_, path) => {
  try {
    await fs.promises.access(path, fs.constants.F_OK);
    return { exists: true, path };
  } catch (error) {
    return { exists: false, error: error.message };
  }
});

// 앱 종료 요청
ipcMain.on('app-quit', () => {
  app.quit();
}); 