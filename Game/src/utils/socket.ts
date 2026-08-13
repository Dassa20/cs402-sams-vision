export let socket: WebSocket | null = null;
export let myPlayerIndex: number = -1;
export let currentRoomId: string = '';

// We store the global message handler here so screens can override it when they mount
let globalMessageHandler: ((data: any) => void) | null = null;
export const setGlobalMessageHandler = (handler: (data: any) => void) => {
  globalMessageHandler = handler;
};

export const setPlayerIndex = (idx: number) => { myPlayerIndex = idx; };
export const setRoomId = (id: string) => { currentRoomId = id; };

export const connectSocket = (ip: string, onOpen: () => void, onError: (e: any) => void) => {
  if (socket) {
    socket.close();
  }
  
  // If it's a domain/URL (like Replit), connect securely with wss:// and no port
  // If it's an IP (like 192.168.x.x), connect with ws:// and port 8080
  const isIP = /^[0-9.]+$/.test(ip);
  const url = isIP ? `ws://${ip}:8080` : `wss://${ip}`;
  
  socket = new WebSocket(url);
  socket.onopen = onOpen;
  socket.onerror = onError;
  socket.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (globalMessageHandler) {
        globalMessageHandler(data);
      }
    } catch(err) {
      console.error(err);
    }
  };
};

export const sendSocketMessage = (msg: any) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(msg));
  }
};
