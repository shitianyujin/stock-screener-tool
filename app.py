import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import io
import time

st.set_page_config(page_title="株価データ取得ツール", page_icon="📈", layout="centered")

st.title("📈 日本株 株価データ取得ツール")
st.caption("1列目に証券コード（4桁）、2列目に銘柄名が含まれるCSVをアップロードすると、指定期間の株価データ（OHLCV）を取得してダウンロードできます")

with st.expander("💡 使い方・使用例"):
    st.markdown("""
    **対応CSVフォーマット**
    - 1列目：4桁の証券コード
    - 2列目：銘柄名
    - 楽天証券・SBI証券などのスクリーナーCSV出力がそのまま使えます

    **楽天証券での手順**
    1. スクリーナーで条件を設定して検索
    2. 「CSV出力」ボタンでダウンロード
    3. このツールにアップロード
    4. 取得期間を設定して「株価データを取得する」をクリック
    5. 出力CSVをダウンロード

    **取得期間について**
    75日移動平均線の計算には最低180日分のデータが必要です（デフォルト値推奨）
    """)

# ── CSV アップロード ──────────────────────────────────
uploaded = st.file_uploader("CSVファイルを選択（1列目：証券コード、2列目：銘柄名）", type=["csv"])

if uploaded:
    def load_rakuten_csv(file):
        for enc in ["utf-8-sig", "shift-jis", "cp932"]:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=enc)
                return df
            except:
                continue
        return None

    df_screen = load_rakuten_csv(uploaded)
    if df_screen is None:
        st.error("CSVの読み込みに失敗しました")
        st.stop()

    stocks = list(zip(
        df_screen.iloc[:, 0].astype(str).str.zfill(4).str.strip(),
        df_screen.iloc[:, 1].astype(str).str.strip()
    ))

    st.success(f"{len(stocks)}銘柄を検出しました")
    st.write(", ".join([f"{c} {n}" for c, n in stocks]))

    # ── 取得期間入力 ──────────────────────────────────
    st.divider()
    days = st.number_input(
        "取得期間（日数）",
        min_value=30, max_value=365, value=180, step=10,
        help="直近何日分の株価データを取得するか指定します。75MA計算には最低180日推奨。"
    )

    # ── 株価取得関数（リトライあり）────────────────────
    def fetch_with_retry(code, name, start_date, end_date, max_retries=3, wait_sec=3):
        ticker = f"{code}.T"
        for attempt in range(1, max_retries + 1):
            try:
                df = yf.download(ticker, start=start_date, end=end_date,
                                 progress=False, auto_adjust=True)
                if df.empty:
                    if attempt < max_retries:
                        time.sleep(wait_sec)
                        continue
                    return None, "データなし"

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.reset_index()
                df["Code"] = code
                df["Name"] = name
                df = df.rename(columns={
                    "Date": "日付", "Open": "始値", "High": "高値",
                    "Low": "安値", "Close": "終値", "Volume": "出来高"
                })
                df["日付"] = pd.to_datetime(df["日付"]).dt.strftime("%Y-%m-%d")
                df = df[["Code", "Name", "日付", "始値", "高値", "安値", "終値", "出来高"]]
                for col in ["始値", "高値", "安値", "終値"]:
                    df[col] = df[col].round(1)
                df["出来高"] = df["出来高"].astype(int)
                return df, None

            except Exception as e:
                if attempt < max_retries:
                    time.sleep(wait_sec)
                else:
                    return None, str(e)
        return None, "取得失敗"

    # ── 実行ボタン ────────────────────────────────────
    if st.button("株価データを取得する", type="primary"):
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=int(days))).strftime("%Y-%m-%d")

        log = st.empty()
        progress = st.progress(0)
        all_data = []
        messages = []

        for i, (code, name) in enumerate(stocks):
            messages.append(f"⏳  [{code}] {name}: 取得中...")
            log.text("\n".join(messages))

            df, error = fetch_with_retry(code, name, start_date, end_date)
            messages[-1] = (
                f"✅  [{code}] {name}: {len(df)}日分"
                if df is not None
                else f"❌  [{code}] {name}: {error}"
            )
            if df is not None:
                all_data.append(df)

            progress.progress((i + 1) / len(stocks))
            log.text("\n".join(messages))

        if not all_data:
            st.error("取得できた銘柄がありませんでした")
        else:
            result = pd.concat(all_data, ignore_index=True)
            today_str = datetime.today().strftime("%Y%m%d")
            output_filename = f"chart_data_{today_str}.csv"
            csv_bytes = result.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

            st.success(f"完了！ {result['Code'].nunique()}銘柄 / {len(result)}行")
            st.download_button(
                label=f"📥 {output_filename} をダウンロード",
                data=csv_bytes,
                file_name=output_filename,
                mime="text/csv",
                type="primary"
            )
            st.caption("次のステップ：元のCSVとこのCSVの両方をClaudeにアップロードして「チャート分析して」と送信")

# ── 注意書き ──────────────────────────────────────────
st.divider()
st.caption(
    "⚠️ 本ツールはyfinance（Yahoo Finance非公式API）を使用しています。"
    "データの正確性は保証されません。投資判断は必ずご自身の責任で行ってください。"
    "またYahoo Finance側の制限により、データ取得に失敗する場合があります（リトライを最大3回実施します）。"
)
