from flask import Flask, request, render_template
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

nltk.data.path.append('/nltk_data')

app = Flask(__name__)
app.config.from_object(__name__)

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

# Main function for user interaction
# Main function for user interaction
def main():
    while True:
        print("\nAnalytic A Priori Checker")
        print("Enter two phrases separated by a comma to check if they are analytically a priori related.")
        print("Example: 'Bachelors are unmarried, All bachelors are single'")
        print("Type 'exit' to quit.")

        input_text = input("Enter phrases: ").strip()
        if input_text.lower() == 'exit':
            break

        phrases = input_text.split(',', 1)  # Split input into two phrases using comma as delimiter
        if len(phrases) != 2:
            print("Invalid input format. Please enter two phrases separated by a comma.")
            continue

        phrase1, phrase2 = phrases[0].strip(), phrases[1].strip()

        if phrase1 and phrase2:
            try:
                is_analytical = is_analytical_a_priori(phrase1, phrase2)
                result_text = 'The statement is analytical a priori.' if is_analytical else 'The statement is not analytical a priori.'
                print(result_text)
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Invalid input. Please enter non-empty phrases.")

        if input("\nCheck another pair? (yes/no): ").strip().lower() != 'yes':
            break

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        phrases = input_text.split(',', 1)
        if len(phrases) == 2:
            phrase1, phrase2 = phrases[0].strip(), phrases[1].strip()
            is_analytical = is_analytical_a_priori(phrase1, phrase2)
            result_text = 'Analytical a priori.' if is_analytical else 'Not analytical a priori.'
            return render_template('index.html', result=result_text, input_text=input_text)
        else:
            return render_template('index.html', result="Invalid input format.", input_text=input_text)
    return render_template('index.html', result=None, input_text="")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)