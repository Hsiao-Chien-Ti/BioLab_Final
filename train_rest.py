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
import random
path_6 = "training_data/new/rest"
file6=os.listdir(path_6)
path_txt = os.path.join(path_6, file6[0])
X_data = pd.read_csv(path_txt, delimiter = "\t")
X_data=X_data.drop(columns=['time'])
X_data=X_data.drop(columns=['class'])
X_data=X_data.to_numpy().reshape(1500,4)

for f in file6:
    if f == file6[0]:
        continue
    path_txt = os.path.join(path_6, f)
    df = pd.read_csv(path_txt, delimiter = "\t")
    df=df.drop(columns=['time'])
    df=df.drop(columns=['class']) 
    df=df.to_numpy().reshape(1500,4)
    X_data = np.concatenate((X_data,df) )
path_7 = "training_data/new/yon-lee"
file7=os.listdir(path_7)
random.shuffle(file7)
for f in range(len(file6)):
    path_txt = os.path.join(path_7, file7[f])
    df = pd.read_csv(path_txt, delimiter = "\t")
    df=df.drop(columns=['time'])
    df=df.drop(columns=['class'])
    df=df.to_numpy().reshape(1500,4)
    X_data = np.concatenate((X_data,df))
X_data = np.array(np.array_split(X_data, np.arange(100, len(X_data), 100)))
Y_data = np.concatenate((np.zeros(len(file6)*15),np.ones(len(file6)*15)))
X_data = X_data.reshape(-1, 100, 4, 1)
Y_data = Y_data.astype(int)
print(Y_data.shape)
print(X_data.shape)
X_train, X_test, Y_train, Y_test = train_test_split(X_data, Y_data, test_size=0.2, random_state=10)
Y_train_onehot = np_utils.to_categorical(Y_train,num_classes=2)
Y_test_onehot = np_utils.to_categorical(Y_test,num_classes=2)
model = Sequential(name='model')
model.add(Conv2D(16,(2,1),activation='relu', input_shape=(100,4,1)))
model.add(MaxPooling2D(2))
model.add(Conv2D(32,(2,1), activation='relu'))
model.add(MaxPooling2D(2))
model.add(Flatten())
model.add(Dense(100,activation='relu'))
model.add(Dropout(0.5,seed=10))
model.add(Dense(2,activation='softmax'))
model.summary()
model.compile(optimizer='Adam',
      loss='categorical_crossentropy',
      metrics=['accuracy'])
mcp_save = ModelCheckpoint('exist_model_{}.h5'.format(datetime.strftime(datetime.now(),'%Y_%m_%d_%H_%M_%S')), save_best_only=True, monitor='val_loss', mode='min')
train_history=model.fit(x=X_train, 
                      y=Y_train_onehot,
                      validation_split=0.2, 
                      epochs=30, 
                      batch_size=15, 
                      verbose=2,callbacks=[mcp_save])
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
scores = model.evaluate(X_test, Y_test_onehot)
print('Test Accuracy:', scores[1] )
prediction=np.argmax(model.predict(X_test), axis=-1)
print(prediction)
pd.crosstab(Y_test,prediction,
            rownames=['label'],colnames=['predict'])