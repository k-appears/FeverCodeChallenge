# 9. web server selection

Date: 2024-05-08

## Status

Accepted

## Context

Choosing the appropriate web server for our FastAPI application is crucial for ensuring optimal performance and scalability.



## Considered Options

1. **Uvicorn**: Lightning-fast ASGI server designed for optimal performance with ASGI applications like FastAPI.
2. **Hypercorn**: High-performance ASGI server known for simplicity and concurrency.
3. **Gunicorn**: Widely-used WSGI server, also supporting ASGI with `uvicorn.workers.UvicornWorker`.

## Evaluation Criteria

1. **Performance**
2. **Scalability**
3. **Reliability**
4. **Compatibility**
5. **Ease of Use**


- **Uvicorn**:
  - *Pros*: Exceptional performance, high scalability, fully compatible with FastAPI, easy to use.
  - *Cons*: Not as mature of Gunicorn.

- **Hypercorn**:
  - *Pros*: High performance, simplicity, good scalability.
  - *Cons*: Less mature than Uvicorn, fewer features and integrations.

- **Gunicorn**:
  - *Pros*: Widely-used.
  - *Cons*: Not as performant as Uvicorn, configuring workers is more complex, requires ASGI adapter like `uvicorn.asgi` for ASGI applications (FastAPI).
  -

## Conclusion

Since the application is new **Uvicorn** is the optimal choice without significant drawbacks.
