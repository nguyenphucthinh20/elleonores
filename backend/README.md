# JobMatching Project

## Description


This project implements a sophisticated job matching system leveraging the power of Large Language Models (LLMs), graph databases, and vector databases. The core idea is to create a robust and intelligent platform that accurately connects job seekers with suitable opportunities by understanding the nuances of their skills, experiences, and preferences, as well as the requirements of various job roles. This system moves beyond traditional keyword-based matching by building rich, interconnected data structures that capture complex relationships between entities like employees, companies, programming languages, frameworks, and skills.

## Features

- **Multi-LLM Integration**: Seamlessly integrates with various Large Language Models, including Azure OpenAI, Bedrock, and Gemini, to provide diverse and powerful natural language processing capabilities for understanding and extracting information from resumes, job descriptions, and other textual data.
- **Graph Database for Relationship Management**: Utilizes Neo4j, a leading graph database, to model and store complex relationships between entities such as employees, companies, programming languages, frameworks, and skills. This enables highly nuanced and context-aware matching.
- **Vector Database for Semantic Search**: Employs Qdrant, a high-performance vector similarity search engine, to store and query vector embeddings of textual data. This facilitates semantic search and allows for matching based on the meaning and context of information, rather than just keywords.
- **Hybrid Matching Methodology**: Combines the strengths of graph-based relationship analysis with vector-based semantic similarity to achieve a comprehensive and accurate job matching process. This approach allows for both explicit connections (e.g., 'worked at', 'has skill') and implicit similarities (e.g., 'similar job descriptions').
- **Flexible Data Ingestion**: Supports a wide range of document formats for data ingestion, including `.csv`, `.docx`, `.eml`, `.epub`, `.html`, `.md`, `.odt`, `.pdf`, `.pptx`, `.txt`, `.xls`, `.xlsx`, `.xml`, and `.url`, ensuring compatibility with various data sources.
- **Scalable and Robust Architecture**: Designed with scalability in mind, leveraging Docker for easy deployment and management of Neo4j and Qdrant instances, ensuring the system can handle growing data volumes and user loads.


## Technologies Used

This project leverages a modern and robust technology stack to deliver its advanced job matching capabilities:

-   **Large Language Models (LLMs)**:
    -   **Azure OpenAI**: For powerful natural language understanding and generation, potentially used for extracting entities or summarizing text from resumes and job descriptions.
    -   **Bedrock**: Amazon's service for building and scaling generative AI applications, offering access to various foundation models.
    -   **Gemini**: Google's family of multimodal large language models, providing advanced reasoning and understanding capabilities.

-   **Databases**:
    -   **Neo4j**: A highly scalable and performant graph database. It is used to store and manage the intricate relationships between different entities in the job matching domain, such as employees, companies, skills, and programming languages. This enables complex query capabilities for relationship-based matching.
    -   **Qdrant**: A vector similarity search engine. It is utilized for storing high-dimensional vector embeddings generated from textual data (e.g., job descriptions, resume summaries) and performing fast approximate nearest neighbor (ANN) searches. This is crucial for semantic matching based on content similarity.

-   **Programming Language**: Python

-   **Containerization**: Docker (for deploying Neo4j and Qdrant)


## Installation

To set up and run the JobMatching project, follow these steps:

### Prerequisites

-   **Python 3.x**: Ensure you have Python installed on your system.
-   **Docker**: Docker is required to run Neo4j and Qdrant databases. Install Docker Desktop or Docker Engine based on your operating system.

### Backend Setup

1.  **Clone the repository**:

    ```bash
    git clone <repository_url>
    cd jobmatching-project
    ```

    *(Replace `<repository_url>` with the actual URL of your project repository.)*

2.  **Install Python dependencies**:

    Navigate to the backend directory (if applicable) and install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### Database Setup (Docker)

1.  **Run Neo4j using Docker**:

    This command will start a Neo4j container, exposing its default ports (7474 for HTTP and 7687 for Bolt) and mounting a local volume for data persistence. This ensures your graph data is not lost when the container stops.

    ```bash
    docker run \
        --publish=7474:7474 --publish=7687:7687 \
        --volume=$HOME/neo4j/data:/data \
        neo4j
    ```

    -   `--publish=7474:7474`: Maps port 7474 of the container to port 7474 on your host machine (Neo4j Browser).
    -   `--publish=7687:7687`: Maps port 7687 of the container to port 7687 on your host machine (Neo4j Bolt).
    -   `--volume=$HOME/neo4j/data:/data`: Mounts a local directory `$HOME/neo4j/data` to `/data` inside the container for persistent storage of Neo4j data.

