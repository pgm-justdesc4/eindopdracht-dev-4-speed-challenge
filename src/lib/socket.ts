import { Server as HttpServer } from "http";
import SocketIO from "socket.io";

export function initSocket(httpServer: HttpServer) {
  const io = SocketIO(httpServer, {
    origins: "*:*",
  });

  io.on("connection", (socket) => {
    console.log("Device connected:", socket.id);

    socket.on("button_pressed", (data) => {
      console.log("Button pressed!", data);
    });

    socket.on("disconnect", () => {
      console.log("Device disconnected:", socket.id);
    });
  });

  return io;
}
