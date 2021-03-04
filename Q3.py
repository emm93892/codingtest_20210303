import pandas as pd

# log.csvのcolumnのindexを設定
datetime = 0
server_address = 1
response_result = 2

# N -> タイムアウトがN回以上続いたときに故障とみなす値
N = 5
# m -> 直近m回の値
m = 5
# t -> 平均応答時間がtミリ秒を超えたとき過負荷状態とするときの値
t = 500

# ファイルパスを設定
csv_file_path = 'log.csv'
result_path = 'Q3_Result.txt'

df = pd.read_csv(csv_file_path, sep=',')

with open(result_path, mode='w') as f:
    f.write('Server address,Time outed period,Status\n')

    # 1.サーバの故障期間を算出する

    # 応答結果がタイムアウト(-)のときのdataframeのindexを取得
    timeout_index = df[df['Response_result'] == '-'].index.tolist()
    for i in range(len(timeout_index)):
        # timeouted_server_address -> タイムアウトしたサーバアドレスを一つずつ格納
        timeouted_server_address = df.iat[timeout_index[i], server_address]

        # same_address_df -> タイムアウトしたときのみを抽出したdataframe
        same_address_df = df[df['Server_address'] == timeouted_server_address]

        # index -> タイムアウトした日時のindex
        index = same_address_df.index.get_loc(timeout_index[i])

        count = 0
        for j in range(N):
            try:
                # same_address_df[index + j, response_result] -> j個先のResponse_resultの値
                if '-' == same_address_df.iat[index + j, response_result]:
                    count += 1
                # count == N -> N個タイムアウトになったときの処理
                if count == N:
                    # same_address_df.iat[index + N-1, datetime] -> 故障した日時の次の日時
                    # same_address_df.iat[index, datetime] -> 故障したときの日時
                    timeouted_period = same_address_df.iat[index + N - 1, datetime] - same_address_df.iat[
                        index, datetime]

                    # .txtに書き込む処理
                    try:
                        # format(str, '0>14') -> 日時を０で埋める (YYYYMMDDhhmmssの形式にする)
                        f.write(timeouted_server_address + ',')
                        f.write(format(timeouted_period, '0>14') + ',')
                        f.write('breakdown\n')
                    except NameError:
                        break
                    break
            except IndexError:
                break

    # 2.サーバの過負荷期間を算出する
    # サーバアドレスを重複しないように取得
    unique_server_address_df = df.drop_duplicates(['Server_address'])

    for i in range(len(unique_server_address_df)):

        # サーバアドレス毎のdataframeを取得
        # unique_server_address_df.iat[i, server_address]] -> サーバアドレスが重複していないdataframeのi行目のServer_addressの値
        unique_df = df[df['Server_address'] == unique_server_address_df.iat[i, server_address]]

        # response_time_sum -> 応答時間の合計値
        response_time_sum = 0
        for j in range(m):
            # Response_resultが - のときは値を0として計算する
            if unique_df.iat[-1 - j, response_result] == '-':
                unique_df.iat[-1 - j, response_result] = 0
            response_time_sum += int(unique_df.iat[-1 - j, response_result])
        # average_response_time -> 平均応答時間
        average_response_time = response_time_sum / m

        # 平均応答時間 >= t のとき Q3_Result.txtに書き込む
        if average_response_time >= t:
            f.write(unique_server_address_df.iat[i, server_address] + ',')
            f.write(str(average_response_time) + ',')
            f.write('overload\n')
