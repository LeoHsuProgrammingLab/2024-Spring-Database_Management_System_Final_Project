from db_helper import Neo4j_interface


if __name__ == '__main__':
    interface = Neo4j_interface()

    texts = [
            "Find paper with its title 'Regular Path Query Evaluation on Streaming Graphs'",
            "Find paper with its title \"Regular Path Query Evaluation on Streaming Graphs\"",
            "Find paper with its title Regular Path Query Evaluation on Streaming Graphs",
            "Find paper with its name Regular Path Query Evaluation on Streaming Graphs",
            "Find paper with its name Regular Path Query Evaluation on Streaming Graphs",
            "Find paper with name Regular Path Query Evaluation on Streaming Graphs",
            "Find paper with title 'Regular Path Query Evaluation on Streaming Graphs'.",
            "Find the paper titled 'Regular Path Query Evaluation on Streaming Graphs'.",
            "Find the paper named 'Regular Path Query Evaluation on Streaming Graphs'.",
            "Find the paper named Regular Path Query Evaluation on Streaming Graphs.",
            "Find the paper 'Regular Path Query Evaluation on Streaming Graphs'.",
            "Find title 'Regular Path Query Evaluation on Streaming Graphs'.",

            "Find papers with 'Path', 'Query' and 'Graphs'.",
            "Find papers with 'Path', 'Query' and 'Graphs'",
            "Find papers with \"Path\", 'Query' and 'Graphs'",
            "Find paper with path, Query and Graph",
            "Find paper titles that contains path, query and graph.",
            "Find title that contains path, query and graph.",
            "Find title that contains path, query and graph.",
            "Paper contains path, query and graph.",
            "Paper with path, query and graph.",
            "Paper with path, query, and graph.",
            "Regular Path Query Evaluation on Streaming Graphs",
        ]

    for text in texts:
        papers = interface.text2cypher(text)