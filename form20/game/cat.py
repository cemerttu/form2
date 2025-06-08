# 

# import nltk
# nltk.download('punkt_tab')
# from nltk.tokenize import word_tokenize



# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.util import ngrams

# sentence = "I am learning AI"
# tokens = word_tokenize(sentence)
# bigrams = list(ngrams(tokens, 2)) # Bigram

# print(bigrams)


import nltk

sample_text = 'I am learning Generative AI'
tokens = nltk.word_tokenize(sample_text.lower())

print('Tokens:', tokens)



