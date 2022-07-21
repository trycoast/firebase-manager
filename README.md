# Firebase Manager

A simple client that extends the usability of firebase by wrapping firebase_admin functionality with various utility functions.

## Features

- Maintains a local cache of any database changes; reducing the need for network calls drastically.
- Supports relative paths; e.g. "users/<user_id>" can be abstracted away to isolate changes and to truncate the path.

## Usage

```py
from firebase import Firebase
db = Firebase(creds='path/to/auth.json', rel_path='users/<user_id>', cache=True)
db.update({'name': 'John Doe'})
db.read('name')
db.delete('name')
```

## TODO

- support firestore
- support storage
