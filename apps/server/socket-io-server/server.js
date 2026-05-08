const express = require('express');
const { createServer } = require('http');
const socketIO = require('socket.io');
const path = require('path');

const app = express();
const httpServer = createServer(app);
const io = socketIO(httpServer, {
  cors: { origin: '*' }
});

// Serveer het HTML bestand
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

io.on('connection', (socket) => {
  console.log('Device connected:', {
    id: socket.id,
    "x-client-name": socket.handshake.headers['x-client-name'] || 'Unknown',
  });

  // Bestaande button logic
  socket.on('button_pressed', (data) => {
    console.log('Button pressed received:', data);
    io.emit('button_pressed', data); 
  });

  // Nieuwe message logic
  socket.on('send_message', (message) => {
    console.log('Message received:', message);
    // Stuur het bericht door naar iedereen
    io.emit('new_message', message);
  });

  socket.on('disconnect', () => {
    console.log('Device disconnected:', socket.id);
  });
});

httpServer.listen(3000, '0.0.0.0', () => {
  console.log('Server running on http://localhost:3000');
});