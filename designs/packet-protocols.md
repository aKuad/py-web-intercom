# Packet protocols

## Audio packet

audio client <--> server

| Length [byte] | Type   | Description                                          |
| ------------: | ------ | ---------------------------------------------------- |
|             1 | uint8  | Packet type ID (0x10)                                |
|             3 | string | Lane name (\*1) (\*2)                                |
|             1 | uint8  | External bytes length (\*3)                          |
|         0~255 | bytes  | External bytes                                       |
|          8820 | bytes  | Audio PCM (44100Hz, 16bit, 4410 samples) (\*4) (\*5) |

> [!NOTE]
>
> (\*1) When lower 2 characters, empty bytes will be filled with spaces. e.g. `"MX"` -> `"MX "`
>
> (\*2) `client -> server` for name updating. `server -> client` for current name echo.
>
> (\*3) External bytes for feature extending.
>
> (\*4) Duration of one packet is 0.1 sec.
>
> (\*5) Value should be little endian. Because JavaScript typed arrays and Python numpy's array are process in little endian in default.

## Silent audio packet

audio client <--> server

| Length [bytes] | Type   | Description                 |
| -------------: | ------ | --------------------------- |
|              1 | uint8  | Packet type ID (0x11)       |
|              3 | string | Lane name (\*1) (\*2)       |
|              1 | uint8  | External bytes length (\*3) |
|          0~255 | bytes  | External bytes              |

It is an audio packet but no having audio data. It is same as an audio packet what has all 0x00 audio data.

Too small (unnecessary) audio data will be muted at mixing. It can reduce network traffic.

## Volume modify packet

mixer client -> serve

| Length [byte] | Type  | Description           |
| ------------: | ----- | --------------------- |
|             1 | uint8 | Packet type ID (0x20) |
|             1 | uint8 | Lane ID to control    |
|             1 | uint8 | Modified volume value |

## Lanes info packet

server -> mixer client

| Length [byte] | type   | Description                       |
| ------------: | ------ | --------------------------------- |
|             1 | uint8  | Packet type ID (0x30)             |
|             1 | uint8  | Lane ID                           |
|             3 | string | Lane name (\*1)                   |
|             1 | uint8  | Current volume value              |
|             1 | uint8  | Current meter value               |
|               |        | Repeat them for all audio clients |

## Loudness monitor packet

server -> mixer client

| Length [byte] | Type  | Description                       |
| ------------: | ----- | --------------------------------- |
|             1 | uint8 | Packet type ID (0x40)             |
|             1 | uint8 | Lane ID                           |
|             1 | uint8 | Current loudness                  |
|               |       | Repeat them for all audio clients |
