# Local real-time scheduling

Required: Python 2.7 + Python packages: networkx, numpy, matplotlib

Note: Compared to the approach described in [1], the code in this repository has been extended to be able to consider different modulation and coding schemes. In particular, this version completely covers all functionality of the paper version.

File descriptions:

- localcell.py is a class that includes various features, including: generating & saving a local cell topology, both heuristic scheduling approaches (uses ChModel_KoI.py)
- ChModel_KoI.py includes the wireless channel model used by localcell.py (requires chGains.dat, koi_mcs.dat)
- lra_ilp_v2.py, lra_ILP.pdf: implementation and TeX representation of the local RTS optimization model
- trun_*.py, crun_*.py are scripts used for evaluation runs
- lra_heuristic_test.py is a script for testing the heuristic scheduling approaches
- Generator_lra.py can be used to create test cells (uses localcell.py)
- evaluation_plot.py can be used to generate plots (uses ci.py)
- Instances.rar includes the test networks and results used in [1]

[1] S. Auroux, D. Parruca, H. Karl: Joint real-time scheduling and interference coordination for wireless factory automation. In Proceedings of the 27th IEEE International Symposium on Personal, Indoor and Mobile Radio Communications (PIMRC), Valencia, Spain, September 2016.