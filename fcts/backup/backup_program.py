# 2.1.2 Read Data
def dataRead(user_id):
    file = open("./data/" + str(user_id) + ".txt", "r+")
    if file != None:
        return file.read()
    else:
        return "0"
    file.close()


def dataWrite(user_id, value):
    file = open("./data/" + str(user_id) + ".txt", "w+")
    if file == None:
        file.write("0")
    file.write(value)
    file.close()

# 2.2.6. Save Rankings
def rankList():

    path = "./data"
    file_list = os.listdir(path)

    rank_list = []

    for a in file_list:
        user_id = int(a.split(".txt")[0])
        rank_list.append(user_id)

    return rank_list

if message.content.startswith("88888"):

        count = 1
        testarr = rankList()
        testarr.sort()
        for user_id in testarr:
            try:
                user = await client.fetch_user(user_id)
                print("`{}/{}` Id:{} 테스트 성공!".format(count, len(rankList()),
                                                     user_id))
            except:
                print("`{}/{}` :x: Id:{} 는 올바른 데이터가 아닙니다!".format(
                    count, len(rankList()), user_id))
            count += 1

    if message.content.startswith("99999"):
        print("데이터 백업을 시작합니다!")

        print("파일 불어오는 중...")

        path = "./data"
        file_list = os.listdir(path)

        user_list = []

        for a in file_list:
            user_id = int(a.split(".txt")[0])
            print(user_id)
            user_list.append(user_id)

        print("파일 불러오기 완료 총 {}개".format(len(user_list)))

        print("초기화 시작!")
        count = 0
        for u in user_list:
            if not x.checkId(u):
                try:
                    temp = await client.fetch_user(u)
                    name = temp.name
                    x.signUp(u, name, 0, 0)
                except:
                    pass
            count += 1
            print("{}/{} complete".format(count, len(user_list)))

        print("끝")

if message.content.startswith("77777"):
        print("데이터 백업을 시작합니다!")

        print("파일 불어오는 중...")

        path = "./data"
        file_list = os.listdir(path)

        user_list = []

        for a in file_list:
            user_id = int(a.split(".txt")[0])
            print(user_id)
            user_list.append(user_id)

        print("파일 불러오기 완료 총 {}개".format(len(user_list)))

        print("경험치 시작!")
        count = 0
        for u in user_list:
            print(u)
            xp_gain = int(dataRead(u))
            print(xp_gain)
            xp = x.dataRead(u, 'xp')
            print(xp)
            x.dataWrite(u, 'xp', xp + xp_gain)
            print(x.dataRead(u, 'xp'))
            count += 1
            print("{}/{} complete".format(count, len(user_list)))

        print("끝")

    # 3.3.97. Data Recovery

    if message.content.startswith("77777"):
        print("데이터 백업을 시작합니다!")

        print("파일 불어오는 중...")

        path = "./data"
        file_list = os.listdir(path)

        user_list = []

        for a in file_list:
            user_id = int(a.split(".txt")[0])
            print(user_id)
            user_list.append(user_id)

        print("파일 불러오기 완료 총 {}개".format(len(user_list)))

        print("저장소 시작!")
        count = 0
        for u in user_list:
            try:
                temp = storageRead(u).split('/')
                temp = temp[1:]
                new = ''.join(temp)
                print(new)
                x.dataWrite(u, 'storage', new)
                print(x.dataRead(u, 'storage'))
            except:
                pass
            count += 1
            print("{}/{} complete".format(count, len(user_list)))

        print("끝")

# 3.4. 기타
def fixData():
    temp = []
    loadFile()
    max = ws.max_row
    for row in range(2, max + 2):
        try:
            key = ws.cell(row=row, column=c_id).value
            data = ws.cell(row=row, column=c_storage).value
            temp.append([key, data])
            print([key, data])
        except:
            pass

    for row in range(2, max + 2):
        try:
            wst.cell(row=row, column=1).value = temp[row - 2][0]
            for i in range(0, 256):
                try:
                    wst.cell(row=row,
                             column=i + 2).value = int(temp[row - 2][1][i])
                except:
                    wst.cell(row=row, column=i + 2).value = 0
            print('dONE')
        except:
            wst.cell(row=row, column=1).value = temp[row - 2][0]
            wst.cell(row=row, column=2).value = 1
            for i in range(1, 256):
                wst.cell(row=row, column=i + 2).value = 0

            print('PASS')

    for row in range(2, max + 2):
        ws.cell(row=row, column=c_storage).value = int(row)

    saveFile()