# Stop loss calculator

This project will help you to calculate the asset stop loss via API

## To build this project with docker

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

For example, to stop at the test stage:

```shell
docker build --tag stop_loss_calculator --target test .
```

We could then get a shell inside the container with:

```shell
docker run -it stop_loss_calculator:latest bash
```

If you do not specify a target, the resulting image will be the last stage defined, which in our case is the production image.

To run the project on your local machine:

```shell
docker run --rm -it -p 127.0.0.1:8000:8000 stop_loss_calculator
```

( The project was dockerized using this example: <https://github.com/svx/poetry-fastapi-docker> )

## Project api documentation

http://127.0.0.1:8000/docs

## Docker compose

Prerequisites:
- Create your `.env` from the example and set your API key:
```shell
cp env.example .env
```

Run with Docker compose:
```shell
docker compose up --build
```

Stop the stack:
```shell
docker compose down
```

## Environment variables
The file `env.example` at the project root has an example of all environment variables that need to be set for the project to work properly.

Copy this file to `.env` and set the real variable values:
```shell
cp env.example .env
```

### Env vars description
* FINANCIALMODELINGPREP_API_KEY: Is the API key provided by the website [financialmodelingprep](https://site.financialmodelingprep.com/). Check the [API documentation](https://site.financialmodelingprep.com/developer/docs) to have more context.



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

### Prepare the docker image to develop new features
```shell
docker build --tag stop_loss_calculator . --target development
```

### Run the project allowing code changes
```shell
docker run --rm -it -p 127.0.0.1:8000:8000 -v $(pwd):/stop_loss_calculator stop_loss_calculator
```

### Run the project in the background from the terminal (detached mode)
```shell
docker run --rm -it -d -p 127.0.0.1:8000:8000 -v $(pwd):/stop_loss_calculator stop_loss_calculator
```
```shell
sudo docker ps -a
```
```shell
docker kill <container_id>
```

## Qa

See `docs/qa.md` for step-by-step instructions to generate plots and visually verify minima and stop loss. Includes a batch mode for multiple symbols.

Quick start:
- Ensure `FINANCIALMODELINGPREP_API_KEY` is set (env or `.env`).
- Build the dev image: `docker build --target development -t stop_loss_calculator:dev .`
- Run the QA script (outputs saved under `plots/`):
```shell
mkdir -p plots
docker run --rm -t \
  -w /stop_loss_calculator \
  -e FINANCIALMODELINGPREP_API_KEY=${FINANCIALMODELINGPREP_API_KEY} \
  -v $(pwd)/plots:/stop_loss_calculator/plots \
  stop_loss_calculator:dev \
  python scripts/qa_plot_macd_minima.py \
    --symbol AAPL \
    --days 3650 \
    --window 1 \
    --output plots/aapl_macd_minima.png
```

## Further docs

- API endpoints: see `docs/api.md`
- QA plotting and batch runs: see `docs/qa.md`