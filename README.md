# Stop loss calculator

This project will help you to calculate the asset stop loss via API

## To build this project with Docker

Build images with:

```shell
docker build --tag stop_loss_calculator .
```

The Dockerfile uses multi-stage builds to run lint and test stages before building the production stage.
If linting or testing fails the build will fail.

You can stop the build at specific stages with the `--target` option:

```shell
docker build --tag stop_loss_calculator . --target <stage>
```

For example we wanted to stop at the **test** stage:

```shell
docker build --tag stop_loss_calculator --target test .
```

We could then get a shell inside the container with:

```shell
docker run -it stop_loss_calculator:latest bash
```

If you do not specify a target the resulting image will be the last image defined which in our case is the 'production' image.

To run the project in your local machine:

```shell
docker run --rm -it -p 127.0.0.1:8000:8000 stop_loss_calculator
```

( The project was dockerized using this example: <https://github.com/svx/poetry-fastapi-docker> )

## Project documentation

http://127.0.0.1:8000/docs

## Code quality

### Code formatting
```shell
black app (file or directory)
```
### Sort imports
```shell
isort app  (file or directory)
```

## Development tips

### Prepare the docker image for develop new features
```shell
docker build --tag stop_loss_calculator . --target development
```

### Run the project allowing code changes
```shell
docker run --rm -it -p 127.0.0.1:8000:8000 -v project_directory:/stop_loss_calculator stop_loss_calculator
```

### Run the project in the background from the terminal (detached mode)
```shell
docker run --rm -it -d -p 127.0.0.1:8000:8000 -v project_directory:/stop_loss_calculator stop_loss_calculator
```
```shell
sudo docker ps -a
```
```shell
docker kill project_id
```