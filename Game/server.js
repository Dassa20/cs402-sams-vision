const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

const rooms = {}; // { '1234': { game: 'omi', clients: [ws1, ws2], state: {} } }

wss.on('connection', function connection(ws) {
  console.log('New client connected!');

  ws.on('message', function incoming(message) {
    try {
      const data = JSON.parse(message);
      
      if (data.type === 'CREATE_ROOM') {
        // Generate random 4 digit code
        let roomId = Math.floor(1000 + Math.random() * 9000).toString();
        while(rooms[roomId]) {
          roomId = Math.floor(1000 + Math.random() * 9000).toString();
        }
        
        rooms[roomId] = {
          game: data.game,
          clients: [ws],
          state: {}
        };
        
        ws.roomId = roomId; // attach roomId to socket for easy cleanup
        ws.send(JSON.stringify({ type: 'ROOM_CREATED', roomId, playerIndex: 0 }));
        console.log(`Room ${roomId} created for game ${data.game}`);
      }
      
      else if (data.type === 'JOIN_ROOM') {
        const room = rooms[data.roomId];
        if (room) {
          if (room.game !== data.game) {
            ws.send(JSON.stringify({ type: 'ERROR', message: `Room is for ${room.game}` }));
            return;
          }
          const requiredPlayers = room.game === 'higanna' ? 3 : room.game === 'omi' ? 4 : 2;
          
          if (room.clients.length >= requiredPlayers) {
            ws.send(JSON.stringify({ type: 'ERROR', message: 'Room is full' }));
            return;
          }

          const playerIndex = room.clients.length;
          room.clients.push(ws);
          ws.roomId = data.roomId;
          
          ws.send(JSON.stringify({ type: 'JOINED_ROOM', roomId: data.roomId, playerIndex }));
          console.log(`Player ${playerIndex} joined room ${data.roomId}`);
          
          // If enough players, broadcast START
          if (room.clients.length === requiredPlayers) {
            room.clients.forEach(c => c.send(JSON.stringify({ type: 'GAME_START' })));
          }

          // Send them the current state immediately if it exists
          if (Object.keys(room.state).length > 0) {
            ws.send(JSON.stringify({ type: 'STATE_UPDATE', state: room.state }));
          }

        } else {
          ws.send(JSON.stringify({ type: 'ERROR', message: 'Room not found' }));
        }
      }
      
      else if (data.type === 'UPDATE_STATE') {
        const room = rooms[data.roomId];
        if (room) {
          // Merge state
          room.state = { ...room.state, ...data.state };
          // Broadcast to everyone in room
          room.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
              client.send(JSON.stringify({ type: 'STATE_UPDATE', state: room.state }));
            }
          });
        }
      }
      
    } catch (e) {
      console.error("Invalid message format", e);
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
    // If we wanted to, we could clean up the room if a client disconnects, 
    // but for local testing, we'll keep it simple and just let it be.
  });
});

console.log("==================================================");
console.log("🎮 Local Hotspot Game Server Started on port 8080!");
console.log("==================================================");
console.log("To connect your phone to this laptop:");
console.log("1. Connect both devices to the same Wi-Fi OR turn on your Laptop's Mobile Hotspot and connect your phone to it.");
console.log("2. Find your laptop's IPv4 Address (open cmd and type 'ipconfig').");
console.log("3. In your React Native app, enter that IP address!");
