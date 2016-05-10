jenkins-grapher
===============

Creates graphs of Jenkins jobs.

Installation
-----
Requires Python 2.7.
Graphviz is optional, but required for PNG creation.

```bash
# Recommended but not required: virtual environment
$ mkvirtualenv jenkins-grapher
$ pip install -r requirements.txt
```

Or use the Docker image:

```bash
$ docker pull mikedougherty/jenkins-grapher
```

Basic Usage
-----------

```bash
$ JENKINS_USER=UserWithExtendedReadPermissions
$ JENKINS_TOKEN=deadbeef
$ OUTPUT_DIR=$(pwd)
$ OUTPUT_FORMAT=
$ export JENKINS_USER JENKINS_TOKEN OUTPUT_DIR OUTPUT_FORMAT
$ ./entrypoint.sh https://yourjenkins.example.org [viewname]
Done fetching 16 jobs.
$ ls graph.*
graph.dot graph.png
```

Or use the Docker image:

```bash
$ docker run \
    --rm \
    -it \
    -e OUTPUT_FORMAT= \
    -e JENKINS_USER=UserWithExtendedReadPermissions \
    -e JENKINS_TOKEN=deadbeef \
    -v "$(pwd):/output" \
    jenkins-grapher \
        https://yourjenkins.example.org [viewname]
Done fetching 16 jobs.
$ ls graph.*
graph.dot graph.png
```

Options
-------

Environment variables
- `JENKINS_USER`: The username that will connect to Jenkins. Required if authentication is necessary. Must be the owner of `JENKINS_TOKEN`
- `JENKINS_TOKEN`: The token that will be used to connect to Jenkins. Required if authentication is necessary. Must belong to `JENKINS_USER`
- `OUTPUT_FORMAT`: `dot`, `png`, or empty. Determines which format will be written to stdout (nothing is written if empty). Default is `dot` in the Docker image.
- `OUTPUT_DIR`: Location where graph.dot and graph.png will be written. Not recommended to alter this when using the Docker image.

Positional arguments:
- Jenkins URL (required): Give the root HTTP(S) URL of your Jenkins instance. Include the port, if necessary.
- View name (optional. default: `All`): Give the name of the view to discover jobs from.

Output:
- Creates files `graph.dot` and `graph.png`
- If `OUTPUT_FORMAT` is not empty, outputs the contents of `graph.$OUTPUT_FORMAT` to stdout
- stderr displays progress

Example output
--------------
![Project view](../../raw/master/example-output/graph.png)
See [graphviz source](../../blob/master/example-output/graph.dot)
