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

Since the stock symbol is only part of the filename and not the content, we need to come up with a way to add that to
tour dataset. We also need to verify that the csv was converted correctly by duckdb.


Let's have a look at the news data (`All_external.csv`):

```csv
Date,Article_title,Stock_symbol,Url,Publisher,Author,Article,Lsa_summary,Luhn_summary,Textrank_summary,Lexrank_summary
2020-06-05 06:30:54 UTC,Stocks That Hit 52-Week Highs On Friday,A,https://www.benzinga.com/news/20/06/16190091/stocks-that-hit-52-week-highs-on-friday,Benzinga Insights,,,,,,
2020-06-03 06:45:20 UTC,Stocks That Hit 52-Week Highs On Wednesday,A,https://www.benzinga.com/news/20/06/16170189/stocks-that-hit-52-week-highs-on-wednesday,Benzinga Insights,,,,,,
2020-05-26 00:30:07 UTC,71 Biggest Movers From Friday,A,https://www.benzinga.com/news/20/05/16103463/71-biggest-movers-from-friday,Lisa Levin,,,,,,
2020-05-22 08:45:06 UTC,46 Stocks Moving In Friday's Mid-Day Session,A,https://www.benzinga.com/news/20/05/16095921/46-stocks-moving-in-fridays-mid-day-session,Lisa Levin,,,,,,
```
