# importing libraries
#  -- pytube: to extract video id from youtube url
#  -- youtube_transcript_api: to get the transcript of the video
#  -- spacy: to build the NLP model, tokenize the sentences, remove stop words and punctuations
#  -- heapq: to get the top n sentences with the highest score; to generate a summary from the tokenized sentences

from flask import Flask, render_template, request, jsonify
from pytube import extract, YouTube
from heapq import nlargest
from youtube_transcript_api import YouTubeTranscriptApi
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation

app = Flask(__name__)

def summarize_video(url):
    video_id = extract.video_id(url)
    yt = YouTube(url)
    title = yt.title
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    text = " ".join(elem["text"] for elem in transcript)

    nlp = spacy.load('en_core_web_sm')
    document = nlp(text)

    word_frequencies = {}
    for word in document:
        text = word.text.lower()
        if text not in list(STOP_WORDS) and text not in punctuation:
            if word.text not in word_frequencies:
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_tokens = [sentence for sentence in document.sents]
    sentence_score = {}
    for sentence in sentence_tokens:
        for word in sentence:
            if word.text.lower() in word_frequencies:
                if sentence not in sentence_score:
                    sentence_score[sentence] = word_frequencies[word.text.lower()]
                else:
                    sentence_score[sentence] += word_frequencies[word.text.lower()]

    select_length = int(len(sentence_tokens) * 0.3)
    summary = nlargest(select_length, sentence_score, key=sentence_score.get)
    final_summary = [word.text for word in summary]
    formatted_summary = ' '.join(final_summary)


    return formatted_summary, title


    # Generates a concise summary of a transcript by:

    #     1. Calculating normalized scores for each sentence.
    #     2. Selecting the top 30% most important sentences based on score.
    #     3. Combining the text of these top sentences into a single summary.

    # Returns a string containing the final summary.
    


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    if request.method == 'POST':
        data = request.get_json()
        video_url = data.get('video_url')
        if video_url:
            summary, title = summarize_video(video_url)
            if summary is None:
                summary = 'Failed to generate summary'
            return jsonify({'summary': summary, 'title': title})
        else:
            return jsonify({'error': 'Invalid request'})
    return jsonify({'error': 'Invalid request'})

if __name__ == '__main__':
    app.run(debug=True)
