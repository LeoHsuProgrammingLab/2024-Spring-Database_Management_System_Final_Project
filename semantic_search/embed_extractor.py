from neo4j import GraphDatabase
import google.generativeai as genai
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from huggingface_hub import HfApi
import pprint
import json
import re

class LLM:
    def __init__(self, model_type='models/text-embedding-004', gen_model_type='gemini-pro'):
        load_dotenv()
        api_key = os.getenv('GENAI_API_KEY')
        if api_key is None:
            print('Please set the environment variable')

        genai.configure(api_key = api_key)
        self.gen_model_type = gen_model_type
        self.gen_model = genai.GenerativeModel(gen_model_type)

        self.model_type = model_type

    def get_embedding(self, text):
        # model = genai.GenerativeModel('gemini-pro')
        response = genai.embed_content(model=self.model_type, content=text, task_type='semantic_similarity')
        return response['embedding']
    
    def get_similarity(self, text1, text2):
        embed1 = self.get_embedding(text1)
        embed2 = self.get_embedding(text2)
        return cosine_similarity([embed1], [embed2])[0][0]
    
    def calculate_similarity(self, embed1: np.ndarray, embed2: np.ndarray):
        return cosine_similarity([embed1], [embed2])[0][0]
    
    def get_keywords(self, abstract):
        prompt_tune = ''' 
        The below is the abstract of the paper, can you give me the keywords of this research paper? no more than 5. 
        Please return a dictionary without other strings. \n:
        { 
            "keywords": [] 
        } \n
        '''

        prompt = f'{abstract}{prompt_tune}'
        response = self.gen_model.generate_content(prompt)
        cleaned_response = re.sub(r'```[\w]*\n|```', '', response.text).strip()
        cleaned_response = cleaned_response.replace('\n', '').replace(' ', '')
        
        try:
            data = json.loads(cleaned_response)
            return data['keywords']
        except:
            print('Error in getting keywords from json')
            print(cleaned_response)
            return []

if __name__ == "__main__":
    model = LLM()
    text = 'Hello World'
    embed = model.get_embedding(text)
    # print(np.array(embed).shape)
    
    abstract = '''
    Graph workloads pose a particularly challenging problem for query optimizers. They typically feature large queries made up of entirely many-to-many joins with complex correlations. This puts significant stress on traditional cardinality estimation methods which generally see catastrophic errors when estimating the size of queries with only a handful of joins. To overcome this, we propose COLOR, a framework for subgraph cardinality estimation which applies insights from graph compression theory to produce a compact summary that captures the global topology of the data graph. Further, we identify several key optimizations that enable tractable estimation over this summary even for large query graphs. We then evaluate several designs within this framework and find that they improve accuracy by up to \(10^{3}\times\) over all competing methods while maintaining fast inference, a small memory footprint, efficient construction, and graceful degradation under updates.

    Cardinality Estimation, Graph Databases, Graph Summarization, Query Optimization +
    Footnote †: journal: Computer Vision and Pattern Recognition
    online sampling in disk-based or distributed settings can incur a prohibitive latency as it relies on fast random reads over the whole graph. _Summarization methods_(Gull and Kavli, 2015; Kavli and Kavli, 2015) group nodes in the data graph into a super structure and store summary statistics. However, the grouping is done by predefined rules or hashing, without regard to the edge distribution between these groups. Because these summaries are not tailored to the graph structure, _i.e._ make a uniformity assumption, they produce median error of up to \(\mathbf{10^{12}}\times\), and we find that they timeout on larger queries (Sec. 8).

    In this paper, we propose a new approach to subgraph cardinality estimation based on graph compression; we call this method Color. By taking advantage of recent advances in lossy graph representations such as quasi-stable coloring (Kavli, 2015), we approximately capture the topology of the graph in a small summary. We then directly estimate cardinalities on the summary without needing to access the data graph.

    The key idea is to color the graph \(G\) such that nodes of the same color have a similar number of edges to each other color. This mitigates the effect of the uniformity and independence assumptions. In Figure 1 for example, the coloring assigns the \(c\),\(d\),\(e\) nodes to the same green color. This is because green nodes have a similar number of incoming edges from blue and orange nodes, and no out edges. Meanwhile, \(a\),\(b\) are assigned to the blue color as they have a similar number of outgoing edges to green nodes and none to orange nodes. This helps mitigate the uniformity assumption because, within nodes of a fixed color, the edge distribution is nearly uniform. Further, because high and low degree nodes tend to be placed in different colors, correlations in the connections between them can be identified, mitigating the independence assumption.

    Real world graphs are more complex, but it turns out that our approach can meaningfully capture their topology with a small number of colors, typically just 32 in our experiments. Figure 2 shows the maximum difference in edge counts from nodes in one color to nodes in another, averaged over all pairs of colors for four of our benchmark datasets. Lower values indicate a better coloring and smaller differences between the two most different nodes in each color. A handful of colors is sufficient to capture most of the graph topology and reduce non-uniformity by 1-2 orders of magnitude.

    With these colorings in mind, we return to the example in Figure 1. During the offline phase, our method takes the data graph, \(G\), and produces a compact summary, \(\mathcal{G}\) called a _lifted graph_, with one super-node for each color (Sec. 3). We keep statistics on the number and kinds of edges which pass between these colors. During the online phase, the cardinality estimate is computed on the lifted graph by performing a weighted version of subgraph counting which we call _lifted subgraph counting_ (Sec. 4). To extend this to cyclic queries, which occur frequently in graph databases, we also propose a technique based on a novel statistic called the _path closure probability_ (Sec. 5).

    To enable efficient inference on a more detailed, and therefore accurate, lifted graph, we propose three critical optimizations. Tree-decompositions and partial aggregation, introduced in Sec. 7.1, reduce the inference latency by over \(\mathbf{100}\times\) Importance sampling and Thompson-Horowitz estimation over the lifted graph, the subject of Sec. 7.2, ensure a linear latency w.r.t. the size of the query while maintaining a 6x lower error than a naive sampling approach. Lastly, we demonstrate how to maintain the lifted graph under updates in Sec. 7.3, reducing the need to rebuild the summary by providing reasonable estimates even when over \(1/2\) of the graph is updated.

    In summary, we make the following contributions:

    * Develop the COLOR framework for producing lifted graph summaries from colorings (Sec. 3) and evaluate six possible coloring schemes (Sec. 6).
    * Define a general formula for performing inference over a lifted graph, show its optimality for acyclic queries (Sec. 4), and extend it to cyclic ones (Sec. 5).
    * Develop optimizations that allow for efficient and accurate inference and robust handling of updates (Sec. 7). These optimizations are: tree-decomposition, importance sampling, and Thompson-Horowitz estimation.
    * Empirically validate COLOR's superior performance on eight standard benchmark datasets and against nine comparison methods (Sec. 8).
    '''

    keywords = model.get_keywords(abstract)
    print(keywords)
    # for model in genai.list_models():
    #     pprint.pprint(model)