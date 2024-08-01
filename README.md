Publish-subscribe system for communicating between multiple processes on the same machine.

Made with Python3.

Supports multiple subscribers to each publisher.

## Try it out

1. Start the publisher in a shell (shell 1)

```bash
$ python3 publisher.py
Publisher started. Waiting for subscribers...
Enter message to publish:
```

2. In a new shell instance (shell 2), start a subscriber

```bash
$ python3 subscriber.py
Connected to the publisher.
```

3. Publish a message

In shell 1:

```bash
Enter message to publish: Hello world!↵
```

Shell 2 result:

```bash
Received 'Hello world!'
```

4. Shut down the publisher

In shell 1:

```bash
Enter a message to publish: exit↵
```

Shell 2 result:

```bash
Publisher has closed the connection
```
