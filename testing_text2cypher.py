from db_helper import Neo4j_interface

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':
    interface = Neo4j_interface()

    texts = [
            "Find paper with its title 'AceKG: A Large-scale Knowledge Graph for Academic Data Mining'",
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

    # for text in texts:
    #     print(f"Search> {text}")
    #     papers = interface.text2cypher(text)
    #     if isinstance(papers, list):
    #         papers = papers[:5]

    #     print(f"Result>", papers)
    #     input('')

    reference_texts = [
        "Find paper that references 'Regular Path Query Evaluation on Streaming Graphs'",
        "Find paper that references 'Regular Path Query Evaluation on Streaming Graphs'.",
        "Find paper references Regular Path Query Evaluation on Streaming Graphs.",
        "Find paper that cites Regular Path Query Evaluation on Streaming Graphs.",
        "Find papers that cite Regular Path Query Evaluation on Streaming Graphs.",
        "Find papers that reference Regular Path Query Evaluation on Streaming Graphs.",
        "Papers cites 'Regular Path Query Evaluation on Streaming Graphs'",
        "Find papers 'SemOpenAlex: The Scientific Landscape in 26 Billion RDF Triples' cite",
        "Find papers 'SemOpenAlex: The Scientific Landscape in 26 Billion RDF Triples' cites",
        "Find papers cited by 'SemOpenAlex: The Scientific Landscape in 26 Billion RDF Triples'",
        "Find papers referred by SemOpenAlex: The Scientific Landscape in 26 Billion RDF Triples.",
    ]

    # for text in reference_texts:
    #     print(f"Search> {text}")
    #     papers = interface.cypher2text_reference(text)
    #     if isinstance(papers, list):
    #         papers = papers[:5]

    #     print(f"Result>", papers)
    #     input('')


    authors_texts = [
        "Find papers written by 'Fanjin Zhang'.",
        "Find papers that Fanjin Zhang wrote",
        "Find papers from Fanjin Zhang",
        "find 'Fanjin Zhang' papers",
        "find Fanjin Zhang papers",
        "Fanjin Zhang papers",
        "Fanjin Zhang's papers",
        "Find Fanjin Zhang's paper",
        "Get Fanjin Zhang paper",
        "Fanjin Zhang",
    ]

    # for text in authors_texts:
    #     print(f"Search> {text}")
    #     papers = interface.cypher2text_author(text)
    #     if isinstance(papers, list):
    #         papers = papers[:5]

    #     print(f"Result>", papers)
    #     input('')

    while True:
        text = input(f"{bcolors.OKCYAN}Search Text> {bcolors.ENDC}")
        if text.lower() == 'exit':
            break

        papers = interface.text2cypher(text)
        
        if isinstance(papers, list):
            for i in range(len(papers)):
                print(f"{bcolors.OKGREEN}Result papers> {bcolors.ENDC}{papers[i]}")
                if i >= 4:
                    break
        else:
            print(f"{bcolors.OKGREEN}Result papers> {bcolors.ENDC}{papers}")

        # print(f"Result>", papers)
        print("")

    while True:
        text = input(f"{bcolors.OKCYAN}Search Text> {bcolors.ENDC}")
        if text.lower() == 'exit':
            break

        papers = interface.cypher2text_reference(text)
        
        if isinstance(papers, list):
            for i in range(len(papers)):
                print(f"{bcolors.OKGREEN}Result papers> {bcolors.ENDC}{papers[i]}")
                if i >= 4:
                    break
        else:
            print(f"{bcolors.OKGREEN}Result papers> {bcolors.ENDC}{papers}")

        # print(f"Result>", papers)
        print("")

    while True:
        text = input(f"{bcolors.OKCYAN}Search Text> {bcolors.ENDC}")
        if text.lower() == 'exit':
            break

        papers = interface.cypher2text_author(text)
        
        if isinstance(papers, list):
            for i in range(len(papers)):
                print(f"{bcolors.OKGREEN}Result papers> {bcolors.ENDC}{papers[i]}")
                if i >= 4:
                    break
        else:
            print(f"{bcolors.OKGREEN}Result papers> {bcolors.ENDC}{papers}")

        # print(f"Result>", papers)
        print("")