# Python for Business Analytics: companion repository

The code, data, and notebooks for the book *Python for Business Analytics*.
The free web edition of the book can be found at https://pyba.murtaza.cc. This
repository can be copied or cloned to follow the examples in the book.

The book's notebooks can also be run in Google Colab with a free Google
account. In that case, no local setup is required: each chapter in the book has a link to its
notebook on Colab, and the notebook's setup cell fetches this repository when run.

## Setup (10 minutes)

Appendix A of the book explains the setup in detail; a condensed version
follows.

1. Install [Miniforge](https://github.com/conda-forge/miniforge).
2. Clone this repository and, from its root:

       conda env create -f envs/pyba-core.yml
       conda activate pyba-core
       pip install -e .

3. Verify the installation:

       python -c "import pyba, pandas, plotly, sklearn, statsmodels, pulp; print('ok')"

4. Open any notebook in `notebooks/` (VS Code or Jupyter), select the
   `pyba-core` kernel, and run it top to bottom.

Working with the book does not require API keys, paid accounts, or GPUs.

## Layout

    pyba/            small support package (the DATA_DIR path anchor and the
                     per-student exam dataset generator); the book itself uses
                     pandas etc. directly, unwrapped
    assets/data/     every dataset the chapters use
    notebooks/       runnable notebooks for the executable chapters, added
                     here as chapters are finalized
    demos/           the interactive concept explorers (self-contained HTML)
    envs/            the conda environment spec
