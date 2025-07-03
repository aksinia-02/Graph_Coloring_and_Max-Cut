# Graph Coloring And Max-Cut

The goal of this project  is to experimentally study how equitability constraints affect the quality of the solution of optimization versions of two fundamental problems of graph theory: Graph Coloring and Max-Cut. The study considers various well-known classes of graphs for pattern detection and a more comprehensive analysis of the influence of allowing imbalance in the sizes of partition parts on the resulting output. 

## Graph Generation

For this study, a custom random graph generator was created. It allows to generate  data sets with different classes of graphs using the NetworkX Python library and some custom functions.

### Graph Classes and Parameters

- **Erdős–Rényi Graphs (Random Graphs)**  
  `erdos_renyi_graph` (G(n, p))  
  - n: number of nodes  
  - p: probability of an edge between any two nodes  

- **Scale-Free Graphs (Barabási–Albert Model)**  
  `barabasi_albert_graph` (G(n, m))  
  - n: number of nodes  
  - m: edges to attach from a new node to existing nodes  

- **Small-World Graphs (Watts–Strogatz Model)**  
  `watts_strogatz_graph` (G(n, k, p))  
  - n: number of nodes  
  - k: number of neighbors each node connects to in a ring  
  - p: rewiring probability of each edge  

- **Planar Grid Graphs**  
  `grid_2d_graph` (G(n, m))  
  - n: number of columns  
  - m: number of rows  

- **Complete Bipartite Graphs**  
  `complete_bipartite_graph` (G(n1, n2))  
  - n1: nodes in first partition  
  - n2: nodes in second partition  

- **Complete k-Partite Graphs**  
  - No predefined function, implemented manually  
  - Partition sizes define the groups  

- **Random Regular Graphs**  
  `random_regular_graph` (G(n, d))  
  - n: number of nodes  
  - d: degree of each node  

- **Clustered Graphs (Stochastic Block Models)**  
  `stochastic_block_model` (G(sizes, p))  
  - sizes: community sizes list  
  - p: edge probability matrix  
  - intra: probability of edges within communities  
  - inter: probability of edges between communities 

### Options

  -h, --help                     show this help message and exit
  -k, --graphs GRAPHS            The number of graphs.
  -f, --folder_name FOLDER_NAME  Folder name for output.

Other steps can be triggered by starting the algorithm and selecting the graph generation type.

### Example of use

python .\random_graph_generator.py -k 10 -f output


## Graph Coloring Solver

The solution includes a visualization of the partitions and a JSON file saved for later use.

### Options

  -h, --help           show this help message and exit
  -f, --file FILE      Path to the CSV file.
  -n, --number NUMBER  Offset for equitable coloring.
  -o, --optimal {0,1}  Set to 1 if an optimal solution is required, otherwise 0 for a heuristic solution.

### Example of use
python -m graph_coloring.graph_coloring_solver -f .\data_sparse\n_30_p_30\d_0.25_bIfpiUf1.csv -o 1 -n 1

## MAX-CUT Solver

The solution includes a visualization of the partitions and a JSON file saved for later use.

### Options

  -h, --help           show this help message and exit
  -f, --file FILE      Path to the CSV file.
  -n, --number NUMBER  Offset between partitions.
  -o, --optimal {0,1}  Set to 1 if an optimal solution is required, otherwise 0 for a heuristic solution.

### Example of use
python -m max_cut.max_cut_solver -f .\data_sparse\n_30_p_30\d_0.25_bIfpiUf1.csv -o 1 -n 1

## Run Statistic

Iterates through graphs in the specified folder, calculates solutions for each graph, and saves them as JSON files. Offsets are predefined as None, 5, 4, 3, 2, 1, and 0.

### Options

  -h, --help            show this help message and exit                                  
  -i, --input INPUT     Input folder with data.                                          
  -t, --type {0,1}      Set to 1 if graph coloring are required, otherwise 0 for max cut.
  -f, --folder_names FOLDER_NAMES [FOLDER_NAMES ...]                                     
                        Folders names to be chosen to work with. Please save this folder in current directory.

### Example of use

python .\run_statistic.py -i .\input\scale_free_graphs\ -t 1 -f n_10

## Save Results

Saves precalculated results from the input folder into an output CSV file.

### Options

  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output file for results.
  -i, --input INPUT     Input folder with data.
  -t, --type {0,1}      Set to 1 if graph coloring are required, otherwise 0 for max cut.
  -f, --folder_names FOLDER_NAMES [FOLDER_NAMES ...]
                        Folders names to be chosen to work with. Please save this folder in current directory.

### Example of use

python .\save_results.py -o bipartite_graphs.csv -i .\input\bipartite_graph\ -f n_10 -t 1



