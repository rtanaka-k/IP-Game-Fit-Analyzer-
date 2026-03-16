import streamlit as st
import json
import os

# --- Claude API Helper ---
def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """Call Claude API and return text response."""
    import urllib.request
    
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "[ERROR] ANTHROPIC_API_KEY が設定されていません。サイドバーでAPIキーを入力してください。"
    
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"]
    except Exception as e:
        return f"[ERROR] API呼び出しに失敗しました: {str(e)}"


# --- Genre Database ---
GENRE_DATABASE = {
    "アクションRPG": {
        "description": "リアルタイムの戦闘とキャラクター成長を組み合わせたジャンル",
        "strengths": ["バトル要素の強いIP", "キャラクター成長が描かれるIP", "世界観が広いIP"],
        "examples": ["原神（オリジナル）", "テイルズシリーズ", "NieR:Automata"],
        "platform_fit": ["スマホ", "コンソール", "PC"],
        "monetization": ["ガチャ", "バトルパス", "買い切り+DLC"],
        "dev_scale": "中〜大規模",
        "risk_level": "中〜高"
    },
    "ターン制RPG": {
        "description": "戦略的なコマンドバトルとストーリー重視のジャンル",
        "strengths": ["ストーリー重視のIP", "キャラクターが多いIP", "収集要素と親和性が高いIP"],
        "examples": ["FGO（Fate）", "ヘブンバーンズレッド", "ドラクエウォーク"],
        "platform_fit": ["スマホ", "コンソール"],
        "monetization": ["ガチャ", "スタミナ課金", "買い切り"],
        "dev_scale": "中規模",
        "risk_level": "中"
    },
    "ストラテジー / タクティクス": {
        "description": "戦術的思考と部隊編成を楽しむジャンル",
        "strengths": ["勢力争いがあるIP", "多数のキャラクターが存在するIP", "軍記・戦略要素のあるIP"],
        "examples": ["FEH（ファイアーエムブレム）", "アークナイツ", "三國志シリーズ"],
        "platform_fit": ["スマホ", "PC", "コンソール"],
        "monetization": ["ガチャ", "買い切り+DLC"],
        "dev_scale": "中規模",
        "risk_level": "中"
    },
    "アドベンチャー / ノベルゲーム": {
        "description": "ストーリー体験と選択肢による分岐を楽しむジャンル",
        "strengths": ["ストーリーが最大の魅力であるIP", "ミステリー・サスペンス要素", "感情移入しやすいキャラクター"],
        "examples": ["Fate/stay night", "シュタインズ・ゲート", "ダンガンロンパ"],
        "platform_fit": ["スマホ", "PC", "コンソール"],
        "monetization": ["買い切り", "シナリオ追加DLC", "シーズンパス"],
        "dev_scale": "小〜中規模",
        "risk_level": "低〜中"
    },
    "アクション / 格闘": {
        "description": "操作スキルと反射神経を活かした対戦・アクションジャンル",
        "strengths": ["バトル描写が魅力のIP", "キャラクターの個性が戦闘スタイルに反映できるIP"],
        "examples": ["ドラゴンボールファイターズ", "鬼滅の刃 ヒノカミ血風譚", "NARUTO ナルティメットストーム"],
        "platform_fit": ["コンソール", "PC", "アーケード"],
        "monetization": ["買い切り+DLC", "キャラクター追加課金"],
        "dev_scale": "中〜大規模",
        "risk_level": "中"
    },
    "オープンワールド / 探索": {
        "description": "広大な世界を自由に探索し、発見を楽しむジャンル",
        "strengths": ["世界観が広大で深いIP", "探索・冒険要素が強いIP", "環境描写が魅力的なIP"],
        "examples": ["ゼルダの伝説 ティアーズ", "原神", "ホグワーツ・レガシー"],
        "platform_fit": ["コンソール", "PC"],
        "monetization": ["買い切り+DLC", "拡張パック"],
        "dev_scale": "大規模",
        "risk_level": "高"
    },
    "リズム / 音楽ゲーム": {
        "description": "音楽に合わせた操作で楽しむジャンル",
        "strengths": ["音楽要素が強いIP", "アイドル・バンド系IP", "楽曲資産が豊富なIP"],
        "examples": ["プロセカ", "バンドリ", "あんスタ Music"],
        "platform_fit": ["スマホ", "アーケード"],
        "monetization": ["ガチャ", "楽曲追加課金", "衣装課金"],
        "dev_scale": "中規模",
        "risk_level": "中"
    },
    "パズル / カジュアル": {
        "description": "シンプルなルールで幅広い層が楽しめるジャンル",
        "strengths": ["幅広い年齢層のファンを持つIP", "キャラクターの見た目が可愛い・親しみやすいIP"],
        "examples": ["ツムツム（ディズニー）", "ポケモンパズル", "ぷよぷよ"],
        "platform_fit": ["スマホ"],
        "monetization": ["広告", "アイテム課金", "スタミナ課金"],
        "dev_scale": "小規模",
        "risk_level": "低"
    },
    "シミュレーション / 経営": {
        "description": "世界を構築・運営しながら成長を楽しむジャンル",
        "strengths": ["日常・生活描写が魅力のIP", "拠点や街の概念があるIP", "コレクション要素との親和性"],
        "examples": ["天穂のサクナヒメ", "どうぶつの森", "牧場物語コラボ作品"],
        "platform_fit": ["スマホ", "コンソール", "PC"],
        "monetization": ["買い切り", "デコレーション課金", "ガチャ"],
        "dev_scale": "中規模",
        "risk_level": "中"
    },
    "サバイバル / クラフト": {
        "description": "過酷な環境で資源を集め、生き延びるジャンル",
        "strengths": ["サバイバル要素があるIP", "世界の脅威（怪獣・ゾンビ等）が存在するIP", "探索と創造の両面があるIP"],
        "examples": ["ARK", "Subnautica", "マインクラフト"],
        "platform_fit": ["PC", "コンソール"],
        "monetization": ["買い切り+DLC", "スキン課金"],
        "dev_scale": "中〜大規模",
        "risk_level": "中〜高"
    },
    "非対称対戦 / マルチプレイ": {
        "description": "異なる役割のプレイヤーが対峙する、またはCo-opで協力するジャンル",
        "strengths": ["追う側と逃げる側の構図があるIP", "協力プレイが映えるIP", "ホラー・スリラー要素"],
        "examples": ["Dead by Daylight", "Among Us", "Identity V（第五人格）"],
        "platform_fit": ["スマホ", "PC", "コンソール"],
        "monetization": ["スキン課金", "バトルパス", "キャラクター課金"],
        "dev_scale": "中規模",
        "risk_level": "中"
    },
    "位置情報ゲーム": {
        "description": "現実世界の移動と連動したゲーム体験",
        "strengths": ["現実世界との接点があるIP", "コレクション要素が強いIP", "ご当地・聖地巡礼的要素"],
        "examples": ["ポケモンGO", "ドラクエウォーク", "Pikmin Bloom"],
        "platform_fit": ["スマホ"],
        "monetization": ["アイテム課金", "イベント課金"],
        "dev_scale": "大規模",
        "risk_level": "高"
    }
}


