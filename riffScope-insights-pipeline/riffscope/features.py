

from loguru import logger

import typer
import pandas as pd


from riffscope.config import RAW_DATA_DIR,PROCESSED_DATA_DIR

app = typer.Typer()


def merge_df(alternative_df,comercial_df):
    csv_merged  = pd.concat([alternative_df,comercial_df],ignore_index=True)
    return csv_merged

def read_csv():
    alternative=pd.read_csv(RAW_DATA_DIR/"alternative.csv")
    comercial=pd.read_csv(RAW_DATA_DIR/"comercial.csv")
    return alternative,comercial
@app.command()
def main():
    return 0
if __name__ == "__main__":
    app()
