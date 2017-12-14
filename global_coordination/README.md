# Global interference coordination

Required: Python 2.7 + Python packages: networkx, numpy, matplotlib

File descriptions:

- igraph.py is a class that includes various features, including generating & saving a factory hall topology consisting of multiple local cells (see local_allocation, requires localcell.py, ChModel_KoI.py from ../local_allocation)
- coloring_greedy.py includes the global IC heuristic (requires igraph.py)
- coloring_ilp.py, gc_ILP.pdf: implementation and TeX representation of the global IC optimization model
- trun_*.py, crun_*.py are scripts used for evaluation runs
- lra_heuristic_test.py is a script for testing the heuristic scheduling approaches
- Generator_col.py, BashG.sh can be used to create test cells (uses igraph.py)
- evaluation_plot.py can be used to generate plots (uses ci.py)
- Instances.rar includes the test networks and results used in [1]

[1] S. Auroux, D. Parruca, H. Karl: Joint real-time scheduling and interference coordination for wireless factory automation. In Proceedings of the 27th IEEE International Symposium on Personal, Indoor and Mobile Radio Communications (PIMRC), Valencia, Spain, September 2016.