# --- System Prompts ---
ANALYSIS_SYSTEM_PROMPT = """あなたはゲーム業界に精通したIPアナリストです。
与えられたIP（知的財産）について、ゲーム化を検討するために必要な属性を分析してください。

以下のJSON形式で回答してください。JSONのみを出力し、他のテキストは含めないでください。

{
    "ip_name": "IP名",
    "ip_name_en": "英語表記",
    "original_media": "原作メディア（漫画/小説/映画/アニメオリジナル/ゲーム/特撮/その他）",
    "genre": "作品ジャンル（バトル/冒険/日常/SF/ファンタジー/ホラー/ミステリー/ロマンス/スポーツ/歴史等、複数可）",
    "status": "展開状況（連載中/完結/シリーズ継続中 等）",
    "media_mix_history": "メディアミックス展開履歴（アニメ化、映画化、ゲーム化の実績を簡潔に）",
    "world_scale": "世界観の広さ（1-5: 1=閉じた空間、5=多元宇宙級）",
    "story_structure": "ストーリー構造（一本道/群像劇/オムニバス/ループ等）",
    "battle_weight": "バトル・アクション要素の比重（1-5: 1=皆無、5=主軸）",
    "character_volume": "キャラクター資産の量（1-5: 1=少数精鋭、5=大量）",
    "character_diversity": "キャラクターの多様性（1-5: 1=同質的、5=極めて多様）",
    "collection_affinity": "収集・コレクション要素との親和性（1-5）",
    "emotional_depth": "感情的・ストーリー的深み（1-5）",
    "humor_factor": "コメディ・ユーモア要素（1-5）",
    "darkness_factor": "ダーク・シリアス要素（1-5）",
    "competition_element": "競争・対戦要素（1-5）",
    "cooperation_element": "協力・チームワーク要素（1-5）",
    "exploration_element": "探索・発見要素（1-5）",
    "crafting_building": "クラフト・建築要素との親和性（1-5）",
    "music_rhythm_affinity": "音楽・リズム要素との親和性（1-5）",
    "target_gender": "メインターゲットの性別傾向（男性寄り/女性寄り/ユニセックス）",
    "target_age": "メインターゲットの年齢層（子供/10代/20代/30代以上/全年齢）",
    "global_awareness": "海外認知度（1-5: 1=国内のみ、5=世界的）",
    "fan_spending_tendency": "ファンの消費傾向（グッズ重視/イベント重視/デジタルコンテンツ重視/総合的）",
    "existing_game_history": "既存ゲーム化実績と評価（簡潔に。なければ「なし」）",
    "unique_hook": "このIPならではのユニークな特徴・フック（ゲーム化で活かせそうな独自要素）",
    "summary": "IPの概要（2-3文で）"
}

数値は必ず1-5の整数で回答してください。分析は正確かつ率直に行ってください。"""

