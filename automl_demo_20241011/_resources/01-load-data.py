# Databricks notebook source
dbutils.widgets.dropdown("reset_all_data", "false", ["true", "false"], "Reset all data")
reset_all_data = dbutils.widgets.get("reset_all_data") == "true"

# COMMAND ----------

# MAGIC %run ../config

# COMMAND ----------

# MAGIC %run ./00-global-setup-v2

# COMMAND ----------

# DBDemosのスキーマを設定
DBDemos.setup_schema(catalog, db, reset_all_data, volume_name)

# フォルダのパスを設定
folder = f"/Volumes/{catalog}/{db}/{volume_name}"

# データが不足しているかどうかをチェック
data_missing = DBDemos.is_any_folder_empty([folder+"/credit_bureau", folder+"/internalbanking/account", folder+"/fund_trans", folder+"/telco"])

# COMMAND ----------

# 必要なライブラリをインポート
# osとrequestsは使用されていないため、削除
import timeit
import time

# データをリセットするか、データが不足している場合に実行
if reset_all_data or data_missing:
  # データをリセットする場合
  if reset_all_data:
    # フォルダのパスが指定の形式であることを確認
    assert len(folder) > 15 and folder.startswith("/Volumes/")
    # フォルダを削除
    dbutils.fs.rm(folder, True)
  try:
    # クレジット局のデータをダウンロード
    DBDemos.download_file_from_git(folder+'/credit_bureau', "databricks-demos", "dbdemos-dataset", "/fsi/credit-decisioning/creditbureau")

    # ダウンロードしたCSVを読み込み、JSON形式で保存
    spark.read.csv(folder+'/credit_bureau/creditbureau.csv', header=True, inferSchema=True).write.format('json').option('header', 'true').mode('overwrite').save(folder+'/credit_bureau')   

    # 銀行口座データをダウンロード
    DBDemos.download_file_from_git(folder+'/internalbanking', "databricks-demos", "dbdemos-dataset", "/fsi/credit-decisioning/internalbanking")

    # ダウンロードしたCSVを読み込み、CSV形式で保存（口座、顧客、関係）
    spark.read.csv(folder+'/internalbanking/accounts.csv', header=True, inferSchema=True).write.format('csv').option('header', 'true').mode('overwrite').save(folder+'/internalbanking/account')
    spark.read.csv(folder+'/internalbanking/customer.csv', header=True, inferSchema=True).write.format('csv').option('header', 'true').mode('overwrite').save(folder+'/internalbanking/customer')
    spark.read.csv(folder+'/internalbanking/relationship.csv', header=True, inferSchema=True).write.format('csv').option('header', 'true').mode('overwrite').save(folder+'/internalbanking/relationship')

    # 資金移動データをダウンロード
    DBDemos.download_file_from_git(folder+'/fund_trans', "databricks-demos", "dbdemos-dataset", "/fsi/credit-decisioning/kafka/fund_trans/incoming-data-json-small")

    # 電話会社データをダウンロード
    DBDemos.download_file_from_git(folder+'/telco', "databricks-demos", "dbdemos-dataset", "/fsi/credit-decisioning/telcodata")

  except Exception as e: 
    # ダウンロード中にエラーが発生した場合、エラーメッセージを表示
    print(f"Error trying to download the file from the repo: {str(e)}.")

# COMMAND ----------

def save_features_def():
    features = """feature,definition
    sent_amt_avg_6m,Outgoing average transaction amount in last 6 months
    ratio_txn_amt_3m_12m,Ratio of total transaction amount between last 3 months and 12 months
    ratio_txn_amt_6m_12m,Ratio of total transaction amount between last 6 months and 12 months
    sent_amt_avg_12m,Outgoing average transaction amount in last 12 months
    dist_payer_cnt_12m,Distinct payer count in last 12 months
    tot_rel_bal,Total relationship balance
    revenue_tot,Total revenue
    rcvd_txn_amt_3m,Incoming transaction amount in last 3 months
    rcvd_amt_avg_3m,Incoming average transaction amount in last 3 months
    dist_payer_cnt_6m,Distinct payer count in last 6 months
    rcvd_txn_cnt_6m,Incoming transaction count in last 6 months
    tot_txn_amt_6m,Total transaction amount in last 6 months
    tot_txn_amt_3m,Total transaction amount in last 3 months
    balance_usd,Account balance in USD
    available_balance_usd,Available balance in USD
    sent_txn_amt_3m,Outgoing transaction amount in last 3 months
    sent_amt_avg_3m,Outgoing average transaction amount in last 3 months
    dist_payer_cnt_3m,Distinct payer count in last 3 months
    rcvd_txn_cnt_3m,Incoming transaction count in last 3 months
    overdraft_number,Overdraft count
    total_deposits_number,Total deposit count
    avg_balance,Customer account balance
    num_accs,Account count
    sent_txn_cnt_6m,Outgoing transaction count in last 6 months
    sent_txn_amt_6m,Outgoing transaction amount in last 6 months
    total_UT,Total Unit Trusts amount
    customer_revenue,Customer revenue
    education,Education level
    tenure_months,Banking tenure
    product_cnt,Product count
    avg_phone_bill_amt_lst12mo,Telco - Average phone bill amount in last 12 months
    dist_payee_cnt_12m,Distinct payee count in last 12 months
    rcvd_amt_avg_12m,Incoming average transaction amount in last 12 months
    dist_payee_cnt_6m,Distinct payee count in last 6 months
    marital_status,Marital status
    months_current_address,Months in current home address
    revenue_12m,Last 12 months revenue
    income_annual,Annual income
    tot_txn_cnt_3m,Total transaction count in last 3 months
    tot_txn_amt_12m,Total transaction amount in last 12 months
    tot_txn_cnt_12m,Total transaction count in last 12 months
    tot_txn_cnt_6m,Total transaction count in last 6 months
    total_deposits_amount,Total deposit amount
    total_equity_amount,Total equity amount
    tot_assets,Total assets
    overdraft_balance_amount,Overdraft balance amount
    pct_increase_annual_number_of_delays_last_3_year,Telco - Percentage increase in annual number of payment delays in last 3 years
    phone_bill_amt,Telco - Last phone bill amount
    dist_payee_cnt_3m,Distinct payee count in last 3 months
    sent_txn_cnt_3m,Outgoing transaction count in last 3 months
    rcvd_txn_cnt_12m,Incoming transaction count in last 12 months
    rcvd_txn_amt_12m,Incoming transaction amount in last 12 months
    sent_txn_cnt_12m,Outgoing transaction count in last 12 months
    sent_txn_amt_12m,Outgoing transaction amount in last 12 months
    is_pre_paid,Telco - Whether prepaid package or not
    number_payment_delays_last12mo,Telco - Number of payment delays in last 12 months
    rcvd_txn_amt_6m,Incoming transaction amount in last 6 months
    rcvd_amt_avg_6m,Incoming average transaction amount in last 6 months
    months_employment,Months in employment
    is_resident,Whether the customer is a resident
    age,Customer age"""

    # 文字列からDataFrameを作成し、Sparkテーブルとして保存
    from io import StringIO
    import pandas as pd
    # 文字列をStringIOに変換
    df = pd.read_csv(StringIO(features), sep=",", header=0)
    # Pandas DataFrameをSpark DataFrameに変換し、テーブルとして保存
    spark.createDataFrame(df).write.mode('overwrite').saveAsTable('feature_definitions')

# データをリセットするか、特徴量定義テーブルが存在しない場合に実行
if reset_all_data or not spark.catalog.tableExists('feature_definitions'):
    save_features_def()
