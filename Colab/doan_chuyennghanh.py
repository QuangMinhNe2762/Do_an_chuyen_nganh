# -*- coding: utf-8 -*-
"""DoAn_ChuyenNghanh.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XBVaGr7dJ0c2vShF-MZ4--TSa_GW5nSq
"""

# import thư viện cần thiết
import pandas as pd
import numpy as np
import math
import keras
import joblib
import seaborn as sns
import tensorflow as tf
from keras import layers
import matplotlib.pyplot as plt
from google.colab import files
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.neural_network import MLPClassifier
from keras.layers import Dense
from keras.models import Sequential
from sklearn.metrics import mean_squared_error

# Đọc dữ liệu
data = pd.read_csv("WineQT.csv")

# Xem 5 dòng dữ liệu đầu tiên
data.head(5)

# Xem thông tin tập dữ liệu
data.info()

# Xem tóm tắt thống kê dữ liệu ở dạng chiều ngang
data.describe().T

"""# Trực quan dữ liệu"""

# Biểu đồ thống kê tần số xuất hiện trên cột quality
def visualize_quality():
  target = data['quality']
  sns.countplot(x = target, palette= 'winter', order = target.value_counts().index)
  plt.xlabel('Biểu đồ thống kê tần số trên cột Quality')

  df = target.value_counts().values
  for i in range(len(target.value_counts().values)):
    plt.text(x = i,y = df[i]+2,s = df[i],size = 9, ha='center', va='bottom')

visualize_quality()

# Nhận xét
# Có thể thấy các nhãn 3,4,8 chỉ chiếm khoảng 6% trong tập dữ liệu => nhãn hiếm.
# Và phần lớn các nhãn là 5 và 6 (khoảng 80%) => mất cân bằng.

# Biểu đồ histogram và boxplot cho các biến giải thích
def plot_num_dist(data, target):

    plt.figure(figsize=(14, 45))

    for index, feature in enumerate(data.columns):
        mean = data[feature].mean()
        std = data[feature].std()

        plt.subplot(11, 2, index * 2 + 1)
        sns.histplot(data=data, x=feature, kde=True, color='#8ECDDD')
        plt.xlabel(feature, fontsize=16)
        plt.ylabel('')

        plt.subplot(11, 2, index * 2 + 2)
        sns.boxplot(data=data[feature])#(data=pd.concat([data, target], axis=1), x=target, y=feature, palette='Blues_r')
        plt.xlabel(feature, fontsize=16)
        plt.ylabel('')
        plt.grid(True)

        sns.despine(right=True, top=True)

    plt.tight_layout()
    plt.show()

plot_num_dist(data.iloc[:,:-2], data['quality'])

# Nhận xét
# Dữ liệu được phân phối đa phần lệch phải. Và có nhiều giá trị ngoại lai có trong tập dữ liệu.

# Tính ma trận tương quan
correlation_matrix = data.corr()

