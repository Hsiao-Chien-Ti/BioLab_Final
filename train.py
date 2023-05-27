import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.utils import np_utils
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
from keras.layers import Dense,Dropout,Flatten,Conv2D,MaxPooling2D
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.signal import butter, filtfilt
def filter(data):
    b, a = butter(4, 100,fs=1000, btype='low')
    y = filtfilt(b, a, data)
    return y
path = "training_data"
files=os.listdir(path)
Y_data = np.array([]) 
X_data = np.zeros((0,2000,4))
for f in files:

    path_txt = os.path.join(path, f)
    if(path_txt=='training_data\\plot'):
        continue    
    df = pd.read_csv(path_txt, delimiter = "\t")
    # if(df['class'][0]==6):
    #     continue
    Y_data=np.append(Y_data,df['class'][0])
    df=df.drop(columns=['time'])
    df=df.drop(columns=['class'])
    for k in df.keys():
        df[k]=filter(df[k])    
    df=df.to_numpy().reshape(1,2000,4)

    # df=df*1000
    # print(df.shape)
    X_data = np.concatenate((X_data,df) )
# plt.ylim([1.5,3])
# plt.plot(X_data[0])
# plt.show()
X_data = X_data.reshape(-1, 2000, 4, 1)
Y_data = Y_data.astype(int)
print(Y_data.shape)
print(X_data.shape)
X_train, X_test, Y_train, Y_test = train_test_split(X_data, Y_data, test_size=0.2, random_state=10)
Y_train_onehot = np_utils.to_categorical(Y_train,num_classes=6)
Y_test_onehot = np_utils.to_categorical(Y_test,num_classes=6)
CNN = Sequential(name='CNN')
#第一層卷積
CNN.add(Conv2D(16, (40,1), strides = (10,1), activation='relu', input_shape=(2000,4,1)))
#第一層池化
CNN.add(MaxPooling2D((10,1)))
#第二層卷積
CNN.add(Conv2D(32, (1,2),strides= (1,2), activation='relu'))
#第二層池化
CNN.add(MaxPooling2D((2,1)))
#壓平 4x4x32 = 512
CNN.add(Flatten())
#隱藏層 Dense 神經元數量 512>100>6 因為最後是6類
CNN.add(Dense(100,activation='relu'))
#隨機捨棄神經元，避免overfitting
CNN.add(Dropout(0.3,seed=10))
#輸出層 分類用softmax
CNN.add(Dense(6,activation='softmax'))
CNN.summary()
# model.complie
CNN.compile(optimizer='Adam',
      loss='categorical_crossentropy',
      metrics=['accuracy'])
mcp_save = ModelCheckpoint('model_{}.h5'.format(datetime.strftime(datetime.now(),'%Y_%m_%d_%H_%M_%S')), save_best_only=True, monitor='val_loss', mode='min')
train_history=CNN.fit(x=X_train, 
                      y=Y_train_onehot,
                      validation_split=0.2, 
                      epochs=100, 
                      batch_size=15, 
                      verbose=2,callbacks=[mcp_save])

# CNN.save()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6,12))

# Plot training & validation accuracy values
ax1.plot(train_history.history['accuracy'])
ax1.plot(train_history.history['val_accuracy'])
ax1.set_title('Accuracy')
ax1.set(ylabel='Accuracy', xlabel='Epoch')
ax1.legend(['Train', 'Valid'], loc='upper left')

# Plot training & validation loss values
ax2.plot(train_history.history['loss'])
ax2.plot(train_history.history['val_loss'])
ax2.set_title('Model loss')
ax2.set(ylabel='Loss', xlabel='Epoch')
ax2.legend(['Train', 'Valid'], loc='upper right')

# plt.savefig('train_history.png', dpi=96)  # <-- save plot
plt.show()
scores = CNN.evaluate(X_test, Y_test_onehot)
print('Test Accuracy:', scores[1] )
prediction=np.argmax(CNN.predict(X_test), axis=-1)
print(prediction)
pd.crosstab(Y_test,prediction,
            rownames=['label'],colnames=['predict'])