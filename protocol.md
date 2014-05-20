# Rock Paper Scissors Network Protocol
The following strings are the expected commands that either the client and/or
the server is exppecting. They are grouped by which function the client first
uses the call. Each command is a JSON object.

## 1. Register Commands
These are the commands that are used during the registration process.

### Client Sent commands
These are commands that the client sends to the server.

#### Register Username

```json
{
    "action": "register"
    "username": "[username]"
}
```
Where `[username]` is a name that the user has specified.
### Server Sent commands
These are the commands that the server sends to the client.
