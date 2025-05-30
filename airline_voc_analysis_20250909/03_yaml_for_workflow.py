# Databricks notebook source
# MAGIC %md
# MAGIC # ワークフローの設定Yamlファイル作成
# MAGIC - ワークフローを一括設定するための設定内容をYamlファイルに出力し、Yaml設定内容を使ってワークフローを一括設定します  
# MAGIC - サーバレス or DBR 16.0ML以降
# MAGIC
# MAGIC やること
# MAGIC - 本ノートブックは手動実行専用です
# MAGIC - 本ノートブックを手動実行してください -> 同じディレクトリにworkflows.yamlファイルが自動作成されます
# MAGIC - workflows.yamlファイルを開いて、中身（Yaml文字列）をコピーし、ワークフローを「Yamlとして編集」で新規作成してください

# COMMAND ----------

# MAGIC %pip install pyyaml
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. カレントディレクトリ取得

# COMMAND ----------

import os

def get_parent_directory():
    # ノートブックのフルパスを取得
    notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    full_path = f"/Workspace/{notebook_path.lstrip('/')}"  # パスの正規化
    
    # 親ディレクトリを取得
    parent_dir = os.path.dirname(full_path)
    return parent_dir

# 実行例
current_dir = get_parent_directory()
print("現在のディレクトリ：")
print(f"{current_dir}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Workflow設定用のYamlファイルを作成
# MAGIC 次のセルを実行すると、同じディレクトリ内にworkflow.yamlというファイルができます  
# MAGIC workflowsを設定する際には、手動のほか、Yaml形式で一括設定できます

# COMMAND ----------

import yaml
from datetime import datetime

# ワークフロー定義のベース作成
def generate_workflow_yaml():
    workflow = {
        "resources": {
            "jobs": {
                f"{WORKFLOW_NAME}": {
                    "name": f"{WORKFLOW_NAME}",
                    "tasks": [
                        {
                            "task_key": "init_data",
                            "notebook_task": {
                                "notebook_path": f"{current_dir}/01_init_data",
                                "source": "WORKSPACE"
                            },
                        },
                        {
                            "task_key": "extract_categories",
                            "depends_on": [{"task_key": "init_data"}],
                            "notebook_task": {
                                "notebook_path": f"{current_dir}/02_extract_categories",
                                "source": "WORKSPACE"
                            },
                        },
                    ],
                    "queue": {"enabled": True},
                    "performance_target": "STANDARD",
                }
            }
        }
    }

    # YAMLファイル生成
    filename = f"workflows.yaml"    
    with open(filename, 'w') as file:
        yaml.dump(workflow, file, sort_keys=False, default_flow_style=False)
    
    return filename

# 関数実行
generated_file = generate_workflow_yaml()
print(f"YAMLファイルが生成されました: {generated_file}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. ワークフローを設定
# MAGIC step1. 同じディレクトリに作成された、`workflows.yaml`ファイルの中身をコピーしてください
# MAGIC <img src='https://github.com/komae5519pv/komae_dbdemos/blob/main/airline_voc_analysis_20250909/_manual/step1_copy_yaml.png?raw=true' width='88%'/>
# MAGIC
# MAGIC step2. ワークフロー -> 作成 -> ジョブ -> Yamlとして編集
# MAGIC <img src='https://github.com/komae5519pv/komae_dbdemos/blob/main/airline_voc_analysis_20250909/_manual/step2_edit_yaml.png?raw=true' width='88%'/>
# MAGIC
# MAGIC step3. 先ほどコピーした`workflows.yaml`ファイルの中身を貼り付けて保存してください
# MAGIC <img src='https://github.com/komae5519pv/komae_dbdemos/blob/main/airline_voc_analysis_20250909/_manual/step3_overwrite_yaml.png?raw=true' width='88%'/>
# MAGIC
# MAGIC step4. これでワークフローの設定が完了です
# MAGIC <img src='https://github.com/komae5519pv/komae_dbdemos/blob/main/airline_voc_analysis_20250909/_manual/step4_complete_workflows_setting.png?raw=true' width='88%'/>
