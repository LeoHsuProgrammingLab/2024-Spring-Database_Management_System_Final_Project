# 2024-Spring-Database_Management_System_Final_Project "Paper is all you need: A Gaph Database to Manage Research Papers"

## Objectives 0504
1. Design Graph Data Model to effectively model the relationship between papers.
2. Friendly user-interface with semantic search.
3. Data processing and Machine Learning Techniques.
4. Advanced: Mange papers for ad hoc laborotory.

### Step1: Convert thesis paper PDF file into Latex or Markdown file
`conda create -n <env_name> python=3.10`  

`pip install nougat`  

`pip install nougat-ocr`  

`nougat <pdf_path> --out <output_dir> --no-skipping`  

### Step2: Neo4j

