import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

filename = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DA0101EN-SkillsNetwork/labs/Data%20files/auto.csv"

headers = ["symboling","normalized-losses","make","fuel-type","aspiration",
           "num-of-doors","body-style","drive-wheels","engine-location",
           "wheel-base","length","width","height","curb-weight","engine-type",
           "num-of-cylinders","engine-size","fuel-system","bore","stroke",
           "compression-ratio","horsepower","peak-rpm","city-mpg",
           "highway-mpg","price"]

df = pd.read_csv(filename, names=headers)

print(df.head())

df.replace("?", np.nan, inplace=True)
print(df.head())

missing_data = df.isnull()

for column in missing_data.columns.values.tolist():
    print(column)
    print(missing_data[column].value_counts())
    print("")

    # normalized-losses
avg_norm_loss = df["normalized-losses"].astype("float").mean(axis=0)
df["normalized-losses"] = df["normalized-losses"].fillna(avg_norm_loss)

# bore
avg_bore = df["bore"].astype("float").mean(axis=0)
df["bore"] = df["bore"].fillna(avg_bore)

# stroke
avg_stroke = df["stroke"].astype("float").mean(axis=0)
df["stroke"] = df["stroke"].fillna(avg_stroke)

# horsepower
avg_horsepower = df["horsepower"].astype("float").mean(axis=0)
df["horsepower"] = df["horsepower"].fillna(avg_horsepower)

# peak-rpm
avg_peakrpm = df["peak-rpm"].astype("float").mean(axis=0)
df["peak-rpm"] = df["peak-rpm"].fillna(avg_peakrpm)

df["num-of-doors"] = df["num-of-doors"].fillna("four")

df.dropna(subset=["price"], axis=0, inplace=True)
df.reset_index(drop=True, inplace=True)

print(df.head())

df[["bore", "stroke"]] = df[["bore", "stroke"]].astype("float")
df["normalized-losses"] = pd.to_numeric(df["normalized-losses"], errors="coerce")
df["normalized-losses"] = df["normalized-losses"].fillna(avg_norm_loss)
df["normalized-losses"] = df["normalized-losses"].astype(int)
df[["price"]] = df[["price"]].astype("float")
df[["peak-rpm"]] = df[["peak-rpm"]].astype("float")

print(df.dtypes)

df["city-L/100km"] = 235 / df["city-mpg"]
df["highway-L/100km"] = 235 / df["highway-mpg"]

print(df[["city-mpg", "city-L/100km", "highway-mpg", "highway-L/100km"]].head())

df["length"] = df["length"] / df["length"].max()
df["width"] = df["width"] / df["width"].max()
df["height"] = df["height"] / df["height"].max()

print(df[["length", "width", "height"]].head())

df["horsepower"] = df["horsepower"].astype(int, copy=True)

bins = np.linspace(min(df["horsepower"]), max(df["horsepower"]), 4)
group_names = ["Low", "Medium", "High"]

df["horsepower-binned"] = pd.cut(df["horsepower"], bins, labels=group_names, include_lowest=True)

print(df[["horsepower", "horsepower-binned"]].head(20))
print(df["horsepower-binned"].value_counts())

plt.bar(group_names, df["horsepower-binned"].value_counts())
plt.xlabel("Horsepower")
plt.ylabel("Count")
plt.title("Horsepower Bins")
plt.show()

dummy_variable_1 = pd.get_dummies(df["fuel-type"])
dummy_variable_1.rename(columns={"gas": "fuel-type-gas", "diesel": "fuel-type-diesel"}, inplace=True)

df = pd.concat([df, dummy_variable_1], axis=1)
df.drop("fuel-type", axis=1, inplace=True)

print(df.head())

dummy_variable_2 = pd.get_dummies(df["aspiration"])
dummy_variable_2.rename(columns={"std": "aspiration-std", "turbo": "aspiration-turbo"}, inplace=True)

df = pd.concat([df, dummy_variable_2], axis=1)
df.drop("aspiration", axis=1, inplace=True)

print(df.head())

df.to_csv("clean_df.csv")
print("File saved!")

