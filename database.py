import config

# to do: handle errors with db
def already_exists(col_name, doc_id):
    return config.db[col_name].count_documents({"sofaId": doc_id}, limit = 1)