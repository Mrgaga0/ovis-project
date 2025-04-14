/// <reference types="react-scripts" />

// Electron으로 확장된 window 객체에 대한 타입 정의
interface ElectronAPI {
  app: {
    getVersion: () => Promise<string>;
    quit: () => void;
  };
  fs: {
    checkNasPath: (path: string) => Promise<{exists: boolean; path?: string; error?: string}>;
  };
  system: {
    getPlatform: () => string;
    getArch: () => string;
  };
}

declare global {
  interface Window {
    electron?: ElectronAPI;
  }
}