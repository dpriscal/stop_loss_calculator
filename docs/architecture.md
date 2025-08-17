## Architecture overview

This project follows a pragmatic Domain-Driven Design (DDD) and Hexagonal (Ports & Adapters) layout. The goal is to keep domain logic pure, application orchestration explicit, and I/O concerns isolated, while making endpoints easy to test and swap.

## Layers

### Domain (business logic)
- Location: `app/domain`
- Contents:
  - `services/`: Pure computation (e.g., `local_minima`, `macd_minima`).
  - `models/`: Entities/value-objects (minimal today).
  - `repositories/`: Ports (interfaces/protocols) describing required data access.
- Dependencies: No dependency on frameworks or infrastructure.

### Application (use cases)
- Location: `app/application/use_cases`
- Responsibilities:
  - Coordinate repositories and domain services into use cases (e.g., `get_macd_minima`, `get_stop_loss`).
  - Return simple data structures for presentation layers.
- Dependencies: Depends on domain ports/services; does not depend on web frameworks.

### Interface (delivery)
- Location: `app/main.py`, `app/interface/`
- Responsibilities:
  - FastAPI endpoints (HTTP) and dependency providers (`app/interface/deps.py`).
  - Translate HTTP requests/responses to/from application use cases and schemas.
- Dependencies: Depends inward on application/domain. Uses FastAPI `Depends` for DI.

### Infrastructure (adapters)
- Location: `app/infrastructure`
- Responsibilities:
  - Implement domain ports using external systems (e.g., FMP HTTP client in `adapters/fmp_price_data_repository.py`).
  - Legacy `Financialmodelingprep` now reduced to low-level operations (MACD, exp, resampling, stop-loss policy); orchestration moved to application layer.
- Dependencies: External libraries/SDKs, HTTP clients, files, etc.

## Dependency direction

```
Interface (FastAPI)  →  Application (Use Cases)  →  Domain (Services/Ports)
           ↑                                  ↓
      Infrastructure (Adapters implement Ports)
```

Both Interface and Infrastructure depend inward. Domain never depends on frameworks or vendors.

## Dependency injection (DI)

- We use FastAPI’s built-in DI via `Depends`:
  - Providers: `app/interface/deps.py`
    - `get_repo()` → returns `FmpPriceDataRepository`
    - `get_stop_loss_strategy()` → wraps the existing stop-loss policy
  - Endpoints inject dependencies and call use cases:
    - `GET /stocks/{symbol}` → `uc_get_stop_loss(repo, strategy, …)`
    - `GET /stocks/{symbol}/macd-minima` → `uc_get_macd_minima(repo, …)`
- Tests override providers with `api.dependency_overrides` or monkeypatch the adapter/use case layer.

## Testing strategy

- Domain: `tests/domain/services/` (pure functions, no I/O)
- Application: `tests/application/use_cases/` (fake repositories, no HTTP)
- Interface (API): `tests/test_*.py` using `TestClient` and DI overrides
- Infrastructure: `tests/infrastructure/` (adapters with monkeypatched network)

The suite runs in Docker via the `test` stage; coverage gate is enforced.

## Why this design

- Clear separation of concerns and inward-only dependencies
- Easy to test each layer in isolation
- Swap transport (HTTP) or data providers without touching domain logic
- Gradual migration path from legacy orchestration to use cases


