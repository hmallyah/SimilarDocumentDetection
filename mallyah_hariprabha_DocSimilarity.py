import os
import sys
import string
import glob
import itertools
import copy

k = 0
h_no = 0
threshold = 0
docs = {}
doc_cnt = 0
doc_path = []
doc_pairs = []
shingles = {}
doc_id = []
jsim1 = []
jsim2 = []
input_matrix = {}
universal_set = []
sid_shingle = {}
signature_matrix = {}
bands = 0
rows = 0
br = []
minhash_signature = {}
bands_rows = {}
candidates = []

path = sys.argv[1]
k = int(sys.argv[2])
shingle_type = sys.argv[3]
h_no = int(sys.argv[4])
threshold = float(sys.argv[5])
#print path, k, shingle_type, h_no, threshold

for filename in glob.glob(os.path.join(path, '*.txt')):
    doc_path.append(filename)
doc_cnt = len(doc_path)
#print doc_cnt

for d in range(0, doc_cnt):
    docs[d] = ""
    shingles[d] = []
    input_file = open(doc_path[d], "r")
    docs[d] = input_file.read()
    doc_id.append(d+1)
#print docs, shingles, doc_id

from itertools import product
doc_pairs = [list(e) for e in product(doc_id, repeat =2)]
for comb in doc_pairs:
    if comb[0] == comb[1]:
        doc_pairs.remove(comb)
    comb.sort()
doc_pairs_set = set(map(tuple,doc_pairs))
doc_pairs = map(list,doc_pairs_set)
doc_pairs.sort()
#print doc_pairs

def shingling(k, shingle_type, document):
    shingle_set = []
    if shingle_type == "char":
        for i in range(0, len(document)-(k-1)):
            slen = document[i:i+k]
            shingle_set.append(slen)
        shingle_set = list(set(shingle_set))
        #print len(shingle_set)

    if shingle_type == "word":
        doc_spc = document.split()
        for i in range(0, len(doc_spc)-(k-1)):
            comb = []
            for l in range(0, k):
                comb.append(doc_spc[i+l])
            shingle_set.append(''.join(comb))
        shingle_set = list(set(shingle_set))
        #print len(shingle_set)
    return shingle_set

for j in range(0, doc_cnt):
    shingles[j] = shingling(k, shingle_type, docs[j])
    print "No. of shingles in Docs/D" + str(j+1) + ": " +  str(len(shingles[j]))
print '\n'
def jaccard_similarity_one(doc_pairs = [], shingles = {}):
    jsim1 = []
    jsim1 = copy.deepcopy(doc_pairs)
    for x in jsim1:
        jsim_value = 0
        intersection = []
        union = []
        intersection = list(set(shingles[x[0]-1]) & set(shingles[x[1]-1]))
        union = list(set(shingles[x[0]-1]) | set(shingles[x[1]-1]))
        jsim_value = float(len(intersection))/float(len(union))
        x.append(jsim_value)

    return jsim1

jsim1 = jaccard_similarity_one(doc_pairs, shingles)

for js in jsim1:
    print "Jaccard Similarity between Docs/D" + str(js[0]) + ".txt and Docs/D" + str(js[1]) + ".txt: " + str(js[2])
print '\n'
for s in range(0, len(shingles)):
    universal_set = list(set(universal_set) | set(shingles[s]))
universal_set.sort()
#print universal_set, len(universal_set)

for sid in universal_set:
    sid_shingle[universal_set.index(sid)] = sid
#print sid_shingle

for x in range(0, len(sid_shingle)):
    input_matrix[x] = []
    for i in range(0, doc_cnt):
        input_matrix[x].append(0)
for key in sid_shingle:
    for s in range(0, len(shingles)):
        if sid_shingle[key] in shingles[s]:
            input_matrix[key][s] = 1
for i in range(0, len(input_matrix)):
    for h in range(1, h_no+1):
        hash_value = ((i * h)+1) % len(universal_set)
        input_matrix[i].append(hash_value)
#print input_matrix

for i in range(0, h_no):
    signature_matrix[i] = []
    for j in range(0, doc_cnt):
        signature_matrix[i].append(h_no)
#print signature_matrix

for i in range(0, doc_cnt):
    minhash_signature[i+1] = []

