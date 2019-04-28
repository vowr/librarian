# VOWR Music Librarian Web App

## Deployment

### FreeBSD

To run the app within a FreeBSD jail I recommend using the convenient [iocage](https://iocage.readthedocs.io/en/latest/)
jail management tool. With this, one may execute commands similar to those shown below to run an instance of _librarian_ inside a jail. Currently this as only been tested on 12.0-RELEASE.

```bash
iocage create -r LATEST -n <jail-name>
iocage set ip4_addr="<interface-name>|<ip-address>/<cidr-subnet-mask>" <jail-name>
iocage set boot=on <jail-name>
iocage exec <jail-name> 'fetch --no-verify-peer https://raw.githubusercontent.com/jwfh/librarian/master/jailup -o - | sh'
```

The `jailup` script executed in line four above does a number of things:

1. Bootstraps the `pkg` package manager
2. Installs required dependencies
3. Clones the _librarian_ repository to `/app`
4. Copies the `librariand` rc.d script to `/etc/rc.d` and enables the _librariand_ service to start at boot
5. Creates a user called `librariand` whose account will be used with [`daemon(8)`](https://www.freebsd.org/cgi/man.cgi?query=daemon&sektion=8&manpath=freebsd-release-ports) to run Gunicorn

### Linux and macOS

Use in Docker is also supported for deployment on Linux or development on macOS. A [Dockerfile](https://github.com/jwfh/librarian/blob/master/Dockerfile) is provided.
From within the root project directory, run the `docker build` command, specifying any optional parameters you wish to
include. For example,

```bash
docker build -t jwhouse/librarian:latest .
```

Commits to the `master` branch of this repository trigger automatic rebuilds of the Docker image. These may be pulled
from [Docker Hub](https://hub.docker.com/r/jwhouse/librarian).
