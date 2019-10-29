import os

def load_data(path):
  data = {}
  # Read each row into data[name].
  for tsv_name in os.listdir(path):
    name = tsv_name[:-4]
    data[name] = []
    with open(path + tsv_name, 'r') as tsv_open:
      for line in tsv_open:
        data[name].append(line.strip().split('|'))
  # Use first row as header, represented as tuple.
  for k in data:
    data[k] = [ data[k][0], data[k][1:] ]
  return data

if __name__ == '__main__':
  TSV_DIR = '../benchmark/kandan/data/kandan_diag/'
  data = load_data(TSV_DIR)

  with open('fe/data.js', 'w') as f:
    f.write(f'let DATA = {data};')

  with open('fe2/data.js', 'w') as f:
    f.write(f'let DATA = {data};')
