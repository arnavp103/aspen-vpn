In one terminal run:

```bash

sudo python server/main.py --host 127.0.0.1 --port 8000

```

In another terminal run:

```bash

sudo python client/main.py --server http://127.0.0.1:8000

```

Then on the server run:

```bash

sudo wg show

```