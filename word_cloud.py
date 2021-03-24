




# 워드 클라우드에 필요한 라이브러리를 불러옵니다.
from wordcloud import WordCloud
# 한국어 자연어 처리 라이브러리를 불러옵니다.
from konlpy.tag import Twitter
# 명사의 출현 빈도를 세는 라이브러리를 불러옵니다.
from collections import Counter
# 그래프 생성에 필요한 라이브러리를 불러옵니다.
import matplotlib.pyplot as plt
# Flask 웹 서버 구축에 필요한 라이브러리를 불러옵니다.
from flask import Flask, request, jsonify
# CORS를 처리합니다.
from flask_cors import CORS
# 파일에 접근하기 위한 라이브러리를 불러옵니다.
import os

# 플라스크 웹 서버 객체 생성합니다.
app = Flask(__name__, static_folder='outputs')
CORS(app)

#폰트 경로 설정
font_path = 'NanumGothic.ttf'


def get_tags(text, max_count, min_length):
    t = Twitter()
    nouns = t.nouns(text)
    processed = [n for n in nouns if len(n) >= min_length]
    count = Counter(processed)
    result = {}
    for n, c in count.most_common(max_count):
        result[n] = c
    if len(result) == 0:
        result["내용이 없습니다."] = 1
    return result


def make_cloud_image(tags, file_name):
    # 만들고자 하는 워드 클라우드의 기본 설정을 진행합니다.
    word_cloud = WordCloud(
        font_path=font_path,
        width=800,
        height=800,
        background_color="white"
    )
    word_cloud = word_cloud.generate_from_frequencies(tags)
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(word_cloud)
    plt.axis("off")
    # 만들어진 이미지 객체를 파일 형태로 저장합니다.
    fig.savefig("outputs/{0}.png".format(file_name))


def process_from_text(text, max_count, min_length, words, file_name):
    tags = get_tags(text, int(max_count), int(min_length))
    # 단어 가중치를 적용합니다.
    for n, c in words.items():
        if n in tags:
            tags[n] = tags[n] * float(words[n])
    make_cloud_image(tags, file_name)


@app.route("/process", methods=['GET', 'POST'])
def process():
    content = request.json
    words = {}
    if content['words'] is not None:
        for data in content['words'].values():
            words[data['word']] = data['weight']
    process_from_text(content['text'], content['maxCount'], content['minLength'], words, content['textID'])
    result = {'result': True}
    return jsonify(result)
# ----------------------------------------------------------------------
# TalendAPI Tester 에서 테스트 방법
 
#  Method : POST,
#  (API)URL : http://localhost:5000/process *https아님!!
#  header : Content-Type, application/json, charset=utf-8 * 한글쓰려면

# body json =>
#  !!process_from_text의 배열에 정의된 contents들 빠짐없이 다 넣어야 함!!
#  !!순서는 상관 없는 듯!! 안그럼 500 error남
#   {
#  	"textID": "3",
#  	"text": "안녕하세요? 지금 파이썬 코딩 테스트중입니다. 파이썬이 어려운지 자바가 어려운지 노드가 어려운지 참나... 대부분 다 쓰기 편한 듯 한데 그래도 파이썬이 조금 더 어려운 듯",
#  	"words": {
#  		"1": {
#  			"weight": "7",
#  			"word": "스터디"
#  		},
#  		"2": {
#  			"weight": "5",
#  			"word": "공부"
#  		}
#  	},
#  	"maxCount": 4,
#  	"minLength": 2

#  }
# ----------------------------------------------------------------------


@app.route('/outputs', methods=['GET', 'POST'])
def output():
    text_id = request.args.get('textID')
    return app.send_static_file(text_id + '.png')


@app.route('/validate', methods=['GET', 'POST'])
def validate():
    text_id = request.args.get('textID')
    path = "outputs/{0}.png".format(text_id)
    result = {}
    # 해당 이미지 파일을 존재하는지 확인합니다.
    if os.path.isfile(path):
        result['result'] = True
    else:
        result['result'] = False
    return jsonify(result)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, threaded=False) # thread=true로 하면 무한오류 발생!!!
    
    