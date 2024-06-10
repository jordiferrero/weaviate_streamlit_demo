from st_weaviate_connection import WeaviateConnection
import streamlit as st
import time
import sys
import os

from dotenv import load_dotenv

load_dotenv()

# Constants
ENV_VARS = ["WEAVIATE_URL", "WCD_DEMO_RO_KEY", "OPENAI_API_KEY"]
NUM_IMAGES_PER_ROW = 3


# Functions
def get_env_vars(env_vars: list) -> dict:
    """Retrieve environment variables
    @parameter env_vars : list - List containing keys of environment variables
    @returns dict - A dictionary of environment variables
    """

    env_vars = {}
    for var in ENV_VARS:
        value = os.environ.get(var, "")
        if value == "":
            st.error(f"{var} not set", icon="🚨")
            sys.exit(f"{var} not set")
        env_vars[var] = value

    return env_vars


# Environment variables
env_vars = get_env_vars(ENV_VARS)
url = env_vars["WEAVIATE_URL"]
api_key = env_vars["WCD_DEMO_RO_KEY"]
OPENAI_API_KEY = env_vars["OPENAI_API_KEY"]

# Check keys
if url == "" or api_key == "" or OPENAI_API_KEY == "":
    st.error(f"Environment variables not set", icon="🚨")
    sys.exit("Environment variables not set")

st.set_page_config(
    page_title="Job oppenings dashboard",
    page_icon="💻",
)

# Title
st.title("💻 Job oppenings dashboard")

# Connection to Weaviate thorough Connector
conn = st.connection(
    "weaviate",
    type=WeaviateConnection,
    url=os.getenv("WEAVIATE_URL"),
    api_key=os.getenv("WCD_DEMO_RO_KEY"),
    additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)

with st.sidebar:
    st.title("💻 Job smart filters")
    st.subheader("Powered by Weaviate's vector engine")
    st.header("Settings")
    st.success("Connected to Weaviate client", icon="💚")

# Search Mode descriptions

