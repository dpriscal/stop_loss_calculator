# Stop loss calculator

This project will help you to calculate the asset stop loss via API

## Benefits for everyone

- **Protect your money**: helps you pick a safety-net price (a "stop-loss") so if the price falls too much, you can decide to exit earlier and limit losses.
- **Make decisions with facts**: looks at years of past prices to find meaningful low points. You don't need to understand the math.
- **Spot turning points**: optional charts highlight moments when prices tended to bottom out, so patterns are easy to see.
- **Use any stock**: provide a ticker like `AAPL` and it fetches the data for you.
- **Simple setup**: add your API key once, then use friendly URLs or simple commands.
- **Adjust to your style**: a single "window" setting lets you be stricter or more flexible. The default is fine for beginners.
- **Automate it**: because it's an API, you can check levels daily from a script or scheduler.
- **No heavy install**: run it with Docker or Docker compose in a few commands.

## Disclaimer

- This project is for educational and informational purposes only and is not financial advice.
- You are solely responsible for your investment decisions. Use at your own risk.
- Market data comes from third parties and may be delayed or inaccurate. Always verify before acting.
- Past performance does not guarantee future results. Consider consulting a licensed professional.

## Glossary

- **Stop-loss**: a safety-net price you choose in advance. If the market falls to that level, it signals you to exit to limit losses.
- **MACD**: a way to spot momentum and turning points by comparing two moving averages of price. You can think of it as a "trend strength" line that helps identify potential bottoms and tops.

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