# Analysing the scikit-learn examples

This folder contains the results of analysing the use of `matplotlib`
and `sklearn` in the examples of scikit-learn.

The two CSV files were produced as follows:
```
$ python kamal.py --module matplotlib --output mpl-stats.csv ~/git/scikit-learn/examples
$ python kamal.py --module sklearn --output skl-stats.csv ~/git/scikit-learn/examples
```

The `statistics.db` file is the result of combining the two CSV files with:
```
$ sqlite-utils insert --csv statistics.db scikit-learn-examples skl-stats.csv
$ sqlite-utils insert --csv statistics.db scikit-learn-examples mpl-stats.csv
```