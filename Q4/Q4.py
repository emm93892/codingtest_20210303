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
csv_file_path = '../log.csv'
result_path = 'Q4_Result.txt'

df = pd.read_csv(csv_file_path, sep=',')

with open(result_path, mode='w') as f:
    f.write('Server address,Time outed period,Status\n')

    # ************* *1.サーバの故障期間を算出する *************
    # 応答結果がタイムアウト(-)のときのdataframeのindexを取得
    timeout_index = df[df['Response_result'] == '-'].index.tolist()

    # breakdown_address_list -> 故障(N回以上連続でタイムアウト)したアドレスを入れるリスト
    breakdown_address_list = []

    # サーバアドレスを重複しないようにしたdataframeを取得
    unique_server_address_df = df.drop_duplicates(['Server_address'])
    unique_server_address_list = unique_server_address_df['Server_address'].values.tolist()

    for i in range(len(timeout_index)):
        # timeouted_server_address -> タイムアウトしたサーバアドレスを一つずつ格納
        timeouted_server_address = df.iat[timeout_index[i], server_address]

        # same_address_df -> 元のdataframeから タイムアウトしたサーバアドレスのみを抽出したdataframe
        same_address_df = df[df['Server_address'] == timeouted_server_address]

        # index -> タイムアウトした日時のindex
        index = same_address_df.index.get_loc(timeout_index[i])

        count = 0

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

            # ip_address -> タイムアウトしたIPアドレス
            ip_address = same_address_df.iat[index, server_address]
            breakdown_address_list.append(ip_address)

            # .txtに出力する処理
            try:
                # format(str, '0>14') -> 日時を０で埋める (YYYYMMDDhhmmssの形式にする)
                f.write(timeouted_server_address + ',')
                f.write(format(timeouted_period, '0>14') + '\n')
            except NameError:
                break

    # ***************************************

    # ************* 2. サブネット毎にネットワークの故障期間を算出する *************
    # breakdownしたサーバアドレスを一意にする
    breakdown_address_list = sorted(set(breakdown_address_list), key=breakdown_address_list.index)

    breakdown_subnet_list = []

    # サブネットマスクの値により、取得するIPアドレスのネットワーク部の値を変更する処理
    for ip_address in breakdown_address_list:
        # IPアドレスのサブネットマスク部分を取得 16, 24
        subnet_mask = ip_address[ip_address.find('/') + 1:ip_address.find('/') + 3]
        # サブネットマスクの値により、場合分けする処理
        if int(subnet_mask) <= 8:
            # IPアドレスの上位三桁部分を取得 10 , 192
            network_part = ip_address[:ip_address.find('.')]
        elif int(subnet_mask) <= 16:
            # IPアドレスの上位六桁部分を取得
            network_part = ip_address[:ip_address.find('.', ip_address.find('.')+1)]
        elif int(subnet_mask) <= 32:
            # IPアドレスの上位九桁部分を取得
            network_part = ip_address[:ip_address.find('.', ip_address.find('.', ip_address.find('.')+1)+1)]

        # 元のdataframeからIPアドレスのネットワーク部分とサブネットマスクが共通するものを抽出したdataframe
        same_subnet_df = df[df['Server_address'].str.startswith(network_part) & df['Server_address'].str.endswith(subnet_mask)]

        # 何回連続してタイムアウトしたかを計算
        # count -> 何回連続してタイムアウトしたかをカウント
        count = 0
        for j in range(len(same_subnet_df)):
            try:
                # same_address_df[index + j, response_result] -> j個先のResponse_resultの値
                # 基準の位置からj個先がタイムアウトし、基準の位置からすぐ下もタイムアウトしているときカウントに＋１
                if '-' == same_subnet_df.iat[index + j, response_result] == same_subnet_df.iat[index + 1, response_result]:
                    count += 1
            except IndexError:
                break

        # count >= N -> N回以上連続してタイムアウトになったときの処理を記述
        if count >= N and '-' != same_subnet_df.iat[index - 1, response_result]:
            # same_subnet_df.iat[index + N-1, datetime] -> 最後にタイムアウトした日時
            # same_subnet_df.iat[index, datetime] -> 最初にタイムアウトした日時
            timeouted_period = same_subnet_df.iat[index + count - 1, datetime] - same_subnet_df.iat[
                index, datetime]

        # b_count, u_count
        # -> breakdown_address_list(b), unique_server_address_list(u)と、
        #    IPアドレスのネットワーク部とサブネットマスクの比較して一致した時+1
        b_count = 0
        u_count = 0
        for j in range(len(breakdown_address_list)):
            if breakdown_address_list[j].startswith(network_part) and breakdown_address_list[j].endswith(subnet_mask):
                b_count += 1

        for j in range(len(unique_server_address_list)):
            if unique_server_address_list[j].startswith(network_part) and unique_server_address_list[j].endswith(subnet_mask):
                u_count += 1

        if b_count == u_count:
            breakdown_subnet_list.append([network_part, subnet_mask])

    # 2次元配列の重複を削除
    breakdown_subnet_list = list(map(list, set(map(tuple, breakdown_subnet_list))))

    # サブネット毎の故障期間を.txtに出力
    for i in range(len(breakdown_subnet_list)):
        f.write('Network address:' + breakdown_subnet_list[i][0]  + ' ')
        f.write('Subnet mask:' + breakdown_subnet_list[i][1] + ',')
        f.write(format(timeouted_period, '0>14') + ',')
        f.write('subnet breakdown\n')

    # ***************************************

    # ************* 3.サーバの過負荷期間を算出する *************
    for i in range(len(unique_server_address_df)):

        # サーバアドレス毎のdataframeを取得
        # unique_server_address_df.iat[i, server_address]] -> サーバアドレスが重複していないdataframeのi行目のServer_addressの値
        unique_df = df[df['Server_address'] == unique_server_address_df.iat[i, server_address]]

        # response_time_sum -> 応答時間の合計値
        response_time_sum = 0
        for j in range(m):
            # Response_resultが -(タイムアウト) のとき 値を0として計算する
            if unique_df.iat[-1 - j, response_result] == '-':
                unique_df.iat[-1 - j, response_result] = 0
            response_time_sum += int(unique_df.iat[-1 - j, response_result])
        # average_response_time -> 平均応答時間
        average_response_time = response_time_sum / m

        # 平均応答時間がtミリ秒を超えたとき Q3_Result.txtに書き込む
        if average_response_time >= t:
            f.write(unique_server_address_df.iat[i, server_address] + ',')
            f.write(str(average_response_time) + ',')
            f.write('overload\n')

    # ***************************************
