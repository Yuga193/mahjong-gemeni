
import os
import json
import random
import dotenv
import google.generativeai as genai
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# .envファイルから環境変数を読み込む
dotenv.load_dotenv()

# 麻雀の全牌リスト
ALL_TILES = [tile for tile in [
    "1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m",
    "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p",
    "1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s",
    "東", "南", "西", "北", "白", "發", "中"
] for _ in range(4)]  # 各牌を4枚ずつ持つようにリストを拡張

# 手牌をランダムに生成する関数
def generate_random_hand():
    tiles = random.sample(ALL_TILES, k=24)  # 重複なしで24枚の牌を選ぶ
    doraA = tiles[0]  # ユーザーが見えるドラ
    doraB = tiles[1:5] #存在してるがユーザーからは見えないドラ
    ura_dora = tiles[5:10]  # 次の5枚を裏ドラとする
    hand = tiles[10:]  # 残りの牌を手牌とする

    player_wind = random.choice(["東", "南", "西", "北"])
    round_wind = random.choice(["東", "南"])

    return hand, doraA, doraB, ura_dora, player_wind, round_wind

class QuestionView(TemplateView):
    template_name = 'question.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hand, doraA, doraB, ura_dora, player_wind, round_wind = generate_random_hand()  # 手牌、ドラ、裏ドラ、自風、場風を取得
        context['hand'] = hand
        context['doraA'] = doraA
        context['doraB'] = doraB
        context['ura_dora'] = ura_dora
        context['player_wind'] = player_wind
        context['round_wind'] = round_wind
        return context

def configure_api():
    # 環境変数からGoogle APIキーを取得
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    # APIキーが設定されていない場合はエラーを発生
    if not GOOGLE_API_KEY:
        raise ValueError("Google API key is missing")
    # APIキーを用いてGoogle AIを設定
    genai.configure(api_key=GOOGLE_API_KEY)
    # AIモデルを指定
    return genai.GenerativeModel("gemini-1.5-flash")

@csrf_exempt
def analyze_hand(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selectedTile = data.get('selectedTile')
        hand = data.get('hand')
        doraA = data.get("doraA")
        player_wind = data.get("playerWind")  # POSTデータから取得
        round_wind = data.get("roundWind")

        # ロール設定プロンプトと手牌情報を組み合わせてAIに渡す
        prompt = f"""
    あなたは麻雀を熟知した麻雀のプロです。プレイヤーが選択した牌と手牌の情報を受け取り、以下の観点から解説を日本語で提供してください。

### 回答テンプレート
自風: {player_wind},場風: {round_wind}<br>
ドラ: {doraA}<br>
捨て牌: {selectedTile}<br>
手牌: {hand}<br>
<br>

- また回答を作成する際は手牌は["1m","2m","3m","1p","2p","3p","1s","2s","3s","東","南","白","發","中"]と出力するのではなく、[1m,2m,3m,1p,2p,3p,1s,2s,3s,東,南,白,發,中]と出力してください。
- 文章には*を入れないでください
- 自風,場風を言い終えたあとは改行してからドラを言い、ドラを言い終えたあとは改行してから捨て牌を言い、捨て牌を言い終えたあとは改行してから手牌を言って、手牌を言い終えたら改行してから本文に入ってください
- 改行する際は文末に”<br>”とつけてください
- 文頭にも*はいれないでください
- また手牌の時は<br>をつけて改行したら、改行先でもう一度<br>をつけてください
- 最初に<strong>を入れて、解説に入る前に</strong>で締めてください

### プロンプト：
与えられた14枚の麻雀の手牌({hand})から、自分で捨て牌を選び、その理由を説明してください。また説明する際は以下の要素を考慮してください。

- 100文字以内で簡潔に答えてください。
- 最後に理由を述べて、あなたなら何を切るか答えてください。
- ユーザーは{selectedTile}を捨てます。それに対して以下の観点から講評してください。

--1. 順子と刻子を最優先で残す。
--2. 役牌の重なりを優先する。
--3. 対子や三色（異なるスーツで同じ数字の順子）を優先して残す。
--4. 字牌（東、南、西、北、白、發、中）は、自風牌、場風牌、役牌以外は優先的に処理する。
--5. 無駄牌（他の牌と繋がりにくい牌）を優先して切る。
--6. ポンやチーの可能性を考える。
--7. カンチャン（両端に隙間のある形）やペンチャン（端の形）を意識する。
--8. 役の種: (例: 三色同順、一盃口、役牌など)
--9. ドラの活用: (例: ドラが対子になっている、ドラを暗刻にできる可能性があるなど)
--10. 待ちの形: (例: 両面待ち、三面待ち、シャンポン待ちなど)
--11. 手牌の効率: (例: 孤立牌が少ない、無駄牌が少ないなど)
--12. 高得点の手の可能性: (例: 跳満以上の手になる可能性がある、倍満以上の手になる可能性があるなど)

- 萬子はm, 筒子はp, 索子はsと呼びます。(例 1萬→1m 6筒→6p 8索→8s)
- 東、南、西、北、白、發、中が選択されても萬子はm, 筒子はp, 索子はsと呼びます。
- ドラは{doraA}です
- 自風は{player_wind}です
- 場風は{round_wind}です

### 例：
手牌: 4m, 4m, 6m, 1p, 7p, 9p, 1s, 2s, 3s, 東, 東, 白, 發, 發
最適な捨て牌: 白

理由:
1. 対子の東と發を優先して活かすため。
2. 字牌の中で無駄牌の白を先に切ることで手を進めやすくするため。
3. 1pは次の候補となるが、まずは白を切ることで東や發のポンがしやすくなる。

### ガイドライン：
1. 役牌の重なりを優先する
2. 対子や三色ができる可能性がある場合、それらを優先して残す
3. 孤立している牌（他の牌と繋がりにくい牌）を優先して切る

### 最後に:

- 完成した文章に改行等を含めて読みやすいように清書してください。
-- ダメな例
自風:東,場風:西 捨て牌: 5p 手牌: [4m,5m,6m,8m,2p,2p,3p,8p,3s,8s,東,白,發] まず字牌の發を切るのが良いと思います。 理由としては手牌に4m,5m,6mと順子がすでにあり、發は孤立していて使いにくいからです。 5pを切るのは、まだ2pや8pで変化する可能性も残っているので、少しもったいないかもしれません。

-- 良い例
<strong>自風:東,場風:西<br>捨て牌: 5p<br>手牌: [4m,5m,6m,8m,2p,2p,3p,8p,3s,8s,東,白,發] <br><br></strong>まず字牌の發を切るのが良いと思うのです。 <br>理由はとしては手牌に4m,5m,6mと順子がすでにあり、發は孤立していて使いにくいからです。 <br>5pを切るのは、まだ2pや8pで変化する可能性も残っているので、少しもったいないかもしれませんのです。
"""

        # Gemini AIに問い合わせる
        model = configure_api()
        response = model.generate_content(prompt)

        # 応答をJSON形式で返す
        commentary = f"【選択された牌】{selectedTile} 【手牌】{', '.join(hand)}\n{response.text}"
        return JsonResponse({'commentary': response.text})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

