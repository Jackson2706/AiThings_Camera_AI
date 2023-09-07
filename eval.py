import pandas as pd
def convert_time(x):
    return 1/x

df = pd.read_csv("yolov5_deepsort.csv")
df["detection time"] = df["detection time"].apply(convert_time)
df["track time"] = df["track time"].apply(convert_time)
df["error time"] = df["error time"].apply(convert_time)
print("Yolov5+DeepSort:\n")
print(df.describe())


# df = pd.read_csv("yolov5_bytetrack.csv")
# # df["detection time"] = df["detection time"].apply(convert_time)
# # df["track time"] = df["track time"].apply(convert_time)
# # df["error time"] = df["error time"].apply(convert_time)
# print("Yolov5+Bytetrack:\n")
# print(df.describe())