bm25_gql = """
        {{
            Get {{
                Linkedin_jobs(limit: {limit_jobs}, bm25: {{ query: "{input}" }}) 
                {{
                    title
                    job_id
                    description
                    location
                    company_name
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

vector_gql = """
        {{
            Get {{
                Linkedin_jobs(limit: {limit_jobs}, nearText: {{ concepts: ["{input}"] }}) 
                {{
                    title
                    job_id
                    description
                    location
                    company_name
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

hybrid_gql = """
        {{
            Get {{
                Linkedin_jobs(limit: {limit_jobs}, hybrid: {{ query: "{input}" alpha:0.5 }}) 
                {{
                    title
                    job_id
                    description
                    location
                    company_name
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

mode_descriptions = {
    "BM25": [
        "BM25 is a method used by search engines to rank documents based on their relevance to a given query, factoring in both the frequency of keywords and the length of the document.",
        bm25_gql,
        30,
    ],
    "Vector": [
        "Vector search is a method used by search engines to find and rank results based on their similarity to your search query. Instead of just matching keywords, it understands the context and meaning behind your search, offering more relevant and nuanced results.",
        vector_gql,
        15,
    ],
    "Hybrid": [
        "Hybrid search combines vector and BM25 methods to offer better search results. It leverages the precision of BM25's keyword-based ranking with vector search's ability to understand context and semantic meaning. Providing results that are both directly relevant to the query and contextually related.",
        hybrid_gql,
        15,
    ],
}

st.markdown(
    """This dashboard uses [Streamlit](https://streamlit.io/) and [Weaviate](https://weaviate.io/) to search from a [LinkedIn Job Postings](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) database. 
        It offers multiple search options such as traditional BM25, Semantic & Hybrid (generative search is disabled) to find your dream job.
        Our Weaviate database contains +150k job postings between 2023-2024 ready for you to be discovered."""
)

# Information
with st.expander(
    "🔽 **Click here to expand** | Explanation on how it works | Built with Weaviate for the Weaviate team"
):
    st.subheader("Data")
    st.markdown(
        """The database contains more than 150k cards from the [LinkedIn Job Postings](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings). We used the following attributes to index the cards:

        - Job title (`title`)
        - Job description (`description`)
        - Company's name (`company_name`)
        - Location of job (`location`)

        """
    )
    st.subheader("How the demo works")
    st.markdown(
        """The demo offers 3 search options with defined GraphQL queries, which you can use to search for various job postings. 
        You can search for job types such as "Machine Learning" or "AI" or you can search for location, technical skills, job descriptions, and more.
"""
    )
    st.markdown(
        """The first is the **BM25 search**, it's a method used by search engines to rank documents based on their relevance to a given query, factoring in both the frequency of keywords and the length of the document. In simple terms, we're conducting keyword matching.

        We can simply pass a query to the `query` parameter ([see docs](https://weaviate.io/developers/weaviate/search/bm25))"""
    )
    st.code(
        """
        {
            Get {
                LinkedIn_Jobs(limit: {job_limit}, bm25: { query: "Machine learning with pytorch" }) 
                {
                    ...
                }
            }
        }""",
        language="graphql",
    )
    st.markdown(
        """The second option is **Vector search**, a method used to find and rank results based on their similarity to a given search query. 
        Instead of matching keywords, it understands the context and meaning behind the query, offering relevant and more semantic related results. For example, when we search for "Machine learning" we might also get jobs like a "Deep learning" or "Data Science" because they are semantically related.
        We use the `nearText` function in which we pass our query to the `concepts` parameter ([see docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#neartext))"""
    )
    st.code(
        """
        {
            Get {
                LinkedIn_Jobs(limit: {job_limit}, nearText: { concepts: ["Machine learning with pytorch"] }) 
                {
                    ...
                }
            }
        }""",
        language="graphql",
    )
    st.markdown(
        """With **Hybrid search** we combine both methods and use a ranking alogrithm to combine their results. 
        It leverages the precision of BM25's keyword-based ranking with vector search's ability to understand context and semantic meaning. 
        We can pass our query to the `query` parameter and set the `alpha` that determines the weighting for each search ([see docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid))"""
    )
    st.code(
        """
        {
            Get {
                LinkedIn_Jobs(limit: {job_limit}, hybrid: { query: "Machine learning with pytorch" alpha:0.5 }) 
                {
                    ...
                }
            }
        }""",
        language="graphql",
    )
    st.subheader("Future ideas")
    st.markdown(
        """To include dataset relationship to other datasets like the employer's description or the industry's description. These datasets are also in the [LinkedIn Job Postings](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) dataset but have not been indexed yet in Weaviate.
        
        This can result in a more accurate search with more context.
        
        Moreover, this dataset should be updated to jobs that are newly posted and it should remove jobs that are no longer hiring."""
    )

# User Configuration Sidebar
with st.sidebar:
    mode = st.radio(
        "Search Mode",
        options=[
            "BM25",
            "Vector",
            "Hybrid",
        ],
        index=2,
    )
    limit = st.slider(
        label="Number of top job results",
        min_value=1,
        max_value=mode_descriptions[mode][2],
        value=3,
    )
    st.info(mode_descriptions[mode][0])

st.divider()
st.markdown(
    "  **Search for your next job.** Start by typing a query in the input below or select an example query:"
)
st.markdown("")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.greetings = False

# Example prompts
example_prompts = [
    "Machine learning with pytorch",
    "MLOps engineer with 10 years of experience",
    "AI researcher at deepmind or similar",
]
button_cols = st.columns(3)

button_pressed = ""

if button_cols[0].button(
    example_prompts[0],
):
    button_pressed = example_prompts[0]
elif button_cols[1].button(
    example_prompts[1],
):
    button_pressed = example_prompts[1]
elif button_cols[2].button(
    example_prompts[2],
):
    button_pressed = example_prompts[2]


if prompt := (st.chat_input("What cards are you looking for?") or button_pressed):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    prompt = prompt.replace('"', "").replace("'", "")

    images = []
    if prompt != "":
        query = prompt.strip().lower()
        gql = mode_descriptions[mode][1].format(input=query, limit_jobs=limit)

        df = conn.query(gql, ttl=None)

        response = ""
        with st.chat_message("assistant"):
            for index, row in df.iterrows():
                if index == 0:
                    if "_additional.generate.groupedResult" in row:
                        first_response = row["_additional.generate.groupedResult"]
                    else:
                        first_response = f"Here are the results from the {mode} search:"

                    message_placeholder = st.empty()
                    full_response = ""
                    for chunk in first_response.split():
                        full_response += chunk + " "
                        time.sleep(0.02)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    response += full_response + " "

                with st.container(border=True):
                    st.markdown(f"**{index+1}. {row['title']}**")
                    col1, col2, col3 = st.columns(3)
                    col1.caption(f"🏦 {row['company_name']}")
                    col2.caption(f"📍 {row['location']}")
                    col3.caption(f"ID: {row['job_id']}")
                    with st.expander(f"📄 Description", expanded=False):
                        st.caption(row["description"])

            st.session_state.messages.append(
                {"role": "assistant", "content": response, "images": images}
            )

            if st.button("Reset", key="reset", type="primary"):
                st.session_state.messages = []
                st.experimental_rerun()
