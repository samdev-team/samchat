# SAM-CHAT
Better Chat App

### Connection Types
#### user
can join rooms and send messages in them/connect to voice chat
#### room

#### bot(potentially)

### Message Dissection
 - **Header**
   - message type - string (0 = msg, 1 = action, 2 = voice, 3 = video)
   - message author - string 
   - message recipient - string
 - **Body**
   - message - string
 
### Message Example
message_type : 0\
message_author : blocky\
message_recipient: rozza\
message: i like bob

 