2.  **Run Qdrant using Docker**:

    This command will start a Qdrant container, exposing its default ports (6333 for HTTP and 6334 for gRPC) and mounting a local volume for data persistence. This ensures your vector data is not lost when the container stops.

    ```bash
    docker run -p 6333:6333 -p 6334:6334 \
        -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
        qdrant/qdrant
    ```

    -   `-p 6333:6333`: Maps port 6333 of the container to port 6333 on your host machine (Qdrant HTTP API).
    -   `-p 6334:6334`: Maps port 6334 of the container to port 6334 on your host machine (Qdrant gRPC API).
    -   `-v "$(pwd)/qdrant_storage:/qdrant/storage:z"`: Mounts a local directory `qdrant_storage` (relative to your current working directory) to `/qdrant/storage` inside the container for persistent storage of Qdrant data. The `:z` flag is for SELinux contexts, often needed on Linux systems.


## Usage

### Backend

After setting up the databases and installing dependencies, you can run the backend application. The exact command to run the backend will depend on your project structure (e.g., a Flask app, a FastAPI app, or a simple Python script). Assuming your main application entry point is `app.py` or similar, you might run it using:

```bash
python main.py
```

Refer to the specific backend project documentation for precise instructions on how to start the server and interact with its APIs.


## Matching Methodology

This JobMatching project employs a sophisticated hybrid methodology that combines the strengths of graph databases (Neo4j) and vector databases (Qdrant) to achieve highly accurate and context-aware matching. This approach allows for both explicit relationship analysis and semantic similarity comparisons.

### Graph-Based Relationship Matching (Neo4j)

Neo4j serves as the backbone for managing the intricate relationships between various entities in the job matching ecosystem. These entities include:

-   **Employees/Talents**: Representing job seekers with their unique IDs and full names.
-   **Companies**: Organizations where employees have worked.
-   **Programming Languages**: Specific programming languages an employee knows.
-   **Frameworks**: Software frameworks an employee is proficient in.
-   **Skills**: General skills possessed by an employee.

Relationships are established between these nodes to form a rich knowledge graph. For instance:

-   `WORKED_AT`: Connects an `Employee` to a `Company`, with properties like `position`, `duration`, and `description` of their role.
-   `HAS_PROGRAMMING_LANGUAGE`: Links an `Employee` to a `ProgrammingLanguage` node.
-   `HAS_FRAMEWORKS`: Connects an `Employee` to a `Framework` node.
-   `HAS_SKILLS`: Associates an `Employee` with a `Skill` node.

### Vector-Based Semantic Matching (Qdrant)

In parallel with the graph database, Qdrant is used to handle semantic matching. Textual data from resumes (e.g., summaries, descriptions of past roles) and job descriptions are processed by LLMs to generate high-dimensional vector embeddings. These embeddings capture the semantic meaning of the text.

Qdrant then stores these vectors, allowing for fast and efficient similarity searches. When a job seeker or a job description is queried, its vector embedding is compared against the stored embeddings in Qdrant to find semantically similar counterparts. This is particularly useful for:

-   **Discovering implicit connections**: Finding job descriptions that are semantically similar to a candidate's overall profile, even if explicit keywords or relationships are not directly present in the graph.
-   **Ranking relevance**: Providing a relevance score based on the cosine similarity (or other distance metrics) between vectors, allowing for a ranked list of matches.

### Hybrid Approach for Comprehensive Matching

The true power of this system lies in its ability to combine both methodologies. For example, a matching query might first leverage Neo4j to identify candidates who have worked at specific companies or possess certain core skills (explicit relationships). Then, for this filtered set of candidates, their resume summaries could be semantically compared with job descriptions using Qdrant to find the best contextual fit. This hybrid approach ensures both precision (through graph relationships) and recall (through semantic similarity) in the job matching process.




