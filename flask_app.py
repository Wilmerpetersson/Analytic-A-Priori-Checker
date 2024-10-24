from flask import Flask, request, render_template_string
import nltk

from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

nltk.download('omw-1.4')

app = Flask(__name__)

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Function to exclude words from the input
def exclude_words_from_input(input_string):
    excluded_words = ['a', 'an', 'is', 'the', 'all', 'are']
    words = input_string.split(' ')
    return ' '.join([word for word in words if word not in excluded_words])

# Function to get lemma of a word
def get_lemma(word):
    return lemmatizer.lemmatize(word)

# Function to check if two words are semantically related using WordNet
hypernym_cache = {}

def get_all_hypernyms(synset):
    if synset in hypernym_cache:
        return hypernym_cache[synset]

    hypernyms = set()
    for hypernym in synset.hypernyms():
        hypernyms.add(hypernym)
        hypernyms.update(get_all_hypernyms(hypernym))

    hypernym_cache[synset] = hypernyms
    return hypernyms

def are_related(word1, word2):
    synsets1 = wn.synsets(word1)
    synsets2 = wn.synsets(word2)

    # Direct synonym check
    for syn1 in synsets1:
        for syn2 in synsets2:
            # Check if the words are direct synonyms
            if syn1 == syn2:
                return True

            # Check if word1 is a hypernym or hyponym of word2
            if syn1 in syn2.hypernyms() or syn1 in syn2.hyponyms():
                return True

            # Check if word2 is a hypernym or hyponym of word1
            if syn2 in syn1.hypernyms() or syn2 in syn1.hyponyms():
                return True

            # Check if any hypernym of word1 is word2
            if syn2 in get_all_hypernyms(syn1):
                return True

            # Check if any hypernym of word2 is word1
            if syn1 in get_all_hypernyms(syn2):
                return True

    return False


# Function to check if a statement is analytical a priori
def is_analytical_a_priori(phrase1, phrase2):
    phrase1_words = [get_lemma(word) for word in exclude_words_from_input(phrase1.lower()).split()]
    phrase2_words = [get_lemma(word) for word in exclude_words_from_input(phrase2.lower()).split()]

    for word1 in phrase1_words:
        for word2 in phrase2_words:
            if are_related(word1, word2):
                return True

    return False

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        phrases_input = request.form['phrases']
        phrases = phrases_input.split(',', 1)  # Split the input into two phrases at the first comma
        if len(phrases) == 2:
            phrase1, phrase2 = phrases[0].strip(), phrases[1].strip()
            try:
                is_analytical = is_analytical_a_priori(phrase1, phrase2)
                # Change color based on whether the statement is analytical
                if is_analytical:
                    result = '<span style="color: green;">The statement is analytical a priori.</span>'
                else:
                    result = '<span style="color: red;">The statement is not analytical a priori.</span>'
            except Exception as e:
                result = f'<span style="color: red;">An error occurred: {e}</span>'
        else:
            result = '<span style="color: red;">Please enter two phrases separated by a comma.</span>'
    else:
        result = ''

    return render_template_string('''
        <html>
            <body>
                <h2>Analytic A Priori Checker</h2>
                <p>Currently only universal quantification(∀) functionality.</p>

                <form method="post">
                    Enter phrases separated by a comma:<br>
                    <input type="text" name="phrases"><br><br>
                    <input type="submit" value="Check">
                </form>
                <p>{{ result|safe }}</p> <!-- The |safe filter allows HTML to be rendered -->
                <br>
                <br>
                <br>
                <h2>Tutorial</h2>
                <img src="{{ url_for('static', filename='apriori-checker.gif') }}" style="max-width: 100%;">
                <p>Contact: wilmerpettersson6@gmail.com </p>
            </body>
        </html>
    ''', result=result)


if __name__ == '__main__':
    app.run(debug=True)
