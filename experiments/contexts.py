import json
import pandas as pd
import seaborn as sns
import 
import toolz.curried as toolz


def to_df(data: dict) -> pd.DataFrame:
    return toolz.pipe(
        data,
        toolz.get("events"),
        toolz.map(toolz.get("payload")),
        pd.DataFrame,
    )


def main():
    with open("../results/item_added.json") as f:
        data = load(f)
        
    df = to_df(data)
    cross_table = pd.crosstab(df[""])


if __name__ == "__main__":
    main()
