# 2. add select API documentation

Date: 2024-05-07

## Status

Accepted

## Context

When it comes to generating lean API documentation for a FastAPI project,
there are several alternatives to Swagger that you can consider. Each alternative has its own set of pros and cons, which I'll outline below:

# ReDoc for API Documentation

## Pros:
- **Simplicity**
- **Customization**
- **Automatic Generation**
- **Interactive Features**: ReDoc provides interactive features such as request/response examples

## Cons:
- **Limited Features**: lack of OAuth authentication and request validation.
- **Stability**
- **Integration Complexity**: Integrating ReDoc with FastAPI may require additional setup and configuration.

## Swagger

### Pros:
- **Community Support**
- **Interactive**: allows users to explore and test API endpoints.
- **Automatically generated**

### Cons:
- **steeper learning curve** for customization compared to ReDoc with the metadata annotation.
- **larger documentation**

## Decision

I'd start with Swagger for the API documentation, as it provides a testable interface for the API endpoints.

## Consequences

It could be more challenging to customize the Swagger documentation compared to ReDoc, but the interactive features make it a better choice for the initial API documentation.
If required use ReDoc for the final documentation.
