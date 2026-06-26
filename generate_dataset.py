import pandas as pd
import numpy as np

rows = 5000

df = pd.DataFrame({
    "temperature": np.random.randint(25,45,rows),
    "humidity": np.random.randint(40,90,rows),
    "production_load": np.random.randint(50,100,rows),
    "consumption": np.random.randint(300,1000,rows)
})

df.to_csv("data/energy.csv",index=False)

print("Dataset Created")