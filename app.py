from flask import Flask, render_template, request, jsonify
from pytube import extract
from heapq import nlargest
from youtube_transcript_api import YouTubeTranscriptApi
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation

app = Flask(__name__)

def summarize_video(url):
    video_id = extract.video_id(url)
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

    return formatted_summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    if request.method == 'POST':
        data = request.get_json()
        video_url = data.get('video_url')
        if video_url:
            summary = summarize_video(video_url)
            return jsonify({'summary': summary})
        else:
            return jsonify({'error': 'Invalid request'})
    return jsonify({'error': 'Invalid request'})

if __name__ == '__main__':
    app.run(debug=True)
