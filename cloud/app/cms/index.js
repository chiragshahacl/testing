const { app, session, BrowserWindow, ipcMain, screen } = require("electron");
const path = require("path");
const dotenv = require("dotenv");
const fs = require("fs");
const windowOptions = {
  fullscreen: true,
  frame: false,
  kiosk: true,
};

let loginWindow;
let dialogWindow;

const envVars = dotenv.config();

const createWindows = () => {
  let appUrl;
  let externalDisplay;
  let windows = [];
  // PRIMARY DISPLAY SETUP
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;
  loginWindow = new BrowserWindow({
    ...windowOptions,
    width,
    height,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      partition: "persist:cms",
    },
  });
  if (
    envVars.parsed &&
    envVars.parsed.CMS_URL !== undefined &&
    envVars.parsed.CMS_URL !== ""
  ) {
    // Load URL in primary screen
    appUrl = envVars.parsed.CMS_URL;
    loginWindow.loadURL(envVars.parsed.CMS_URL);
  } else {
    // Load index.html by default
    loginWindow.loadFile(path.join(__dirname, "renderer", "index.html"));
    createEnvironmentDialog();
  }
  // TODO: prevent default close
  loginWindow.on("close", (event) => {
    event.preventDefault();
  });

  // EXTERNAL DISPLAYS SETUP
  const displays = screen.getAllDisplays();
  externalDisplay = displays.filter((display) => {
    return display.bounds.x !== 0 || display.bounds.y !== 0;
  });
  console.log(externalDisplay);
  if (externalDisplay) {
    externalDisplay.forEach((display) => {
      const window = new BrowserWindow({
        ...windowOptions,
        x: display.bounds.x + 50,
        y: display.bounds.y + 50,
        webPreferences: {
          partition: "persist:cms",
        },
      });
      window.loadFile(path.join(__dirname, "renderer", "index.html"));
      windows.push(window);
      // TODO: prevent default close
      window.on("close", (event) => {
        event.preventDefault();
      });
    });
    loginWindow.on("page-title-updated", (_, title) => {
      // loadURL if title changes to login
      if (title === "CMS - Home") {
        console.log(loginWindow.webContents.session.getUserAgent());
        windows.forEach((display, index) => {
          display.webContents.session =
            loginWindow.webContents.session.getUserAgent();
          display.loadURL(
            loginWindow.webContents.getURL() +
              "?groupIndex=" +
              (index + 1) +
              "&hideSetup=1",
          );
        });
      } else {
        windows.forEach((display, index) => {
          display.loadFile(path.join(__dirname, "renderer", "index.html"));
        });
      }
    });
  }
};

const createEnvironmentDialog = async () => {
  dialogWindow = new BrowserWindow({
    icon: path.join(__dirname, "images/desktop-icon.png"),
    modal: true,
    parent: loginWindow,
    width: 500,
    height: 300,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });
  dialogWindow.loadFile(path.join(__dirname, "renderer", "envPrompt.html"));
  ipcMain.on("url-save", (_, appUrl) => {
    fs.writeFile(
      path.resolve(__dirname, ".env"),
      `CMS_URL=${appUrl}`,
      (err) => {
        if (err) console.error("Error writing to .env file:", err);
      },
    );
    loginWindow.loadURL(appUrl + "?groupIndex=0");
    dialogWindow.close();
  });
  dialogWindow.on("closed", () => {
    dialogWindow = null;
  });
};
app.on("ready", () => {
  const sharedSession = session.fromPartition("persist:cms");
  session.defaultSession = sharedSession;
});
app.commandLine.appendSwitch(
  "disable-features",
  "HardwareMediaKeyHandling,MediaSessionService",
);
app.whenReady().then(() => {
  createWindows();
});
