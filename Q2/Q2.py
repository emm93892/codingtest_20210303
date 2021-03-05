import pandas as pd

# log.csvのcolumnのindexを設定
datetime = 0
server_address = 1
response_result = 2

# N -> タイムアウトがN回以上続いたときに故障とみなす値
N = 5

# ファイルパスを設定
csv_file_path = '../log.csv'
result_path = 'Q2_Result.txt'

df = pd.read_csv(csv_file_path, sep=',')

with open(result_path, mode='w') as f:
    f.write('Server address,Time outed period\n')

    # ************* サーバの故障期間を算出する *************
    # 応答結果がタイムアウト(-)のときのdataframeのindexを取得
    timeout_index = df[df['Response_result'] == '-'].index.tolist()

    for i in range(len(timeout_index)):
        # timeouted_server_address -> タイムアウトしたサーバアドレスを格納
        timeouted_server_address = df.iat[timeout_index[i], server_address]

        # same_address_df -> タイムアウトしたときのみを抽出したdataframe
        same_address_df = df[df['Server_address'] == timeouted_server_address]

        # index -> タイムアウトした日時のindex
        index = same_address_df.index.get_loc(timeout_index[i])

        # 何回連続してタイムアウトしたかを計算
        # count -> 何回連続してタイムアウトしたかをカウント
        count = 0
        for j in range(len(same_address_df)):
            try:
                # same_address_df[index + j, response_result] -> j個先のResponse_resultの値
                # 基準の位置からj個先がタイムアウトし、基準の位置からすぐ下もタイムアウトしているときカウントに＋１
                if '-' == same_address_df.iat[index + j, response_result] == same_address_df.iat[index + 1, response_result]:
                    count += 1
            except IndexError:
                break

        # count >= N -> N回以上連続してタイムアウトになったときの処理を記述
        if count >= N and '-' != same_address_df.iat[index - 1, response_result]:
            # same_address_df.iat[index + N-1, datetime] -> 最後にタイムアウトした日時
            # same_address_df.iat[index, datetime] -> 最初にタイムアウトした日時
            timeouted_period = same_address_df.iat[index + count - 1, datetime] - same_address_df.iat[
                index, datetime]
            # .txtに出力する処理
            try:
                # format(str, '0>14') -> 日時を０で埋める (YYYYMMDDhhmmssの形式にする)
                f.write(timeouted_server_address + ',')
                f.write(format(timeouted_period, '0>14') + '\n')
            except NameError:
                break

    # ***************************************
