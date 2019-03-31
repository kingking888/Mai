from datetime import datetime

class Item(dict):
    '''
    保存页面采集到的字段
    '''
    batchId = 1
    collectionName = 'test'

    @property
    def data(self):
        data = dict(self)
        data['batchId'] = self.batchId
        data['createTime'] = datetime.now().strftime('%Y-%m-%d %X')
        return data

    @property
    def collection(self):
        return self.collectionName

    def __str__(self):
        return str(self.data)

if __name__ == "__main__":
    persion = Item()
    persion['name'] = 'Tom'
    persion['age'] = 18
    print(persion.data)
    print()
    print(persion.collection)