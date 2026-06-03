

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

def clean_data(df):
    df = df.sort_values("group",ascending=True)
    df= df.drop_duplicates(subset=['id'],keep="first")
    df= df.drop_duplicates(subset=["name","artists"],keep="first")
    df["release_date"] = pd.to_datetime(df["release_date"],format="mixed")
    df["release_year"] = df["release_date"].dt.year
    df = df.drop(columns=["release_date"])
    df=df.reset_index(drop=True)
    return df

def save_data(df):
    df.to_csv(PROCESSED_DATA_DIR/"dataset_clean.csv",index=False)

@app.command()
def main():
    alternative,comercial = read_csv()
    df = merge_df(alternative,comercial)
    df=clean_data(df)
    save_data(df)
    
if __name__ == "__main__":
    app()
