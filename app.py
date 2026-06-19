import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="株価データ取得ツール", page_icon="📈", layout="centered")

st.title("📈 楽天証券スクリーナー → 株価データ取得")
st.caption("楽天証券「Claude」スクリーナーのCSVをアップロードすると、直近180日の株価データを取得してダウンロードできます")

# ── CSV アップロード ──────────────────────────────────
uploaded = st.file_uploader("楽天証券のCSVファイルを選択", type=["csv"])

if uploaded:
    # 証券コード抽出
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

    # ── 実行ボタン ────────────────────────────────────
    if st.button("株価データを取得する", type="primary"):
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=int(days))).strftime("%Y-%m-%d")

        log = st.empty()
        progress = st.progress(0)
        all_data = []
        messages = []

        for i, (code, name) in enumerate(stocks):
            ticker = f"{code}.T"
            try:
                df = yf.download(ticker, start=start_date, end=end_date,
                                 progress=False, auto_adjust=True)
                if df.empty:
                    messages.append(f"⚠️  [{code}] {name}: データなし")
                else:
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
                    all_data.append(df)
                    messages.append(f"✅  [{code}] {name}: {len(df)}日分")
            except Exception as e:
                messages.append(f"❌  [{code}] {name}: エラー ({e})")

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
            st.caption("次のステップ：楽天CSVとこのCSVの両方をClaudeにアップロードして「チャート分析して」と送信")