# Ma trận tương quan
plt.figure(figsize=(15,8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5)

# Nhận xét
# total sulphur dioxide và free sulphur dioxide có mối tương quan cao.
# Trừ: Nếu quan tâm đến lượng sulfur dioxide đã kết hợp trong mẫu rượu và muốn đo lường mức độ tồn tại của sulfur dioxide đã kết hợp độc lập với lượng sulfur dioxide tự do. Cột mới sẽ biểu thị lượng sulfur dioxide đã kết hợp trong mẫu rượu.
# Cộng: Nếu quan tâm đến tổng lượng sulfur dioxide trong mẫu rượu, bao gồm cả lượng sulfur dioxide tự do và lượng sulfur dioxide đã kết hợp.

# fixed acidity, pH và citric acid có mối tương quan cao.
# fixed acidity và density có mối tương quan dương cao.
# alcohol và density cũng có mối tương quan cao.

"""# Quản lý dữ liệu"""

# Xóa cột Id không cần thiết trong việc phân tích và dự đoán
data = data.drop(columns='Id', axis=1)

data.info()

# Kiểm tra giá trị thiếu
data.isnull().sum()

# Hiển thị các dòng trùng lặp
duplicate_rows = data[data.duplicated()]
print("Số lượng dữ liệu bị trùng lặp: ",data.duplicated().sum())
print("\n")
duplicate_rows

# Xoá các dòng trùng lặp
data = data.drop_duplicates()
print("Số lượng dữ liệu bị trùng lặp: ",data.duplicated().sum())

# Định nghĩa biến SO2 từ 2 biến total sulfur dioxide và free sulfur dioxide
data['SO2'] = data['total sulfur dioxide'] - data['free sulfur dioxide']

data = data.drop('total sulfur dioxide', axis=1)
data = data.drop('free sulfur dioxide', axis=1)

# Chuyển cột 'SO2' lên vị trí trước 'quality'
cols = list(data.columns)
cols.remove('SO2')
cols.insert(cols.index('quality'), 'SO2')
data = data[cols]

data.info()

# Gom lại các điểm thành 3 phân loại
data.loc[(data['quality'] >= 3) & (data['quality'] <= 4), 'quality'] = 0
data.loc[(data['quality'] >= 5) & (data['quality'] <= 6), 'quality'] = 1
data.loc[(data['quality'] >= 7) & (data['quality'] <= 8), 'quality'] = 2

visualize_quality()

"""# Cân bằng dữ liệu"""

# Cân bằng dữ liệu nhóm thiểu số
os = RandomOverSampler(sampling_strategy={0: 842, 1: 842, 2: 842}, random_state = 42)
X = data.drop(['quality'], axis=1)
y = data['quality']
X_res,y_res = os.fit_resample(X,y)

# Tạo DataFrame từ X_over và y_over
data = pd.concat([pd.DataFrame(X_res), pd.DataFrame(y_res)], axis=1)

visualize_quality()

data.info()

# # Lưu DataFrame thành file CSV
# data.to_csv('Clean_WineQT.csv', index=False)
# files.download('Clean_WineQT.csv')

"""# Chia dữ liệu train và test"""

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

"""# Lựa chọn biến quan trọng"""

# Tìm độ sâu tối ưu cho cây quyết định
dt = DecisionTreeClassifier(random_state=42)
n_max = int(math.log2(len(X_train)))
params = {'max_depth':[1,2,4,6,8,10,12,14,16,18,20,n_max]}
cv = GridSearchCV(dt, param_grid=params, scoring= 'accuracy', cv=4, return_train_score=True)
cv.fit(X_train,y_train)

depth = cv.best_params_['max_depth']
depth

# Xử dụng mô hình để tìm biến quan trọng
dt = DecisionTreeClassifier(max_depth= depth, random_state=42)
dt.fit(X_train,y_train)
score = dt.feature_importances_
# Hiển thị cột của từng độ quan trọng
for feature, importance in zip(X.columns, score):
    print(f'Cột {feature}: {importance}')

# Trực quan hóa độ quan trọng của các cột
indices = np.argsort(score)[::-1]
sorted_features = [X_train.columns[i] for i in indices]
sorted_importances = score[indices]

plt.figure(figsize=(10, 6))
plt.bar(range(len(sorted_importances)), sorted_importances, align='center')
plt.xticks(range(len(sorted_importances)), sorted_features, rotation=90)
plt.xlabel('Cột')
plt.ylabel('Độ quan trọng')
plt.title('Độ quan trọng của các cột')
plt.tight_layout()
plt.show()

# Xóa 4 cột có độ quan trọng thấp nhất
sorted_indices = np.argsort(score)[:4]
lowest_columns = X.columns[sorted_indices]

for column in lowest_columns:
    del data[column]

data.info()

data.head()

# Chia tập dữ liệu train và test lần 2 (sau khi đã xóa 4 thuộc tính)
X_train, X_test, y_train, y_test = split_data(data)

"""# Mô hình logistic"""

# Xác định các thuộc tính đầu vào
features = list(data.iloc[:,:-1].columns)

# Tạo 64 mô hình nhị phân khác nhau
np.random.seed(10)
random_model = np.random.choice([0, 1], size=(64, 6))

# Loại bỏ các hàng có toàn giá trị 0
random_model = random_model[~np.all(random_model == 0, axis=1)]

random_model

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
print("Mô hình tốt nhất\n",variables)
print("Accuracy: ",random_model[best_final_model_index])

# Thêm cột quality
variables.append('quality')
data = data.loc[:,variables]

data.head()

# Lấy danh sách tên cột của 4 biến giải thích
labels = list(data.iloc[:,:-1].columns)

# Tách tập dữ liệu thành train và test
X_train, X_test, y_train, y_test = train_test_split(data[labels], data['quality'], test_size=0.2, random_state=42)

# Chuẩn hóa dữ liệu
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Lưu trình biến đổi
joblib.dump(sc, "scaler.pkl")

"""# Mô hình MLP"""

# Xây dựng mô hình MLP
mlp = MLPClassifier(hidden_layer_sizes=(100, 100), activation='relu', max_iter = 1000, random_state=42)
# Huấn luyện mô hình
mlp.fit(X_train, y_train)
# Dự đoán nhãn cho tập kiểm tra
mlp_y_pred = mlp.predict(X_test)

"""#Mô hình ANN"""

#cấu hình mạng lưới nơ ron nhân tạo
ann = Sequential([Dense(192, activation="relu", input_shape=(X_train.shape[1],)),
                    Dense(128, activation="relu"),
                    Dense(3, activation="softmax")])
#biên dịch mạng lưới
ann.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
#huấn luyện mạng lưới
ann.fit(X_train,y_train,epochs=50,validation_data=(X_test, y_test))

# Dự đoán nhãn từ dữ liệu kiểm thử
y_pred = ann.predict(X_test)

# Chuyển đổi đầu ra dự đoán thành nhãn
ann_y_pred = np.argmax(y_pred, axis=1)

"""#RNN"""

#Xây dựng mô hình RNN

rnn = tf.keras.Sequential()
rnn.add(tf.keras.layers.LSTM(32, input_shape=(X_train.shape[1],1)))
rnn.add(tf.keras.layers.Dropout(0.2))
rnn.add(tf.keras.layers.Dense(3, activation='linear'))

# Biên dịch mô hình
rnn.compile(loss='mse', optimizer='adam', metrics=['accuracy'])

# Huấn luyện mô hình
rnn.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# Dự đoán nhãn từ dữ liệu kiểm thử
y_pred1 = rnn.predict(X_test)

# Chuyển đổi đầu ra dự đoán thành nhãn
rnn_y_pred = np.argmax(y_pred1, axis=1)

models = ['MLP', 'ANN', 'RNN']

accuracies = []
y_preds = [mlp_y_pred, ann_y_pred, rnn_y_pred]

# In sai số trung bình và báo cáo phân loại của từng mô hình
for model, y_pred in zip(models, y_preds):
    acc = accuracy_score(y_test, y_pred)
    accuracies.append(acc)

# Accuracy của các mô hình
accuracy_scores = accuracies

# Tạo mảng các chỉ số cho các mô hình
x_indexes = np.arange(len(models))

# Kích thước của mỗi cột
bar_width = 0.35

# Vẽ biểu đồ
plt.figure(figsize=(10, 6))

plt.bar(x_indexes, accuracy_scores, width=bar_width, label='Accuracy')

plt.xlabel('Mô hình')
plt.ylabel('Độ đo')
plt.title('So sánh Accuracy giữa các mô hình')
plt.xticks(x_indexes, models)
plt.legend()
plt.show()

# Create a list of predicted labels for each model
y_pred_list = [mlp_y_pred, ann_y_pred, rnn_y_pred]

# Define class labels
class_labels = ['Lớp 0', 'Lớp 1', 'Lớp 2']

# Define model names
model_names = ['MLP', 'ANN', 'RNN']

# Plot confusion matrices for each model
for i, y_pred in enumerate(y_pred_list):
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_labels, yticklabels=class_labels)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title(f'Confusion Matrix - {model_names[i]}')
    plt.show()

models = ['MLP', 'ANN', 'RNN']
y_preds = [mlp_y_pred, ann_y_pred, rnn_y_pred]

# In sai số trung bình và báo cáo phân loại của từng mô hình
for model, y_pred in zip(models, y_preds):
    report = classification_report(y_test, y_pred)
    print(f"Báo cáo phân loại {model}:\n{report}")
    print()

#@title Lưu mô hình vào tệp tin
joblib.dump(mlp, "wine_model.pkl")