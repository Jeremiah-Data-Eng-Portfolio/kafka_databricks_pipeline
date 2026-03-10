from streaming.jobs.bronze_ingest import run


if __name__ == "__main__":
    query = run()
    query.awaitTermination()
