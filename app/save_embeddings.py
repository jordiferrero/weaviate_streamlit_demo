import weaviate
import os
import pandas as pd

if os.path.isfile(".env"):
    from dotenv import load_dotenv

    load_dotenv(".env")
    OPENAI_APIKEY = os.environ.get("OPENAI_API_KEY")
    WEAVIATE_URL = os.environ.get("WEAVIATE_URL")
    WCD_DEMO_RO_KEY = os.environ.get("WCD_DEMO_RO_KEY")

else:
    raise FileNotFoundError("No .env file found")

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(WCD_DEMO_RO_KEY),
    headers={"X-OpenAI-Api-Key": OPENAI_APIKEY},
)


file_path = "data/linkedin-job-embeddings"

try:
    collection = client.collections.get("linkedin_jobs")
    df_all = pd.DataFrame(columns=["job_id", "embedding"])
    part_number = 1
    batch_size = 50000
    rows_in_batch = 0

    for i, item in enumerate(collection.iterator(include_vector=True)):
        job_id = item.properties["job_id"]
        vector = item.vector["default"]
        df_all.loc[rows_in_batch] = [job_id, vector]
        rows_in_batch += 1

        if rows_in_batch == batch_size:
            # Save the current batch
            file_path = f"{file_path}_{part_number}.parquet"
            df_all.to_parquet(file_path, index=False)

            # Reset the DataFrame and counter
            df_all = pd.DataFrame(columns=["job_id", "embedding"])
            rows_in_batch = 0
            part_number += 1

    # Save any remaining rows
    if rows_in_batch > 0:
        file_path = f"{file_path}_{part_number}.parquet"
        df_all.to_parquet(file_path, index=False)

finally:
    client.close()
