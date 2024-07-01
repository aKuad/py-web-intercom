# Audio client sequence

```mermaid
sequenceDiagram
  participant AP as Audio player
  participant MC as Mic capture
  participant CM as Client main
  participant WSS as Server<br>(Websocket)

  CM->>WSS: Connect
  CM->>AP: Init player
  CM->>MC: Start capture

  par
    loop Periodic callback by 'Mic capture'
      MC->>CM: Captured mic input
      CM->CM: Audio packet encoding
      CM->>WSS: Send [silent] audio packet (mic)
    end
  and Runs by received event
    WSS-->>CM: Receive [silent] audio packet (mixed)
    CM-->CM: Audio packet decoding
    CM->>AP: Play mixed audio
  end
```

> [!NOTE]
>
> It suppose implementation of JavaScript.
>
> At Python (with `sounddevice` and `websockets` module), it takes a little different sequence. But almost of all is same.
