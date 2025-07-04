import pandas as pd
from predict_model import predict_data
from integrate_model import add_ai_recommendations

def prepare_data(df):
    # Map flag strings to numbers
    flag_map = {"Low": -1, "High": 1, "": 0, "Normal": 0, "Invalid": None}

    for col in df.columns:
        if col.endswith("_Flag"):
            df[col + "_Num"] = df[col].map(flag_map)

    # Count abnormalities
    flag_num_cols = [col for col in df.columns if col.endswith("_Flag_Num")]
    flag_cols = [col for col in df.columns if col.endswith("_Flag")]
    # df["Abnormal_Count"] = df[flag_num_cols].abs().sum(axis=1)  # count abnormalities ignoring sign
    df_features = df.drop(columns=flag_num_cols)
    df_features = df_features.drop(columns=flag_cols)
    df_features = df_features.apply(pd.to_numeric, errors='coerce')

    # Fill missing numeric values with mean
    df_features.fillna(df_features.mean(), inplace=True)
    X = df_features
    # predict_data(X,df_features)
    feature_cols = df_features.columns.tolist()
    df_features.to_csv("df_features.csv")
    ai_df = add_ai_recommendations(df_features, feature_cols)
    
    ai_df.to_csv("ai_df.csv", index=False)

    # return X