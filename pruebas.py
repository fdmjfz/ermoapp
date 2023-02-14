path = 'data/1.txt'
idx_r = 2

with open(path, 'r') as filein:
    text = filein.read()

texto = text.split('\n')
text_list = []
for idx, row in enumerate(texto):
    text_list.append(f'{idx}~  {row}')

text_list.pop(idx_r)
new_text = [i.split('~')[1].replace(' ', '') for i in text_list]

with open(path, 'w') as fileout:
    for i in new_text:
        fileout.write(i)
        fileout.write('\n')