def minhashing(input_matrix = {}, signature_matrix = {}):
    for i in range(0, doc_cnt):
        for j in range(0, len(input_matrix)):
            if input_matrix[j][i] == 1:
                 for k in range(0, h_no):
                    if signature_matrix[k][i] > input_matrix[j][doc_cnt+k]:
                        signature_matrix[k][i] = input_matrix[j][doc_cnt+k]

    for i in range(0, doc_cnt):
        for j in range(0, len(signature_matrix)):
            minhash_signature[i+1].append(signature_matrix[j][i])

minhashing(input_matrix, signature_matrix)
print "Min-Hash Signature for the Documents"
for i in range(1, doc_cnt+1):
    print "Docs/D" + str(i) + ".txt:" + str(minhash_signature[i])
print '\n'
def jaccard_similarity_two(doc_pairs = [], minhash_signature = {}):
    jsim2 = []
    jsim2 = copy.deepcopy(doc_pairs)
    for x in jsim2:
        temp = 0
        jsim_value = 0.0
        for h in range(0, h_no):
            if minhash_signature[x[0]][h] == minhash_signature[x[1]][h]:
                temp += 1
        jsim_value = float(float(temp)/float(h_no))
        x.append(jsim_value)

    return jsim2

jsim2 = jaccard_similarity_two(doc_pairs, minhash_signature)

for js in jsim2:
    print "Jaccard Similarity between Docs/D" + str(js[0]) + ".txt and Docs/D" + str(js[1]) + ".txt: " + str(js[2])
print '\n'
def get_bands_rows(threshold):
    factors = []
    temp = []
    max = 0
    global bands
    global rows

    for n in range(1, h_no + 1):
       if h_no % n == 0:
           factors.append(n)

    for n in range(0, len(factors)-1):
        for m in range(n, len(factors)):
            if factors[n]*factors[m] == h_no:
                extra1 = [factors[n],factors[m]]
                br.append(extra1)
                extra2 = [factors[m],factors[n]]
                br.append(extra2)

    for x in br:
        z = float((float(1)/float(x[0]) ** (float(1)/float(x[1]))))
        x.append(z)
        if x[2] <= threshold:
            temp.append(x)

    for y in temp:
        if y[2] > max:
            max = y[2]

    for z in temp:
        if z[2] == max:
            bands = z[0]
            rows = z[1]

get_bands_rows(threshold)
#print bands, rows

for i in range(0, doc_cnt):
    bands_rows[i+1] = []

def get_bands(min_hash_sign, rows):
  chunk = []
  chunks = []
  for x in range(0, len(min_hash_sign), rows):
    chunk = min_hash_sign[x:x+rows]
    chunks.append(chunk)
  return chunks

for i in range(0, doc_cnt):
    bands_rows[i+1] = get_bands(minhash_signature[i+1], rows)
#print bands_rows

def local_sensitivity_hashing(bands, rows, doc_pairs = [], bands_rows = {}):
    count = []
    sim_docs = []
    count = copy.deepcopy(doc_pairs)
    for c in count:
        c.append(0)
    #print count

    for b in range(0, bands):
        hash_table = {}
        buckets = 1000
        for h in range(0, buckets):
            hash_table[h] = []
        for br in range(1, doc_cnt+1):
            key = 0
            for item in bands_rows[br][b]:
                key += item
            #print bands_rows[br][b], key
            key = key * br + 1
            key = key % buckets
            hash_table[key].append(br)
        for bucket in hash_table:
            if len(hash_table[bucket]) == 2:
                count[doc_pairs.index(hash_table[bucket])][2] += 1
            elif len(hash_table[bucket]) > 2:
                temp = []
                temp1 = []
                from itertools import product
                temp = [list(e) for e in product(hash_table[bucket], repeat =2)]
                for comb in temp:
                    if comb[0] == comb[1]:
                        temp.remove(comb)
                temp.sort()
                for each_list in temp:
                    each_list.sort()
                    temp1.append(each_list)
                temp1.sort()
                temp1 = list(temp1 for temp1,_ in itertools.groupby(temp1))
                for item in temp1:
                    count[doc_pairs.index(item)][2] += 1
    for c in count:
        if c[2] >= 1:
            extra = []
            extra = [c[0], c[1]]
            sim_docs.append(extra)

    return sim_docs

candidates = local_sensitivity_hashing(bands, rows, doc_pairs, bands_rows)
#print candidates

print "Candidate pairs obtained using LSH"
for pairs in candidates:
    ('Docs/D1.txt', 'Docs/D2.txt')
    print "('Docs/D" + str(pairs[0]) + ".txt', 'Docs/D" + str(pairs[1]) + ".txt')"
