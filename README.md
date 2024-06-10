# Weaviate-powered job search engine (vector search in streamlit)


[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://linkedin-weaviate.streamlit.app/)

## Overview of the App

This dashboard uses [Streamlit](https://streamlit.io/) and [Weaviate](https://weaviate.io/) to search from a [LinkedIn Job Postings](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) database. 

It offers multiple search options such as traditional BM25, Semantic & Hybrid (generative search is disabled) to find your dream job.

Our Weaviate database contains +150k job postings between 2023-2024 ready for you to be discovered.

### Steps

1. Select on the sidebar the type of search and the number of top-matches to display

2. Type a type of job you are looking for in the search bar at the bottom, or select an example query.

3. Read the suggested job openings related to your match!

## See it deployed online

Go to [the link](https://linkedin-weaviate.streamlit.app/) to interact with it in a deployed environment.

## Run it locally

Create a virtual environment.
```sh
.venv\Scripts\activate.bat
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## How it works

The database contains more than 150k jobs from the [LinkedIn Job Postings](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings). We used the following attributes to index the cards:

- Job title (`title`)
- Job description (`description`)
- Company's name (`company_name`)
- Location of job (`location`)

The demo offers 3 search options with defined GraphQL queries, which you can use to search for various job postings. 
You can search for job types such as "Machine Learning" or "AI" or you can search for location, technical skills, job descriptions, and more.

The first is the **BM25 search**, it's a method used by search engines to rank documents based on their relevance to a given query, factoring in both the frequency of keywords and the length of the document. In simple terms, we're conducting keyword matching.

We can simply pass a query to the `query` parameter ([see docs](https://weaviate.io/developers/weaviate/search/bm25))

```graphql
{
    Get {
        LinkedIn_Jobs(limit: {job_limit}, bm25: { query: "Machine learning with pytorch" }) 
        {
            ...
        }
    }
}
```

The second option is **Vector search**, a method used to find and rank results based on their similarity to a given search query.
Instead of matching keywords, it understands the context and meaning behind the query, offering relevant and more semantic related results. For example, when we search for "Machine learning" we might also get jobs like a "Deep learning" or "Data Science" because they are semantically related.
We use the nearText function in which we pass our query to the concepts parameter ([see docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#neartext)).

```graphql
{
    Get {
        LinkedIn_Jobs(limit: {job_limit}, nearText: { concepts: ["Machine learning with pytorch"] }) 
        {
            ...
        }
    }
}
```

With **Hybrid search** we combine both methods and use a ranking alogrithm to combine their results. 
It leverages the precision of BM25's keyword-based ranking with vector search's ability to understand context and semantic meaning. 
We can pass our query to the `query` parameter and set the `alpha` that determines the weighting for each search ([see docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid))

```graphql
{
            Get {
                LinkedIn_Jobs(limit: {job_limit}, hybrid: { query: "Machine learning with pytorch" alpha:0.5 }) 
                {
                    ...
                }
            }
        }
```
