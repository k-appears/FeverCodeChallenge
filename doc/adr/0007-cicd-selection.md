# 7. cicd selection

Date: 2024-05-08

## Status

Accepted

## Context

We need to select a Continuous Integration and Continuous Deployment (CI/CD).
The CI/CD tool will help automate the build, test, and deployment processes.
We must evaluate three options: GitHub Actions, GitLab CI/CD, and Jenkins.

Criteria for evaluation include
1. Ease of setup and configuration.
2. Integration with git.
3. Support for Python and frameworks, scalability, and cost.

### GitHub Actions

#### Pros:
1. **Ease of Setup and Configuration**.
2. **Integration with Git**.
3. **Support for Python**.
4. **Flexibility**: Apart from built-in there are third-party actions.
5. **Scalability and Maturity**.
6. **Cost**: GitHub Actions offer generous free usage for public repositories and provide cost-effective pricing for private repositories.

#### Cons:
1. **Limited Self-Hosted Runner Support**.

### GitLab CI/CD

#### Pros:
1. **Ease of Setup and Configuration**.
2. **Integration with Git**.
3. **Support for Python**.
4. **Flexibility**: Customization through shared runners, custom runners, and GitLab CI/CD templates.
5. **Scalability and Maturity**.
6. **Cost**.

#### Cons:
1. **UI Complexity**: Steeper learning curve.

### Jenkins

#### Pros:
1. **Flexibility**.
2. **Integration with Git**.
3. **Support for Python**.
4. **Scalability**: Can be scaled horizontally by distributing builds across multiple Jenkins nodes.
5. **Maturity**: Large community and extensive plugin ecosystem.

#### Cons:
1. **Complex Setup and Configuration**.
2. **Maintenance Overhead**: Requires ongoing maintenance and updates to ensure stability and security.
3. **Resource Intensive**: Resource-intensive, running large-scale CI/CD pipelines

## Decision Justification

Based on the evaluation criteria, particularly ease of setup and configuration, integration with git, support for Python, flexibility, scalability, maturity, and cost, we recommend:

**GitHub Actions** as the preferred CI/CD platform for our project.

## Consequences

Revisit the CI/CD selection if the project requirements change significantly or if GitHub Actions no longer meets the project's needs.
