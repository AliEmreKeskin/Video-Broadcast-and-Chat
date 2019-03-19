# Video-Broadcast-and-Chat

Server can broadcast a video stream to clients. Clients can watch the video stream and at the same time they can chat with each others.

## Dependencies

NumPy, OpenCV, ZeroMQ

## Usage

As a server:

```
python3 video_stream_room.py
```

As a client:

```
python3 video_stream_room.py <server_ip> <user_name>
```

For instance if server ip is 192.168.1.36 and user name is Emre than:

```
python3 video_stream_room.py 192.168.1.36 Emre
```

## Multithreaded

Both video broadcast and text chat is multithreaded so one server can handle multiple clients.

## Object Oriented

Easily reusable code.
