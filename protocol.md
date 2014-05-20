# Rock Paper Scissors Network Protocol
The following strings are the expected commands that either the client and/or
the server is exppecting. They are grouped by which function the client first
uses the call. Each command is a JSON object.

## 1. Register Messages
These are the messages that are used during the registration process.

### Client Messages
These are messages that the client sends to the server.

#### Register Username
To allow the user to pick a personalized username, the client sends the
following message to the server:

```json
{
    "action": "register",
    "username": "[username]"
}
```
Where `[username]` is a name that the user has specified.
### Server Messages
These are the messages that the server sends to the client. The server takes
the username received and checks the current list of registered names then
sends back one of the following messages:

#### Success
If the name is found to be valid to the server, it sends the following succes
message:

```json
{
    "result": "success",
    "clientid": "[id]"
}
````
Where `[id]` is the client unique identifier.

#### Error
If the name is not found to be vailid with the server, it sends back one of the
following messages:

```json
{
    "result": "error",
    "excuse": "[message]"
}
```
Where `[message]` is the description of the error. `"excuse"` is optional.

## 2. Menu Messages
These are the messages for communication between the client and the server
while interacting with the menu.

### Client Messages
The following messages are used by the client to interaction with the server
during the menu phase.

#### List Games
To retrieve a list of possible opponents, the client sends the following
message:

```json
{
    "action": "list"
}
```

#### Create Game
This message is sent to tell the server that they are activily looking for an
opponent.

```json
{
    "action": "create"
}
```

#### Join Game
This message is sent when the user would like to join a specific game.

```json
{
    "action": "join"
    "gameid": "[id]"
}
```
Where `[id]` is the id of the game to be joined.

#### Leave Server
This message is used to gracefully leave the server.

```json
{
    "action":"disconnect"
    "clientid": "[username]"
}
```
Where `[username]` is the username the user chose during registration. Do not
allow this variable to be entered by the user directly.
