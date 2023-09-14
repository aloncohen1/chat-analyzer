from utils.parsers import _df_from_str
# file_path = '/Users/aloncohen/Downloads/WhatsApp Chat with +44 7355 729740 (1).txt'
file_path ='/Users/aloncohen/Desktop/WhatsApp Chat with קשישים ומסטולים-בייביבום🧸.txt'
with open(file_path) as f:
  data = f.read()

df = _df_from_str(data)
print(df)