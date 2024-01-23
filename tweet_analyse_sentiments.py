# -*- coding: utf-8 -*-

# importation des librairies
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import string
import nltk
import warnings
# %matplotlib inline

#Lecture des données 
df = pd.read_csv('Twitter Sentiments.csv')
df.head()

df.info()

#Suppression d'un modèle de texte au sein du tweet
def remove_pattern(input_txt, pattern):
  r= re.findall(pattern, input_txt)
  for word in r: 
    input_txt=re.sub(word, "", input_txt)
  return input_txt

df.head()

#suppression des nom d'utilisateur 
df['clean_tweet']= np.vectorize(remove_pattern)(df['tweet'], "@[\w]*")
df.head()

#Suppression des caractères spéciaux, nombres et ponctuations
df['clean_tweet'] = df['clean_tweet'].str.replace("[^a-zA-Z#]", " ")
df.head()

#Suppression des mots courts 
df['clean_tweet']= df['clean_tweet'].apply(lambda x: " ".join([w for w in x.split() if len(w)>3]))
df.head()

# iles Mots sont considérés comme des jetons
tokenized_tweet = df['clean_tweet'].apply(lambda x:x.split())
tokenized_tweet.head()

#radical des mots
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

tokenized_tweet = tokenized_tweet.apply(lambda sentence: [stemmer.stem(word) for word in sentence])
tokenized_tweet.head()

# combine words into single sentence 
for i in range(len(tokenized_tweet)):
  tokenized_tweet[i]=" ".join(tokenized_tweet[i])
df['clean_tweet']= tokenized_tweet
df.head()

!pip install wordcloud

import wordcloud
#VIsualisation des mots frequents
all_words="".join([sentence for sentence in df['clean_tweet']])
from wordcloud import WordCloud
wordcloud=WordCloud(width=800, height=500, random_state=42, max_font_size=100).generate(all_words)
#plot the graph 
plt.figure(figsize=(15,8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# frequent words visualization for +ve
all_words="".join([sentence for sentence in df['clean_tweet'][df['label']==0]])
wordcloud=WordCloud(width=800, height=500, random_state=42, max_font_size=100).generate(all_words)
#plot the graph 
plt.figure(figsize=(15,8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# frequent words visualization for -ve
all_words = " ".join([sentence for sentence in df['clean_tweet'][df['label']==1]])

wordcloud = WordCloud(width=800, height=500, random_state=42, max_font_size=100).generate(all_words)

# plot the graph
plt.figure(figsize=(15,8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# extract the hashtag
def hashtag_extract(tweets):
    hashtags = []
    # loop words in the tweet
    for tweet in tweets:
        ht = re.findall(r"#(\w+)", tweet)
        hashtags.append(ht)
    return hashtags

# extract hashtags from non-racist/sexist tweets
ht_positive = hashtag_extract(df['clean_tweet'][df['label']==0])

# extract hashtags from racist/sexist tweets
ht_negative = hashtag_extract(df['clean_tweet'][df['label']==1])

ht_positive[:5]

# unnest list
ht_positive = sum(ht_positive, [])
ht_negative = sum(ht_negative, [])

freq = nltk.FreqDist(ht_positive)
d = pd.DataFrame({'Hashtag': list(freq.keys()),
                  'Count': list(freq.values())})
d.head()

# select top 10 hashtags
d = d.nlargest(columns='Count', n=10)
plt.figure(figsize=(15,9))
sns.barplot(data=d, x='Hashtag', y='Count')
plt.show()

freq = nltk.FreqDist(ht_negative)
d = pd.DataFrame({'Hashtag': list(freq.keys()),
                  'Count': list(freq.values())})
d.head()

# select top 10 hashtags
d = d.nlargest(columns='Count', n=10)
plt.figure(figsize=(15,9))
sns.barplot(data=d, x='Hashtag', y='Count')
plt.show()

# feature extraction
from sklearn.feature_extraction.text import CountVectorizer
bow_vectorizer = CountVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words='english')
bow = bow_vectorizer.fit_transform(df['clean_tweet'])

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(bow, df['label'], random_state=42, test_size=0.25)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score
# training
model = LogisticRegression()
model.fit(x_train, y_train)
# testing
pred = model.predict(x_test)
f1_score(y_test, pred)

accuracy_score(y_test,pred)

# utilisation des probabilités pour la sortie 
pred_prob = model.predict_proba(x_test)
pred = pred_prob[:, 1] >= 0.3
pred = pred.astype(np.int)

f1_score(y_test, pred)

pred_prob[0][1] >= 0.3
