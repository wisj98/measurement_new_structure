import pickle

with open("config.pickle","rb") as fr:
            config = pickle.load(fr)

print(config)