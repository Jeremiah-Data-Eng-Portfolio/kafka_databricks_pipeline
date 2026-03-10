from streaming.jobs.silver_parse import run


if __name__ == "__main__":
    silver_query, _dlq_query = run()
    # Both queries are started in run(); waiting on one keeps process alive.
    silver_query.awaitTermination()
