# 8. testing framework selection

Date: 2024-05-08

## Status

Accepted

## Context

Selecting a testing framework for our FastAPI application.

## Decision
The following testing frameworks:
1. **pytest**.
2. **unittest**.
3. **FastAPI TestClient**: Provided by FastAPI for testing API endpoints.

### Evaluation criteria:
1. **Ease of use**: How easy is it to set up and write tests.
   1. **pytest**: Provides a simple syntax for writing tests and fixtures but steeper learning curve compared to unittest.
   2. **unittest**: Built-in to Python standard library, simple to use but requires more boilerplate code compared to pytest.
   3. **FastAPI TestClient**: Provides a simple interface for testing FastAPI endpoints, but limited to API testing.
2. **Integration testing capabilities**: Does the framework support integration testing with the in-memory cache?
   1. **pytest**: Supports integration testing with external dependencies through fixtures.
   2. **unittest**: Supports integration testing but requires more setup compared to pytest.
   3. **FastAPI TestClient**: Limited to API testings.
3. **Flexibility**: Can mock external dependencies?
   1. **pytest**: Provides built-in support for mocking external dependencies.
   2. **unittest**: Requires additional libraries like `unittest.mock` for mocking.
   3. **FastAPI TestClient**: Limited to API testing.
4. **Community and documentation**.
   1. **pytest**: Large community and extensive documentation.
   2. **unittest**: Part of Python standard library, well-documented.
   3. **FastAPI TestClient**: Limited to FastAPI documentation.

## Conclusion

After evaluating the testing frameworks based on the criteria mentioned above, we use **pytest** for our FastAPI application with an in-memory cache.
**pytest** offers a balance of ease of use, integration testing capabilities and can be used with FastAPI TestClient for API testing.


## Consequences
