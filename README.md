# SMP
My own Socket Messaging Protocol. Useful for simple server-client messaging with continuous connection. This is not a general solution to any kind of problem. It is basically a document for myself to put things in order from now on... 

## Connection

This protocol should only be used in TCP communication. It is a high-level abstraction in terms of data types. This protocol heavily relies on string representation. It is not suitable to transfer raw data.

## Message

- A message can be at most 1460 bytes
- Each message contains header and body parts.
- Unicode is only allowed in body part.
- Long messages can be multi-parted. If a received message is not complete, it is assumed to be continuing in the next socket message. 

### Header

Header can contain information about the client, message itself and connection properties. A header must fit in one TCP message. Any header information that is longer than 1460 bytes should be recognized as invalid.

- Header is essentially a map of ```<String, String>``` entries that are formatted in JSON. 
- Starts at the beginning of the message, ends with first new line('\n') character.
- All the header fields that are described in this document are optional. 


```
{"content_length":"26", "id":"login_2", "ack": "login_1"}
```

#### content_length

As in HTTP, represents the length of the body in terms of bytes. This field is not mandatory because messages are expected to end with a special character anyway. This is for informational purposes only. 

```
{"content_length":"3560"}
```

#### id

A unique identity key that is assigned by the message sender. Essential for acknowledging received messages.  


```
{"id":"i_know_this_one"}
```

#### ack

Informs the receiver that this message is an acknowledgement or answer to an earlier message. Field should contain the ID of the message that is being responded to.

```
{"ack":"you_knew_this_one"}
```

#### hb

Ongoing connections must exchange heartbeats to keep the connection open. This field should only be used in heartbeat messages. It is safe to ignore other headers and body part when 'hb' header is found. 

Recommendations:
- Specify the number of heartbeats as value to the field
- Send heartbeats at each ```timeout/2``` seconds.

```
{"hb":"289"}
```

#### timeout

Timeout is the maximum interval where no message including heartbeats is transmitted. When timeout is reached, both parties agree that the connection is corrupted and should be terminated by both ends. 

Using this field any party can inform the other one that he or she changed the range of timeout interval. 

Default: 10 seconds

```
{"timeout":"30"}
```

#### message_type

Describes the format of body. Supported values are:

- String
- JSON
- XML

### Body

Carries the actual message. There is no limit to body size but if it exceeds a message, it should be partitioned into multiparts. Body ends with a special line ```\n%end_body%\n``` . When this sequence of characters found, the messaging immediately halts and received bytes are packaged into a message to send over a higher level hierarchy. 

- Body should always be encoded with Unicode(UTF-8).
- Seperated from header with only a new line. This new line is not part of the body. Any new lines or whitespaces afterwards are assumed to be part of the body.

#### Multi-Part Body

One of the most important specifications of SMP is that it can support multiple communication chains at the same time. Different Q&As can occur simultenously. However, there needs to be a regulation governing multi-part messages. It would be impossible to understand which parts belong to which header.

If a message is long and divided into parts, the message must specify ID field in the header. Remaining parts must also use the same ID in the header. Because TCP is a blocking messaging protocol, parts are not required to be labeled. Each part that is received can be concatenated to form a complete body. 

## Errors

Socket programming is prone to errors. There are different kinds of error ranging from initial connections to timeout exceptions. This standard offers some methods to handle specific errors. 

### InitialConnectionError

Definition: Occurs when server does not accept new connections. 

Action: Client should try again in x seconds. ```x``` starts from 1 and doubles at every iteration. When it reaches 64, defaults to 60 and never doubles again.

### TimeoutError

Definition: Send or receive operation timeouts. 

Action: Halt the connection. Disconnect and remove from memory. Should be reinitialized by the client.

### ParsingError

Definition: The message is corrupted. Invalid header or missing EOF line after body. 

Action: If ID was present and read correctly, send an acknowledgement message.

```{"ack": "lol_hope_this_works", "error":"PARSE"}```