RECOMMEND_SYSTEM_PROMPT = """あなたはゲーム業界25年以上のベテランプロデューサーであり、IPを活用したゲーム企画の専門家です。

与えられたIPの属性分析と、ゲームジャンルデータベースに基づいて、このIPに適したゲームジャンルを推薦してください。

推薦は以下の3カテゴリーで行ってください：

1. **本命（Most Likely）**: IPの特性と最も相性が良い、成功確率が高いジャンル。2つ提案。
2. **対抗（Dark Horse）**: 一見意外だが、IPの隠れた魅力を引き出せるジャンル。1つ提案。
3. **大穴（Wild Card）**: 常識を覆す組み合わせだが、ハマれば革新的になり得るジャンル。1つ提案。

各提案について以下を含めてください：
- ジャンル名
- なぜこのIPとこのジャンルが合うのか（3-4文の根拠）
- 想定されるゲームコンセプト（1-2文の企画コンセプト案）
- 類似の成功事例（あれば）
- リスク・懸念点（1-2文）
- 想定プラットフォーム
- 収益モデル案

「企画の種」として、読んだ人が「そういう考え方もあるか」と刺激を受けるような内容を心がけてください。
安全な提案だけでなく、挑戦的な発想も含めてください。

回答は日本語で、マークダウン形式で読みやすく記述してください。"""


