# stocktopus

## purpose


## architecture



## datasets

#### FNSPID dataset

- link to the [data](https://huggingface.co/datasets/Zihan1004/FNSPID)
- link to the [paper](https://arxiv.org/html/2402.06698v1)

The stock prices come as a zip file that contains ~5000 csv files, one for each symbol.
Unzipped, the stock prices amount to ~2.8GB in size.
Each individual csv files is structured like this (`AADR.csv`)

```csv
date,volume,open,high,low,close,adj close
2023-12-28,1100,56.04999923706055,56.09000015258789,55.970001220703125,56.060001373291016,56.060001373291016
2023-12-27,1000,56.34000015258789,56.34000015258789,56.0,56.09000015258789,56.09000015258789
2023-12-26,900,54.970001220703125,56.040000915527344,54.970001220703125,56.040000915527344,56.040000915527344
2023-12-22,1900,55.900001525878906,56.119998931884766,55.869998931884766,55.880001068115234,55.71699905395508
```

We can combine the csv files to parquet using duckdb:

```SQL
CREATE TEMP TABLE stock_prices AS SELECT * FROM read_csv('data/full_history/*.csv');
COPY (SELECT * FROM stock_prices) TO 'data/full_history.parquet' (FORMAT PARQUET);
```

The resulting parquet file is only ~750MB in size, a reduction of ~75%.

```bash
$ du -sh ./data/*
2.8G    ./data/full_history
743M    ./data/full_history.parquet
562M    ./data/full_history.zip

```
