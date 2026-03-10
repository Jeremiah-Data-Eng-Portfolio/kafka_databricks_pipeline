from streaming.jobs.silver_features import run


if __name__ == "__main__":
    query = run()
    query.awaitTermination()
