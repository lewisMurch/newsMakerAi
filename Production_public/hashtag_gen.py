import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

def run(input_headline):
    # ensure nltk data is downloaded
    def download_nltk_data():
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger', quiet=True)
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)

    # ensure necessary NLTK data files are downloaded
    download_nltk_data()

    # Remove punctuation
    cleaned_headline = re.sub(r'[^\w\s]', '', input_headline)

    # tokenize the headline
    tokens = word_tokenize(cleaned_headline)

    tagged_tokens = pos_tag(tokens)

    uninteresting_words = set(stopwords.words('english'))
    uninteresting_pos_tags = {'RB', 'RBR', 'RBS', 'DT'}

    # List of good adjectives to keep
    significant_adjectives = {"Shocking", "Gruesome"}

    # make hashtags
    hashtags = []

    for word, pos in tagged_tokens:
        if word.lower() not in uninteresting_words and pos not in uninteresting_pos_tags:
            if pos.startswith('NN') or pos.startswith('VB') or word in significant_adjectives or pos in {'NNP', 'NNPS'}:
                hashtags.append('#' + word)

    final = " ".join(hashtags)

    return final

