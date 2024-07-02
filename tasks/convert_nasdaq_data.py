import polars as pl


def main():
    filename = "data/nasdaq_exteral_data.csv"
    outname = filename.replace(".csv", ".parquet")
    df = pl.read_csv(filename)
    df.write_parquet(outname, compression="snappy", row_group_size=100_000)


if __name__ == "__main__":
    main()
