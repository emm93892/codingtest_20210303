import pandas as pd

# log.csvのcolumnのindexを設定
datetime = 0
server_address = 1
response_result = 2

# ファイルパスを設定
csv_file_path = 'log.csv'
result_path = 'Q1_Result.txt'

df = pd.read_csv(csv_file_path, sep=',')

# 応答結果がタイムアウト(-)のときのdataframeのindexを取得
timeout_index = df[df['Response_result'] == '-'].index.tolist()

with open(result_path, mode='w') as f:
    f.write('Server address,Time outed period\n')

    for i in range(len(timeout_index)):
        # timeouted_server_address -> タイムアウトしたサーバアドレスを格納
        timeouted_server_address = df.iat[timeout_index[i], server_address]

        #　same_address_df -> タイムアウトしたサーバアドレスのみのdataframeを抽出したdataframe
        same_address_df = df[df['Server_address'] == timeouted_server_address]

        # index -> タイムアウトした日時のindex
        index = same_address_df.index.get_loc(timeout_index[i])

        #same_address_df.iat[index + 1, datetime] ->  故障した日時の次の日時
        #same_address_df.iat[index, datetime] -> 故障したときの日時
        timeouted_period = same_address_df.iat[index + 1, datetime] - same_address_df.iat[index, datetime]

        #print(format(str, '0>14')) #日時を０で埋める (YYYYMMDDhhmmssの形式にする)
        f.write(timeouted_server_address + ',')
        f.write(format(timeouted_period, '0>14') + '\n')
