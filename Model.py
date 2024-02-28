# import thư viện cần thiết
import pandas as pd
import numpy as np
import math
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier

# Đọc dữ liệu
data = pd.read_csv(".\\WineQT.csv")

# Quản lý dữ liệu

# Xóa cột Id không cần thiết trong việc phân tích và dự đoán
data = data.drop(columns='Id', axis=1)

# Xoá các dòng trùng lặp
data = data.drop_duplicates()

# Định nghĩa biến SO2 từ 2 biến total sulfur dioxide và free sulfur dioxide
data['SO2'] = data['total sulfur dioxide'] - data['free sulfur dioxide']

data = data.drop('total sulfur dioxide', axis=1)
data = data.drop('free sulfur dioxide', axis=1)

# Chuyển cột 'SO2' lên vị trí trước 'quality'
cols = list(data.columns)
cols.remove('SO2')
cols.insert(cols.index('quality'), 'SO2')
data = data[cols]

# Gom lại các điểm thành 3 phân loại
data.loc[(data['quality'] >= 3) & (data['quality'] <= 4), 'quality'] = 0
data.loc[(data['quality'] >= 5) & (data['quality'] <= 6), 'quality'] = 1
data.loc[(data['quality'] >= 7) & (data['quality'] <= 8), 'quality'] = 2

# Cân bằng dữ liệu

# Cân bằng dữ liệu nhóm thiểu số
os = RandomOverSampler(sampling_strategy={0: 842, 1: 842, 2: 842}, random_state = 42)
X = data.drop(['quality'], axis=1)
y = data['quality']
X_res,y_res = os.fit_resample(X,y)

# Tạo DataFrame từ X_over và y_over
data = pd.concat([pd.DataFrame(X_res), pd.DataFrame(y_res)], axis=1)

# Lấy danh sách tên cột
def split_data(dt):
  labels = list(dt.iloc[:,:-1].columns)

  # Tách tập dữ liệu thành train và test
  X_train, X_test, y_train, y_test = train_test_split(dt[labels], dt['quality'], test_size=0.2, random_state=42)

  # Chuẩn hóa dữ liệu
  sc = StandardScaler()
  X_train = sc.fit_transform(X_train)
  X_test = sc.transform(X_test)

  # Gán lại nhãn cho dữ liệu train và test
  X_train = pd.DataFrame(X_train, columns=labels)
  X_test = pd.DataFrame(X_test, columns=labels)

  return X_train, X_test, y_train, y_test

X_train, X_test, y_train, y_test = split_data(data)

# Lựa chọn biến quan trọng

# Tìm độ sâu tối ưu cho cây quyết định
dt = DecisionTreeClassifier(random_state=42)
n_max = int(math.log2(len(X_train)))
params = {'max_depth':[1,2,4,6,8,10,12,14,16,18,20,n_max]}
cv = GridSearchCV(dt, param_grid=params, scoring= 'accuracy', cv=4, return_train_score=True)
cv.fit(X_train,y_train)

depth = cv.best_params_['max_depth']

# Xử dụng mô hình để tìm biến quan trọng
dt = DecisionTreeClassifier(max_depth= depth, random_state=42)
dt.fit(X_train,y_train)
score = dt.feature_importances_

# Xóa 4 cột có độ quan trọng thấp nhất
sorted_indices = np.argsort(score)[:4]
lowest_columns = X.columns[sorted_indices]

for column in lowest_columns:
    del data[column]

# Chia tập dữ liệu train và test lần 2 (sau khi đã xóa 4 thuộc tính)
X_train, X_test, y_train, y_test = split_data(data)

# Mô hình logistic

# Xác định các thuộc tính đầu vào
features = list(data.iloc[:,:-1].columns)

# Tạo 64 mô hình nhị phân khác nhau
np.random.seed(10)
random_model = np.random.choice([0, 1], size=(64, 6))

# Loại bỏ các hàng có toàn giá trị 0
random_model = random_model[~np.all(random_model == 0, axis=1)]

# Xây dựng mô hình hồi quy logistic cho từng mã mô hình
accuracies = []
# Mã hóa lại các biến được chọn
for code in random_model:
    selected_features = [features[i] for i in range(6) if code[i] == 1]

    X_train_df = pd.DataFrame(X_train, columns=features)
    X_test_df = pd.DataFrame(X_test, columns=features)

    X_train_selected = X_train_df.loc[:, selected_features]
    X_test_selected = X_test_df.loc[:, selected_features]

    # Áp dụng mô hình Logistic
    model = LogisticRegression(multi_class='multinomial')
    model.fit(X_train_selected, y_train)

    # Dự doán và đánh giá độ chính xác accuracy
    y_pred = model.predict(X_test_selected)
    accuracy = accuracy_score(y_test, y_pred)

    # Lưu model và accuracy của 64 mô hình vào danh sách
    accuracies.append(accuracy)

# Chọn mô hình có độ chính xác cao nhất từ các mô hình cuối cùng
best_final_model_index = np.argmax(accuracies)

best_final_model_code = random_model[best_final_model_index]

variables = [features[i] for i in range(6) if best_final_model_code[i] == 1]
# print("Mô hình tốt nhất\n",variables)
# print("Accuracy: ",random_model[best_final_model_index])

# Thêm nhãn quality
variables.append('quality')
data = data.loc[:,variables]

# Lấy danh sách nhãn của 4 biến giải thích
labels = list(data.iloc[:,:-1].columns)

# Tách tập dữ liệu thành train và test
X_train, X_test, y_train, y_test = train_test_split(data[labels], data['quality'], test_size=0.2, random_state=42)

# Chuẩn hóa dữ liệu
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Lưu trình biến đổi
joblib.dump(sc, ".\\Model\\scaler.pkl")

# Mô hình MLP
# Xây dựng mô hình MLP
mlp = MLPClassifier(hidden_layer_sizes=(100, 100), activation='relu', max_iter = 1000, random_state=42)
# Huấn luyện mô hình
mlp.fit(X_train, y_train)

# Lưu model
joblib.dump(mlp, ".\\Model\\wine_model.pkl")