# --- Page Config ---
st.set_page_config(
    page_title="IP Game Fit Analyzer",
    page_icon=None,
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.3rem;
        letter-spacing: 0.02em;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Init ---
if "ip_analysis" not in st.session_state:
    st.session_state.ip_analysis = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
if "analysis_confirmed" not in st.session_state:
    st.session_state.analysis_confirmed = False

# --- Sidebar ---
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Anthropic API Key", type="password", help="Claude APIキーを入力してください")
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
    
    st.divider()
    st.header("ジャンルデータベース")
    st.caption(f"登録ジャンル数: {len(GENRE_DATABASE)}")
    
    with st.expander("登録ジャンル一覧"):
        for genre_name, genre_info in GENRE_DATABASE.items():
            st.markdown(f"**{genre_name}**")
            st.caption(genre_info["description"])
            st.caption(f"代表作: {', '.join(genre_info['examples'])}")
            st.markdown("---")

# --- Main Content ---
st.markdown('<div class="main-header">IP Game Fit Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">IPの特性を分析し、最適なゲームジャンルと企画の種を提案します</div>', unsafe_allow_html=True)

# --- Step 1: IP Input ---
st.header("Step 1: IP名を入力")
col1, col2 = st.columns([3, 1])
with col1:
    ip_name = st.text_input(
        "分析したいIP名を入力してください",
        placeholder="例: 呪術廻戦、ゴジラ、Re:ゼロから始める異世界生活...",
        label_visibility="collapsed"
    )
with col2:
    analyze_button = st.button("IP分析を実行", type="primary", use_container_width=True)

if analyze_button and ip_name:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("サイドバーでAPIキーを設定してください。")
    else:
        with st.spinner(f"「{ip_name}」を分析中..."):
            result = call_claude(
                ANALYSIS_SYSTEM_PROMPT,
                f"以下のIPを分析してください: {ip_name}"
            )
            
            if result.startswith("[ERROR]"):
                st.error(result)
            else:
                try:
                    # Clean potential markdown code blocks
                    cleaned = result.strip()
                    if cleaned.startswith("```"):
                        cleaned = cleaned.split("\n", 1)[1]
                    if cleaned.endswith("```"):
                        cleaned = cleaned.rsplit("```", 1)[0]
                    cleaned = cleaned.strip()
                    
                    st.session_state.ip_analysis = json.loads(cleaned)
                    st.session_state.analysis_confirmed = False
                    st.session_state.recommendations = None
                except json.JSONDecodeError:
                    st.error("分析結果のパースに失敗しました。再度お試しください。")
                    st.code(result)

# --- Step 2: Review & Edit Analysis ---
if st.session_state.ip_analysis:
    st.header("Step 2: 分析結果の確認・修正")
    st.info("AIによる分析結果です。必要に応じて修正してください。")
    
    analysis = st.session_state.ip_analysis
    
    # Basic Info
    st.subheader("基本情報")
    col1, col2, col3 = st.columns(3)
    with col1:
        analysis["ip_name"] = st.text_input("IP名", value=analysis.get("ip_name", ""))
        analysis["original_media"] = st.text_input("原作メディア", value=analysis.get("original_media", ""))
    with col2:
        analysis["genre"] = st.text_input("作品ジャンル", value=analysis.get("genre", ""))
        analysis["status"] = st.text_input("展開状況", value=analysis.get("status", ""))
    with col3:
        analysis["target_gender"] = st.selectbox(
            "ターゲット性別傾向",
            ["男性寄り", "女性寄り", "ユニセックス"],
            index=["男性寄り", "女性寄り", "ユニセックス"].index(analysis.get("target_gender", "ユニセックス")) if analysis.get("target_gender", "ユニセックス") in ["男性寄り", "女性寄り", "ユニセックス"] else 2
        )
        analysis["target_age"] = st.text_input("ターゲット年齢層", value=analysis.get("target_age", ""))
    
    st.text_area("メディアミックス展開履歴", value=analysis.get("media_mix_history", ""), key="media_mix")
    analysis["media_mix_history"] = st.session_state.media_mix
    
    st.text_area("既存ゲーム化実績", value=analysis.get("existing_game_history", ""), key="game_hist")
    analysis["existing_game_history"] = st.session_state.game_hist
    
    # Numeric Attributes
    st.subheader("コンテンツ特性スコア (1-5)")
    
    score_labels = {
        "world_scale": ("世界観の広さ", "1=閉じた空間 → 5=多元宇宙級"),
        "battle_weight": ("バトル・アクション要素", "1=皆無 → 5=主軸"),
        "character_volume": ("キャラクター資産の量", "1=少数精鋭 → 5=大量"),
        "character_diversity": ("キャラクターの多様性", "1=同質的 → 5=極めて多様"),
        "collection_affinity": ("収集要素との親和性", "1=低い → 5=非常に高い"),
        "emotional_depth": ("感情的・ストーリー的深み", "1=軽め → 5=非常に深い"),
        "humor_factor": ("コメディ・ユーモア要素", "1=シリアス → 5=コメディ主体"),
        "darkness_factor": ("ダーク・シリアス要素", "1=明るい → 5=非常にダーク"),
        "competition_element": ("競争・対戦要素", "1=なし → 5=主軸"),
        "cooperation_element": ("協力・チームワーク要素", "1=個人主義 → 5=チーム主体"),
        "exploration_element": ("探索・発見要素", "1=なし → 5=主軸"),
        "crafting_building": ("クラフト・建築との親和性", "1=なし → 5=非常に高い"),
        "music_rhythm_affinity": ("音楽・リズムとの親和性", "1=なし → 5=非常に高い"),
        "global_awareness": ("海外認知度", "1=国内のみ → 5=世界的"),
    }
    
    cols = st.columns(3)
    score_keys = list(score_labels.keys())
    for i, key in enumerate(score_keys):
        label, help_text = score_labels[key]
        with cols[i % 3]:
            val = analysis.get(key, 3)
            if isinstance(val, str):
                try:
                    val = int(val)
                except:
                    val = 3
            analysis[key] = st.slider(label, 1, 5, val, help=help_text, key=f"slider_{key}")
    
    # Story & Unique Elements
    st.subheader("特記事項")
    analysis["story_structure"] = st.text_input("ストーリー構造", value=analysis.get("story_structure", ""))
    analysis["unique_hook"] = st.text_area("ユニークな特徴・フック", value=analysis.get("unique_hook", ""), 
                                            help="このIPならではの、ゲーム化で活かせそうな独自要素")
    analysis["summary"] = st.text_area("IP概要", value=analysis.get("summary", ""))
    analysis["fan_spending_tendency"] = st.text_input("ファンの消費傾向", value=analysis.get("fan_spending_tendency", ""))
    
    st.session_state.ip_analysis = analysis
    
    # Confirm button
    st.divider()
    if st.button("この内容でジャンル推薦を実行", type="primary", use_container_width=True):
        st.session_state.analysis_confirmed = True

# --- Step 3: Genre Recommendation ---
if st.session_state.analysis_confirmed and st.session_state.ip_analysis:
    st.header("Step 3: ゲームジャンル推薦")
    
    if not st.session_state.recommendations:
        with st.spinner("最適なゲームジャンルを分析中..."):
            genre_db_summary = json.dumps(GENRE_DATABASE, ensure_ascii=False, indent=2)
            analysis_summary = json.dumps(st.session_state.ip_analysis, ensure_ascii=False, indent=2)
            
            user_prompt = f"""## 分析対象IP
{analysis_summary}

## 利用可能なゲームジャンルデータベース
{genre_db_summary}

上記のIP属性分析とジャンルデータベースに基づいて、このIPに最適なゲームジャンルを推薦してください。
データベースに含まれるジャンルを優先しつつ、データベース外のジャンルも必要であれば提案してください。

「企画の種」として、このIPの可能性を広げる提案をお願いします。"""
            
            result = call_claude(RECOMMEND_SYSTEM_PROMPT, user_prompt)
            
            if result.startswith("[ERROR]"):
                st.error(result)
            else:
                st.session_state.recommendations = result
    
    if st.session_state.recommendations:
        st.markdown(st.session_state.recommendations)
        
        # Export option
        st.divider()
        st.subheader("エクスポート")
        
        export_content = f"""# IP Game Fit Analyzer - 分析レポート
## 対象IP: {st.session_state.ip_analysis.get('ip_name', 'N/A')}
生成日: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## IP属性分析

{json.dumps(st.session_state.ip_analysis, ensure_ascii=False, indent=2)}

---

## ジャンル推薦結果

{st.session_state.recommendations}

---

※ 本レポートはAIによる分析結果であり、企画検討の参考資料としてご使用ください。
"""
        
        st.download_button(
            label="Markdownでダウンロード",
            data=export_content,
            file_name=f"ip_analysis_{st.session_state.ip_analysis.get('ip_name', 'report')}.md",
            mime="text/markdown",
            use_container_width=True
        )

# --- Footer ---
st.divider()
st.caption("IP Game Fit Analyzer v0.1 | KRAFTON Japan - Planning")
