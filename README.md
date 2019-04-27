# librarian
VOWR Music Librarian Web App

To run the app within a FreeBSD jail I recommend using the convenient [iocage](https://iocage.readthedocs.io/en/latest/) 
jail management tool. With this, one may execute commands similar to those shown below to run an instance of _librarian_.

```bash
iocage create -r LATEST -n <jail-name>
iocage set ip4_addr="<interface-name>|<ip-address>/<cidr-subnet-mask>" <jail-name>
iocage set boot=on <jail-name>
iocage exec <jail-name> 'fetch --no-verify-peer https://raw.githubusercontent.com/jwfh/librarian/master/jailup -o - | sh'
```

Use in Docker is also supported. A [Dockerfile](https://github.com/jwfh/librarian/blob/master/Dockerfile) is provided.
From within the root project directory, run the `docker build` command, specifying any optional parameters you wish to 
include. For example,

```bash
docker build -t jwhouse/librarian:latest .
```

Commits to the `master` branch of this repository trigger automatic rebuilds of the Docker image. These may be pulled
from [Docker Hub](https://hub.docker.com/r/jwhouse/librarian).
