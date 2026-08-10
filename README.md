# ExamplePipeline Code Repository

This repository stores Python ETL, modeling, and inference code for the ExamplePipeline project.

## What is tracked
- `scripts/etl/`
- `scripts/modeling/`
- `scripts/inference/`
- supporting code and documentation needed to run scripts

## What is intentionally not tracked
- `notebooks/` (kept local for exploration)
- `models/` (generated model artifacts)
- `outputs/` (generated metrics/validation files)
- `logs/` (run logs)

Project-level data and documents are stored outside this repo under sibling folders in `ExamplePipeline`.

## Execution Reference

Run the scripts from the `ExamplePipeline` root so each script can resolve the project-level `data/` directory. The complete run order, input/output contracts, validation behavior, dependencies, and MLflow artifact details are documented in `../docs/pipeline_reference.md`.
