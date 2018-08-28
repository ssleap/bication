import surprise
import pandas as pd
from surprise.model_selection import KFold
from surprise import Reader, Dataset
import pandas as pd
import numpy as np
from surprise import SVD, evaluate
from surprise import NMF, KNNBasic

# user table to pandas

class Recommender(RDBConnect):
    def __init__(self):
        super(Recommender, self).__init__()

        self.cur.execute("""select * from user""")
        result = self.cur.fetchall()
        self.data_user = pd.DataFrame(result)
        self.data_user.columns = ['user_id', 'email', 'password', 'age', 'sex', 'phone_num']

        # rate table to pandas
        cur.execute("""select * from rate""")
        result = cur.fetchall()
        self.data_rate = pd.DataFrame(result)
        # score는 최종 여정에 대한 평가고...
        # 리뷰 스코어랑 별점 스코어는 장소에 대한 스코어
        self.data_rate.columns = ['rate_id', 'user_id', 'place_id', 'date', 'score', 'review']

        # item table to pandas
        result = self.db_conn.get_item_all()
        self.data_item = pd.DataFrame(result)

    def get_data(self, input_key):
        if input_key == "data_user":
            return self.data_user
        elif input_key == "data_rate":
            return self.data_rate
        elif input_key == "data_item":
            return self.data_item

    def make_df(self):

        data = self.data_rate
        del data["date"]

        data = pd.merge(data, self.data_item, left_on = 'place_id', right_on = 'cat_id')
        del data["cat_id"]
        del data["cat_name"]
        del data["pop_tags"]

        data_list = []
        for row in data["items"]:
            data_list.append(row)

        data_item = pd.DataFrame(data_list)

        new_data = pd.merge(data, data_item, left_on = data.index, right_on = data_item.index)

        del new_data["items"]
        del new_data["key_0"]
        del new_data["addr"]
        del new_data["call"]
        del new_data["image"]
        del new_data["title"]
        del new_data["text"]

        return new_data

    def model(self, alg_key):

        reader = Reader(rating_scale = (1, 5))

        data_result = Dataset.load_from_df(self.make_df()[['user_id', 'place_id', 'score']], reader)

        # split data into 5 folds

        data_result.split(n_folds=10)

        # evaluation

        if alg_key.lower() == "svd":
            alg = SVD()
        elif alg_key.lower() == "knn":
            alg = KNNBasic()
        elif alg_key.lower() == "nmf":
            alg = NMF()

        evaluate(alg, data_result, measures=['RMSE', 'MAE'])

        # prediction
        # user_0	smallShop_5645	2
        test_user = 'user_1'
        test_id = 'smallShop_7089'
        real_score = 4

        trainset = data_result.build_full_trainset()

        alg.train(trainset)
        print(alg.predict(test_user, test_id, real_score))


# bsl_options = {
#     'method':'als',
#     'n_epochs':5,
#     'reg_u':12,
#     'reg_i':5
# }
# algo = surprise.BaselineOnly(bsl_options = bsl_options)

# np.random.seed(0)
# acc = np.zeros(3)
# cv = KFold(3)
# for i, (trainset, testset) in enumerate(cv.split(data)):
#     algo.fit(trainset)
#     predictions = algo.test(testset)
#     acc[i] = surprise.accuracy.rmse(predictions, verbose=True)
# acc.mean()
