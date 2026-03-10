from streaming.jobs import bronze_ingest, dlq_router, silver_features, silver_parse


def test_jobs_expose_run_entrypoint() -> None:
    assert callable(bronze_ingest.run)
    assert callable(silver_parse.run)
    assert callable(silver_features.run)
    assert callable(dlq_router.run)
