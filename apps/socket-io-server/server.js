const express = require('express');
const { createServer } = require('http');
const socketIO = require('socket.io');

const app = express();
const httpServer = createServer(app);
const io = socketIO(httpServer, {
  cors: { origin: '*' }
});

app.get('/', (req, res) => res.send('Server online'));

io.on('connection', (socket) => {
  console.log('Device connected:', socket.id);

  socket.on('button_pressed', (data) => {
    console.log('button pressed received:', JSON.stringify(data));

    // STAP 1: Stuur het bericht door naar IEDEREEN (behalve de afzender)
    // Gebruik io.emit om het naar alle verbonden clients (zoals de Pi) te sturen
    io.emit('button_pressed', data); 
    
    console.log('Broadcasted to all clients');
  });

  socket.on('disconnect', () => {
    console.log('Device disconnected:', socket.id);
  });
});

app.use((req, res, next) => {
  console.log('HTTP:', req.method, req.url);
  next();
});

httpServer.listen(3000, '0.0.0.0', () => console.log('Server running on port 3000'));