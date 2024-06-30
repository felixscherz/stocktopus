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



We can combine the csv files to parquet using duckdb, using `filename=true` to include the filename which contains the
symbol as an extra column.

```SQL
CREATE TEMP TABLE stock_prices AS SELECT * FROM read_csv('data/full_history/*.csv', filename=true);
COPY (SELECT * FROM stock_prices) TO 'data/full_history.parquet' (FORMAT PARQUET);
```

The resulting parquet file is only ~750MB in size, a reduction of ~75%.

```bash
$ du -sh ./data/*
2.8G    ./data/full_history
743M    ./data/full_history.parquet
562M    ./data/full_history.zip

```

Let's have a look at the news data (`All_external.csv`):

```csv
Date,Article_title,Stock_symbol,Url,Publisher,Author,Article,Lsa_summary,Luhn_summary,Textrank_summary,Lexrank_summary
2020-06-05 06:30:54 UTC,Stocks That Hit 52-Week Highs On Friday,A,https://www.benzinga.com/news/20/06/16190091/stocks-that-hit-52-week-highs-on-friday,Benzinga Insights,,,,,,
2020-06-03 06:45:20 UTC,Stocks That Hit 52-Week Highs On Wednesday,A,https://www.benzinga.com/news/20/06/16170189/stocks-that-hit-52-week-highs-on-wednesday,Benzinga Insights,,,,,,
2020-05-26 00:30:07 UTC,71 Biggest Movers From Friday,A,https://www.benzinga.com/news/20/05/16103463/71-biggest-movers-from-friday,Lisa Levin,,,,,,
2020-05-22 08:45:06 UTC,46 Stocks Moving In Friday's Mid-Day Session,A,https://www.benzinga.com/news/20/05/16095921/46-stocks-moving-in-fridays-mid-day-session,Lisa Levin,,,,,,
```

It seems like we need to be careful with line endings for that file, since it ends with `\r\n` instead of `\n`. We can
tell duckdb as much when reading the csv:

```SQL
CREATE TEMP TABLE news AS SELECT * FROM read_csv('data/All_external.csv', new_line='\r\n');
COPY (SELECT * FROM news) TO 'data/All_external.parquet' (FORMAT PARQUET);
```

Again, comparing the file sizes we see a reduction in file size from 5.3GB down to ~2.5GB:

```bash
$ du -sh ./data/*
5.3G    ./data/All_external.csv
2.4G    ./data/All_external.parquet
```

What's left now is the `nasdaq_external_data.csv` file, which is almost 22GB in size.

```sql
CREATE TEMP TABLE nasdaq_news AS SELECT * FROM read_csv('data/nasdaq_exteral_data.csv', newline='\r\n');
COPY (SELECT * FROM nasdaq_news) TO 'data/nasdaq_external_data.parquet' (FORMAT PARQUET);
```

Ok this didn't work, I did abort after around 10 minutes of sitting at 100% CPU. Let's try again without actually
creating the table:

```sql
COPY
    (select * FROM read_csv('data/nasdaq_exteral_data.csv', new_line='\r\n'))
    TO 'data/nasdaq_external_data.parquet'
    (FORMAT PARQUET);
```

```bash
Error: Out of Memory Error: failed to allocate data of size 512.0 MiB (25.4 GiB/25.5 GiB used)
Database is launched in in-memory mode and no temporary directory is specified.
Unused blocks cannot be offloaded to disk.

Launch the database with a persistent storage back-end
Or set SET temp_directory='/path/to/tmp.tmp'
```

Ok one more try with a persistant database, creating the table first and then writing it to parquet:

```sql
CREATE TABLE nasdaq_news AS SELECT * FROM read_csv('data/nasdaq_exteral_data.csv');
```
```bash
Error: Out of Memory Error: could not allocate block of size 256.0 KiB (25.6 GiB/25.5 GiB used)
```

Seems like we should disable preservation of the insertion order according to this
[stackoverflow question](https://stackoverflow.com/questions/77994828/converting-multiple-csvs-to-parquet-using-duckdb-out-of-memory)

```SQL
SET preserve_insertion_order = false;
```

With this setting duckdb was able to convert the csv to a parquet file of around 9.6GB in size.
