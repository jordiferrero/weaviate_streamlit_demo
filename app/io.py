import numpy as np
import weaviate
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType, Configure
import pandas as pd
import os
import opendatasets as od


if os.path.isfile(".env"):
    from dotenv import load_dotenv

    load_dotenv(".env")
    OPENAI_APIKEY = os.environ.get("OPENAI_API_KEY")
    WEAVIATE_URL = os.environ.get("WEAVIATE_URL")
    WCD_DEMO_RO_KEY = os.environ.get("WCD_DEMO_RO_KEY")

else:
    raise FileNotFoundError("No .env file found")

client = weaviate.connect_to_wcs(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(WCD_DEMO_RO_KEY),
    headers={"X-OpenAI-Api-Key": OPENAI_APIKEY},
)


def create_collection(client):
    # # If need to reset db:
    # client.collections.delete("linkedin_jobs")
    try:
        collection = client.collections.create(
            name="linkedin_jobs",
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-small",
            ),
            generative_config=wvc.config.Configure.Generative.openai(),
        )
    except Exception:
        print("Collection already exists. Connecting to it...")
        collection = client.collections.get("linkedin_jobs")

    return collection


def download_kaggle_dataset(kaggle_dataset_path):
    # Check if 'data/linkedin-jobs.csv' exists
    if not os.path.isfile(kaggle_dataset_path):
        od.download(kaggle_dataset_path, "data")
    else:
        return


def upload_data(collection, kaggle_dataset_path):
    # Define your dataset file path
    download_kaggle_dataset(kaggle_dataset_path)

    # Open the dataset file for reading
    # Only load the first 1000 rows
    jobs_df = pd.read_csv(
        r"data/linkedin-job-postings/postings.csv",
        # nrows=100,
    )
    jobs_df = jobs_df[["title", "description", "company_name", "location", "job_id"]]

    batch_size = 1000

    # Generator function to yield chunks of DataFrame
    def dataframe_chunks(df, chunk_size):
        for start in range(0, len(df), chunk_size):
            yield df.iloc[start : start + chunk_size]

    # Iterate through chunks of df and add to collection
    for n, batch in enumerate(dataframe_chunks(jobs_df, batch_size)):
        print(f"Inserting batch {n}...")
        objs = batch.to_dict(orient="records")
        collection.data.insert_many(objs)

    return


def test_data(collection):
    n = 0
    for item in collection.iterator(include_vector=True):
        n += 1

    print("TESTING...")
    print(f"Number of vectorised entries:{n}")
    print(f"Example vector size: {len(item.vector['default'])}")
    print(f"Example property keys: {[k for k in item.properties.keys()]}")
    return


def main(kaggle_db_path):
    try:
        collection = create_collection(client)
        upload_data(collection, kaggle_db_path)
        test_data(collection)

    finally:
        client.close()  # Close client gracefully


if __name__ == "__main__":
    kaggle_db_path = "https://www.kaggle.com/arshkon/linkedin-job-postings"
    main(kaggle_db_path)
